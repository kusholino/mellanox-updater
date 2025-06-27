"""
Output processing utilities for SerialLink.

Handles cleaning and formatting of command output:
- Removes command echoes
- Filters out pagination artifacts
- Cleans prompt lines
"""

import re


class OutputProcessor:
    """Processes and cleans command output for display and conditional logic."""
    
    def __init__(self, logger):
        """
        Initialize output processor with cleanup patterns.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger
        # Pagination patterns to remove from output
        self.pagination_cleanup_patterns = [
            r'--More--.*',
            r'--- MORE ---.*',
            r'Press any key to continue.*',
            r'\(q\)uit.*more.*',
            r'Continue\? \[y/n\].*',
            r'Next page\?.*',
            r'--\s*Press\s+SPACE\s+to\s+continue.*',
            r'\(Press q to quit\).*',
            r'Type <space> for more.*',
            r'More \(.*\).*',
            r'--More-- \(.*\).*',
            r'\[Press space to continue\].*',
            r'Press SPACE to continue or Q to quit.*',
        ]
        
        try:
            self.cleanup_regex = re.compile('|'.join(self.pagination_cleanup_patterns), re.IGNORECASE)
        except re.error as e:
            self.logger.log_warning(f"Error compiling cleanup regex: {e}")
            self.cleanup_regex = None
    
    def clean_output_for_display(self, captured_output, last_command_sent, wait_value, detected_prompt):
        """
        Clean command output for verbose display.
        
        Args:
            captured_output (str): Raw command output
            last_command_sent (str): The command that was sent
            wait_value (str): The text we were waiting for
            detected_prompt (str): Auto-detected prompt
            
        Returns:
            list: List of cleaned output lines
        """
        if not captured_output.strip():
            return []
            
        lines = captured_output.strip().split('\n')
        output_lines = []
        
        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip the command echo (usually the first non-empty line)
            if last_command_sent and last_command_sent in line and i == 0:
                continue
                
            # Skip the final prompt line (ends with the wait value or detected prompt)
            is_final_prompt = (line.endswith(wait_value) and i == len(lines) - 1)
            if not is_final_prompt and detected_prompt:
                # Also check if line ends with detected prompt
                is_final_prompt = (detected_prompt in line and i == len(lines) - 1)
            if is_final_prompt:
                continue
            
            # Remove pagination artifacts
            if self.cleanup_regex:
                try:
                    if self.cleanup_regex.search(line):
                        self.logger.log_debug(f"Cleaned pagination artifact: '{line[:50]}...'")
                        continue
                except Exception as e:
                    self.logger.log_warning(f"Error applying cleanup regex: {e}")
                    # Continue without regex cleanup
                    
            output_lines.append(line)
        
        return output_lines
    
    def display_output(self, output_lines):
        """
        Display cleaned output lines.
        
        Args:
            output_lines (list): List of cleaned output lines
        """
        if output_lines:
            for line in output_lines:
                print(f"  {line}")
        else:
            self.logger.log_info("No output or command completed successfully")
        print()  # Add spacing after output
    
    def clean_output_for_conditions(self, captured_output):
        """
        Clean output for use in conditional logic (minimal cleaning).
        
        Args:
            captured_output (str): Raw command output
            
        Returns:
            str: Cleaned output for conditional evaluation
        """
        # For conditional logic, we want minimal cleaning to preserve
        # as much context as possible for pattern matching
        return captured_output.strip() if captured_output else ""
    
    def process_output(self, captured_output, last_command_sent, wait_value, detected_prompt):
        """
        Process command output for display (wrapper method for compatibility).
        
        Args:
            captured_output (str): Raw command output
            last_command_sent (str): The last command that was sent
            wait_value (str): The value being waited for
            detected_prompt (str): The detected prompt string
            
        Returns:
            list: List of cleaned output lines
        """
        return self.clean_output_for_display(captured_output, last_command_sent, wait_value, detected_prompt)
