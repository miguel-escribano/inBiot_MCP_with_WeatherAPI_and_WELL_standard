# InBiot MCP Server - Anne IAQ Expert

A Model Context Protocol (MCP) server for [InBiot](https://www.inbiot.es/) air quality monitoring devices, featuring **Anne**, a digital Indoor Air Quality (IAQ) consultant and WELL Accredited Professional (WELL AP).

> Evolución del CustomGPT original: [Anne - AAQ & IAQ & WELL AP Consultant](https://chatgpt.com/g/g-68fbca77e29481918230000b31ec7c35-anne-aaq-iaq-well-ap-consultant)

## Meet Anne

Anne is your digital IAQ consultant with expertise in:
- **WELL Building Standard v2** (Features A01-A08 Air, T01-T07 Thermal)
- **ASHRAE 62.1/55** (Ventilation & Thermal Comfort)
- **WHO Indoor Air Quality Guidelines**
- **ISO 16000 series** (indoor air pollutants)

She interprets real InBiot MICA sensor data and **never simulates or estimates data** - all values come directly from verified API endpoints.

---

## Quick Start (Remote Server)

The easiest way to use Anne. No installation required, just configure your MCP client.

### Cursor IDE

Add to `~/.cursor/mcp.json` (Windows: `%USERPROFILE%\.cursor\mcp.json`):

```json
{
  "mcpServers": {
    "inbiot-Anne-IAQ-expert": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.miguel-escribano.com/inbiot/sse",
        "--header",
        "X-MCP-Token: <YOUR_TOKEN>"
      ]
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`):

```json
{
  "mcpServers": {
    "inbiot-Anne-IAQ-expert": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.miguel-escribano.com/inbiot/sse",
        "--header",
        "X-MCP-Token: <YOUR_TOKEN>"
      ]
    }
  }
}
```

> **Note:** Contact the administrator for an access token. Requires [Node.js 18+](https://nodejs.org/).

**Available devices:** `cafeteria`, `main_office`, `laboratory`, `miguel_demo`

---

## Available Tools

### Monitoring
| Tool | Description |
|------|-------------|
| `list_devices` | List all configured devices |
| `get_all_devices_summary` | Facility-wide dashboard with status indicators (🟢🟡🔴⚫) |
| `get_latest_measurements` | Current readings from a device |
| `get_historical_data` | Historical measurements with statistics |

### WELL Compliance
| Tool | Description |
|------|-------------|
| `well_compliance_check` | WELL Standard compliance assessment |
| `well_feature_compliance` | Detailed A01-A08, T01-T07 breakdown |
| `well_certification_roadmap` | Prioritized path to certification with ROI ranking |
| `health_recommendations` | Context-aware health advice with specific targets |

### Analytics
| Tool | Description |
|------|-------------|
| `detect_patterns` | Find daily/weekly air quality patterns |
| `get_data_statistics` | Statistical analysis with trend detection |
| `export_historical_data` | Export to CSV/JSON with time aggregation |

### Weather Context
| Tool | Description |
|------|-------------|
| `outdoor_snapshot` | Current outdoor weather and air quality |
| `indoor_vs_outdoor` | Compare indoor vs outdoor conditions |

---

## Usage Examples

```
# Quick facility overview
Give me a quick overview of all devices - which spaces need attention?

# WELL compliance
Check WELL compliance for main_office with recommendations

# Certification roadmap
What's the fastest path to Platinum certification for main_office?

# Pattern analysis
Analyze air quality patterns for main_office over the last month

# Health recommendations
Provide health recommendations for main_office with specific targets

# Indoor vs outdoor
Compare indoor air quality at main_office with outdoor conditions
```

---

## Available Resources

| URI | Description |
|-----|-------------|
| `inbiot://docs/thresholds` | Unified thresholds (WELL v2, ASHRAE, WHO) |
| `inbiot://docs/ashrae-iso` | ASHRAE 62.1/55, ISO 16000 reference table |
| `inbiot://docs/parameters` | Air quality parameters guide |
| `inbiot://docs/well-standards` | WELL Building Standard criteria |

---

## Local Installation

<details>
<summary><strong>Click to expand local installation instructions</strong></summary>

### Prerequisites
- Python 3.10+
- InBiot MICA device(s) with API access from [My inBiot](https://my.inbiot.es)
- OpenWeather API key (optional) from [OpenWeather](https://openweathermap.org/api)

### Installation

```bash
git clone https://github.com/miguel-escribano/inBiot_MCP_with_WeatherAPI_and_WELL_standard.git
cd inBiot_MCP_with_WeatherAPI_and_WELL_standard

# Easy setup (recommended)
python setup.py

# Or manual
pip install -e .
```

### Configuration

Create `inbiot-config.yaml`:

```yaml
openweather_api_key: "your-key-here"  # Optional

devices:
  office:
    name: "Main Office"
    api_key: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    system_id: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    latitude: 40.416775
    longitude: -3.703790
```

> Get credentials from [My inBiot Platform](https://my.inbiot.es) → Device Settings

### MCP Client Configuration (Local)

**Cursor IDE** - Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "inbiot-Anne-IAQ-expert": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/server.py"]
    }
  }
}
```

**Claude Desktop** - Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "inbiot-Anne-IAQ-expert": {
      "command": "uvx",
      "args": ["--from", "/ABSOLUTE/PATH/TO/repo", "inbiot-mcp-server"]
    }
  }
}
```

### Running Tests

```bash
pytest tests/ -v
```

### Project Structure

```
├── server.py              # Main FastMCP server
├── src/
│   ├── skills/            # Modular tools (monitoring, analytics, compliance, weather)
│   ├── api/               # InBiot & OpenWeather clients
│   ├── well/              # WELL compliance engine
│   └── utils/             # Utilities (aggregation, export, retry)
├── resources/             # Documentation resources
└── tests/                 # Test suite
```

</details>

---

## API Rate Limits

- **InBiot API**: 6 requests per device per hour
- **OpenWeather API**: Depends on subscription tier
- Automatic retry with exponential backoff for transient failures

## WELL Certification Levels

| Level | Score |
|-------|-------|
| Platinum | 90%+ |
| Gold | 75%+ |
| Silver | 60%+ |
| Bronze | 40%+ |

---

## Links

- [InBiot](https://www.inbiot.es/) - Air quality monitoring devices
- [My inBiot Platform](https://my.inbiot.es) - Device management
- [WELL Building Standard](https://www.wellcertified.com/) - Building certification
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification

## License

MIT
