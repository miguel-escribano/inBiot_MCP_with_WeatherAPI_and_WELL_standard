"""InBiot API client for fetching air quality measurements."""

import httpx
from typing import Optional
from datetime import datetime

from src.models.schemas import ParameterData, DeviceConfig


class InBiotAPIError(Exception):
    """Exception raised when InBiot API call fails."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InBiotClient:
    """Client for the InBiot Public API."""

    BASE_URL = "https://myinbiotpublicapi.com"

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    async def get_latest_measurements(
        self, device: DeviceConfig
    ) -> list[ParameterData]:
        """
        Get the latest measurements from an InBiot device.

        Args:
            device: Device configuration with API key and system ID

        Returns:
            List of parameter data with measurements

        Raises:
            InBiotAPIError: If the API call fails
        """
        endpoint = f"/last-measurements/{device.api_key}/{device.system_id}"
        return await self._make_request(endpoint)

    async def get_historical_data(
        self,
        device: DeviceConfig,
        start_date: datetime,
        end_date: datetime,
    ) -> list[ParameterData]:
        """
        Get historical measurements from an InBiot device.

        Args:
            device: Device configuration with API key and system ID
            start_date: Start of the time range
            end_date: End of the time range

        Returns:
            List of parameter data with measurements

        Raises:
            InBiotAPIError: If the API call fails
        """
        # Format dates as ISO-8601 with milliseconds
        start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S.000")
        end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S.999")

        endpoint = f"/measurements-by-time/{device.api_key}/{device.system_id}/{start_str}/{end_str}"
        return await self._make_request(endpoint)

    async def _make_request(self, endpoint: str) -> list[ParameterData]:
        """
        Make an HTTP request to the InBiot API.

        Args:
            endpoint: API endpoint path

        Returns:
            List of parameter data

        Raises:
            InBiotAPIError: If the request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)

                if response.status_code == 404:
                    raise InBiotAPIError(
                        "Device not found with this API key",
                        status_code=404,
                    )
                elif response.status_code == 429:
                    raise InBiotAPIError(
                        "Rate limit exceeded (6 requests per device per hour)",
                        status_code=429,
                    )
                elif response.status_code >= 500:
                    raise InBiotAPIError(
                        f"InBiot server error: {response.status_code}",
                        status_code=response.status_code,
                    )
                elif response.status_code != 200:
                    raise InBiotAPIError(
                        f"Unexpected response: {response.status_code}",
                        status_code=response.status_code,
                    )

                data = response.json()

                # Handle both direct array and wrapped response
                if isinstance(data, dict) and "systemData" in data:
                    data = data["systemData"]

                return [ParameterData.model_validate(item) for item in data]

            except httpx.TimeoutException:
                raise InBiotAPIError("Request timed out")
            except httpx.RequestError as e:
                raise InBiotAPIError(f"Request failed: {str(e)}")

    @property
    def endpoint_info(self) -> str:
        """Return the base URL for provenance tracking."""
        return self.BASE_URL

