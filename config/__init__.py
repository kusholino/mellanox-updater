"""
Configuration modules for the SerialLink device updater.

This package contains configuration management including:
- Configuration file parsing and validation
- Playbook loading and command parsing
- Settings management
"""

from .config_manager import ConfigManager, PlaybookCommand

__all__ = ['ConfigManager', 'PlaybookCommand']
