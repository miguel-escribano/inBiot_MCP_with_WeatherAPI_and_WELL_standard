"""Compliance tools for WELL Building Standard assessment."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from src.api.inbiot import InBiotClient, InBiotAPIError
from src.models.schemas import DeviceConfig
from src.well.compliance import WELLComplianceEngine
from src.utils.provenance import (
    generate_provenance,
    create_data_unavailable_error,
)


def register_compliance_tools(
    mcp: FastMCP,
    devices: dict[str, DeviceConfig],
    inbiot_client: InBiotClient,
    well_engine: WELLComplianceEngine,
):
    """Register compliance tools with the MCP server."""

    @mcp.tool()
    async def well_compliance_check(
        device: Annotated[str, Field(description="Device ID to check WELL compliance for")]
    ) -> str:
        """
        Assess WELL Building Standard compliance for an InBiot device.

        Evaluates current air quality against WELL v2, ASHRAE 62.1/55, and WHO Indoor
        standards. Returns certification level eligibility and parameter-by-parameter assessment.
        """
        if device not in devices:
            return f"Unknown device: {device}. Use list_devices to see available options."

        device_config = devices[device]
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
    async def well_feature_compliance(
        device: Annotated[str, Field(description="Device ID for WELL feature analysis")]
    ) -> str:
        """
        Get WELL Building Standard compliance broken down by individual features (A01-A08, T01-T07).

        Shows compliance status for each WELL v2 feature with specific scores and
        recommendations. More detailed than standard compliance check.
        """
        if device not in devices:
            return f"Unknown device: {device}. Use list_devices to see available options."

        device_config = devices[device]

        try:
            from src.well.features import WELL_FEATURES
            from src.well.thresholds import normalize_parameter_name

            data = await inbiot_client.get_latest_measurements(device_config)

            # Group parameters by feature
            feature_data = {}
            for feature_id, feature in WELL_FEATURES.items():
                feature_params = []
                for param in data:
                    if normalize_parameter_name(param.type) in feature.parameters:
                        feature_params.append(param)

                if feature_params:
                    # Assess parameters for this feature
                    assessments = []
                    total_score = 0
                    max_score = 0

                    for param in feature_params:
                        assessment = well_engine._assess_parameter(param)
                        if assessment:
                            assessments.append(assessment)
                            total_score += assessment.score
                            max_score += 4

                    percentage = (total_score / max_score * 100) if max_score > 0 else 0

                    feature_data[feature_id] = {
                        "feature": feature,
                        "score": total_score,
                        "max_score": max_score,
                        "percentage": round(percentage, 1),
                        "level": well_engine._determine_well_level(percentage),
                        "compliant": percentage >= 50,
                        "assessments": assessments,
                    }

            # Format results
            result = f"## WELL Feature Compliance: {device_config.name}\n\n"

            # Air quality features
            result += "### Air Quality Features (A01-A08)\n\n"
            result += "| Feature | Name | Score | Level | Status |\n"
            result += "|---------|------|-------|-------|--------|\n"

            for feature_id in ["A01", "A03", "A05", "A06", "A08"]:
                if feature_id in feature_data:
                    fd = feature_data[feature_id]
                    status = "✅" if fd["compliant"] else "❌"
                    result += f"| {feature_id} | {fd['feature'].name} | {fd['score']}/{fd['max_score']} | {fd['level']} | {status} |\n"

            # Thermal comfort features
            result += "\n### Thermal Comfort Features (T01-T07)\n\n"
            result += "| Feature | Name | Score | Level | Status |\n"
            result += "|---------|------|-------|-------|--------|\n"

            for feature_id in ["T01", "T06", "T07"]:
                if feature_id in feature_data:
                    fd = feature_data[feature_id]
                    status = "✅" if fd["compliant"] else "❌"
                    result += f"| {feature_id} | {fd['feature'].name} | {fd['score']}/{fd['max_score']} | {fd['level']} | {status} |\n"

            # Feature-specific recommendations
            result += "\n### Feature-Specific Recommendations\n\n"

            for feature_id, fd in feature_data.items():
                if not fd["compliant"]:
                    result += f"**{feature_id} - {fd['feature'].name}** ({fd['percentage']:.0f}% compliant)\n"
                    result += f"- Health Impact: {fd['feature'].health_impact}\n"
                    result += "- Actions:\n"
                    for strategy in fd['feature'].mitigation_strategies[:3]:
                        result += f"  • {strategy}\n"
                    result += "\n"

            if all(fd["compliant"] for fd in feature_data.values()):
                result += "✅ All monitored features are compliant. Excellent performance!\n"

            return result

        except InBiotAPIError as e:
            return create_data_unavailable_error(
                device_name=device_config.name,
                error_message=e.message,
            )

    @mcp.tool()
    async def health_recommendations(
        device: Annotated[str, Field(description="Device ID to generate recommendations for")]
    ) -> str:
        """
        Generate health and comfort recommendations based on current air quality.

        Provides actionable advice for building managers and occupants based on
        current sensor readings and WELL Building Standard guidelines.
        """
        if device not in devices:
            return f"Unknown device: {device}. Use list_devices to see available options."

        device_config = devices[device]

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
