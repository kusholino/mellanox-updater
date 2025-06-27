"""
Conditional logic processor for SerialLink.

Handles IF/ELIF/ELSE/ENDIF statements with support for:
- Text matching (case-sensitive and case-insensitive)
- Regular expression patterns
- NOT conditions
"""

import re
from typing import Optional, List


class ConditionalState:
    """Represents the state of a conditional block."""
    
    def __init__(self, condition_type: str, condition_met: bool = False, executed: bool = False):
        self.condition_type = condition_type  # 'if', 'elif', 'else'
        self.condition_met = condition_met   # Was the condition true?
        self.executed = executed             # Has this branch been executed?


class ConditionalProcessor:
    """Handles evaluation and execution of conditional statements in playbooks."""
    
    def __init__(self, logger):
        """
        Initialize the conditional processor.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger
        self.last_command_output = ""
        self.condition_stack: List[ConditionalState] = []
    
    def reset(self):
        """Reset the processor state for a new playbook execution."""
        self.last_command_output = ""
        self.condition_stack = []
    
    def update_last_output(self, output: str):
        """
        Update the last command output for conditional evaluation.
        
        Args:
            output: The output from the last command
        """
        self.last_command_output = output
        # Only log in debug mode when there are issues
        # self.logger.log_debug(f"Updated last output for conditionals: {len(output)} characters")
    
    def should_execute_command(self, command) -> bool:
        """
        Determine if a command should be executed based on conditional logic.
        
        Args:
            command: The command to check
            
        Returns:
            True if command should be executed, False otherwise
        """
        # If no conditional blocks are active, execute the command
        if not self.condition_stack:
            return True
        
        # Check the current conditional state
        current_state = self.condition_stack[-1]
        
        # If we're in an IF/ELIF block and the condition was met, execute
        if current_state.condition_type in ['if', 'elif'] and current_state.condition_met:
            return True
        
        # If we're in an ELSE block and no previous conditions were met, execute
        if current_state.condition_type == 'else' and not current_state.executed:
            return True
        
        # Otherwise, skip the command
        return False
    
    def _evaluate_condition(self, condition_cmd: str, search_text: str) -> bool:
        """
        Evaluate a conditional statement against the last command output.
        
        Args:
            condition_cmd: The condition command (e.g., 'if_contains', 'if_not_contains')
            search_text: The text to search for
            
        Returns:
            True if condition is met, False otherwise
        """
        if not self.last_command_output:
            self.logger.log_debug(f"No output available for condition evaluation: {condition_cmd}")
            return False
        
        # Remove verbose debug logging for normal operation
        # self.logger.log_debug(f"Evaluating condition: {condition_cmd} with text: '{search_text}'")
        # self.logger.log_debug(f"Against output: '{self.last_command_output[:100]}...'")
        
        # Case-sensitive conditions
        if condition_cmd == 'if_contains':
            result = search_text in self.last_command_output
        elif condition_cmd == 'if_not_contains':
            result = search_text not in self.last_command_output
        elif condition_cmd == 'elif_contains':
            result = search_text in self.last_command_output
        elif condition_cmd == 'elif_not_contains':
            result = search_text not in self.last_command_output
            
        # Case-insensitive conditions
        elif condition_cmd == 'if_contains_i':
            result = search_text.lower() in self.last_command_output.lower()
        elif condition_cmd == 'if_not_contains_i':
            result = search_text.lower() not in self.last_command_output.lower()
        elif condition_cmd == 'elif_contains_i':
            result = search_text.lower() in self.last_command_output.lower()
        elif condition_cmd == 'elif_not_contains_i':
            result = search_text.lower() not in self.last_command_output.lower()
            
        # Regular expression conditions
        elif condition_cmd in ['if_regex', 'elif_regex']:
            try:
                result = bool(re.search(search_text, self.last_command_output))
            except re.error as e:
                self.logger.log_error(f"Invalid regex pattern '{search_text}': {e}")
                result = False
        elif condition_cmd in ['if_not_regex', 'elif_not_regex']:
            try:
                result = not bool(re.search(search_text, self.last_command_output))
            except re.error as e:
                self.logger.log_error(f"Invalid regex pattern '{search_text}': {e}")
                result = False
        
        else:
            self.logger.log_warning(f"Unknown condition type: {condition_cmd}")
            result = False
        
        # Only log the final result, not all the debug details
        # self.logger.log_debug(f"Condition '{condition_cmd}' with '{search_text}' evaluated to: {result}")
        return result
    
    def process_if_command(self, command):
        """Process an IF command."""
        condition_cmd = command.command  # e.g., 'if_contains', 'if_not_contains'
        search_text = command.expected_text
        
        condition_met = self._evaluate_condition(condition_cmd, search_text)
        
        # Create new conditional state
        state = ConditionalState('if', condition_met, condition_met)
        self.condition_stack.append(state)
        
        # Only log for user clarity, not internal debug
        # self.logger.log_debug(f"IF condition: {condition_cmd} '{search_text}' -> {condition_met}")
    
    def process_elif_command(self, command):
        """Process an ELIF command."""
        if not self.condition_stack or self.condition_stack[-1].condition_type not in ['if', 'elif']:
            self.logger.log_error("ELIF without matching IF")
            return
        
        current_state = self.condition_stack[-1]
        
        # Only evaluate ELIF if no previous conditions were met
        if not current_state.executed:
            condition_cmd = command.command  # e.g., 'elif_contains', 'elif_not_contains'
            search_text = command.expected_text
            
            condition_met = self._evaluate_condition(condition_cmd, search_text)
            
            # Update the current state
            current_state.condition_type = 'elif'
            current_state.condition_met = condition_met
            if condition_met:
                current_state.executed = True
        else:
            # Previous condition was already met, so skip this ELIF
            current_state.condition_type = 'elif'
            current_state.condition_met = False
        
        # Remove verbose debug logging
        # self.logger.log_debug(f"ELIF condition evaluated, should execute: {current_state.condition_met}")
    
    def process_else_command(self, command):
        """Process an ELSE command."""
        if not self.condition_stack or self.condition_stack[-1].condition_type not in ['if', 'elif']:
            self.logger.log_error("ELSE without matching IF")
            return
        
        current_state = self.condition_stack[-1]
        
        # ELSE executes if no previous conditions were met
        current_state.condition_type = 'else'
        current_state.condition_met = not current_state.executed
        
        # Remove verbose debug logging
        # self.logger.log_debug(f"ELSE condition, should execute: {current_state.condition_met}")
    
    def process_endif_command(self, command):
        """Process an ENDIF command."""
        if not self.condition_stack:
            self.logger.log_error("ENDIF without matching IF")
            return
        
        # Pop the current conditional state
        self.condition_stack.pop()
        # Remove verbose debug logging
        # self.logger.log_debug("ENDIF processed, conditional block closed")
