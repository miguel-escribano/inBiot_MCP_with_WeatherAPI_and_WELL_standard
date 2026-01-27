# InBiot MCP Server

A Model Context Protocol (MCP) server for [InBiot](https://www.inbiot.es/) air quality monitoring devices, with WELL Building Standard compliance analysis. Built with [FastMCP](https://github.com/jlowin/fastmcp).

> Este MCP es la evolución del CustomGPT original: [Anne - AAQ & IAQ & WELL AP Consultant](https://chatgpt.com/g/g-68fbca77e29481918230000b31ec7c35-anne-aaq-iaq-well-ap-consultant)

## Cómo Usar

Hay dos opciones:

| Opción | Ventaja | Requisitos |
|--------|---------|------------|
| **A) Servidor remoto** | Listo para usar, sin instalación | [Node.js 18+](https://nodejs.org/) |
| **B) Instalación local** | Configura tus propios dispositivos | Python 3.10+, credenciales InBiot |

---

## Opción A: Servidor Remoto (Demo)

Hay un servidor de demostración disponible en `mcp.miguel-escribano.com`. Requiere autenticación por token.

### Seguridad

El servidor implementa:
- **Autenticación por token** (`X-MCP-Token`) - Sin token válido = 401 Unauthorized
- **Sanitización de credenciales** - API keys y system IDs nunca se exponen en respuestas

### Configuración

**Cursor** - Añade esto a `~/.cursor/mcp.json` (Windows: `%USERPROFILE%\.cursor\mcp.json`):

```json
"inbiot": {
  "command": "npx",
  "args": ["-y", "mcp-remote", "https://mcp.miguel-escribano.com/inbiot/sse", "--header", "X-MCP-Token: TU_TOKEN"]
}
```

**Claude Desktop** - Añade esto a `claude_desktop_config.json`:

```json
"inbiot": {
  "command": "npx",
  "args": ["-y", "mcp-remote", "https://mcp.miguel-escribano.com/inbiot/sse", "--header", "X-MCP-Token: TU_TOKEN"]
}
```

> **Nota:** Contacta al administrador para obtener un token de acceso.

**Dispositivos disponibles:** `cafeteria`, `main_office`, `laboratory`, `miguel_demo`

**Ejemplos de uso:** Una vez conectado, prueba estas preguntas:

1. *"How can you help me? Explain your capabilities and available tools"*
2. *"List available devices, then get latest measurements from main_office"*
3. *"Compare indoor vs outdoor air quality for main_office at Pamplona, Spain"*
4. *"WELL compliance check for laboratory with recommendations and provenance"*

---

## Opción B: Instalación Local

Si quieres configurar tus propios dispositivos InBiot, sigue las instrucciones de instalación más abajo.

---

## Features

### Core Capabilities
- **Real-time Air Quality Monitoring** - Get latest measurements from InBiot MICA sensors
- **Historical Data Retrieval** - Access measurements between specific dates with statistical analysis
- **WELL Building Standard Compliance** - Assess air quality against WELL v2, ASHRAE 62.1/55, and WHO Indoor standards
- **Outdoor Context** - Compare indoor conditions with outdoor weather and air quality (via OpenWeather)
- **Health Recommendations** - Generate actionable advice based on current conditions
- **Data Authenticity** - All responses include mandatory provenance tracking (no simulated data)

### Advanced Features
- **Modular Skills Architecture** - Organized into monitoring, analytics, compliance, and weather skills for easy maintenance
- **YAML/JSON Configuration** - Easy device management with config files (backward compatible with .env)
- **Automatic Retries** - Exponential backoff for transient API failures and rate limits
- **Data Export** - Export historical data to CSV/JSON formats with optional time aggregation
- **Statistical Analysis** - Comprehensive statistics (min/max/mean/median/std dev/quartiles) and trend detection
- **Feature-Level WELL Compliance** - Detailed breakdown by WELL v2 features (A01-A08, T01-T07) with specific mitigation strategies

## Prerequisites

- Python 3.10 or higher
- InBiot MICA device(s) with API access from [My inBiot](https://my.inbiot.es)
- OpenWeather API key (optional, for outdoor data) from [OpenWeather](https://openweathermap.org/api)

## Quick Start

### Easy Installation (Recommended)

```bash
git clone https://github.com/miguel-escribano/inBiot_MCP_with_WeatherAPI_and_WELL_standard.git
cd inBiot_MCP_with_WeatherAPI_and_WELL_standard

# Run interactive setup
python setup.py
```

The setup script will:
- Check Python version
- Install dependencies (automatically tries uv, falls back to pip)
- Create configuration template
- Optionally run tests

## Manual Installation

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

Create `inbiot-config.yaml` from the example:

```bash
copy inbiot-config.example.yaml inbiot-config.yaml   # Windows
cp inbiot-config.example.yaml inbiot-config.yaml     # Linux/macOS
```

Edit `inbiot-config.yaml`:

```yaml
openweather_api_key: "your-key-here"  # Optional

devices:
  office:  # Device ID (any name you want)
    name: "Main Office"
    api_key: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    system_id: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    latitude: 40.416775
    longitude: -3.703790

  lab:  # Add more devices as needed
    name: "Laboratory"
    api_key: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    system_id: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    latitude: 40.416775
    longitude: -3.703790
```

> **Where to find your credentials:**
> - **InBiot API Key & System ID**: [My inBiot Platform](https://my.inbiot.es) → Device Settings
> - **OpenWeather API Key**: [OpenWeather](https://openweathermap.org/api) (free tier available)
> - **Coordinates**: [LatLong.net](https://www.latlong.net/) or Google Maps
>
> **Note:** JSON and environment variable configurations are also supported for backward compatibility. See the code for details.

## MCP Client Configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Recommended (no manual dependency installation needed):**

```json
{
  "mcpServers": {
    "inbiot-well": {
      "command": "uvx",
      "args": [
        "--from",
        "/ABSOLUTE/PATH/TO/InBiot_MCP",
        "inbiot-mcp-server"
      ]
    }
  }
}
```

This uses `uvx` to automatically manage dependencies in an isolated environment.

**Alternative (requires `pip install -e .` first):**

```json
{
  "mcpServers": {
    "inbiot-well": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/InBiot_MCP/server.py"]
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

#### Statistical Analysis (NEW)
```
Get comprehensive statistics for the office device from 2024-01-01 to 2024-01-31
including min, max, mean, median, standard deviation, and trend analysis
```

#### Data Export (NEW)
```
Export historical data from the office device for January 2024 to CSV format
with daily aggregation for external analysis
```

#### Feature-Level WELL Compliance (NEW)
```
Show me the detailed WELL Building Standard compliance breakdown by feature
(A01-A08 for air quality, T01-T07 for thermal comfort) for the Main Office device,
including specific mitigation strategies for any non-compliant features
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
| `get_historical_data` | Get measurements between dates with statistics | `device`, `start_date`, `end_date` (YYYY-MM-DD) |
| `well_compliance_check` | Assess WELL Standard compliance | `device` (string) |
| `well_feature_compliance` | **NEW:** Detailed WELL v2 feature breakdown (A01-A08, T01-T07) | `device` (string) |
| `outdoor_snapshot` | Get outdoor weather and air quality | `device` (string) |
| `indoor_vs_outdoor` | Compare indoor vs outdoor conditions | `device` (string) |
| `health_recommendations` | Generate health recommendations | `device` (string) |
| `export_historical_data` | **NEW:** Export historical data to CSV/JSON | `device`, `start_date`, `end_date`, `format` (csv/json), `aggregation` (none/hourly/daily/weekly) |
| `get_data_statistics` | **NEW:** Comprehensive statistical analysis with trends | `device`, `start_date`, `end_date` |

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

## API Rate Limits & Resilience

- **InBiot API**: 6 requests per device per hour
- **OpenWeather API**: Depends on your subscription tier

**Automatic Retry Handling:**
- Exponential backoff for transient failures (network timeouts, 5xx errors)
- Respects 429 rate limit headers with proper retry timing
- Configurable retry attempts (default: 3) with increasing delays
- Maximum delay capped at 30 seconds to prevent excessive waits

## WELL Building Standard

Assesses air quality against:
- **WELL v2** - Features A01-A08 (Air) and T01-T07 (Thermal Comfort)
- **ASHRAE 62.1 & 55** - Ventilation and thermal comfort standards
- **WHO Indoor Air Quality Guidelines** - Health-based thresholds

**Certification levels**: Platinum (90%+), Gold (75%+), Silver (60%+), Bronze (40%+)

## Architecture

### Modular Skills Design

The MCP server is organized into **modular skills** for better maintainability and scalability:

**🔍 Monitoring Skill** (`src/skills/monitoring/`)
- `list_devices` - List all configured devices
- `get_latest_measurements` - Real-time air quality data
- `get_historical_data` - Historical measurements with trends

**📊 Analytics Skill** (`src/skills/analytics/`)
- `get_data_statistics` - Comprehensive statistical analysis
- `export_historical_data` - CSV/JSON export with aggregation

**✅ Compliance Skill** (`src/skills/compliance/`)
- `well_compliance_check` - WELL Building Standard assessment
- `well_feature_compliance` - Feature-by-feature breakdown (A01-A08, T01-T07)
- `health_recommendations` - Actionable health advice

**🌤️ Weather Skill** (`src/skills/weather/`)
- `outdoor_snapshot` - Current outdoor conditions
- `indoor_vs_outdoor` - Indoor/outdoor comparison

**Benefits:**
- ✅ Easy to maintain - Each skill is self-contained
- ✅ Easy to extend - Add new skills without touching existing code
- ✅ Easy to test - Test skills independently
- ✅ Clear organization - Tools grouped by domain

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
├── server.py                      # Main FastMCP server (modular, uses skills)
├── setup.py                       # Easy setup script
├── inbiot-config.yaml             # YAML configuration (recommended)
├── inbiot-config.example.yaml    # YAML config template
├── src/
│   ├── skills/                    # Modular skills (NEW!)
│   │   ├── monitoring/            # Device monitoring tools
│   │   │   └── tools.py           # list_devices, get_latest, get_historical
│   │   ├── analytics/             # Data analysis tools
│   │   │   └── tools.py           # statistics, export
│   │   ├── compliance/            # WELL compliance tools
│   │   │   └── tools.py           # well_check, feature_compliance, recommendations
│   │   └── weather/               # Weather comparison tools
│   │       └── tools.py           # outdoor_snapshot, indoor_vs_outdoor
│   ├── api/                       # API clients (InBiot, OpenWeather)
│   │   ├── inbiot.py              # With retry logic
│   │   └── openweather.py         # With retry logic
│   ├── config/                    # Configuration management
│   │   ├── loader.py              # YAML/JSON/ENV config loader
│   │   └── validator.py           # Config validation
│   ├── models/                    # Pydantic schemas
│   │   └── schemas.py
│   ├── well/                      # WELL compliance engine
│   │   ├── compliance.py          # Assessment engine
│   │   ├── features.py            # WELL v2 feature definitions
│   │   └── thresholds.py          # WELL/ASHRAE/WHO thresholds
│   └── utils/                     # Utilities
│       ├── aggregation.py         # Statistical analysis
│       ├── exporters.py           # CSV/JSON exporters
│       ├── provenance.py          # Data authenticity tracking
│       └── retry.py               # Exponential backoff retry logic
├── resources/                     # Static documentation
└── tests/                         # Test suite
```

## What's New (Recent Improvements)

### Configuration Simplification
- **YAML/JSON Config Files**: Easier device management compared to environment variables
- **Auto-detection**: Loads YAML → JSON → ENV automatically (backward compatible)
- **Validation**: Warns about common issues (duplicate IDs, default coordinates)
- **Easy Setup**: Interactive `setup.py` script for guided installation

### Enhanced Reliability
- **Automatic Retries**: Exponential backoff for transient failures
- **Rate Limit Handling**: Respects 429 Retry-After headers
- **Better Error Messages**: Context-rich error reporting with endpoint details
- **Configurable**: Customize retry attempts and delays

### Data Export & Analysis
- **CSV/JSON Export**: Professional data export for external analysis
- **Time Aggregation**: Hourly, daily, or weekly data summarization
- **Statistical Analysis**: Min/max/mean/median/std dev/quartiles
- **Trend Detection**: Automatic trend identification (increasing/decreasing/stable)

### Enhanced WELL Compliance
- **Feature-Level Breakdown**: Explicit A01-A08 (Air) and T01-T07 (Thermal) reporting
- **Specific Mitigation Strategies**: 5+ actionable strategies per feature
- **Health Impact Details**: Clear explanation of health implications
- **Targeted Recommendations**: Parameter and feature-specific advice

All improvements maintain **full backward compatibility** with existing configurations.

## Troubleshooting

### Server Not Connecting
1. Check the MCP logs in your IDE/application
2. Verify the absolute path in your configuration
3. Ensure configuration file exists (`inbiot-config.yaml`, `inbiot-config.json`, or `.env`)
4. Test manually: `python server.py` (should see FastMCP initialization)
5. Run setup: `python setup.py` for guided troubleshooting

### API Rate Limit Errors
- InBiot API allows 6 requests per device per hour
- Server automatically retries with exponential backoff
- If you hit the limit, wait for the retry window or space out requests

### Configuration Not Loading
- Check configuration priority: YAML → JSON → ENV
- Verify YAML/JSON syntax (use online validators if needed)
- Look for validation warnings on server startup
- Test config: `python -c "from src.config.loader import ConfigLoader; print(ConfigLoader.load())"`

### Missing Outdoor Data
- Verify your OpenWeather API key in configuration
- Check that device coordinates are correct (not 0, 0)
- Free tier has usage limits

### Dependency Installation Fails
- If running in active venv: deactivate first, then run `python setup.py`
- Try manual install: `pip install fastmcp httpx pydantic python-dotenv pyyaml`
- Windows permission errors: Run as administrator or use fresh venv

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
