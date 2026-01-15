"""Monitoring tools for real-time and historical air quality data."""

from datetime import datetime
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from src.api.inbiot import InBiotClient, InBiotAPIError
from src.models.schemas import DeviceConfig
from src.utils.provenance import (
    generate_provenance,
    create_data_unavailable_error,
)
from src.utils.aggregation import DataAggregator


def register_monitoring_tools(
    mcp: FastMCP,
    devices: dict[str, DeviceConfig],
    inbiot_client: InBiotClient,
):
    """Register monitoring tools with the MCP server."""

    @mcp.tool()
    def list_devices() -> str:
        """
        List all available InBiot air quality monitoring devices.

        Returns a list of device IDs and their human-readable names.
        """
        device_list = []
        for device_id, config in devices.items():
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
        if device not in devices:
            return f"Unknown device: {device}. Use list_devices to see available options."

        device_config = devices[device]
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
        if device not in devices:
            return f"Unknown device: {device}. Use list_devices to see available options."

        device_config = devices[device]

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

            # Statistics summary
            aggregator = DataAggregator()
            result += "### Quick Statistics\n\n"
            result += "| Parameter | Count | Min | Max | Mean |\n"
            result += "|-----------|-------|-----|-----|------|\n"

            for param in data:
                if param.measurements:
                    stats = aggregator.calculate_statistics(param.measurements)
                    result += f"| {param.type} ({param.unit}) | {stats['count']} | {stats['min']:.1f} | {stats['max']:.1f} | {stats['mean']:.1f} |\n"

            result += "\n### Detailed Breakdown\n\n"

            for param in data:
                if param.measurements:
                    stats = aggregator.calculate_statistics(param.measurements)
                    trends = aggregator.detect_trends(param.measurements)

                    result += f"#### {param.type} ({param.unit})\n"
                    result += f"- **Measurements**: {len(param.measurements)}\n"
                    result += f"- **Latest value**: {param.latest_value}\n"
                    result += f"- **Range**: {stats['min']:.1f} - {stats['max']:.1f}\n"
                    result += f"- **Average**: {stats['mean']:.1f}\n"
                    result += f"- **Trend**: {trends['trend']} ({trends['change_percentage']:+.1f}%)\n"
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
