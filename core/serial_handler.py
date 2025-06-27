"""
Serial communication handler for the Mellanox device updater.

This module handles all serial port operations including:
- Opening and closing serial connections
- Reading and writing data
- Managing the output buffer
- Handling device initialization
"""

import serial
import serial.tools.list_ports
import time
from typing import Optional, Tuple, List

from utils.logger import Logger
from utils.pagination import PaginationHandler
from utils.output_processor import OutputProcessor
from core.prompt_detector import PromptDetector


class SerialHandler:
    """Handles serial port communication and device management."""
    
    def __init__(self, logger: Logger, pagination_handler: PaginationHandler, 
                 output_processor: OutputProcessor, prompt_detector: PromptDetector):
        """
        Initialize the serial handler.
        
        Args:
            logger: Logger instance for output
            pagination_handler: Handler for pagination responses
            output_processor: Processor for cleaning output
            prompt_detector: Detector for command prompts
        """
        self.logger = logger
        self.pagination_handler = pagination_handler
        self.output_processor = output_processor
        self.prompt_detector = prompt_detector
        self.ser: Optional[serial.Serial] = None
        self.full_output_buffer = ""
        self.is_connected = False
    
    def open_port(self, port: str, baudrate: int) -> bool:
        """
        Open a serial port with the specified parameters.
        
        Args:
            port: The COM port to connect to
            baudrate: The baud rate for the connection
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.log_section("Serial Connection Setup")
        self.logger.log_info(f"Opening port {port} at {baudrate} baud")
        
        try:
            # Check if port is already in use by another process
            self._check_port_availability(port, baudrate)
            
            self.ser = serial.Serial(port, baudrate, timeout=1)
            self.is_connected = True
            self.logger.log_success("Serial port opened successfully")
            return True
            
        except serial.SerialException as e:
            self._handle_serial_exception(e)
            return False
        except Exception as e:
            self.logger.log_error(f"Unexpected error opening port: {e}")
            return False
    
    def _check_port_availability(self, port: str, baudrate: int):
        """Check if the port is available for use."""
        try:
            # Try to open with exclusive access
            test_ser = serial.Serial()
            test_ser.port = port
            test_ser.baudrate = baudrate
            test_ser.timeout = 0.5
            # Note: exclusive flag may not be supported on all platforms
            if hasattr(test_ser, 'exclusive'):
                test_ser.exclusive = True  # This will fail if port is in use
            test_ser.open()
            test_ser.close()
            self.logger.log_debug("Port availability check passed")
        except serial.SerialException as e:
            if "access denied" in str(e).lower() or "permission denied" in str(e).lower():
                self.logger.log_error(f"Port {port} is already in use by another application or requires elevated permissions")
                self.logger.log_error("Please close other serial applications or run with appropriate permissions")
                raise
            elif "device busy" in str(e).lower() or "resource busy" in str(e).lower():
                self.logger.log_error(f"Port {port} is currently busy/locked by another process")
                self.logger.log_error("Please close other applications using this serial port")
                raise
            else:
                # Other serial exceptions, continue with normal opening
                self.logger.log_debug(f"Port check exception (proceeding): {e}")
        except Exception as e:
            # Non-serial exceptions, continue with normal opening
            self.logger.log_debug(f"Port check failed (proceeding): {e}")
    
    def _handle_serial_exception(self, e: serial.SerialException):
        """Handle serial port opening exceptions with specific error messages."""
        error_msg = str(e).lower()
        if "access denied" in error_msg or "permission denied" in error_msg:
            self.logger.log_error("Failed to open serial port: Permission denied")
            self.logger.log_error("Try running with sudo or check if another application is using the port")
        elif "device busy" in error_msg or "resource busy" in error_msg:
            self.logger.log_error("Failed to open serial port: Port is busy")
            self.logger.log_error("Another application may be using this serial port")
        elif "no such file" in error_msg or "cannot find" in error_msg:
            self.logger.log_error("Failed to open serial port: Port not found")
            self.logger.log_error("Please check if the device is connected and the port exists")
        else:
            self.logger.log_error(f"Failed to open serial port: {e}")
    
    def close_port(self):
        """Close the serial port if it's open."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                self.is_connected = False
                self.logger.log_info("Serial port closed")
            except Exception as e:
                self.logger.log_error(f"Error closing serial port: {e}")
    
    def send_initialization_sequence(self) -> bool:
        """
        Send the device initialization sequence.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.log_section("Device Initialization")
        self.logger.log_info("Sending initialization sequence (Enter, Ctrl+C, Enter)")
        
        try:
            self.ser.write(b'\n')
            time.sleep(0.2)
            self.ser.write(b'\x03')  # Ctrl+C
            time.sleep(0.2)
            self.ser.write(b'\n')
            time.sleep(1)
            self.logger.log_success("Initialization sequence sent")
            return True
        except Exception as e:
            self.logger.log_error(f"Failed to send initialization sequence: {e}")
            return False
    
    def read_initial_output(self, duration: float = 2.0) -> bool:
        """
        Read initial output for the specified duration to populate the buffer.
        
        Args:
            duration: Time to read in seconds
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.log_section("Initial Device Communication")
        self.logger.log_info(f"Reading initial output for {duration} seconds")
        
        try:
            start_time = time.time()
            while time.time() - start_time < duration:
                if self.ser.in_waiting > 0:
                    self.full_output_buffer += self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
                time.sleep(0.1)
            self.logger.log_success("Initial output reading completed")
            return True
        except Exception as e:
            self.logger.log_error(f"Error reading initial output: {e}")
            return False
    
    def check_if_logged_in(self, detected_prompt: Optional[str], prompt_symbol: str) -> bool:
        """
        Check if we're already at a command prompt (logged in).
        
        Args:
            detected_prompt: Auto-detected prompt string
            prompt_symbol: Fallback prompt symbol
            
        Returns:
            True if logged in, False if need to login
        """
        try:
            # Check the existing buffer for login indicators
            buffer_lower = self.full_output_buffer.lower()
            
            # If we see login prompts, we're definitely NOT logged in
            if any(login_indicator in buffer_lower for login_indicator in 
                   ['login:', 'username:', 'password:', 'user name:']):
                self.logger.log_debug("Found login prompts in buffer - not logged in")
                return False
            
            # If we see command prompts, we might be logged in
            if detected_prompt and detected_prompt in self.full_output_buffer:
                self.logger.log_debug(f"Found detected prompt '{detected_prompt}' - appears logged in")
                return True
            elif any(prompt in self.full_output_buffer for prompt in ['#', '>', '$']):
                self.logger.log_debug("Found command prompt characters - appears logged in")
                return True
            
            # If buffer is mostly empty or unclear, assume we need to login
            if len(self.full_output_buffer.strip()) < 10:
                self.logger.log_debug("Buffer too short to determine - assuming need login")
                return False
            
            # Default to requiring login if unclear
            self.logger.log_debug("Cannot determine login status - assuming need login")
            return False
            
        except Exception as e:
            self.logger.log_error(f"Error checking login status: {e}")
            return False
            
        except Exception as e:
            self.logger.log_debug(f"Login check failed: {e}")
            return False
    
    def send_command(self, command: str) -> bool:
        """
        Send a command to the device.
        
        Args:
            command: The command to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ser.write(command.encode('utf-8') + b'\n')
            # Give a small delay for the command to be processed
            time.sleep(0.1)
            return True
        except Exception as e:
            self.logger.log_error(f"Failed to send command: {e}")
            return False
    
    def wait_for_output(self, expected_text: str, wait_timeout: int, 
                       detected_prompt: Optional[str], prompt_symbol: str,
                       check_existing_buffer: bool = True, 
                       handle_pagination: bool = True) -> Tuple[bool, str]:
        """
        Wait for specific text in the serial output with pagination handling.
        
        Args:
            expected_text: Text to wait for (or 'PROMPT' for auto-detected prompt)
            wait_timeout: Timeout in seconds
            detected_prompt: Auto-detected prompt string
            prompt_symbol: Fallback prompt symbol
            check_existing_buffer: If True, check pre-existing buffer first
            handle_pagination: If True, automatically respond to pagination prompts
        
        Returns:
            Tuple of (success, captured_output)
        """
        try:
            # Handle dynamic prompt detection
            if expected_text.upper() == 'PROMPT':
                if detected_prompt:
                    actual_expected_text = detected_prompt
                else:
                    actual_expected_text = prompt_symbol
            else:
                actual_expected_text = expected_text
            
            # Use pagination handler for pagination management
            handle_pagination = handle_pagination and self.pagination_handler.is_enabled()
            
            # For login prompts and initial waits, check existing buffer first
            if check_existing_buffer:
                # Case-insensitive search for login prompts
                search_text = actual_expected_text.lower()
                buffer_text = self.full_output_buffer.lower()
                
                if search_text in buffer_text:
                    self.logger.log_debug(f"Found expected text: '{actual_expected_text}' (pre-existing)")
                    
                    # Find the actual match in the original case buffer
                    match_index = self.full_output_buffer.lower().find(search_text)
                    end_of_match = match_index + len(actual_expected_text)
                    
                    captured_output = self.full_output_buffer[:end_of_match]
                    self.full_output_buffer = self.full_output_buffer[end_of_match:]  # Consume the matched part
                    return True, captured_output
            
            # Read new data from serial port
            start_time = time.time()
            new_output = ""
            last_data_time = start_time
            consecutive_empty_reads = 0
            
            while time.time() - start_time < wait_timeout:
                try:
                    if self.ser.in_waiting > 0:
                        incoming_bytes = self.ser.read(self.ser.in_waiting)
                        incoming_text = incoming_bytes.decode('utf-8', errors='ignore')
                        new_output += incoming_text
                        self.full_output_buffer += incoming_text
                        last_data_time = time.time()
                        consecutive_empty_reads = 0
                        
                        # For long outputs, show progress
                        if len(new_output) > 1000 and len(new_output) % 2000 == 0:
                            lines = new_output.count('\n')
                            self.logger.log_debug(f"Receiving data: {len(new_output)} chars, {lines} lines")
                    
                        # PAGINATION HANDLING: Check for pagination prompts and respond automatically
                        if handle_pagination:
                            pagination_response = self.pagination_handler.check_and_respond(
                                self.ser, self.full_output_buffer
                            )
                            if pagination_response:
                                continue  # Continue reading without checking for expected text yet

                        # Check for the expected text
                        search_in = new_output if not check_existing_buffer else self.full_output_buffer
                        if actual_expected_text in search_in:
                            self.logger.log_debug(f"Found expected text: '{actual_expected_text}'")
                            
                            # For command prompts (>), use LAST occurrence to capture full output
                            # For other text, use first occurrence
                            if actual_expected_text == '>' or actual_expected_text == detected_prompt:
                                match_index = search_in.rfind(actual_expected_text)  # Use rfind for last occurrence
                            else:
                                match_index = search_in.find(actual_expected_text)   # Use find for first occurrence
                            
                            end_of_match = match_index + len(actual_expected_text)
                            
                            if check_existing_buffer:
                                # For login waits, return from full buffer
                                captured_output = self.full_output_buffer[:end_of_match]
                                self.full_output_buffer = self.full_output_buffer[end_of_match:]
                            else:
                                # For command waits, return only new output
                                captured_output = new_output[:end_of_match]
                                # Clear the consumed part from full buffer using rfind for prompts
                                if actual_expected_text == '>' or actual_expected_text == detected_prompt:
                                    consumed_from_full = self.full_output_buffer.rfind(actual_expected_text) + len(actual_expected_text)
                                else:
                                    consumed_from_full = self.full_output_buffer.find(actual_expected_text) + len(actual_expected_text)
                                if consumed_from_full > 0:
                                    self.full_output_buffer = self.full_output_buffer[consumed_from_full:]
                            
                            return True, captured_output
                    else:
                        consecutive_empty_reads += 1
                    
                    # Adaptive sleep timing for better performance with long outputs
                    if consecutive_empty_reads > 20:
                        # If no data for a while, sleep longer to reduce CPU usage
                        time.sleep(0.1)
                    elif self.ser.in_waiting > 0:
                        # If more data is available, don't sleep at all
                        continue
                    else:
                        # Normal case: short sleep to prevent busy waiting
                        time.sleep(0.01)  # Reduced from 0.1 to 0.01 for better responsiveness
                
                except serial.SerialException as e:
                    self.logger.log_error(f"Serial communication error: {e}")
                    return False, new_output
                except Exception as e:
                    self.logger.log_error(f"Unexpected error during data reading: {e}")
                    continue  # Try to continue reading
            
            # This block is reached only on timeout
            self.logger.log_warning(f"Timeout: Did not find '{actual_expected_text}' within {wait_timeout} seconds")
            captured_output = new_output if new_output else self.full_output_buffer
            self.full_output_buffer = ""  # Clear buffer on timeout to prevent cascading errors
            return False, captured_output
            
        except Exception as e:
            self.logger.log_error(f"Error in wait_for_output: {e}")
            return False, ""
    
    @staticmethod
    def select_com_port(logger: Logger) -> Optional[str]:
        """
        List available COM ports and prompt the user to select one.
        
        Args:
            logger: Logger instance for output
            
        Returns:
            Selected port string or None if cancelled/error
        """
        try:
            available_ports = serial.tools.list_ports.comports()
            if not available_ports:
                logger.log_error("No serial ports found. Please connect a device and try again.")
                return None

            if logger.verbose_mode:
                logger.log_section("Available COM Ports")
            else:
                print(f"\n{logger.colors.BOLD}Available COM Ports:{logger.colors.END}")
                
            for i, port in enumerate(available_ports):
                print(f"  {i + 1}: {port.device} - {port.description}")

            while True:
                try:
                    choice_str = input("\nPlease select a port (enter the number): ")
                    if not choice_str:
                        print("Please enter a valid number.")
                        continue
                    choice = int(choice_str)
                    if 1 <= choice <= len(available_ports):
                        selected_port = available_ports[choice - 1].device
                        logger.log_success(f"Selected port: {selected_port}")
                        return selected_port
                    else:
                        print(f"Please enter a number between 1 and {len(available_ports)}.")
                except ValueError:
                    print("Please enter a valid number.")
                except (KeyboardInterrupt, EOFError):
                    logger.log_info("Port selection cancelled by user.")
                    return None
        except Exception as e:
            logger.log_error(f"Error listing COM ports: {e}")
            return None
