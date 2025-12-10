"""
InBiot MCP Server

A Model Context Protocol server for air quality monitoring and WELL Building Standard compliance.
Built with FastMCP.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Annotated

from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import Field

# Load environment variables from .env file
load_dotenv()

from src.api.inbiot import InBiotClient, InBiotAPIError
from src.api.openweather import OpenWeatherClient, OpenWeatherAPIError
from src.models.schemas import DeviceConfig
from src.well.compliance import WELLComplianceEngine
from src.utils.provenance import (
    generate_provenance,
    create_data_unavailable_error,
    generate_outdoor_provenance,
)


# Load device configuration
def load_devices() -> dict[str, DeviceConfig]:
    """Load device configurations entirely from environment variables."""
    devices = {}
    
    # Find all device IDs by looking for INBIOT_*_API_KEY patterns
    device_ids = set()
    for key in os.environ:
        if key.startswith("INBIOT_") and key.endswith("_API_KEY"):
            # Extract device ID: INBIOT_{DEVICE_ID}_API_KEY
            device_id = key[7:-8]  # Remove "INBIOT_" prefix and "_API_KEY" suffix
            device_ids.add(device_id)
    
    for device_id in device_ids:
        api_key = os.environ.get(f"INBIOT_{device_id}_API_KEY")
        system_id = os.environ.get(f"INBIOT_{device_id}_SYSTEM_ID")
        
        if not api_key or not system_id:
            continue
        
        # Get optional metadata
        name = os.environ.get(f"INBIOT_{device_id}_NAME", device_id.replace("_", " ").title())
        lat = float(os.environ.get(f"INBIOT_{device_id}_LAT", "0"))
        lon = float(os.environ.get(f"INBIOT_{device_id}_LON", "0"))
        
        devices[device_id] = DeviceConfig(
            name=name,
            api_key=api_key,
            system_id=system_id,
            coordinates=(lat, lon),
        )
    
    return devices


# Load resources from files
def load_resource(filename: str) -> str:
    """Load a resource file content."""
    resource_path = Path(__file__).parent / "resources" / filename
    if resource_path.exists():
        return resource_path.read_text(encoding="utf-8")
    return f"Resource not found: {filename}"


# Initialize components
DEVICES = load_devices()
DEVICE_NAMES = list(DEVICES.keys())
inbiot_client = InBiotClient()
well_engine = WELLComplianceEngine()

# Initialize FastMCP server
mcp = FastMCP(
    "InBiot MCP Server",
    instructions="""
    InBiot MCP Server provides air quality monitoring and WELL Building Standard compliance analysis.
    
    IMPORTANT DATA AUTHENTICITY RULES:
    - All data comes from real InBiot MICA sensors - NO simulated data
    - Every response includes mandatory data provenance
    - If API calls fail, analysis is terminated rather than using estimates
    
    Available capabilities:
    - Get latest and historical air quality measurements
    - Assess WELL Building Standard compliance
    - Compare indoor vs outdoor conditions
    - Generate health recommendations
    
    Use list_devices to see available monitoring locations.
    """,
)


# ============================================================================
# TOOLS
# ============================================================================


@mcp.tool()
def list_devices() -> str:
    """
    List all available InBiot air quality monitoring devices.

    Returns a list of device IDs and their human-readable names.
    """
    device_list = []
    for device_id, config in DEVICES.items():
        device_list.append(f"- **{device_id}**: {config.name}")

    return "## Available Devices\n\n" + "\n".join(device_list)


@mcp.tool()
async def get_latest_measurements(
    device: Annotated[str, Field(description="Device ID (use list_devices to see options)")]
) -> str:
    """
    Get the latest air quality measurements from an InBiot device.

    Returns current values for all monitored parameters including temperature,
    humidity, CO2, particulate matter, VOCs, and composite indicators.
    """
    if device not in DEVICES:
        return f"Unknown device: {device}. Use list_devices to see available options."

    device_config = DEVICES[device]
    endpoint = f"/last-measurements/{device_config.api_key}/{device_config.system_id}"

    try:
        data = await inbiot_client.get_latest_measurements(device_config)

        # Format results
        result = f"## Latest Measurements: {device_config.name}\n\n"
        result += "| Parameter | Value | Unit |\n|-----------|-------|------|\n"

        for param in data:
            if param.latest_value is not None:
                result += f"| {param.type} | {param.latest_value} | {param.unit} |\n"

        # Add provenance
        result += generate_provenance(
            device_name=device_config.name,
            device_api_key=device_config.api_key,
            endpoint=endpoint,
            data=data,
            analysis_type="Latest Measurements",
        )

        return result

    except InBiotAPIError as e:
        return create_data_unavailable_error(
            device_name=device_config.name,
            error_message=e.message,
            endpoint=endpoint,
        )


@mcp.tool()
async def get_historical_data(
    device: Annotated[str, Field(description="Device ID")],
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD or ISO-8601)")],
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD or ISO-8601)")],
) -> str:
    """
    Get historical air quality measurements from an InBiot device.

    Retrieves measurements between the specified dates.
    Note: InBiot API is rate-limited to 6 requests per device per hour.
    """
    if device not in DEVICES:
        return f"Unknown device: {device}. Use list_devices to see available options."

    device_config = DEVICES[device]

    # Parse dates
    try:
        if "T" in start_date:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        else:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        if "T" in end_date:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        else:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59
            )
    except ValueError as e:
        return f"Invalid date format: {e}. Use YYYY-MM-DD or ISO-8601 format."

    endpoint = f"/measurements-by-time/{device_config.api_key}/{device_config.system_id}/..."

    try:
        data = await inbiot_client.get_historical_data(device_config, start_dt, end_dt)

        # Format results
        result = f"## Historical Data: {device_config.name}\n\n"
        result += f"**Period**: {start_date} to {end_date}\n\n"

        for param in data:
            if param.measurements:
                result += f"### {param.type} ({param.unit})\n"
                result += f"- Measurements: {len(param.measurements)}\n"
                if param.latest_value is not None:
                    result += f"- Latest value: {param.latest_value}\n"
                result += "\n"

        # Add provenance
        result += generate_provenance(
            device_name=device_config.name,
            device_api_key=device_config.api_key,
            endpoint=endpoint,
            data=data,
            analysis_type="Historical Data",
        )

        return result

    except InBiotAPIError as e:
        return create_data_unavailable_error(
            device_name=device_config.name,
            error_message=e.message,
            endpoint=endpoint,
        )


@mcp.tool()
async def well_compliance_check(
    device: Annotated[str, Field(description="Device ID to check WELL compliance for")]
) -> str:
    """
    Assess WELL Building Standard compliance for an InBiot device.

    Evaluates current air quality against WELL v2, ASHRAE 62.1/55, and WHO Indoor
    standards. Returns certification level eligibility and parameter-by-parameter assessment.
    """
    if device not in DEVICES:
        return f"Unknown device: {device}. Use list_devices to see available options."

    device_config = DEVICES[device]
    endpoint = f"/last-measurements/{device_config.api_key}/{device_config.system_id}"

    try:
        data = await inbiot_client.get_latest_measurements(device_config)
        assessment = well_engine.assess(device_config.name, data)

        # Format results
        result = f"## WELL Compliance Assessment: {device_config.name}\n\n"
        result += f"### Overall Score: {assessment.overall_score}/{assessment.max_score} ({assessment.percentage}%)\n"
        result += f"### Certification Level: **{assessment.well_level}**\n\n"

        result += "### Parameter Assessment\n\n"
        result += "| Parameter | Value | Level | WELL Compliant |\n"
        result += "|-----------|-------|-------|----------------|\n"

        for param in assessment.parameters:
            compliant = "✅" if param.well_compliant else "❌"
            result += f"| {param.parameter} | {param.value} {param.unit} | {param.level} | {compliant} |\n"

        result += "\n### Recommendations\n\n"
        for rec in assessment.recommendations:
            result += f"- {rec}\n"

        # Add provenance
        result += generate_provenance(
            device_name=device_config.name,
            device_api_key=device_config.api_key,
            endpoint=endpoint,
            data=data,
            analysis_type="WELL Compliance Assessment",
        )

        return result

    except InBiotAPIError as e:
        return create_data_unavailable_error(
            device_name=device_config.name,
            error_message=e.message,
            endpoint=endpoint,
        )


@mcp.tool()
async def outdoor_snapshot(
    device: Annotated[str, Field(description="Device ID (uses device coordinates for location)")]
) -> str:
    """
    Get current outdoor weather and air quality conditions.

    Uses the device's configured coordinates to fetch outdoor data from OpenWeather.
    This data is for contextual comparison only - NOT used for WELL indoor scoring.
    """
    if device not in DEVICES:
        return f"Unknown device: {device}. Use list_devices to see available options."

    device_config = DEVICES[device]
    lat, lon = device_config.coordinates

    try:
        openweather = OpenWeatherClient()
        conditions = await openweather.get_outdoor_conditions(
            lat=lat,
            lon=lon,
            location_name=device_config.name,
        )

        # Format results
        result = f"## Outdoor Conditions near {device_config.name}\n\n"

        result += "### Weather\n\n"
        result += f"- **Temperature**: {conditions.temperature}°C\n"
        result += f"- **Humidity**: {conditions.humidity}%\n"
        result += f"- **Pressure**: {conditions.pressure} hPa\n"
        result += f"- **Wind**: {conditions.wind_speed} m/s\n"
        result += f"- **Conditions**: {conditions.description}\n\n"

        result += "### Air Quality\n\n"
        aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        result += f"- **AQI**: {conditions.aqi} ({aqi_labels.get(conditions.aqi, 'Unknown')})\n"
        result += f"- **PM2.5**: {conditions.pm25} µg/m³\n"
        result += f"- **PM10**: {conditions.pm10} µg/m³\n"
        result += f"- **O₃**: {conditions.o3} µg/m³\n"
        result += f"- **NO₂**: {conditions.no2} µg/m³\n"
        result += f"- **CO**: {conditions.co} µg/m³\n"

        result += generate_outdoor_provenance(
            location=device_config.name,
            coordinates=device_config.coordinates,
            endpoint="/data/2.5/weather + /data/2.5/air_pollution",
        )

        return result

    except OpenWeatherAPIError as e:
        return f"## Outdoor Data Unavailable\n\n**Error**: {e.message}\n\nSet OPENWEATHER_API_KEY environment variable to enable outdoor data."


@mcp.tool()
async def indoor_vs_outdoor(
    device: Annotated[str, Field(description="Device ID for comparison")]
) -> str:
    """
    Compare indoor air quality with outdoor conditions.

    Shows side-by-side comparison of key parameters and calculates
    filtration effectiveness. Useful for understanding building envelope performance.
    """
    if device not in DEVICES:
        return f"Unknown device: {device}. Use list_devices to see available options."

    device_config = DEVICES[device]
    lat, lon = device_config.coordinates

    # Get indoor data
    try:
        indoor_data = await inbiot_client.get_latest_measurements(device_config)
    except InBiotAPIError as e:
        return create_data_unavailable_error(
            device_name=device_config.name,
            error_message=e.message,
        )

    # Get outdoor data
    try:
        openweather = OpenWeatherClient()
        outdoor = await openweather.get_outdoor_conditions(lat, lon, device_config.name)
    except OpenWeatherAPIError as e:
        return f"## Comparison Unavailable\n\nIndoor data retrieved but outdoor data failed: {e.message}"

    # Build comparison
    result = f"## Indoor vs Outdoor Comparison: {device_config.name}\n\n"

    # Create lookup for indoor values
    indoor_values = {}
    for param in indoor_data:
        if param.latest_value is not None:
            indoor_values[param.type.lower()] = (param.latest_value, param.unit)

    result += "| Parameter | Indoor | Outdoor | Δ (Indoor-Outdoor) | Assessment |\n"
    result += "|-----------|--------|---------|-------------------|------------|\n"

    # Temperature
    if "temperature" in indoor_values and outdoor.temperature:
        indoor_temp, unit = indoor_values["temperature"]
        delta = indoor_temp - outdoor.temperature
        assessment = "Controlled" if abs(delta) > 2 else "Similar"
        result += f"| Temperature | {indoor_temp}°C | {outdoor.temperature}°C | {delta:+.1f}°C | {assessment} |\n"

    # Humidity
    if "humidity" in indoor_values and outdoor.humidity:
        indoor_hum, unit = indoor_values["humidity"]
        delta = indoor_hum - outdoor.humidity
        assessment = "Controlled" if abs(delta) > 10 else "Similar"
        result += f"| Humidity | {indoor_hum}% | {outdoor.humidity}% | {delta:+.1f}% | {assessment} |\n"

    # PM2.5
    if "pm25" in indoor_values and outdoor.pm25:
        indoor_pm, unit = indoor_values["pm25"]
        delta = indoor_pm - outdoor.pm25
        if outdoor.pm25 > 0:
            reduction = ((outdoor.pm25 - indoor_pm) / outdoor.pm25) * 100
            assessment = f"{reduction:.0f}% reduction" if reduction > 0 else "Higher indoors"
        else:
            assessment = "N/A"
        result += f"| PM2.5 | {indoor_pm} µg/m³ | {outdoor.pm25} µg/m³ | {delta:+.1f} | {assessment} |\n"

    # PM10
    if "pm10" in indoor_values and outdoor.pm10:
        indoor_pm, unit = indoor_values["pm10"]
        delta = indoor_pm - outdoor.pm10
        if outdoor.pm10 > 0:
            reduction = ((outdoor.pm10 - indoor_pm) / outdoor.pm10) * 100
            assessment = f"{reduction:.0f}% reduction" if reduction > 0 else "Higher indoors"
        else:
            assessment = "N/A"
        result += f"| PM10 | {indoor_pm} µg/m³ | {outdoor.pm10} µg/m³ | {delta:+.1f} | {assessment} |\n"

    result += "\n*Note: Outdoor data is for context only and is NOT used for WELL indoor scoring.*\n"

    return result


@mcp.tool()
async def health_recommendations(
    device: Annotated[str, Field(description="Device ID to generate recommendations for")]
) -> str:
    """
    Generate health and comfort recommendations based on current air quality.

    Provides actionable advice for building managers and occupants based on
    current sensor readings and WELL Building Standard guidelines.
    """
    if device not in DEVICES:
        return f"Unknown device: {device}. Use list_devices to see available options."

    device_config = DEVICES[device]

    try:
        data = await inbiot_client.get_latest_measurements(device_config)
        assessment = well_engine.assess(device_config.name, data)

        result = f"## Health Recommendations: {device_config.name}\n\n"

        # Overall status
        if assessment.percentage >= 75:
            result += "### Overall Status: ✅ Good\n\n"
            result += "Air quality conditions are favorable for occupant health and productivity.\n\n"
        elif assessment.percentage >= 50:
            result += "### Overall Status: ⚠️ Moderate\n\n"
            result += "Some parameters need attention. Review recommendations below.\n\n"
        else:
            result += "### Overall Status: ❌ Needs Improvement\n\n"
            result += "Multiple air quality issues detected. Immediate action recommended.\n\n"

        # Specific recommendations
        result += "### Specific Recommendations\n\n"

        for param in assessment.parameters:
            if param.score <= 1:
                result += f"**🔴 {param.parameter.upper()}** ({param.value} {param.unit})\n"
                result += f"- Status: {param.level}\n"
                result += f"- Action: Immediate intervention required\n"
                result += _get_parameter_advice(param.parameter, "critical")
                result += "\n"
            elif param.score == 2:
                result += f"**🟡 {param.parameter.upper()}** ({param.value} {param.unit})\n"
                result += f"- Status: {param.level}\n"
                result += _get_parameter_advice(param.parameter, "moderate")
                result += "\n"

        # General advice
        result += "### General Guidance\n\n"
        result += "- Monitor air quality trends over time\n"
        result += "- Ensure HVAC systems are properly maintained\n"
        result += "- Consider air purifiers for high-traffic areas\n"
        result += "- Communicate with occupants about air quality status\n"

        return result

    except InBiotAPIError as e:
        return create_data_unavailable_error(
            device_name=device_config.name,
            error_message=e.message,
        )


def _get_parameter_advice(parameter: str, severity: str) -> str:
    """Get specific advice for a parameter."""
    advice = {
        "co2": {
            "critical": "- Increase ventilation immediately\n- Check HVAC operation\n- Consider reducing occupancy",
            "moderate": "- Review ventilation settings\n- Monitor occupancy levels",
        },
        "pm25": {
            "critical": "- Activate air filtration\n- Check for pollution sources\n- Consider limiting outdoor air intake if outdoor levels are high",
            "moderate": "- Review filter maintenance schedule\n- Check for dust sources",
        },
        "temperature": {
            "critical": "- Adjust HVAC setpoints\n- Check for equipment malfunctions",
            "moderate": "- Fine-tune temperature settings\n- Consider occupant feedback",
        },
        "humidity": {
            "critical": "- Activate humidification/dehumidification\n- Check for water intrusion or leaks",
            "moderate": "- Monitor humidity trends\n- Review HVAC humidity control",
        },
    }
    return advice.get(parameter, {}).get(severity, "- Review parameter and consult guidelines")


# ============================================================================
# RESOURCES
# ============================================================================


@mcp.resource("inbiot://docs/parameters")
def get_parameters_reference() -> str:
    """Air quality parameters reference guide."""
    return load_resource("parameters.md")


@mcp.resource("inbiot://docs/well-standards")
def get_well_standards() -> str:
    """WELL Building Standard air quality criteria."""
    return load_resource("well_standards.md")


@mcp.resource("inbiot://docs/iaq")
def get_iaq_guide() -> str:
    """InBiot Indoor Air Quality Indicator guide."""
    return load_resource("indicators/iaq.md")


@mcp.resource("inbiot://docs/thermal-comfort")
def get_thermal_guide() -> str:
    """InBiot Thermal Comfort Indicator guide."""
    return load_resource("indicators/thermal.md")


@mcp.resource("inbiot://docs/virus-resistance")
def get_virus_guide() -> str:
    """InBiot Virus Resistance Indicator guide."""
    return load_resource("indicators/virus.md")


@mcp.resource("inbiot://docs/ventilation")
def get_ventilation_guide() -> str:
    """InBiot Ventilation Efficiency Indicator guide."""
    return load_resource("indicators/ventilation.md")


# ============================================================================
# PROMPTS
# ============================================================================


@mcp.prompt()
def air_quality_analysis(device: str, time_period: str = "latest") -> str:
    """
    Comprehensive air quality analysis prompt.

    Args:
        device: Device ID to analyze
        time_period: Time period (latest, today, week)
    """
    return f"""You are an air quality expert analyzing data from the {device} InBiot device.

Please analyze the {time_period} measurements and provide:

1. **Overall Air Quality Assessment** - Summary of current conditions
2. **Key Findings** - Notable observations and concerns
3. **Trends or Patterns** - Any patterns you notice in the data
4. **Specific Recommendations** - Actionable improvements
5. **Health Implications** - Potential health impacts for occupants

Use the get_latest_measurements tool to fetch current data for the {device} device.
Apply WELL Building Standard criteria for your assessment.

IMPORTANT: Only use real sensor data. Do not estimate or simulate values."""


@mcp.prompt()
def compare_devices(device1: str, device2: str) -> str:
    """
    Compare air quality between two devices.

    Args:
        device1: First device ID
        device2: Second device ID
    """
    return f"""You are an air quality expert. Compare the air quality between {device1} and {device2}.

Use the get_latest_measurements tool for both devices and provide:

1. **Side-by-Side Comparison** - Key parameters from both locations
2. **Overall Winner** - Which location has better air quality
3. **Specific Differences** - Where each location excels or needs improvement
4. **Recommendations** - Suggestions for the location with poorer air quality

Present your analysis in a clear, structured format with specific data points.

IMPORTANT: Only use real sensor data. Do not estimate or simulate values."""


@mcp.prompt()
def well_certification_analysis(device: str) -> str:
    """
    WELL Building Standard certification analysis.

    Args:
        device: Device ID to analyze
    """
    return f"""You are a WELL Building Standard expert. Analyze the current air quality data from {device} against WELL certification criteria.

Use the well_compliance_check tool to get the assessment, then provide:

1. **WELL Certification Level** - Current eligibility status
2. **Parameter-by-Parameter Analysis** - Detailed breakdown
3. **Compliance Gaps** - What needs improvement for higher certification
4. **Health and Wellness Impact** - Benefits of current conditions
5. **Priority Actions** - Most impactful improvements

Format your response as a professional building assessment report.

IMPORTANT: Only use real sensor data. Do not estimate or simulate values."""


@mcp.prompt()
def health_recommendations_prompt(device: str) -> str:
    """
    Health and comfort recommendations.

    Args:
        device: Device ID to analyze
    """
    return f"""You are a public health expert specializing in indoor air quality.

Based on the current air quality data from {device}, provide specific health and comfort recommendations.

Use the get_latest_measurements tool to get current data, then provide:

1. **Health Risk Assessment** - Current risks for occupants
2. **Sensitive Individuals** - Special considerations for vulnerable groups
3. **Comfort Optimization** - How to improve occupant comfort
4. **Immediate Actions** - What to do right now
5. **Long-term Improvements** - Strategic recommendations

Focus on actionable advice that building managers can implement.

IMPORTANT: Only use real sensor data. Do not estimate or simulate values."""


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    mcp.run()
