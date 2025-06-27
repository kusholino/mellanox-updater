"""
Playbook executor for the Mellanox device updater.

This module handles the execution of playbook commands including:
- Processing individual commands
- Handling command flow and timing
- Managing different command types (send_only, wait_for_output, etc.)
- Progress tracking and reporting
"""

import time
from typing import Dict, List, Optional, Tuple

from utils.logger import Logger
from utils.output_processor import OutputProcessor
from core.serial_handler import SerialHandler
from core.conditional_logic import ConditionalProcessor
from config.config_manager import PlaybookCommand


class PlaybookExecutor:
    """Handles execution of playbook commands."""
    
    def __init__(self, logger: Logger, serial_handler: SerialHandler, 
                 output_processor: OutputProcessor, conditional_processor: ConditionalProcessor):
        """
        Initialize the playbook executor.
        
        Args:
            logger: Logger instance for output
            serial_handler: Serial communication handler
            output_processor: Output processor for cleaning text
            conditional_processor: Processor for conditional logic
        """
        self.logger = logger
        self.serial_handler = serial_handler
        self.output_processor = output_processor
        self.conditional_processor = conditional_processor
        
        # Execution state
        self.total_commands = 0
        self.completed_commands = 0
        self.execution_times = []
        self.detected_prompt = None
        self.prompt_symbol = ">"
    
    def execute_playbook(self, commands: List[PlaybookCommand], 
                        detected_prompt: Optional[str], prompt_symbol: str) -> bool:
        """
        Execute a complete playbook of commands.
        
        Args:
            commands: List of playbook commands to execute
            detected_prompt: Auto-detected prompt string
            prompt_symbol: Fallback prompt symbol
            
        Returns:
            True if all commands executed successfully, False otherwise
        """
        self.detected_prompt = detected_prompt
        self.prompt_symbol = prompt_symbol
        self.total_commands = len(commands)
        self.completed_commands = 0
        self.execution_times = []
        
        # Display initial progress
        self.logger.log_section("Playbook Execution")
        self.logger.show_progress(0, self.total_commands, "Starting playbook execution...")
        
        # Initialize conditional processor
        self.conditional_processor.reset()
        
        success = True
        command_index = 0
        
        while command_index < len(commands):
            command = commands[command_index]
            step_num = command_index + 1
            
            # Prepare action description for logging
            action_desc = self._get_action_description(command, step_num)
            
            # Log the step we're executing
            self.logger.log_command_execution(action_desc, command.command, step_num)
            
            # Check if we should skip this command due to conditional logic
            if not self.conditional_processor.should_execute_command(command):
                self.logger.log_debug(f"Skipping command due to conditional logic: {command.command}")
                command_index += 1
                continue
            
            # Execute the command
            command_success = self._execute_single_command(command, step_num)
            
            if not command_success:
                success = False
                if not self._handle_command_failure(command, step_num):
                    break
            
            self.completed_commands += 1
            command_index += 1
            
            # Update progress
            progress_desc = f"Completed {self.completed_commands}/{self.total_commands} commands"
            self.logger.show_progress(self.completed_commands, self.total_commands, progress_desc)
        
        # Show final results
        self._show_execution_summary(success)
        return success
    
    def _get_action_description(self, command: PlaybookCommand, step_num: int) -> str:
        """
        Generate a user-friendly action description.
        
        Args:
            command: The command to describe
            step_num: Step number for verbose mode
            
        Returns:
            Action description string
        """
        if command.command_type == "send_only":
            if self.logger.verbose_mode:
                return f"Step {step_num}: Sending command"
            else:
                # Clean action description for progress bar
                cmd_display = command.command[:30] + "..." if len(command.command) > 30 else command.command
                return f"Sending: {cmd_display}"
        elif command.command_type == "wait_for_output":
            if command.expected_text.upper() == "PROMPT":
                if self.logger.verbose_mode:
                    if self.detected_prompt:
                        return f"Step {step_num}: Waiting for auto-detected prompt '{self.detected_prompt}'"
                    else:
                        return f"Step {step_num}: Waiting for fallback prompt '{self.prompt_symbol}'"
                else:
                    return "Waiting for prompt"
            else:
                if self.logger.verbose_mode:
                    return f"Step {step_num}: Waiting for '{command.expected_text}'"
                else:
                    exp_display = command.expected_text[:20] + "..." if len(command.expected_text) > 20 else command.expected_text
                    return f"Waiting for: {exp_display}"
        else:
            if self.logger.verbose_mode:
                return f"Step {step_num}: {command.command_type}"
            else:
                return command.command_type
    
    def _execute_single_command(self, command: PlaybookCommand, step_num: int) -> bool:
        """
        Execute a single playbook command.
        
        Args:
            command: The command to execute
            step_num: Step number for logging
            
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        
        try:
            # Handle different command types
            if command.command_type == "IF":
                return self._handle_conditional_command(command)
            elif command.command_type in ["ELIF", "ELSE", "ENDIF"]:
                return self._handle_conditional_command(command)
            elif command.command_type == "send_only":
                return self._execute_send_only_command(command, step_num)
            elif command.command_type == "wait_for_output":
                return self._execute_wait_for_output_command(command, step_num)
            else:
                self.logger.log_error(f"Unknown command type: {command.command_type}")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Error executing command {step_num}: {e}")
            return False
        finally:
            execution_time = time.time() - start_time
            self.execution_times.append(execution_time)
    
    def _handle_conditional_command(self, command: PlaybookCommand) -> bool:
        """
        Handle conditional logic commands (IF/ELIF/ELSE/ENDIF).
        
        Args:
            command: The conditional command
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            if command.command_type == "IF":
                self.conditional_processor.process_if_command(command)
            elif command.command_type == "ELIF":
                self.conditional_processor.process_elif_command(command)
            elif command.command_type == "ELSE":
                self.conditional_processor.process_else_command(command)
            elif command.command_type == "ENDIF":
                self.conditional_processor.process_endif_command(command)
            
            return True
        except Exception as e:
            self.logger.log_error(f"Error processing conditional command: {e}")
            return False
    
    def _execute_send_only_command(self, command: PlaybookCommand, step_num: int) -> bool:
        """
        Execute a send-only command (no output expected).
        
        Args:
            command: The send-only command
            step_num: Step number for logging
            
        Returns:
            True if successful, False otherwise
        """
        # Send the command
        if not self.serial_handler.send_command(command.command):
            return False
        
        # Wait for any specified delay
        if command.delay and command.delay > 0:
            time.sleep(command.delay)
        
        # Log success
        if self.logger.verbose_mode:
            self.logger.log_command_success(f"Step {step_num}: Command sent", command.command)
        else:
            self.logger.log_command_success("Command sent")
        return True
    
    def _execute_wait_for_output_command(self, command: PlaybookCommand, step_num: int) -> bool:
        """
        Execute a command that waits for specific output.
        
        Args:
            command: The wait-for-output command
            step_num: Step number for logging
            
        Returns:
            True if successful, False otherwise
        """
        # Send the command if there is one
        if command.command and not self.serial_handler.send_command(command.command):
            return False
        
        # Wait for the expected output
        # Only check existing buffer for the very first wait command (login prompt)
        # and for actual login/password prompts that could already be visible
        is_first_command = self.completed_commands == 0
        is_login_prompt = command.expected_text.lower() in ['login:', 'username:']
        
        check_buffer = is_first_command or is_login_prompt
        
        success, raw_output = self.serial_handler.wait_for_output(
            command.expected_text,
            command.wait_timeout,
            self.detected_prompt,
            self.prompt_symbol,
            check_existing_buffer=check_buffer,
            handle_pagination=True
        )
        
        if success:
            # Process and display the output
            cleaned_output = self.output_processor.process_output(
                raw_output, command.command, command.expected_text, self.detected_prompt
            )
            
            if cleaned_output and isinstance(cleaned_output, list):
                output_text = '\n'.join(cleaned_output)
            else:
                output_text = cleaned_output or raw_output
            
            if output_text and output_text.strip():
                self.logger.log_output(output_text)
            
            # Update conditional processor with the output
            self.conditional_processor.update_last_output(output_text)
            
            # Log command success
            if command.command:
                if self.logger.verbose_mode:
                    self.logger.log_command_success(f"Step {step_num}: Command completed", command.command)
                else:
                    self.logger.log_command_success("Command completed")
            else:
                self.logger.log_success(f"Found expected text: '{command.expected_text}'")
            return True
        else:
            # Handle timeout or failure
            self.logger.log_warning(f"Timeout waiting for '{command.expected_text}'")
            
            # Still process any output we got
            if raw_output.strip():
                cleaned_output = self.output_processor.process_output(
                    raw_output, command.command, command.expected_text, self.detected_prompt
                )
                
                if cleaned_output and isinstance(cleaned_output, list):
                    output_text = '\n'.join(cleaned_output)
                else:
                    output_text = cleaned_output or raw_output
                    
                if output_text and output_text.strip():
                    self.logger.log_output(output_text)
                
                # Update conditional processor even on timeout
                self.conditional_processor.update_last_output(output_text)
            
            return False
    
    def _handle_command_failure(self, command: PlaybookCommand, step_num: int) -> bool:
        """
        Handle command execution failure.
        
        Args:
            command: The failed command
            step_num: Step number of the failed command
            
        Returns:
            True to continue execution, False to stop
        """
        self.logger.log_error(f"Command {step_num} failed: {command.command}")
        
        # For now, stop execution on failure
        # Could be enhanced to support continue-on-error mode
        return False
    
    def _show_execution_summary(self, success: bool):
        """
        Show a summary of the playbook execution.
        
        Args:
            success: Whether the overall execution was successful
        """
        # Close progress bar before showing summary
        self.logger.close_progress_bar()
        
        self.logger.log_section("Execution Summary")
        
        # Calculate statistics
        total_time = sum(self.execution_times)
        avg_time = total_time / len(self.execution_times) if self.execution_times else 0
        max_time = max(self.execution_times) if self.execution_times else 0
        
        # Show results
        if success:
            self.logger.log_success(f"Playbook completed successfully!")
        else:
            self.logger.log_warning("Playbook completed with some errors")
        
        self.logger.log_info(f"Commands executed: {self.completed_commands}/{self.total_commands}")
        self.logger.log_info(f"Total execution time: {total_time:.2f} seconds")
        
        if self.execution_times:
            self.logger.log_info(f"Average command time: {avg_time:.2f} seconds")
            self.logger.log_info(f"Longest command time: {max_time:.2f} seconds")
    
    def handle_login_sequence(self, username: str, password: str) -> bool:
        """
        Handle the device login sequence.
        
        Args:
            username: Username for login
            password: Password for login
            
        Returns:
            True if login successful, False otherwise
        """
        self.logger.log_section("Device Login")
        
        try:
            # Wait for username prompt
            self.logger.log_info("Waiting for username prompt...")
            success, output = self.serial_handler.wait_for_output(
                "username:", 10, self.detected_prompt, self.prompt_symbol,
                check_existing_buffer=True
            )
            
            if not success:
                self.logger.log_error("Username prompt not found")
                return False
            
            # Send username
            self.logger.log_info(f"Sending username: {username}")
            if not self.serial_handler.send_command(username):
                return False
            
            # Wait for password prompt
            self.logger.log_info("Waiting for password prompt...")
            success, output = self.serial_handler.wait_for_output(
                "password:", 10, self.detected_prompt, self.prompt_symbol
            )
            
            if not success:
                self.logger.log_error("Password prompt not found")
                return False
            
            # Send password
            self.logger.log_info("Sending password...")
            if not self.serial_handler.send_command(password):
                return False
            
            # Wait for command prompt
            self.logger.log_info("Waiting for command prompt...")
            success, output = self.serial_handler.wait_for_output(
                "PROMPT", 15, self.detected_prompt, self.prompt_symbol
            )
            
            if success:
                self.logger.log_success("Login successful!")
                return True
            else:
                self.logger.log_error("Login failed - command prompt not found")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Error during login sequence: {e}")
            return False
