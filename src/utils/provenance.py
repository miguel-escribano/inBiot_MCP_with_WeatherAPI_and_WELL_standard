"""Data provenance and authenticity tracking.

This module ensures all data outputs include mandatory provenance information
to prevent use of simulated or estimated data.
"""

from datetime import datetime, timezone
from typing import Optional

from src.models.schemas import ParameterData


def generate_provenance(
    device_name: str,
    device_api_key: str,
    endpoint: str,
    data: list[ParameterData],
    analysis_type: str = "Data Retrieval",
) -> str:
    """
    Generate mandatory data provenance footer.

    Args:
        device_name: Human-readable device name
        device_api_key: API key (will be truncated for security)
        endpoint: API endpoint that was called
        data: List of parameter data retrieved
        analysis_type: Type of analysis performed

    Returns:
        Formatted provenance string
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # Get data timestamp from first measurement
    data_date = "Unknown"
    if data and data[0].measurements:
        data_date = data[0].latest_timestamp.isoformat() if data[0].latest_timestamp else "Unknown"

    # Get sample parameter values
    sample_params = []
    for param in data[:3]:
        if param.latest_value is not None:
            sample_params.append(f"{param.type}: {param.latest_value} {param.unit}")

    # Truncate API key for security
    truncated_key = f"{device_api_key[:8]}..." if device_api_key else "N/A"

    return f"""

---
## DATA PROVENANCE & TRACEABILITY

**VERIFIED REAL DATA** - This analysis is based on authenticated sensor data only

| Field | Value |
|-------|-------|
| Live API Call | `{endpoint}` |
| Device Identity | {device_name} (API Key: `{truncated_key}`) |
| Sensor Data Collected | {data_date} |
| Analysis Type | {analysis_type} |
| Processing Time | {timestamp} |
| Sample Values | {', '.join(sample_params) if sample_params else 'N/A'} |
| Parameters Count | {len(data)} measurements |

**NO SIMULATED DATA** - All values above are from actual InBiot MICA sensors

*Any response without this provenance footer contains unreliable data and should be disregarded.*
"""


def create_data_unavailable_error(
    device_name: str,
    error_message: str,
    endpoint: Optional[str] = None,
) -> str:
    """
    Create error response when data is unavailable.

    This ensures no simulated data is generated when API calls fail.

    Args:
        device_name: Name of the device
        error_message: Error description
        endpoint: Optional endpoint that failed

    Returns:
        Formatted error message
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    return f"""
## DATA UNAVAILABLE - ANALYSIS CANNOT PROCEED

| Field | Value |
|-------|-------|
| Device | {device_name} |
| Error Time | {timestamp} |
| Issue | {error_message} |
| Endpoint | {endpoint or 'N/A'} |

**CRITICAL WARNING**: No real sensor data is available. Analysis has been **TERMINATED** to prevent use of simulated or estimated data.

**Required Actions:**
1. Verify InBiot API connectivity
2. Check device sensor status
3. Confirm network connectivity
4. Retry request when sensor data is available

**NO ENVIRONMENTAL ANALYSIS PROVIDED** - Real data required for all assessments.
"""


def generate_outdoor_provenance(
    location: str,
    coordinates: tuple[float, float],
    endpoint: str,
) -> str:
    """
    Generate provenance for outdoor data.

    Args:
        location: Location name
        coordinates: Lat/lon tuple
        endpoint: OpenWeather endpoint used

    Returns:
        Formatted provenance string
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    return f"""

---
## OUTDOOR DATA PROVENANCE

| Field | Value |
|-------|-------|
| Source | OpenWeather API |
| Endpoint | `{endpoint}` |
| Location | {location} |
| Coordinates | {coordinates[0]:.6f}, {coordinates[1]:.6f} |
| Retrieved | {timestamp} |

**Note**: Outdoor data is for contextual comparison only and is NOT used for WELL indoor scoring.
"""

