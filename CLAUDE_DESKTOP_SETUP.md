# Claude Desktop Setup Guide

This guide explains how to use the InBiot MCP in Claude Desktop without manually installing dependencies.

## Why `uvx` is Recommended

Unlike traditional Python scripts, MCPs in Claude Desktop should run in isolated environments. Using `uvx` (part of the `uv` package manager) automatically:

- Creates an isolated environment
- Installs all dependencies automatically
- Avoids conflicts with your system Python
- No need to run `pip install` manually

## Prerequisites

1. **Install `uv`** (if not already installed):

   **Windows (PowerShell):**
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   **macOS/Linux:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone this repository** (or download it):
   ```bash
   git clone https://github.com/miguel-escribano/inBiot_MCP_with_WeatherAPI_and_WELL_standard.git
   ```

3. **Configure your devices** - Create `inbiot-config.yaml` with your sensor credentials:
   ```bash
   cp inbiot-config.example.yaml inbiot-config.yaml
   # Edit inbiot-config.yaml with your API keys
   ```

## Configuration

### Step 1: Locate Claude Desktop Config

Open the configuration file for your OS:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Add InBiot MCP

Add this configuration (replace `/ABSOLUTE/PATH/TO/InBiot_MCP` with your actual path):

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

**Example paths:**

- Windows: `"C:\\code\\mcp-servers-repos\\InBiot_MCP"`
- macOS/Linux: `"/Users/username/projects/InBiot_MCP"`

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop completely.

## Verify It's Working

In Claude Desktop, try asking:

> "List available InBiot devices"

or

> "Get latest air quality measurements from the office"

Claude should be able to access your InBiot sensors and provide real-time data.

## Troubleshooting

### "Command not found: uvx"

Make sure `uv` is installed and in your PATH:

```bash
uv --version
```

If not found, reinstall `uv` following the prerequisites above.

### "No device configuration found"

Make sure `inbiot-config.yaml` exists in the repository root with valid credentials:

```bash
cd /path/to/InBiot_MCP
ls inbiot-config.yaml  # Should exist
```

### "Module not found" errors

This usually means the path in the config is wrong. Double-check:

1. The path is **absolute** (not relative)
2. The path points to the **repository root** (where `server.py` is)
3. On Windows, use **double backslashes** (`\\`) or forward slashes (`/`)

### Still not working?

Try the alternative method (requires manual installation):

```json
{
  "mcpServers": {
    "inbiot-well": {
      "command": "python",
      "args": [
        "/ABSOLUTE/PATH/TO/InBiot_MCP/server.py"
      ]
    }
  }
}
```

But first install dependencies:

```bash
cd /path/to/InBiot_MCP
pip install -e .
```

## Available Tools

Once configured, Claude Desktop will have access to these tools:

- `list_devices` - List all configured InBiot devices
- `get_latest_measurements` - Get current air quality readings
- `get_historical_data` - Retrieve historical data with date ranges
- `get_data_statistics` - Comprehensive statistical analysis
- `well_compliance_check` - WELL Building Standard compliance assessment
- `well_feature_compliance` - Detailed WELL feature breakdown
- `health_recommendations` - Personalized health and comfort advice
- `outdoor_snapshot` - Current outdoor weather and air quality
- `indoor_vs_outdoor` - Compare indoor/outdoor conditions
- `export_historical_data` - Export data to CSV/JSON

## Example Queries

Try these in Claude Desktop:

- "Show me the current air quality in all my spaces"
- "Is the office compliant with WELL Building Standard?"
- "Get statistics for the lab from January 1 to January 31"
- "Compare indoor and outdoor air quality for the cafeteria"
- "What health recommendations do you have based on current readings?"
- "Export last week's data from the office to CSV"

## Security Note

Your `inbiot-config.yaml` file contains sensitive API keys. Make sure:

- ✅ It's listed in `.gitignore` (already done)
- ✅ Never commit it to version control
- ✅ Keep it in the local repository only

The example file `inbiot-config.example.yaml` is safe to share and commit.
