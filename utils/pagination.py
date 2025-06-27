"""
Pagination handling utilities for SerialLink.

Automatically detects and responds to device pagination prompts like:
- --More--
- Press any key to continue
- Continue? [y/n]
"""

import re
import time


class PaginationHandler:
    """Handles automatic pagination detection and responses."""
    
    def __init__(self, logger, enabled=True, delay=0.1, custom_patterns=None):
        """
        Initialize pagination handler.
        
        Args:
            logger: Logger instance for output
            enabled (bool): Whether pagination handling is enabled
            delay (float): Delay after sending pagination responses
            custom_patterns (list): Additional pagination patterns from config
        """
        self.logger = logger
        self.enabled = enabled
        self.delay = delay
        self.custom_patterns = custom_patterns or []
        
        # Common pagination prompts to detect
        self.default_patterns = [
            r'--More--',
            r'--- MORE ---',
            r'Press any key to continue',
            r'\(q\)uit.*more',
            r'Continue\? \[y/n\]',
            r'Next page\?',
            r'--\s*Press\s+SPACE\s+to\s+continue',
            r'\(Press q to quit\)',
            r'Type <space> for more',
            r'More \(.*\)',
            r'--More-- \(.*\)',
            r'\[Press space to continue\]',
            r'Press SPACE to continue or Q to quit',
        ]
        
        # Combine default and custom patterns
        all_patterns = self.default_patterns + self.custom_patterns
        
        # Compile regex patterns for efficiency
        try:
            self.pagination_regex = re.compile('|'.join(all_patterns), re.IGNORECASE | re.MULTILINE)
        except re.error as e:
            self.logger.log_error(f"Error compiling pagination regex: {e}")
            self.pagination_regex = None
            self.enabled = False
    
    def check_and_respond(self, serial_connection, output_buffer):
        """
        Check for pagination prompts and respond automatically.
        
        Args:
            serial_connection: The serial connection object
            output_buffer (str): Recent output to check for pagination
            
        Returns:
            bool: True if pagination prompt was detected and handled
        """
        if not self.enabled or not self.pagination_regex:
            return False
            
        try:
            # Look for pagination prompts in the recent output (last 200 chars to be efficient)
            recent_output = output_buffer[-200:] if len(output_buffer) > 200 else output_buffer
            pagination_match = self.pagination_regex.search(recent_output)
            
            if pagination_match:
                pagination_prompt = pagination_match.group()
                self.logger.log_debug(f"Pagination detected: '{pagination_prompt}'")
                
                # Determine the appropriate response based on the prompt
                if any(keyword in pagination_prompt.lower() for keyword in ['space', 'continue', '--more--', '--- more ---']):
                    # Send space for "press space to continue" type prompts
                    serial_connection.write(b' ')
                    self.logger.log_debug("Sent: SPACE")
                elif 'any key' in pagination_prompt.lower():
                    # Send enter for "press any key" prompts
                    serial_connection.write(b'\n')
                    self.logger.log_debug("Sent: ENTER")
                elif '[y/n]' in pagination_prompt.lower() or 'continue?' in pagination_prompt.lower():
                    # Send 'y' for yes/no continue prompts
                    serial_connection.write(b'y\n')
                    self.logger.log_debug("Sent: y + ENTER")
                else:
                    # Default: send space (most common for pagination)
                    serial_connection.write(b' ')
                    self.logger.log_debug("Sent: SPACE (default)")
                
                # Small delay after pagination response
                time.sleep(self.delay)
                return True
                
        except Exception as e:
            self.logger.log_warning(f"Error in pagination handling: {e}")
            
        return False
    
    def is_enabled(self) -> bool:
        """
        Check if pagination handling is enabled.
        
        Returns:
            True if pagination handling is enabled, False otherwise
        """
        return self.enabled
