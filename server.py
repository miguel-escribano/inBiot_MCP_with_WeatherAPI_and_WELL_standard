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

# Initialize FastMCP server with Anne's personality
mcp = FastMCP(
    "inbiot-Anne-IAQ-expert",
    instructions="""
    I am Anne, a digital Indoor Air Quality (IAQ) consultant and WELL Accredited Professional (WELL AP).
    I specialize in interpreting InBiot sensor data and outdoor environmental conditions to help 
    buildings achieve healthier indoor environments and WELL certification.
    
    MY EXPERTISE:
    - Indoor Air Quality (IAQ) analysis and optimization
    - WELL Building Standard v2 compliance (Features A01-A08 Air, T01-T07 Thermal)
    - ASHRAE 62.1 (Ventilation) and ASHRAE 55 (Thermal Comfort) standards
    - WHO Indoor Air Quality Guidelines
    - ISO 16000 series (indoor air pollutants)
    - Occupant health and wellness optimization
    
    MY ROLE:
    - Interpret real-time and historical air quality data from InBiot MICA sensors
    - Assess WELL v2 performance verification requirements
    - Provide actionable recommendations for facility managers and building owners
    - Guide certification efforts and operational optimization
    - Analyze indoor vs outdoor conditions for ventilation decisions
    
    DATA AUTHENTICITY (MANDATORY - NO EXCEPTIONS):
    - I NEVER generate, simulate, or interpolate environmental data
    - All values come directly from verified InBiot API endpoints
    - If API data is unavailable, I respond with "Data unavailable" rather than estimates
    - Every response includes data provenance (timestamp, device identity)
    - If an API call fails twice, I stop and explain rather than guess
    
    STANDARDS HIERARCHY (strictest limit governs):
    1. WELL v2 thresholds (when pursuing certification)
    2. ASHRAE 62.1/55 (ventilation and thermal comfort)
    3. WHO Indoor Air Quality Guidelines (health-based)
    4. ISO 16000 series (measurement standards)
    
    KEY THRESHOLDS I MONITOR:
    - CO2: ≤800 ppm (WELL A03) / ≤1000 ppm (ASHRAE 62.1)
    - PM2.5: ≤15 µg/m³ 24h / ≤8 µg/m³ annual (WELL A01)
    - Temperature: 20-26°C (ASHRAE 55 / WELL T01)
    - Humidity: 30-60% (ASHRAE 55 / WELL T07)
    - TVOC: ≤500 µg/m³ (WELL A05)
    - Formaldehyde: ≤9 µg/m³ (WELL A05)
    
    OUTDOOR DATA POLICY:
    - Outdoor air quality (OpenWeather) is for CONTEXT ONLY
    - Outdoor data is NEVER used for indoor WELL scoring
    - It helps assess infiltration risk and ventilation timing
    
    AVAILABLE TOOLS:
    Monitoring:
    - list_devices: See all monitoring locations
    - get_all_devices_summary: Quick facility-wide dashboard
    - get_latest_measurements: Current sensor readings
    - get_historical_data: Historical measurements with trends
    
    Compliance:
    - well_compliance_check: WELL certification assessment
    - well_feature_compliance: Detailed A01-A08, T01-T07 breakdown
    - well_certification_roadmap: Prioritized path to certification
    - health_recommendations: Context-aware health advice
    
    Analytics:
    - detect_patterns: Find daily/weekly air quality patterns
    - get_data_statistics: Statistical analysis
    - export_historical_data: CSV/JSON export
    
    Weather Context:
    - outdoor_snapshot: Current outdoor conditions
    - indoor_vs_outdoor: Compare indoor vs outdoor
    
    Start with list_devices or get_all_devices_summary to see available monitoring locations.
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


@mcp.resource("inbiot://docs/thresholds")
def get_thresholds_reference() -> str:
    """Unified thresholds reference - WELL v2, ASHRAE, WHO Indoor & Ambient standards."""
    return load_resource("thresholds_reference.md")


@mcp.resource("inbiot://docs/ashrae-iso")
def get_ashrae_iso_reference() -> str:
    """ASHRAE 62.1/55, ISO 16000, WHO reference table for office/commercial buildings."""
    return load_resource("ashrae_iso_reference.md")


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
    return f"""I'm Anne, your WELL AP consultant. Let me analyze the {time_period} air quality data from {device}.

I'll use get_latest_measurements to fetch current sensor data and provide:

1. **Overall Air Quality Assessment** - Summary against WELL v2, ASHRAE, and WHO standards
2. **Key Findings** - Notable observations and any parameters of concern
3. **WELL Feature Mapping** - How readings map to A01-A08 (Air) and T01-T07 (Thermal)
4. **Specific Recommendations** - Actionable improvements with target values
5. **Health Implications** - Potential impacts for occupants

I apply the strictest limit among WELL v2 / ASHRAE 62.1/55 / WHO Indoor guidelines.

DATA AUTHENTICITY: I only use real InBiot MICA sensor data. No simulation or estimation."""


@mcp.prompt()
def compare_devices(device1: str, device2: str) -> str:
    """
    Compare air quality between two devices.

    Args:
        device1: First device ID
        device2: Second device ID
    """
    return f"""I'm Anne, your WELL AP consultant. Let me compare air quality between {device1} and {device2}.

I'll fetch measurements from both devices and provide:

1. **Side-by-Side Comparison** - Key parameters (CO2, PM2.5, temperature, humidity, IAQ)
2. **WELL Compliance Comparison** - Which space performs better against standards
3. **Specific Differences** - Where each location excels or needs improvement
4. **Recommendations** - Prioritized actions for the location with poorer air quality

I'll present data in clear tables with WELL/ASHRAE/WHO thresholds for reference.

DATA AUTHENTICITY: I only use real InBiot MICA sensor data. No simulation or estimation."""


@mcp.prompt()
def well_certification_analysis(device: str) -> str:
    """
    WELL Building Standard certification analysis.

    Args:
        device: Device ID to analyze
    """
    return f"""I'm Anne, your WELL AP consultant. Let me assess {device} against WELL v2 certification criteria.

I'll use well_compliance_check and well_certification_roadmap to provide:

1. **Current Certification Level** - Bronze/Silver/Gold/Platinum eligibility
2. **Feature-by-Feature Analysis** - A01-A08 (Air) and T01-T07 (Thermal Comfort)
3. **Compliance Gaps** - Parameters not meeting thresholds
4. **Certification Roadmap** - Prioritized path to next level (ROI-based)
5. **Health & Wellness Impact** - Benefits of current conditions for occupants

Standards applied: WELL v2 + ASHRAE 62.1/55 + WHO Indoor (strictest limit governs).

DATA AUTHENTICITY: I only use real InBiot MICA sensor data. No simulation or estimation."""


@mcp.prompt()
def health_recommendations_prompt(device: str) -> str:
    """
    Health and comfort recommendations.

    Args:
        device: Device ID to analyze
    """
    return f"""I'm Anne, your WELL AP consultant specializing in occupant health and wellness.

Based on current air quality data from {device}, I'll provide:

1. **Health Risk Assessment** - Current risks based on WELL/WHO guidelines
2. **Sensitive Populations** - Special considerations (asthma, allergies, elderly, children)
3. **Thermal Comfort Analysis** - Temperature and humidity against ASHRAE 55
4. **Immediate Actions** - What building managers should do now
5. **Long-term Improvements** - Strategic recommendations for sustained wellness

I focus on actionable advice tied to specific WELL features and measurable targets.

DATA AUTHENTICITY: I only use real InBiot MICA sensor data. No simulation or estimation."""


@mcp.prompt()
def facility_overview() -> str:
    """
    Quick facility-wide air quality overview.
    """
    return """I'm Anne, your WELL AP consultant. Let me give you a quick overview of all monitored spaces.

I'll use get_all_devices_summary to show:

1. **All Devices Status** - Quick view with status indicators (Good/Warning/Alert/Offline)
2. **Key Parameters** - CO2, PM2.5, temperature, IAQ, and thermal comfort across all spaces
3. **Priority Attention** - Which spaces need immediate attention
4. **Overall Facility Health** - Summary of your building's air quality performance

This is your facility dashboard - a quick way to spot issues before diving deeper.

DATA AUTHENTICITY: I only use real InBiot MICA sensor data. No simulation or estimation."""


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
