# InBiot MCP Server

A Model Context Protocol (MCP) server for [InBiot](https://www.inbiot.es/) air quality monitoring devices, with WELL Building Standard compliance analysis. Built with [FastMCP](https://github.com/jlowin/fastmcp).

## Features

- **Real-time Air Quality Monitoring** - Get latest measurements from InBiot MICA sensors
- **Historical Data Retrieval** - Access measurements between specific dates
- **WELL Building Standard Compliance** - Assess air quality against WELL v2, ASHRAE 62.1/55, and WHO Indoor standards
- **Outdoor Context** - Compare indoor conditions with outdoor weather and air quality (via OpenWeather)
- **Health Recommendations** - Generate actionable advice based on current conditions
- **Data Authenticity** - All responses include mandatory provenance tracking (no simulated data)

## Prerequisites

- Python 3.10 or higher
- InBiot MICA device(s) with API access from [My inBiot](https://my.inbiot.es)
- OpenWeather API key (optional, for outdoor data) from [OpenWeather](https://openweathermap.org/api)

## Installation

### 1. Clone and Install

```bash
git clone https://github.com/miguel-escribano/inBiot_MCP_with_WeatherAPI_and_WELL_standard.git
cd inBiot_MCP_with_WeatherAPI_and_WELL_standard

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### 2. Configure Your Devices

Create your `.env` file from the template:

```bash
copy env.example .env   # Windows
cp env.example .env     # Linux/macOS
```

Edit `.env` and add your devices:

```bash
# OpenWeather API (optional, for outdoor weather context)
OPENWEATHER_API_KEY=your_openweather_key

# Add each InBiot device with these 5 variables:
INBIOT_OFFICE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
INBIOT_OFFICE_SYSTEM_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
INBIOT_OFFICE_NAME=Main Office
INBIOT_OFFICE_LAT=40.416775
INBIOT_OFFICE_LON=-3.703790

# Add more devices as needed...
INBIOT_LAB_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
INBIOT_LAB_SYSTEM_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
INBIOT_LAB_NAME=Laboratory
INBIOT_LAB_LAT=40.416775
INBIOT_LAB_LON=-3.703790
```

> **Where to find your credentials:**
> - **InBiot API Key & System ID**: [My inBiot Platform](https://my.inbiot.es) → Device Settings
> - **OpenWeather API Key**: [OpenWeather](https://openweathermap.org/api) (free tier available)
> - **Coordinates**: [LatLong.net](https://www.latlong.net/) or Google Maps

## MCP Client Configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "inbiot": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/inbiot-mcp",
        "run",
        "inbiot-mcp"
      ]
    }
  }
}
```

Or with Python directly:

```json
{
  "mcpServers": {
    "inbiot": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/inbiot-mcp/server.py"]
    }
  }
}
```

### Cursor IDE

Create `.cursor/mcp.json` in your project root (project-specific) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "inbiot": {
      "command": "python",
      "args": ["${workspaceFolder}/server.py"]
    }
  }
}
```

Or with `uv`:

```json
{
  "mcpServers": {
    "inbiot": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE/PATH/TO/inbiot-mcp", "run", "python", "server.py"]
    }
  }
}
```

### VS Code with Cline Extension

Add to Cline's MCP settings:

**macOS**: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`  
**Windows**: `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "inbiot": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/inbiot-mcp/server.py"]
    }
  }
}
```

**Important Notes:**
- Replace `/ABSOLUTE/PATH/TO/inbiot-mcp` with the actual absolute path to your installation
- Restart your IDE/application after configuration changes
- Check MCP logs: Open Output panel (`Cmd+Shift+U`) → Select "MCP Logs"

## Usage Examples

### For AI Assistants (Cursor, Claude, etc.)

Use these prompts to interact with the InBiot MCP server:

#### Basic Air Quality Check
```
Show me the current air quality readings from all InBiot devices
```

#### WELL Compliance Analysis
```
Check WELL Building Standard compliance for the Main Office device and 
provide detailed recommendations for any parameters that don't meet the standards
```

#### Indoor vs Outdoor Comparison
```
Compare the indoor air quality at the Laboratory with current outdoor conditions 
and explain any significant differences
```

#### Historical Analysis
```
Get historical data for the Main Office device from 2024-01-01 to 2024-01-31 
and analyze trends in CO2 and PM2.5 levels
```

#### Health Recommendations
```
Based on current readings from all devices, provide health and comfort 
recommendations for occupants
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_devices` | List all configured InBiot devices | None |
| `get_latest_measurements` | Get current readings from a device | `device` (string) |
| `get_historical_data` | Get measurements between dates | `device`, `startDate`, `endDate` (ISO-8601) |
| `well_compliance_check` | Assess WELL Standard compliance | `device` (string) |
| `outdoor_snapshot` | Get outdoor weather and air quality | `device` (string) |
| `indoor_vs_outdoor` | Compare indoor vs outdoor conditions | `device` (string) |
| `health_recommendations` | Generate health recommendations | `device` (string) |

## Available Resources

| URI | Description |
|-----|-------------|
| `inbiot://docs/parameters` | Air quality parameters reference |
| `inbiot://docs/well-standards` | WELL Building Standard criteria |
| `inbiot://docs/iaq` | IAQ indicator guide |
| `inbiot://docs/thermal-comfort` | Thermal comfort guide |
| `inbiot://docs/virus-resistance` | Virus resistance indicator guide |
| `inbiot://docs/ventilation` | Ventilation efficiency guide |

## Available Prompts

| Prompt | Description |
|--------|-------------|
| `air_quality_analysis` | Comprehensive air quality analysis |
| `compare_devices` | Compare two devices |
| `well_certification_analysis` | WELL certification assessment |
| `health_recommendations_prompt` | Health recommendations |

## API Rate Limits

- **InBiot API**: 6 requests per device per hour
- **OpenWeather API**: Depends on your subscription tier

## WELL Building Standard

Assesses air quality against:
- **WELL v2** - Features A01-A08 (Air) and T01-T07 (Thermal Comfort)
- **ASHRAE 62.1 & 55** - Ventilation and thermal comfort standards
- **WHO Indoor Air Quality Guidelines** - Health-based thresholds

**Certification levels**: Platinum (90%+), Gold (75%+), Silver (60%+), Bronze (40%+)

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Running the Server Manually
```bash
python server.py
# or
uv run python server.py
```

### Project Structure
```
inbiot-mcp/
├── server.py              # Main FastMCP server
├── .env                   # Your device credentials (not committed)
├── env.example            # Template for .env
├── src/
│   ├── api/               # API clients (InBiot, OpenWeather)
│   ├── models/            # Pydantic schemas
│   ├── well/              # WELL compliance engine
│   └── utils/             # Utilities (provenance tracking)
├── resources/             # Static documentation
└── tests/                 # Test suite
```

## Troubleshooting

### Server Not Connecting
1. Check the MCP logs in your IDE/application
2. Verify the absolute path in your configuration
3. Ensure `.env` file exists and contains valid credentials
4. Test manually: `uv run python server.py`

### API Rate Limit Errors
- InBiot API allows 6 requests per device per hour
- Space out your requests or cache results when possible

### Missing Outdoor Data
- Verify your OpenWeather API key in `.env`
- Check that device coordinates are correct
- Free tier has usage limits

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Links

- [InBiot](https://www.inbiot.es/) - Air quality monitoring devices
- [My inBiot Platform](https://my.inbiot.es) - Device management and API keys
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP framework
- [WELL Building Standard](https://www.wellcertified.com/) - Building certification
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
