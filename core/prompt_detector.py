"""
Prompt detection utilities for SerialLink.

Automatically detects command prompts from various network devices:
- hostname>
- admin@switch01#
- switch01(config)#
"""

import re
from typing import Optional


class PromptDetector:
    """Handles automatic prompt detection for network devices."""
    
    def __init__(self, logger):
        """
        Initialize the prompt detector.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger
    
    def detect_prompt_from_output(self, buffer_text: str) -> Optional[str]:
        """
        Automatically detect the command prompt from device output.
        Returns the detected prompt or None if not found.
        
        Args:
            buffer_text: The output buffer to analyze
            
        Returns:
            Detected prompt string or None
        """
        try:
            if not buffer_text or not buffer_text.strip():
                self.logger.log_debug("Empty buffer provided for prompt detection")
                return None
            
            # Common prompt patterns for network devices (ordered by specificity)
            prompt_patterns = [
                r'[\w\-\.@]+\([^)]+\)[>#]\s*$',     # hostname(config)# or user@host(config)>
                r'[\w\-\.@]+[:#]\~?[\w/]*[\$>#]\s*$', # user@host:~/path$ or user@host#
                r'[\w\-\.]+[>#]\s*$',               # hostname> or hostname#
                r'[>#]\s*$',                        # Simple > or #
                r'[\w\-\.]+:\s*$',                  # hostname:
            ]
            
            lines = buffer_text.strip().split('\n')
            for line in reversed(lines[-15:]):  # Check last 15 lines for better coverage
                line = line.strip()
                if not line:
                    continue
                    
                # Skip obvious non-prompt lines
                if any(skip in line.lower() for skip in ['password', 'login', 'welcome', 'last login']):
                    continue
                    
                for pattern in prompt_patterns:
                    try:
                        match = re.search(pattern, line)
                        if match:
                            detected = match.group().strip()
                            self.logger.log_success(f"Auto-detected prompt: '{detected}'")
                            return detected
                    except re.error as e:
                        self.logger.log_warning(f"Regex error in prompt detection pattern '{pattern}': {e}")
                        continue
            
            self.logger.log_debug("No prompt pattern matched in buffer text")
            return None
        except ImportError:
            self.logger.log_error("Failed to import 're' module for prompt detection")
            return None
        except Exception as e:
            self.logger.log_error(f"Error in prompt detection: {e}")
            return None
    
    def check_if_logged_in(self, output_buffer: str, detected_prompt: Optional[str], 
                          prompt_symbol: str) -> bool:
        """
        Check if device output indicates we're already logged in.
        
        Args:
            output_buffer: Output buffer to analyze
            detected_prompt: Previously detected prompt
            prompt_symbol: Fallback prompt symbol
            
        Returns:
            True if appears to be logged in, False otherwise
        """
        try:
            # Check if response contains a command prompt
            if detected_prompt and detected_prompt in output_buffer:
                return True
            elif prompt_symbol in output_buffer:
                return True
            elif any(prompt in output_buffer for prompt in ['#', '>', '$', '(config)']):
                return True
            
            # If we get help output or command response, we're logged in
            if any(keyword in output_buffer.lower() for keyword in ['commands', 'help', 'available', 'syntax']):
                return True
            elif any(prompt in output_buffer for prompt in ['#', '>', '$']):
                return True
            
            return False
            
        except Exception as e:
            self.logger.log_debug(f"Login check failed: {e}")
            return False
