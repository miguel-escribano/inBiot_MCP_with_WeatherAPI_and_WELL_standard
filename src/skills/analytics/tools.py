"""Analytics tools for statistical analysis and data export."""

from datetime import datetime
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from src.api.inbiot import InBiotClient, InBiotAPIError
from src.models.schemas import DeviceConfig
from src.utils.provenance import create_data_unavailable_error
from src.utils.aggregation import DataAggregator
from src.utils.exporters import CSVExporter, JSONExporter


def register_analytics_tools(
    mcp: FastMCP,
    devices: dict[str, DeviceConfig],
    inbiot_client: InBiotClient,
):
    """Register analytics tools with the MCP server."""

    @mcp.tool()
    async def get_data_statistics(
        device: Annotated[str, Field(description="Device ID")],
        start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")],
        end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")],
    ) -> str:
        """
        Get comprehensive statistical analysis of historical data.

        Returns min, max, mean, median, std dev, quartiles, and trend analysis
        for each air quality parameter over the specified time range.
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

        try:
            data = await inbiot_client.get_historical_data(device_config, start_dt, end_dt)

            aggregator = DataAggregator()
            result = f"## Statistical Analysis: {device_config.name}\n\n"
            result += f"**Period**: {start_date} to {end_date}\n\n"

            for param in data:
                if param.measurements:
                    stats = aggregator.calculate_statistics(param.measurements)
                    trends = aggregator.detect_trends(param.measurements)

                    result += f"### {param.type} ({param.unit})\n\n"

                    # Statistics table
                    result += "| Statistic | Value |\n"
                    result += "|-----------|-------|\n"
                    result += f"| Count | {stats['count']} |\n"
                    result += f"| Min | {stats['min']:.2f} |\n"
                    result += f"| Max | {stats['max']:.2f} |\n"
                    result += f"| Mean | {stats['mean']:.2f} |\n"
                    result += f"| Median | {stats['median']:.2f} |\n"
                    result += f"| Std Dev | {stats['std_dev']:.2f} |\n"

                    if stats["q1"] is not None:
                        result += f"| Q1 (25th %) | {stats['q1']:.2f} |\n"
                        result += f"| Q3 (75th %) | {stats['q3']:.2f} |\n"

                    # Trend analysis
                    result += "\n**Trend Analysis**:\n"
                    result += f"- Direction: {trends['trend'].upper()}\n"
                    result += f"- Change: {trends['change_percentage']:+.1f}%\n"
                    result += f"- First half average: {trends['first_half_avg']}\n"
                    result += f"- Second half average: {trends['second_half_avg']}\n\n"

            return result

        except InBiotAPIError as e:
            return create_data_unavailable_error(
                device_name=device_config.name,
                error_message=e.message,
            )

    @mcp.tool()
    async def export_historical_data(
        device: Annotated[str, Field(description="Device ID")],
        start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")],
        end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")],
        format: Annotated[str, Field(description="Export format: 'csv' or 'json'")] = "csv",
        aggregation: Annotated[
            str, Field(description="Aggregation period: 'none', 'hourly', 'daily', or 'weekly'")
        ] = "none",
    ) -> str:
        """
        Export historical air quality data in CSV or JSON format.

        Supports raw measurements or time-aggregated data with statistics.
        Useful for external analysis, reporting, or archival purposes.
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

        # Validate format
        if format not in ["csv", "json"]:
            return "Invalid format. Use 'csv' or 'json'."

        # Validate aggregation
        if aggregation not in ["none", "hourly", "daily", "weekly"]:
            return "Invalid aggregation. Use 'none', 'hourly', 'daily', or 'weekly'."

        try:
            data = await inbiot_client.get_historical_data(device_config, start_dt, end_dt)

            if aggregation == "none":
                # Export raw measurements
                if format == "csv":
                    return CSVExporter.export_measurements(data)
                else:
                    return JSONExporter.export_measurements(data)
            else:
                # Export aggregated data
                aggregator = DataAggregator()
                result = f"## Aggregated Data Export: {device_config.name}\n\n"
                result += f"**Period**: {start_date} to {end_date}\n"
                result += f"**Aggregation**: {aggregation}\n\n"

                for param in data:
                    if param.measurements:
                        aggregated = aggregator.aggregate_by_period(
                            param.measurements, aggregation
                        )

                        result += f"### {param.type} ({param.unit})\n\n"

                        if format == "csv":
                            result += "```csv\n"
                            result += CSVExporter.export_aggregated_by_period(aggregated)
                            result += "```\n\n"
                        else:
                            result += "```json\n"
                            result += JSONExporter.export_aggregated_by_period(
                                param.type, param.unit, aggregation, aggregated
                            )
                            result += "```\n\n"

                return result

        except InBiotAPIError as e:
            return create_data_unavailable_error(
                device_name=device_config.name,
                error_message=e.message,
            )
