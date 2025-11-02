"""
Vapi configuration module.

Contains configuration loader and YAML config files.
Vapi client and manager moved to src.services.vapi.
"""

from .config_loader import load_config, validate_config

__all__ = ["load_config", "validate_config"]

