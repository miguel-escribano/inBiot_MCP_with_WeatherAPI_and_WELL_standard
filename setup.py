#!/usr/bin/env python3
"""Easy setup script for InBiot MCP Server."""

import os
import sys
import subprocess
from pathlib import Path

# Simple ASCII symbols for Windows compatibility
OK = "[OK]"
WARN = "[!]"
ERROR = "[X]"
INFO = "[*]"


def print_header(text):
    """Print a nice header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_python_version():
    """Check if Python version is sufficient."""
    if sys.version_info < (3, 10):
        print(f"{ERROR} Python 3.10 or higher is required!")
        print(f"   You have Python {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    print(f"{OK} Python {sys.version_info.major}.{sys.version_info.minor} detected")


def install_dependencies():
    """Install required dependencies."""
    print_header("Installing Dependencies")

    # Check if we're in an active virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

    if in_venv:
        print(f"{WARN} Running inside an active virtual environment")
        print(f"   If installation fails, try: deactivate && python setup.py\n")

    # Check if uv is available
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        print(f"{INFO} Using uv to install dependencies...")
        try:
            subprocess.run(["uv", "sync"], check=True)
            print(f"{OK} Dependencies installed with uv")
            return
        except subprocess.CalledProcessError as e:
            print(f"{WARN} uv sync failed, trying pip...")
    except FileNotFoundError:
        pass  # uv not available

    # Try pip installation
    print(f"{INFO} Using pip to install dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        print(f"{OK} Dependencies installed with pip")
    except subprocess.CalledProcessError as e:
        print(f"\n{ERROR} Dependency installation failed!")
        print(f"\nThis can happen if you're running inside an active virtual environment.")
        print(f"\nTo fix this, try one of these options:\n")
        print(f"  Option 1 (Recommended):")
        print(f"    1. Deactivate the virtual environment: deactivate")
        print(f"    2. Run setup again: python setup.py\n")
        print(f"  Option 2 (Manual installation):")
        print(f"    pip install fastmcp httpx pydantic python-dotenv pyyaml\n")
        print(f"  Option 3 (Fresh virtual environment):")
        print(f"    1. Delete .venv folder")
        print(f"    2. Create new venv: python -m venv .venv")
        print(f"    3. Activate: .venv\\Scripts\\activate (Windows) or source .venv/bin/activate (Mac/Linux)")
        print(f"    4. Run setup: python setup.py\n")

        response = input("Continue with setup anyway? (y/n): ").strip().lower()
        if response != 'y':
            sys.exit(1)


def setup_config():
    """Guide user through configuration setup."""
    print_header("Configuration Setup")

    config_file = Path("inbiot-config.yaml")

    if config_file.exists():
        print(f"{OK} Configuration file already exists: {config_file}")
        return

    print("No configuration found. Let's create one!")
    print("\nDo you want to create a configuration file now?")
    print("  1. Yes - Create inbiot-config.yaml from template")
    print("  2. No - I'll do it manually later")

    choice = input("\nEnter choice (1-2): ").strip()

    if choice == "1":
        # Copy YAML example
        example = Path("inbiot-config.example.yaml")
        if example.exists():
            import shutil
            shutil.copy(example, config_file)
            print(f"\n{OK} Created {config_file}")
            print(f"\n{WARN} IMPORTANT: Edit {config_file} with your device credentials!")
            print("   - Add your InBiot API keys from https://my.inbiot.es")
            print("   - Add device coordinates for weather data")
            print("   - Optionally add OpenWeather API key for outdoor data")
        else:
            print(f"{ERROR} Example file not found")
    else:
        print(f"\n{WARN} Skipping configuration. You'll need to set it up manually.")
        print(f"   Copy inbiot-config.example.yaml to inbiot-config.yaml and edit it.")


def run_tests():
    """Run tests if user wants to."""
    print_header("Testing (Optional)")

    response = input("Run tests to verify installation? (y/n): ").strip().lower()

    if response == 'y':
        try:
            subprocess.run(["pytest", "tests/", "-v"], check=True)
            print(f"{OK} All tests passed!")
        except subprocess.CalledProcessError:
            print(f"{WARN} Some tests failed. Check output above.")
        except FileNotFoundError:
            print(f"{WARN} pytest not found. Install with: pip install pytest pytest-asyncio")
    else:
        print(f"{INFO} Skipping tests")


def print_next_steps():
    """Print what to do next."""
    print_header("Setup Complete!")

    print(f"{OK} InBiot MCP Server is ready!\n")

    print("Next Steps:\n")
    print("1. Edit your configuration file:")

    if Path("inbiot-config.yaml").exists():
        print("   - Open: inbiot-config.yaml")
        print("   - Add your InBiot device credentials from https://my.inbiot.es")
        print("   - Add OpenWeather API key (optional)")
    else:
        print("   - Create inbiot-config.yaml (see inbiot-config.example.yaml)")

    print("\n2. Configure your MCP client:")
    print("   - Claude Desktop: See README.md 'Claude Desktop' section")
    print("   - Cursor IDE: See README.md 'Cursor IDE' section")

    print("\n3. Test the server:")
    print("   python server.py")

    print("\nFull documentation: README.md")
    print("Report issues: https://github.com/miguel-escribano/inBiot_MCP_with_WeatherAPI_and_WELL_standard/issues")

    print("\n" + "=" * 60)


def main():
    """Main setup function."""
    print_header("InBiot MCP Server - Easy Setup")

    # Check Python version
    check_python_version()

    # Install dependencies
    install_dependencies()

    # Setup configuration
    setup_config()

    # Run tests
    run_tests()

    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{ERROR} Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{ERROR} Setup failed: {e}")
        sys.exit(1)
