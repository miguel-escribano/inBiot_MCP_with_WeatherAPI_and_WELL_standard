"""
InBiot MCP Server

A Model Context Protocol server for air quality monitoring and WELL Building Standard compliance.
Built with FastMCP.
"""

import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

from src.api.inbiot import InBiotClient
from src.well.compliance import WELLComplianceEngine
from src.config.loader import ConfigLoader
from src.config.validator import validate_devices, print_validation_warnings

# Import skills
from src.skills.monitoring import register_monitoring_tools
from src.skills.analytics import register_analytics_tools
from src.skills.compliance import register_compliance_tools
from src.skills.weather import register_weather_tools


# ============================================================================
# CONFIGURATION
# ============================================================================


def load_devices():
    """
    Load device configurations from YAML, JSON, or environment variables.

    Priority:
    1. inbiot-config.yaml
    2. inbiot-config.json
    3. Environment variables (INBIOT_*_API_KEY, etc.)

    Returns:
        Dictionary mapping device IDs to DeviceConfig objects
    """
    try:
        devices = ConfigLoader.load()

        # Validate configuration and print warnings
        warnings = validate_devices(devices)
        if warnings:
            print_validation_warnings(warnings)

        return devices
    except Exception as e:
        print(f"Error loading device configuration: {e}")
        raise


def load_resource(filename: str) -> str:
    """Load a resource file content."""
    resource_path = Path(__file__).parent / "resources" / filename
    if resource_path.exists():
        return resource_path.read_text(encoding="utf-8")
    return f"Resource not found: {filename}"


# ============================================================================
# INITIALIZATION
# ============================================================================

# Load devices and initialize clients
DEVICES = load_devices()
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
# REGISTER SKILLS
# ============================================================================

# Register monitoring tools (list_devices, get_latest_measurements, get_historical_data)
register_monitoring_tools(mcp, DEVICES, inbiot_client)

# Register analytics tools (get_data_statistics, export_historical_data)
register_analytics_tools(mcp, DEVICES, inbiot_client)

# Register compliance tools (well_compliance_check, well_feature_compliance, health_recommendations)
register_compliance_tools(mcp, DEVICES, inbiot_client, well_engine)

# Register weather tools (outdoor_snapshot, indoor_vs_outdoor)
register_weather_tools(mcp, DEVICES, inbiot_client)


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


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
