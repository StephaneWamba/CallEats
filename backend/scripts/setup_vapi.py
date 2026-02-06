#!/usr/bin/env python3
"""Vapi setup script for Restaurant Voice Assistant.

This script manages Vapi resources (tools and assistants) for the Restaurant Voice Assistant.
It loads configuration from YAML files and creates/updates Vapi resources via the Vapi API.

Features:
    - Creates function tools from config/vapi/tools.yaml
    - Creates or updates shared assistant from config/vapi/assistant.yaml
    - Configures webhooks and prompts
    - Supports cleanup (delete all resources) and list-only modes
    - Validates configuration before deployment

Required Environment Variables:
    - VAPI_API_KEY: Vapi API key for authentication
    - PUBLIC_BACKEND_URL: Public URL of the backend API (for webhooks)

Optional Environment Variables:
    - VAPI_BASE_URL: Vapi API base URL (default: https://api.vapi.ai)

Usage:
    # List existing resources
    python scripts/setup_vapi.py --list-only
    
    # Create/update resources (keeps existing)
    python scripts/setup_vapi.py
    
    # Clean up and create fresh resources
    python scripts/setup_vapi.py --cleanup
    
    # Override environment variables
    python scripts/setup_vapi.py --api-key YOUR_KEY --backend-url https://your-backend.com

Examples:
    # Basic setup
    export VAPI_API_KEY="your_api_key"
    export PUBLIC_BACKEND_URL="https://your-backend.railway.app"
    python scripts/setup_vapi.py
    
    # Clean setup (removes existing resources first)
    python scripts/setup_vapi.py --cleanup
    
    # Just check what exists
    python scripts/setup_vapi.py --list-only
"""
import logging
from restaurant_voice_assistant.infrastructure.vapi.manager import VapiResourceManager
import argparse
import sys
import os
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}\n{text}\n{'=' * 60}")


def print_section(text: str):
    """Print a formatted section header."""
    print(f"\n{'-' * 60}\n{text}\n{'-' * 60}")


def list_resources(manager: VapiResourceManager):
    """List existing Vapi resources."""
    print_section("Existing Resources")

    try:
        resources = manager.list_resources()
        assistants = resources.get("assistants", [])
        tools = resources.get("tools", [])

        print(f"\nAssistants ({len(assistants)}):")
        if assistants:
            for a in assistants:
                name = a.get("name", "Unnamed")
                aid = a.get("id", "N/A")
                phone = a.get("phoneNumberId", "No phone")
                print(f"  - {name} (ID: {aid}, Phone: {phone})")
        else:
            print("  No assistants found")

        print(f"\nTools ({len(tools)}):")
        if tools:
            for t in tools:
                name = t.get("function", {}).get("name", "Unnamed")
                tid = t.get("id", "N/A")
                print(f"  - {name} (ID: {tid})")
        else:
            print("  No tools found")

    except Exception as e:
        logger.warning(f"Could not list resources: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Setup and manage Vapi assistants and tools for Restaurant Voice Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List existing resources
  python scripts/setup_vapi.py --list-only
  
  # Create new resources (keeps existing)
  python scripts/setup_vapi.py
  
  # Clean up and create fresh resources
  python scripts/setup_vapi.py --cleanup
  
  # Override environment variables
  python scripts/setup_vapi.py --api-key YOUR_KEY --backend-url https://your-backend.com
        """
    )

    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete all existing assistants and tools before creating new ones"
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list existing resources, don't create anything"
    )
    parser.add_argument(
        "--backend-url",
        type=str,
        help="Backend URL (overrides PUBLIC_BACKEND_URL env var)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Vapi API key (overrides VAPI_API_KEY env var)"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="https://api.vapi.ai",
        help="Vapi API base URL (default: https://api.vapi.ai)"
    )

    args = parser.parse_args()

    # Get API key and backend URL
    api_key = args.api_key or os.environ.get("VAPI_API_KEY")
    backend_url = args.backend_url or os.environ.get("PUBLIC_BACKEND_URL")

    if not api_key:
        print("Error: VAPI_API_KEY required (--api-key or env var)", file=sys.stderr)
        print("Set it with: export VAPI_API_KEY='your_api_key'", file=sys.stderr)
        sys.exit(1)

    if not backend_url:
        print(
            "Error: PUBLIC_BACKEND_URL required (--backend-url or env var)", file=sys.stderr)
        print("Set it with: export PUBLIC_BACKEND_URL='https://your-backend.com'", file=sys.stderr)
        sys.exit(1)

    # Initialize manager
    manager = VapiResourceManager(
        api_key=api_key,
        backend_url=backend_url,
        base_url=args.base_url
    )

    print_header("Vapi Setup - Restaurant Voice Assistant")
    print(f"Backend URL: {backend_url}")
    print(f"API Base URL: {args.base_url}")

    # List existing resources
    try:
        list_resources(manager)
    except Exception as e:
        logger.warning(f"Could not list existing resources: {e}")
        print("Continuing anyway...")

    if args.list_only:
        print_section("Info")
        print("Listing complete. Use without --list-only to create resources.")
        return

    # Load and validate configuration
    try:
        print_section("Loading Configuration")
        config = manager.load_and_validate_config()
        print(f"✓ Loaded {len(config['tools'])} tools")
        print(
            f"✓ Loaded assistant configuration: {config['assistant'].get('name', 'Unnamed')}")
        print(f"✓ Loaded prompts configuration")

        # Cleanup if requested
        if args.cleanup:
            print_section("Cleaning Up Old Resources")
            try:
                deleted = manager.cleanup_all_resources()
                print(
                    f"\n✓ Cleaned up {deleted['assistants']} assistants and {deleted['tools']} tools")
            except Exception as e:
                logger.warning(
                    f"Cleanup failed (this is okay if API key is incorrect): {e}")
                print("Continuing with creation...")

        # Create tools
        print_section("Creating Tools")
        tool_map = manager.create_tools()

        if not tool_map:
            print("Error: No tools were created", file=sys.stderr)
            sys.exit(1)

        print(f"✓ Created {len(tool_map)} tools:")
        for tool_name, tool_id in tool_map.items():
            print(f"  - {tool_name}: {tool_id}")

        # Check for existing assistant or create new one
        print_section("Creating/Updating Assistant")
        assistants = manager.client.list_assistants()
        assistant_name = config['assistant'].get(
            'name', 'Restaurant Voice Assistant')
        existing_assistant = next(
            (a for a in assistants if a.get("name") == assistant_name),
            None
        )

        if existing_assistant:
            assistant_id = existing_assistant.get("id")
            print(f"✓ Using existing assistant: {assistant_id}")
            print(f"  Name: {assistant_name}")

            # Update existing assistant with new tools
            try:
                assistant_config = config["assistant"].copy()
                assistant_config.pop("voice", None)

                system_prompt = config["prompts"]["system_prompt"]
                model_config = assistant_config.get("model", {}).copy()
                model_config["messages"] = [
                    {"role": "system", "content": system_prompt}
                ]

                tools_block = [
                    manager.build_tool_config(tool_def, for_assistant=True)
                    for tool_def in config["tools"]
                    if tool_def["name"] in tool_map
                ]
                model_config["tools"] = tools_block

                unified_server_url = f"{backend_url}/api/vapi/server"
                first_message = config["prompts"].get("first_message")

                update_data = {
                    "model": model_config,
                    "server": {
                        "url": unified_server_url
                    },
                    "serverUrl": unified_server_url,
                    "serverUrlSecret": api_key
                }
                if first_message:
                    update_data["firstMessage"] = first_message

                manager.client.update_assistant(assistant_id, update_data)
                print(f"✓ Updated assistant with new configuration")
            except Exception as e:
                logger.warning(f"Could not update assistant: {e}")
                print("Assistant exists but update failed (may need manual update)")
        else:
            assistant_id = manager.create_assistant(tool_map)
            print(f"✓ Created new assistant: {assistant_id}")
            print(f"  Name: {assistant_name}")

        # Success summary
        print_header("Setup Complete!")
        print(f"Assistant ID: {assistant_id}")
        print(f"Assistant Name: {assistant_name}")
        print(f"\n📋 Next Steps:")
        print(
            f"  1. Test assistant: https://dashboard.vapi.ai/assistant/{assistant_id}")
        print(f"  2. Configure webhooks in Vapi dashboard:")
        print(f"     - Server URL: {backend_url}/api/vapi/server")
        print(f"     - Secret: {api_key}")
        print(f"  3. Assign phone numbers to restaurants via API")
        print(f"\n📁 Configuration Files:")
        config_files = ["tools.yaml", "assistant.yaml", "prompts.yaml"]
        for config_file in config_files:
            config_path = Path(__file__).parent.parent / \
                "config" / "vapi" / config_file
            if config_path.exists():
                print(f"  ✓ config/vapi/{config_file}")
            else:
                print(f"  ✗ config/vapi/{config_file} (missing)")

    except FileNotFoundError as e:
        print(f"Error: Configuration file not found: {e}", file=sys.stderr)
        print("Ensure config/vapi/ directory contains tools.yaml, assistant.yaml, and prompts.yaml", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Configuration validation failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
