#!/usr/bin/env python3
"""
SerialLink - Main Entry Point

A modular tool for automating serial communication with network devices
using configurable playbooks. Supports conditional logic, pagination handling,
and comprehensive logging.

Usage:
    python main.py [options]
    
Options:
    -p, --port <port>           Serial port (e.g., COM3, /dev/ttyUSB0)
    -b, --baudrate <rate>       Baud rate (default: 115200)
    -c, --config <file>         Configuration file (default: config.ini)
    -v, --verbose               Enable verbose logging
    -u, --username <user>       Username for device login
    --password <pass>           Password for device login
    --no-color                  Disable colored output
    --no-pagination             Disable automatic pagination handling
    --prompt-symbol <symbol>    Override prompt symbol (default: >)
    --help                      Show this help message
"""

import argparse
import sys
import os
from typing import Optional

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import Logger
from utils.pagination import PaginationHandler
from utils.output_processor import OutputProcessor
from core.prompt_detector import PromptDetector
from core.conditional_logic import ConditionalProcessor
from core.serial_handler import SerialHandler
from core.playbook_executor import PlaybookExecutor
from config.config_manager import ConfigManager


class SerialLinkUpdater:
    """Main application class for the serial device updater."""
    
    def __init__(self):
        """Initialize the application."""
        self.logger = None
        self.config_manager = None
        self.serial_handler = None
        self.playbook_executor = None
        
        # Application state
        self.config_file = "config.ini"
        self.playbook_file = None
        self.baudrate = 115200
        self.username = None
        self.password = None
        self.verbose = False
        self.use_colors = True
        self.use_pagination = True
        self.prompt_symbol = ">"
    def parse_arguments(self) -> bool:
        """
        Parse command line arguments.
        
        Returns:
            True if arguments parsed successfully, False if should exit
        """
        parser = argparse.ArgumentParser(
            description="SerialLink - Automated serial communication tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
    python main.py -u admin --password secret
    python main.py --verbose
    python main.py -c custom_config.ini --no-color
    python main.py -p custom_playbook.txt --verbose
            """
        )
        
        parser.add_argument("-b", "--baudrate", type=int, default=115200,
                          help="Baud rate (default: 115200)")
        parser.add_argument("-c", "--config", default="config.ini",
                          help="Configuration file (default: config.ini)")
        parser.add_argument("-p", "--playbook",
                          help="Playbook file (overrides config setting)")
        parser.add_argument("-v", "--verbose", action="store_true",
                          help="Enable verbose logging")
        parser.add_argument("-u", "--username",
                          help="Username for device login")
        parser.add_argument("--password",
                          help="Password for device login")
        parser.add_argument("--no-color", action="store_true",
                          help="Disable colored output")
        parser.add_argument("--no-pagination", action="store_true",
                          help="Disable automatic pagination handling")
        parser.add_argument("--prompt-symbol", default=">",
                          help="Override prompt symbol (default: >)")
        
        try:
            args = parser.parse_args()
            
            # Store parsed arguments
            self.baudrate = args.baudrate
            self.config_file = args.config
            self.playbook_file = args.playbook
            self.verbose = args.verbose
            self.username = args.username
            self.password = args.password
            self.use_colors = not args.no_color
            self.use_pagination = not args.no_pagination
            self.prompt_symbol = args.prompt_symbol
            
            return True
            
        except SystemExit:
            return False
    
    def initialize_components(self) -> bool:
        """
        Initialize all application components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize logger
            self.logger = Logger(verbose=self.verbose, use_colors=self.use_colors)
            self.logger.log_section("SerialLink")
            self.logger.log_info("Initializing components...")
            
            # Initialize configuration manager
            self.config_manager = ConfigManager(self.logger)
            
            # Load configuration
            if not self.config_manager.load_config(self.config_file):
                return False
            
            # Override config values with command line arguments
            self._override_config_with_args()
            
            # Initialize other components
            pagination_handler = PaginationHandler(self.logger, enabled=self.use_pagination)
            output_processor = OutputProcessor(self.logger)
            prompt_detector = PromptDetector(self.logger)
            conditional_processor = ConditionalProcessor(self.logger)
            
            # Initialize serial handler
            self.serial_handler = SerialHandler(
                self.logger, pagination_handler, output_processor, prompt_detector
            )
            
            # Initialize playbook executor
            self.playbook_executor = PlaybookExecutor(
                self.logger, self.serial_handler, output_processor, conditional_processor
            )
            
            self.logger.log_success("Components initialized successfully")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Failed to initialize components: {e}")
            else:
                print(f"Error: Failed to initialize components: {e}")
            return False
    
    def _override_config_with_args(self):
        """Override configuration values with command line arguments."""
        config = self.config_manager.config
        
        if self.baudrate != 115200:  # Only override if different from default
            config['DEFAULT']['baudrate'] = str(self.baudrate)
        if self.username:
            config['DEFAULT']['username'] = self.username
        if self.password:
            config['DEFAULT']['password'] = self.password
        if self.prompt_symbol != ">":
            config['DEFAULT']['prompt_symbol'] = self.prompt_symbol
    
    def setup_serial_connection(self) -> bool:
        """
        Set up the serial connection.
        
        Returns:
            True if connection established, False otherwise
        """
        try:
            # Get port from config or prompt user
            port = self.config_manager.get_port()
            if not port:
                port = SerialHandler.select_com_port(self.logger)
                if not port:
                    return False
            
            # Get baud rate
            baudrate = self.config_manager.get_baudrate()
            
            # Open the serial port
            if not self.serial_handler.open_port(port, baudrate):
                return False
            
            # Send initialization sequence
            if not self.serial_handler.send_initialization_sequence():
                return False
            
            # Read initial output
            if not self.serial_handler.read_initial_output():
                return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Failed to setup serial connection: {e}")
            return False
    
    def detect_device_state(self) -> Optional[str]:
        """
        Detect the current device state and prompt.
        
        Returns:
            Detected prompt string or None if detection failed
        """
        try:
            self.logger.log_section("Device State Detection")
            
            # Create prompt detector
            prompt_detector = PromptDetector(self.logger)
            
            # Detect prompt from initial output
            detected_prompt = prompt_detector.detect_prompt_from_output(
                self.serial_handler.full_output_buffer
            )
            
            if detected_prompt:
                self.logger.log_success(f"Auto-detected prompt: '{detected_prompt}'")
            else:
                self.logger.log_info(f"Using default prompt symbol: '{self.prompt_symbol}'")
                detected_prompt = self.prompt_symbol
                
            return detected_prompt
            
        except Exception as e:
            self.logger.log_error(f"Failed to detect device state: {e}")
            return None
    
    def check_pre_login_status(self, detected_prompt: str) -> bool:
        """
        Check if device is already logged in and filter playbook accordingly.
        
        Args:
            detected_prompt: The detected prompt string
            
        Returns:
            True if already logged in, False if login required
        """
        try:
            self.logger.log_section("Pre-Login Check")
            self.logger.log_info("Checking if already logged in to device")
            
            # Check if already logged in
            already_logged_in = self.serial_handler.check_if_logged_in(detected_prompt, self.prompt_symbol)
            
            if already_logged_in:
                self.logger.log_success("Device appears to be already logged in - skipping login steps")
                return True
            else:
                self.logger.log_info("Device requires login - proceeding with full playbook")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Failed to check login status: {e}")
            return False
    
    def handle_device_login(self, detected_prompt: str) -> bool:
        """
        Handle device login if required.
        
        Args:
            detected_prompt: The detected prompt string
            
        Returns:
            True if login successful or not required, False otherwise
        """
        try:
            # Check if we need to login
            if self.serial_handler.check_if_logged_in(detected_prompt, self.prompt_symbol):
                return True
            
            # Get credentials
            username = self.config_manager.get_username()
            password = self.config_manager.get_password()
            
            if not username or not password:
                self.logger.log_error("Username and password required for login")
                return False
            
            # Perform login
            return self.playbook_executor.handle_login_sequence(username, password)
            
        except Exception as e:
            self.logger.log_error(f"Failed to handle device login: {e}")
            return False
    
    def execute_playbook(self, detected_prompt: str, skip_login: bool = False) -> bool:
        """
        Execute the configured playbook.
        
        Args:
            detected_prompt: The detected prompt string
            skip_login: Whether to skip login steps
            
        Returns:
            True if playbook executed successfully, False otherwise
        """
        try:
            # Load playbook commands
            commands = self.config_manager.load_playbook()
            if not commands:
                self.logger.log_error("No playbook commands to execute")
                return False
            
            # Filter login steps if device is already logged in
            if skip_login:
                commands = self.config_manager.filter_login_steps(commands)
            
            # Execute the playbook
            return self.playbook_executor.execute_playbook(
                commands, detected_prompt, self.prompt_symbol
            )
            
        except Exception as e:
            self.logger.log_error(f"Failed to execute playbook: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources and close connections."""
        try:
            if self.serial_handler:
                self.serial_handler.close_port()
            
            if self.logger:
                self.logger.log_section("Cleanup")
                self.logger.log_info("Application terminated")
                
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Error during cleanup: {e}")
    
    def run(self) -> int:
        """
        Main application entry point.
        
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            # Parse command line arguments
            if not self.parse_arguments():
                return 1
            
            # Initialize components
            if not self.initialize_components():
                return 1
            
            # Setup serial connection
            if not self.setup_serial_connection():
                return 1
            
            # Detect device state
            detected_prompt = self.detect_device_state()
            if not detected_prompt:
                return 1
            
            # Check pre-login status
            skip_login = self.check_pre_login_status(detected_prompt)
            
            # Execute playbook (will handle login if needed)
            if not self.execute_playbook(detected_prompt, skip_login):
                return 1
            
            # Show success message (custom or default)
            success_msg = self.config_manager.get_success_message()
            if success_msg:
                self.logger.log_success(success_msg)
            else:
                self.logger.log_success("Application completed successfully!")
            return 0
            
        except KeyboardInterrupt:
            if self.logger:
                self.logger.log_info("Application interrupted by user")
            else:
                print("\nApplication interrupted by user")
            return 1
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Unexpected error: {e}")
            else:
                print(f"Error: {e}")
            return 1
        finally:
            self.cleanup()


def main():
    """Entry point for the application."""
    app = SerialLinkUpdater()
    exit_code = app.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
