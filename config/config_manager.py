"""
Configuration management for Mellanox Device Updater.

Handles loading and parsing of configuration files and playbooks.
"""

import os
import configparser
from typing import Optional, List, Dict, Any, NamedTuple


class PlaybookCommand(NamedTuple):
    """Represents a single playbook command."""
    command_type: str
    command: str
    expected_text: Optional[str] = None
    wait_timeout: int = 30
    delay: float = 0.0


class ConfigManager:
    """Manages configuration loading and playbook parsing."""
    
    def __init__(self, logger):
        """
        Initialize the configuration manager.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger
        self.config = configparser.ConfigParser()
        self.config_loaded = False
        self.success_message = None  # Store custom success message from SUCCESS command
    
    def load_config(self, config_file: str) -> bool:
        """
        Load configuration from file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.log_info(f"Loading configuration from {config_file}")
            
            if not os.path.exists(config_file):
                self.logger.log_error(f"Configuration file not found: {config_file}")
                return False
            
            # Set defaults
            self.config['DEFAULT'] = {
                'port': '',
                'baudrate': '115200',
                'username': '',
                'password': '',
                'prompt_symbol': '>',
                'wait_timeout': '30',
                'login_wait_timeout': '10'
            }
            
            self.config['PLAYBOOK'] = {
                'playbook_file': 'playbook.txt'
            }
            
            self.config['PAGINATION'] = {
                'enabled': 'true',
                'response_delay': '0.1',
                'custom_patterns': ''
            }
            
            # Read the config file
            self.config.read(config_file)
            self.config_loaded = True
            
            self.logger.log_success("Configuration loaded successfully")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error loading configuration: {e}")
            return False
    
    def get_port(self) -> Optional[str]:
        """Get the serial port from config."""
        if not self.config_loaded:
            return None
        port = self.config.get('DEFAULT', 'port', fallback='')
        return port if port else None
    
    def get_baudrate(self) -> int:
        """Get the baud rate from config."""
        if not self.config_loaded:
            return 115200
        return self.config.getint('DEFAULT', 'baudrate', fallback=115200)
    
    def get_username(self) -> Optional[str]:
        """Get the username from config."""
        if not self.config_loaded:
            return None
        username = self.config.get('DEFAULT', 'username', fallback='')
        return username if username else None
    
    def get_password(self) -> Optional[str]:
        """Get the password from config."""
        if not self.config_loaded:
            return None
        password = self.config.get('DEFAULT', 'password', fallback='')
        return password if password else None
    
    def get_prompt_symbol(self) -> str:
        """Get the prompt symbol from config."""
        if not self.config_loaded:
            return '>'
        return self.config.get('DEFAULT', 'prompt_symbol', fallback='>')
    
    def get_wait_timeout(self) -> int:
        """Get the wait timeout from config."""
        if not self.config_loaded:
            return 30
        return self.config.getint('DEFAULT', 'wait_timeout', fallback=30)
    
    def load_playbook(self, playbook_file_override: Optional[str] = None) -> List[PlaybookCommand]:
        """
        Load and parse playbook commands.
        
        Args:
            playbook_file_override: Optional override for playbook file path
            
        Returns:
            List of playbook commands
        """
        if not self.config_loaded:
            self.logger.log_error("Configuration not loaded")
            return []
        
        try:
            # Determine playbook file
            if playbook_file_override:
                playbook_file = playbook_file_override
                self.logger.log_info(f"Using override playbook: {playbook_file}")
            else:
                playbook_file = self.config.get('PLAYBOOK', 'playbook_file', fallback='playbook.txt')
                self.logger.log_debug(f"Using config playbook: {playbook_file}")
            
            # Handle relative paths
            if not os.path.isabs(playbook_file):
                # Make relative to config file directory or current directory
                playbook_file = os.path.abspath(playbook_file)
            
            # Read playbook file
            if not os.path.exists(playbook_file):
                self.logger.log_error(f"Playbook file not found: {playbook_file}")
                return []
            
            with open(playbook_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.log_debug(f"Loaded playbook from: {playbook_file}")
            
            # Parse commands
            commands = self._parse_playbook_content(content)
            self.logger.log_success(f"Parsed {len(commands)} playbook commands")
            
            return commands
            
        except Exception as e:
            self.logger.log_error(f"Error loading playbook: {e}")
            return []
    
    def _parse_playbook_content(self, content: str) -> List[PlaybookCommand]:
        """
        Parse playbook content into commands.
        
        Args:
            content: Raw playbook content
            
        Returns:
            List of parsed commands
        """
        commands = []
        lines = content.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            try:
                command = self._parse_playbook_line(line)
                if command:  # Only add non-None commands
                    commands.append(command)
            except Exception as e:
                self.logger.log_error(f"Error parsing line {i}: {line} - {e}")
                # Continue parsing other lines
        
        return commands
    
    def _parse_playbook_line(self, line: str) -> Optional[PlaybookCommand]:
        """
        Parse a single playbook line into a command.
        
        Args:
            line: The line to parse
            
        Returns:
            Parsed command or None if invalid
        """
        parts = line.split(' ', 1)
        if len(parts) < 1:
            return None
        
        action = parts[0].upper()
        value = parts[1].strip() if len(parts) > 1 else ""
        
        # Remove quotes if present
        if len(value) >= 2 and ((value.startswith('"') and value.endswith('"')) or 
                              (value.startswith("'") and value.endswith("'"))):
            value = value[1:-1]
        
        # Handle different command types
        if action == 'SEND':
            return PlaybookCommand(
                command_type="send_only",
                command=value
            )
        elif action == 'WAIT':
            return PlaybookCommand(
                command_type="wait_for_output", 
                command="",
                expected_text=value,
                wait_timeout=self.get_wait_timeout()
            )
        elif action == 'PAUSE':
            try:
                delay = float(value)
                return PlaybookCommand(
                    command_type="send_only",
                    command="",
                    delay=delay
                )
            except ValueError:
                raise ValueError(f"Invalid pause time: {value}")
        elif action.startswith('IF_'):
            return PlaybookCommand(
                command_type="IF",
                command=action.lower(),
                expected_text=value
            )
        elif action.startswith('ELIF_'):
            return PlaybookCommand(
                command_type="ELIF", 
                command=action.lower(),
                expected_text=value
            )
        elif action == 'ELSE':
            return PlaybookCommand(
                command_type="ELSE",
                command="else"
            )
        elif action == 'ENDIF':
            return PlaybookCommand(
                command_type="ENDIF",
                command="endif"
            )
        elif action == 'SUCCESS':
            # SUCCESS command sets custom success message but doesn't get executed
            self.success_message = value
            return None  # Don't add to command list
        else:
            # Treat as regular command
            return PlaybookCommand(
                command_type="wait_for_output",
                command=line,
                expected_text="PROMPT",
                wait_timeout=self.get_wait_timeout()
            )
    
    def get_success_message(self) -> Optional[str]:
        """Get the custom success message if one was defined in the playbook."""
        return self.success_message
    
    def filter_login_steps(self, commands: List[PlaybookCommand]) -> List[PlaybookCommand]:
        """
        Filter out login-related steps from the playbook.
        
        Args:
            commands: Original list of playbook commands
            
        Returns:
            Filtered list with login steps removed
        """
        filtered_commands = []
        login_keywords = ['login:', 'username:', 'user:', 'password:', 'admin', 'enable']
        common_login_cmds = ['admin', 'enable', 'login', 'su']
        in_login_sequence = True  # Start assuming we're in login sequence
        
        for command in commands:
            is_login_step = False
            
            if in_login_sequence:
                if command.command_type == 'wait_for_output':
                    # Check for login-related wait patterns
                    if command.expected_text:
                        wait_value_lower = command.expected_text.lower().strip()
                        if any(keyword in wait_value_lower for keyword in login_keywords):
                            is_login_step = True
                        elif wait_value_lower in ['prompt', '>', '#', '$']:
                            is_login_step = True  # Prompt waits during login
                elif command.command_type == 'send_only':
                    # Check for login-related send patterns
                    if command.command:
                        send_value_lower = command.command.lower().strip()
                        if any(keyword in send_value_lower for keyword in login_keywords):
                            is_login_step = True
                        elif send_value_lower in common_login_cmds:
                            is_login_step = True
                        elif len(command.command.strip()) < 20 and not any(cmd in command.command.lower() for cmd in ['show', 'config', 'display', 'get', 'set']):
                            # Short non-command strings (likely passwords/usernames)
                            is_login_step = True
                        
                        # If we see actual configuration commands, we're past login
                        if any(cmd in command.command.lower() for cmd in ['show', 'config', 'display', 'get', 'set']):
                            in_login_sequence = False
                            is_login_step = False
                
                # Special handling for wait_for_output with commands (treated as 'command' type in original)
                if command.command_type == 'wait_for_output' and command.command and command.expected_text == "PROMPT":
                    # This is a regular command (not a wait), we're past login
                    in_login_sequence = False
                    is_login_step = False
            
            if is_login_step:
                self.logger.log_debug(f"Skipping login step: {command.command_type.upper()} {command.command or command.expected_text}")
            else:
                filtered_commands.append(command)
        
        self.logger.log_info(f"Filtered playbook to {len(filtered_commands)} steps (skipped {len(commands) - len(filtered_commands)} login steps)")
        return filtered_commands
