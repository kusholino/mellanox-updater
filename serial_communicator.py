import serial
import time
import configparser
import sys
import os
import argparse
import serial.tools.list_ports
from tqdm import tqdm

# ANSI color codes for console output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Global variables for verbose mode and progress tracking
VERBOSE_MODE = False
PROGRESS_BAR = None

def log_info(message):
    """Print an informational message in blue."""
    if VERBOSE_MODE:
        print(f"{Colors.BLUE}[INFO]{Colors.END} {message}")

def log_success(message):
    """Print a success message in green."""
    if VERBOSE_MODE:
        print(f"{Colors.GREEN}[OK]{Colors.END} {message}")
    # In non-verbose mode, only show critical success messages
    elif "Serial port opened successfully" in message or "Playbook completed successfully" in message or "Configuration loaded successfully" in message:
        if PROGRESS_BAR:
            PROGRESS_BAR.write(f"{Colors.GREEN}[OK]{Colors.END} {message}")
        else:
            print(f"{Colors.GREEN}[OK]{Colors.END} {message}")

def log_warning(message):
    """Print a warning message in yellow."""
    if VERBOSE_MODE:
        print(f"{Colors.YELLOW}[WARN]{Colors.END} {message}")
    # In non-verbose mode, always show warnings as they might be important
    elif PROGRESS_BAR:
        PROGRESS_BAR.write(f"{Colors.YELLOW}[WARN]{Colors.END} {message}")
    else:
        print(f"{Colors.YELLOW}[WARN]{Colors.END} {message}")

def log_error(message):
    """Print an error message in red."""
    # Always show errors regardless of mode
    if VERBOSE_MODE:
        print(f"{Colors.RED}[ERROR]{Colors.END} {message}")
    elif PROGRESS_BAR:
        PROGRESS_BAR.write(f"{Colors.RED}[ERROR]{Colors.END} {message}")
    else:
        print(f"{Colors.RED}[ERROR]{Colors.END} {message}")

def log_debug(message):
    """Print a debug message in cyan."""
    if VERBOSE_MODE:
        print(f"{Colors.CYAN}[DEBUG]{Colors.END} {message}")

def log_section(message):
    """Print a section header."""
    if VERBOSE_MODE:
        print(f"\n{Colors.BOLD}{Colors.WHITE}[SECTION]{Colors.END} {message}")
        print("-" * (len(message) + 10))

def log_command_success(command, step_num):
    """Log successful command execution - shown in both modes."""
    if VERBOSE_MODE:
        print(f"{Colors.GREEN}[OK]{Colors.END} Step {step_num}: Command '{command}' completed successfully")
    elif PROGRESS_BAR:
        # Show abbreviated command info in non-verbose mode
        cmd_display = command[:30] + "..." if len(command) > 30 else command
        PROGRESS_BAR.write(f"{Colors.GREEN}[OK]{Colors.END} Step {step_num}: {cmd_display}")
    else:
        cmd_display = command[:30] + "..." if len(command) > 30 else command
        print(f"{Colors.GREEN}[OK]{Colors.END} Step {step_num}: {cmd_display}")

def update_progress(description=None):
    """Update progress bar with optional description."""
    global PROGRESS_BAR
    if PROGRESS_BAR and not VERBOSE_MODE:
        if description:
            PROGRESS_BAR.set_description(description)
        PROGRESS_BAR.update(1)

def execute_playbook(port, baudrate, playbook_steps, timeout, prompt_symbol='>', pagination_enabled=True, pagination_delay=0.1, custom_pagination_patterns=None, verbose=False):
    """
    Opens a serial port and executes a playbook of commands and waits.

    Args:
        port (str): The COM port to connect to.
        baudrate (int): The baud rate for the connection.
        playbook_steps (list): A list of (type, value) tuples for the playbook.
        timeout (int): The timeout in seconds for each wait operation.
        prompt_symbol (str): Fallback prompt symbol if auto-detection fails.
        pagination_enabled (bool): Whether to enable automatic pagination handling.
        pagination_delay (float): Delay after sending pagination responses.
        custom_pagination_patterns (list): Additional pagination patterns from config.
        verbose (bool): Whether to run in verbose mode.

    Returns:
        bool: True if the playbook completed successfully, False otherwise.
    """
    global VERBOSE_MODE, PROGRESS_BAR
    VERBOSE_MODE = verbose
    
    # Initialize progress bar if not in verbose mode
    if not verbose:
        total_steps = len([step for step in playbook_steps if step[0] in ['command', 'send', 'wait', 'pause']])
        PROGRESS_BAR = tqdm(total=total_steps + 3, desc="Connecting", unit="step", 
                           bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
    
    ser = None
    try:
        log_section("Serial Connection Setup")
        log_info(f"Opening port {port} at {baudrate} baud")
        update_progress("Opening serial port")
        
        try:
                # Check if port is already in use by another process
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
                    log_debug("Port availability check passed")
                except serial.SerialException as e:
                    if "access denied" in str(e).lower() or "permission denied" in str(e).lower():
                        log_error(f"Port {port} is already in use by another application or requires elevated permissions")
                        log_error("Please close other serial applications or run with appropriate permissions")
                        return False
                    elif "device busy" in str(e).lower() or "resource busy" in str(e).lower():
                        log_error(f"Port {port} is currently busy/locked by another process")
                        log_error("Please close other applications using this serial port")
                        return False
                    else:
                        # Other serial exceptions, continue with normal opening
                        log_debug(f"Port check exception (proceeding): {e}")
                except Exception as e:
                    # Non-serial exceptions, continue with normal opening
                    log_debug(f"Port check failed (proceeding): {e}")
                
                ser = serial.Serial(port, baudrate, timeout=1)
        except serial.SerialException as e:
            error_msg = str(e).lower()
            if "access denied" in error_msg or "permission denied" in error_msg:
                log_error(f"Failed to open serial port: Permission denied")
                log_error("Try running with sudo or check if another application is using the port")
            elif "device busy" in error_msg or "resource busy" in error_msg:
                log_error(f"Failed to open serial port: Port is busy")
                log_error("Another application may be using this serial port")
            elif "no such file" in error_msg or "cannot find" in error_msg:
                log_error(f"Failed to open serial port: Port not found")
                log_error("Please check if the device is connected and the port exists")
            else:
                log_error(f"Failed to open serial port: {e}")
            return False
        except Exception as e:
            log_error(f"Unexpected error opening port: {e}")
            return False
            
        log_success("Serial port opened successfully")
        
        full_output_buffer = ""
        
        # Initialize pagination settings and prompt detection (use config values)
        if custom_pagination_patterns is None:
            custom_pagination_patterns = []
        detected_prompt = None  # Will store auto-detected prompt

        log_section("Device Initialization")
        log_info("Sending initialization sequence (Enter, Ctrl+C, Enter)")
        update_progress("Initializing device")
        try:
            ser.write(b'\n')
            time.sleep(0.2)
            ser.write(b'\x03') # Ctrl+C
            time.sleep(0.2)
            ser.write(b'\n')
            time.sleep(1)
            log_success("Initialization sequence sent")
        except Exception as e:
            log_error(f"Failed to send initialization sequence: {e}")
            return False

        def auto_detect_prompt(buffer_text):
            """
            Automatically detect the command prompt from device output.
            Returns the detected prompt or None if not found.
            """
            try:
                import re
                
                if not buffer_text or not buffer_text.strip():
                    log_debug("Empty buffer provided for prompt detection")
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
                                log_success(f"Auto-detected prompt: '{detected}'")
                                return detected
                        except re.error as e:
                            log_warning(f"Regex error in prompt detection pattern '{pattern}': {e}")
                            continue
                
                log_debug("No prompt pattern matched in buffer text")
                return None
            except ImportError:
                log_error("Failed to import 're' module for prompt detection")
                return None
            except Exception as e:
                log_error(f"Error in prompt detection: {e}")
                return None

        def wait_for_output(expected_text, wait_timeout, check_existing_buffer=True, handle_pagination=True):
            """
            Waits for specific text in the serial output with pagination handling.
            
            Args:
                expected_text: Text to wait for (or 'PROMPT' for auto-detected prompt)
                wait_timeout: Timeout in seconds
                check_existing_buffer: If True, check pre-existing buffer first (for login prompts)
                                     If False, only check new incoming data (for command outputs)
                handle_pagination: If True, automatically respond to pagination prompts
            
            Returns a tuple: (bool_success, str_captured_output).
            """
            nonlocal full_output_buffer, pagination_enabled, pagination_delay, custom_pagination_patterns
            nonlocal detected_prompt, prompt_symbol
            
            try:
                # Handle dynamic prompt detection
                if expected_text.upper() == 'PROMPT':
                    if detected_prompt:
                        actual_expected_text = detected_prompt
                    else:
                        actual_expected_text = prompt_symbol
                else:
                    actual_expected_text = expected_text
                
                # Use global pagination settings
                handle_pagination = handle_pagination and pagination_enabled
                
                # Common pagination prompts to detect
                pagination_patterns = [
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
                
                # Add custom patterns from config
                pagination_patterns.extend(custom_pagination_patterns)
                
                # Compile regex patterns for efficiency
                try:
                    import re
                    pagination_regex = re.compile('|'.join(pagination_patterns), re.IGNORECASE | re.MULTILINE)
                except (ImportError, re.error) as e:
                    log_error(f"Error compiling pagination regex: {e}")
                    pagination_regex = None
                    handle_pagination = False
                
                # For login prompts and initial waits, check existing buffer first
                if check_existing_buffer and actual_expected_text in full_output_buffer:
                    log_debug(f"Found expected text: '{actual_expected_text}' (pre-existing)")
                    
                    # For command prompts (>), use LAST occurrence to capture full output
                    # For login prompts, use first occurrence
                    if actual_expected_text == '>' or actual_expected_text == detected_prompt:
                        match_index = full_output_buffer.rfind(actual_expected_text)  # Last occurrence for prompts
                    else:
                        match_index = full_output_buffer.find(actual_expected_text)   # First occurrence for login
                    
                    end_of_match = match_index + len(actual_expected_text)
                    
                    captured_output = full_output_buffer[:end_of_match]
                    full_output_buffer = full_output_buffer[end_of_match:] # Consume the matched part
                    return True, captured_output
                
                # Read new data from serial port
                start_time = time.time()
                new_output = ""
                last_data_time = start_time
                consecutive_empty_reads = 0
                
                while time.time() - start_time < wait_timeout:
                    try:
                        if ser.in_waiting > 0:
                            incoming_bytes = ser.read(ser.in_waiting)
                            incoming_text = incoming_bytes.decode('utf-8', errors='ignore')
                            new_output += incoming_text
                            full_output_buffer += incoming_text
                            last_data_time = time.time()
                            consecutive_empty_reads = 0
                            
                            # For long outputs, show progress
                            if len(new_output) > 1000 and len(new_output) % 2000 == 0:
                                lines = new_output.count('\n')
                                log_debug(f"Receiving data: {len(new_output)} chars, {lines} lines")
                        
                            # PAGINATION HANDLING: Check for pagination prompts and respond automatically
                            if handle_pagination and pagination_regex:
                                try:
                                    # Look for pagination prompts in the recent output (last 200 chars to be efficient)
                                    recent_output = full_output_buffer[-200:] if len(full_output_buffer) > 200 else full_output_buffer
                                    pagination_match = pagination_regex.search(recent_output)
                                    
                                    if pagination_match:
                                        pagination_prompt = pagination_match.group()
                                        log_debug(f"Pagination detected: '{pagination_prompt}'")
                                        
                                        # Determine the appropriate response based on the prompt
                                        if any(keyword in pagination_prompt.lower() for keyword in ['space', 'continue', '--more--', '--- more ---']):
                                            # Send space for "press space to continue" type prompts
                                            ser.write(b' ')
                                            log_debug("Sent: SPACE")
                                        elif 'any key' in pagination_prompt.lower():
                                            # Send enter for "press any key" prompts
                                            ser.write(b'\n')
                                            log_debug("Sent: ENTER")
                                        elif '[y/n]' in pagination_prompt.lower() or 'continue?' in pagination_prompt.lower():
                                            # Send 'y' for yes/no continue prompts
                                            ser.write(b'y\n')
                                            log_debug("Sent: y + ENTER")
                                        else:
                                            # Default: send space (most common for pagination)
                                            ser.write(b' ')
                                            log_debug("Sent: SPACE (default)")
                                        
                                        # Small delay after pagination response
                                        time.sleep(pagination_delay)
                                        continue  # Continue reading without checking for expected text yet
                                except (serial.SerialException, OSError) as e:
                                    log_error(f"Error sending pagination response: {e}")
                                    return False, new_output
                                except Exception as e:
                                    log_warning(f"Error in pagination handling: {e}")
                                    # Continue without pagination handling

                            # Check for the expected text
                            search_in = new_output if not check_existing_buffer else full_output_buffer
                            if actual_expected_text in search_in:
                                log_debug(f"Found expected text: '{actual_expected_text}'")
                                
                                # For command prompts (>), use LAST occurrence to capture full output
                                # For other text, use first occurrence
                                if actual_expected_text == '>' or actual_expected_text == detected_prompt:
                                    match_index = search_in.rfind(actual_expected_text)  # Use rfind for last occurrence
                                else:
                                    match_index = search_in.find(actual_expected_text)   # Use find for first occurrence
                                
                                end_of_match = match_index + len(actual_expected_text)
                                
                                if check_existing_buffer:
                                    # For login waits, return from full buffer
                                    captured_output = full_output_buffer[:end_of_match]
                                    full_output_buffer = full_output_buffer[end_of_match:]
                                else:
                                    # For command waits, return only new output
                                    captured_output = new_output[:end_of_match]
                                    # Clear the consumed part from full buffer using rfind for prompts
                                    if actual_expected_text == '>' or actual_expected_text == detected_prompt:
                                        consumed_from_full = full_output_buffer.rfind(actual_expected_text) + len(actual_expected_text)
                                    else:
                                        consumed_from_full = full_output_buffer.find(actual_expected_text) + len(actual_expected_text)
                                    if consumed_from_full > 0:
                                        full_output_buffer = full_output_buffer[consumed_from_full:]
                                
                                return True, captured_output
                        else:
                            consecutive_empty_reads += 1
                        
                        # Adaptive sleep timing for better performance with long outputs
                        if consecutive_empty_reads > 20:
                            # If no data for a while, sleep longer to reduce CPU usage
                            time.sleep(0.1)
                        elif ser.in_waiting > 0:
                            # If more data is available, don't sleep at all
                            continue
                        else:
                            # Normal case: short sleep to prevent busy waiting
                            time.sleep(0.01)  # Reduced from 0.1 to 0.01 for better responsiveness
                    
                    except serial.SerialException as e:
                        log_error(f"Serial communication error: {e}")
                        return False, new_output
                    except Exception as e:
                        log_error(f"Unexpected error during data reading: {e}")
                        continue  # Try to continue reading
                
                # This block is reached only on timeout
                log_warning(f"Timeout: Did not find '{actual_expected_text}' within {wait_timeout} seconds")
                captured_output = new_output if new_output else full_output_buffer
                full_output_buffer = "" # Clear buffer on timeout to prevent cascading errors
                return False, captured_output
                
            except Exception as e:
                log_error(f"Error in wait_for_output: {e}")
                return False, ""

        # Read initial output for 2 seconds to populate the buffer with any login prompt.
        log_section("Initial Device Communication")
        log_info("Reading initial output for 2 seconds")
        update_progress("Reading initial output")
        try:
            start_time = time.time()
            while time.time() - start_time < 2:
                if ser.in_waiting > 0:
                    full_output_buffer += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                time.sleep(0.1)
            log_success("Initial output reading completed")
        except Exception as e:
            log_error(f"Error reading initial output: {e}")
            return False
        
        # Try to auto-detect the command prompt from initial output
        detected_prompt = auto_detect_prompt(full_output_buffer)
        if detected_prompt:
            log_success(f"Command prompt detected: '{detected_prompt}'")
        else:
            log_warning(f"Could not auto-detect prompt, using fallback: '{prompt_symbol}'")
        
        # Keep track of the last command sent for better output filtering
        last_command_sent = None
        # Track if we're in login phase (before first command prompt)
        login_phase = True
        
        # Pre-login check: See if we're already logged in
        log_section("Pre-Login Check")
        log_info("Checking if already logged in to device")
        update_progress("Checking login status")
        
        def check_if_logged_in():
            """
            Check if we're already at a command prompt (logged in).
            Returns True if logged in, False if need to login.
            """
            nonlocal full_output_buffer
            try:
                # Send a harmless command that should work at any prompt level
                ser.write(b'\n')
                time.sleep(0.5)
                
                # Read any immediate response
                if ser.in_waiting > 0:
                    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    full_output_buffer += response
                    
                    # Check if response contains a command prompt
                    if detected_prompt and detected_prompt in response:
                        return True
                    elif prompt_symbol in response:
                        return True
                    elif any(prompt in response for prompt in ['#', '>', '$', '(config)']):
                        return True
                
                # Try sending a simple command to test
                ser.write(b'?\n')
                time.sleep(1)
                
                if ser.in_waiting > 0:
                    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    full_output_buffer += response
                    
                    # If we get help output or command response, we're logged in
                    if any(keyword in response.lower() for keyword in ['commands', 'help', 'available', 'syntax']):
                        return True
                    elif any(prompt in response for prompt in ['#', '>', '$']):
                        return True
                
                return False
                
            except Exception as e:
                log_debug(f"Login check failed: {e}")
                return False
        
        already_logged_in = check_if_logged_in()
        
        if already_logged_in:
            log_success("Device appears to be already logged in - skipping login steps")
            login_phase = False  # Skip login phase
            
            # Skip login-related steps in playbook with improved detection
            filtered_playbook_steps = []
            login_keywords = ['login:', 'username:', 'user:', 'password:', 'admin', 'enable']
            common_login_cmds = ['admin', 'enable', 'login', 'su']
            in_login_sequence = True  # Start assuming we're in login sequence
            
            for step_type, value in playbook_steps:
                # Check if this is a login-related step
                is_login_step = False
                
                if in_login_sequence:
                    if step_type == 'wait':
                        # Check for login-related wait patterns
                        wait_value_lower = value.lower().strip()
                        if any(keyword in wait_value_lower for keyword in login_keywords):
                            is_login_step = True
                        elif wait_value_lower in ['prompt', '>', '#', '$']:
                            is_login_step = True  # Prompt waits during login
                    elif step_type == 'send':
                        # Check for login-related send patterns
                        send_value_lower = value.lower().strip()
                        if any(keyword in send_value_lower for keyword in login_keywords):
                            is_login_step = True
                        elif send_value_lower in common_login_cmds:
                            is_login_step = True
                        elif len(value.strip()) < 20 and not any(cmd in value.lower() for cmd in ['show', 'config', 'display', 'get', 'set']):
                            # Short non-command strings (likely passwords/usernames)
                            is_login_step = True
                        
                        # If we see actual configuration commands, we're past login
                        if any(cmd in value.lower() for cmd in ['show', 'config', 'display', 'get', 'set']):
                            in_login_sequence = False
                    elif step_type == 'command':
                        # Any COMMAND type step means we're past login
                        in_login_sequence = False
                        is_login_step = False
                
                if is_login_step:
                    log_debug(f"Skipping login step: {step_type.upper()} {value}")
                else:
                    filtered_playbook_steps.append((step_type, value))
            
            playbook_steps = filtered_playbook_steps
            log_info(f"Filtered playbook to {len(playbook_steps)} steps (skipped login)")
        else:
            log_info("Device requires login - proceeding with full playbook")
        
        log_section("Executing Playbook")
        
        # Track last command output for conditional logic
        last_command_output = ""
        
        # Execute playbook with conditional support using step indices
        step_idx = 0
        while step_idx < len(playbook_steps):
            step_num = step_idx + 1
            step_type, value = playbook_steps[step_idx]
            
            try:
                # Handle conditional commands
                if step_type in ['if_contains', 'if_contains_i', 'if_not_contains', 'if_not_contains_i', 'if_regex']:
                    log_info(f"Step {step_num}: Evaluating condition {step_type.upper()} '{value}'")
                    
                    # Find matching ENDIF
                    endif_idx = None
                    depth = 1
                    for i in range(step_idx + 1, len(playbook_steps)):
                        if playbook_steps[i][0] in ['if_contains', 'if_contains_i', 'if_not_contains', 'if_not_contains_i', 'if_regex']:
                            depth += 1
                        elif playbook_steps[i][0] == 'endif':
                            depth -= 1
                            if depth == 0:
                                endif_idx = i
                                break
                    
                    if endif_idx is None:
                        log_error("Conditional block missing ENDIF")
                        return False
                    
                    # Evaluate condition
                    condition_met = False
                    log_debug(f"Evaluating condition against last output: '{last_command_output[:100]}...' (length: {len(last_command_output)})")
                    
                    if step_type == 'if_contains':
                        # Case-sensitive search by default
                        condition_met = value in last_command_output
                        log_debug(f"IF_CONTAINS '{value}' -> {condition_met}")
                    elif step_type == 'if_contains_i':
                        # Case-insensitive search
                        condition_met = value.lower() in last_command_output.lower()
                        log_debug(f"IF_CONTAINS_I '{value}' -> {condition_met}")
                    elif step_type == 'if_not_contains':
                        # Case-sensitive search by default
                        condition_met = value not in last_command_output
                        log_debug(f"IF_NOT_CONTAINS '{value}' -> {condition_met}")
                    elif step_type == 'if_not_contains_i':
                        # Case-insensitive search
                        condition_met = value.lower() not in last_command_output.lower()
                        log_debug(f"IF_NOT_CONTAINS_I '{value}' -> {condition_met}")
                    elif step_type == 'if_regex':
                        try:
                            import re
                            condition_met = bool(re.search(value, last_command_output, re.IGNORECASE))
                            log_debug(f"IF_REGEX '{value}' -> {condition_met}")
                        except re.error as e:
                            log_warning(f"Invalid regex pattern '{value}': {e}")
                            condition_met = False
                    
                    log_info(f"Condition result: {condition_met}")
                    
                    if condition_met:
                        # Condition is true - continue to next step (execute the IF block)
                        log_info("Condition met, executing IF block")
                        step_idx += 1
                    else:
                        # Condition false - skip to ENDIF without executing the block
                        log_info("Condition not met, skipping IF block")
                        step_idx = endif_idx + 1
                    
                    # Continue to next iteration
                    continue
                
                # Handle ELIF, ELSE, ENDIF when encountered during normal execution
                elif step_type in ['elif_contains', 'elif_contains_i', 'elif_not_contains', 'elif_not_contains_i', 'elif_regex', 'else', 'endif']:
                    if step_type == 'endif':
                        # Just move past this ENDIF - we're done with this conditional block
                        pass  # Let the main loop increment normally
                    else:
                        # This is ELIF or ELSE - we're already executing a TRUE condition, 
                        # so skip to the matching ENDIF
                        depth = 1
                        endif_idx = None
                        for i in range(step_idx + 1, len(playbook_steps)):
                            if playbook_steps[i][0] in ['if_contains', 'if_contains_i', 'if_not_contains', 'if_not_contains_i', 'if_regex']:
                                depth += 1
                            elif playbook_steps[i][0] == 'endif':
                                depth -= 1
                                if depth == 0:
                                    endif_idx = i
                                    break
                        
                        if endif_idx is not None:
                            step_idx = endif_idx - 1  # Set to endif_idx - 1 because main loop will increment
                        else:
                            log_error(f"No matching ENDIF found for {step_type.upper()} at step {step_num}")
                            return False
                
                # Handle regular commands
                elif step_type == 'command' or step_type == 'send':
                    log_info(f"Step {step_num}: Sending command '{value}'")
                    update_progress(f"Sending: {value[:20]}..." if len(value) > 20 else f"Sending: {value}")
                    last_command_sent = value
                    # We're past login phase once we start sending commands
                    login_phase = False
                    try:
                        ser.write(value.encode('utf-8') + b'\n')
                        # Give a small delay for the command to be processed
                        time.sleep(0.1)
                        log_success("Command sent successfully")
                    except Exception as e:
                        log_error(f"Failed to send command: {e}")
                        
                elif step_type == 'pause':
                    log_info(f"Step {step_num}: Pausing for {value} seconds")
                    update_progress(f"Pausing {value}s")
                    try:
                        time.sleep(value)
                        log_success("Pause completed")
                    except Exception as e:
                        log_error(f"Error during pause: {e}")
                        return False
                        
                elif step_type == 'wait':
                    # Resolve PROMPT to actual detected prompt for better logging
                    if value.upper() == 'PROMPT':
                        if detected_prompt:
                            display_prompt = detected_prompt
                            log_info(f"Step {step_num}: Waiting for auto-detected prompt '{display_prompt}' (timeout: {timeout}s)")
                            update_progress(f"Waiting for prompt")
                        else:
                            display_prompt = prompt_symbol
                            log_info(f"Step {step_num}: Waiting for fallback prompt '{display_prompt}' (timeout: {timeout}s)")
                            update_progress(f"Waiting for prompt")
                    else:
                        log_info(f"Step {step_num}: Waiting for '{value}' (timeout: {timeout}s)")
                        wait_desc = value[:15] + "..." if len(value) > 15 else value
                        update_progress(f"Waiting for: {wait_desc}")
                    
                    # For login phase, check existing buffer. For commands, use fresh data only
                    check_existing = login_phase or value in ['login:', 'Password:', 'password:']
                    # Enable pagination handling for command prompts, disable for login prompts
                    enable_pagination = not login_phase and (value == '>' or value.upper() == 'PROMPT')
                    success, captured_output = wait_for_output(value, timeout, check_existing, enable_pagination)
                    
                    if not success:
                        log_error("Playbook failed at wait step")
                        return False
                    
                    # Mark end of login phase when we see the command prompt
                    is_command_prompt = (value == '>' or value.upper() == 'PROMPT' or 
                                       (detected_prompt and value == detected_prompt))
                    if is_command_prompt and success:
                        login_phase = False
                        # Try to detect prompt again from the successful output for better accuracy
                        if not detected_prompt or value.upper() == 'PROMPT':
                            new_detection = auto_detect_prompt(captured_output)
                            if new_detection and new_detection != detected_prompt:
                                detected_prompt = new_detection
                                log_success(f"Updated detected prompt: '{detected_prompt}'")
                    
                    # For commands that were just executed, show completion status in non-verbose mode
                    if last_command_sent and not login_phase:
                        log_command_success(last_command_sent, step_num)
                    
                    # Process and display output if available (only in verbose mode)
                    if captured_output.strip() and VERBOSE_MODE:
                        log_section("Command Output")
                        # Clean up the output - remove the command echo and prompt
                        lines = captured_output.strip().split('\n')
                        output_lines = []
                        
                        # Pagination patterns to remove from output
                        pagination_cleanup_patterns = [
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
                            import re
                            cleanup_regex = re.compile('|'.join(pagination_cleanup_patterns), re.IGNORECASE)
                        except (ImportError, re.error) as e:
                            log_warning(f"Error compiling cleanup regex: {e}")
                            cleanup_regex = None
                        
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
                            is_final_prompt = (line.endswith(value) and i == len(lines) - 1)
                            if not is_final_prompt and detected_prompt:
                                # Also check if line ends with detected prompt
                                is_final_prompt = (detected_prompt in line and i == len(lines) - 1)
                            if is_final_prompt:
                                continue
                            
                            # Remove pagination artifacts
                            if cleanup_regex:
                                try:
                                    if cleanup_regex.search(line):
                                        log_debug(f"Cleaned pagination artifact: '{line[:50]}...'")
                                        continue
                                except Exception as e:
                                    log_warning(f"Error applying cleanup regex: {e}")
                                    # Continue without regex cleanup
                                
                            output_lines.append(line)
                        
                        if output_lines:
                            for line in output_lines:
                                print(f"  {line}")
                        else:
                            log_info("No output or command completed successfully")
                        print()  # Add spacing after output
                    # For commands that were just executed, show completion status in non-verbose mode
                    if last_command_sent and not login_phase:
                        log_command_success(last_command_sent, step_num)
                    
                    # Store command output for conditional logic
                    if captured_output.strip():
                        last_command_output = captured_output
                    else:
                        log_debug("No output captured to store for conditional logic")
                
                # Move to next step
                step_idx += 1
                        
            except Exception as e:
                log_error(f"Error in step {step_num}: {e}")
                return False

        log_success("Playbook finished all steps")
        if PROGRESS_BAR:
            PROGRESS_BAR.close()
        return True

    except serial.SerialException as e:
        log_error(f"Serial communication error: {e}")
        if PROGRESS_BAR:
            PROGRESS_BAR.close()
        return False
    except Exception as e:
        log_error(f"Unexpected error during playbook execution: {e}")
        if PROGRESS_BAR:
            PROGRESS_BAR.close()
        return False
    finally:
        if ser and ser.is_open:
            try:
                ser.close()
                log_info("Serial port closed")
                if PROGRESS_BAR and not PROGRESS_BAR.disable:
                    PROGRESS_BAR.write("Serial port closed")
            except Exception as e:
                log_error(f"Error closing serial port: {e}")

def parse_config_and_playbook(config_file, playbook_file_override=None):
    """
    Reads and validates the config file.
    Returns playbook steps, settings, pagination config, and a custom success message.
    
    Args:
        config_file (str): Path to the configuration file
        playbook_file_override (str, optional): Path to playbook file to use instead of config setting
    """
    try:
        log_info("Parsing configuration file")
        config = configparser.ConfigParser()
        if not config.read(config_file):
            raise FileNotFoundError(f"Config file '{config_file}' not found or is empty.")

        # Parse Serial configuration
        try:
            serial_config = config['Serial']
            baud_rate = serial_config.getint('BaudRate')
            timeout = serial_config.getint('Timeout', fallback=10)
            # Read the configurable prompt symbol. Default to '>' if not found.
            prompt_symbol = serial_config.get('PromptSymbol', fallback='>')
            log_debug(f"Serial config: BaudRate={baud_rate}, Timeout={timeout}, PromptSymbol='{prompt_symbol}'")
        except KeyError as e:
            raise ValueError(f"Missing required section or key in config: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid value in Serial configuration: {e}")

        # Read pagination settings from config
        pagination_enabled = True
        pagination_delay = 0.1
        custom_pagination_patterns = []
        
        try:
            if 'Pagination' in config:
                pagination_config = config['Pagination']
                pagination_enabled = pagination_config.getboolean('Enabled', fallback=True)
                pagination_delay = pagination_config.getfloat('ResponseDelay', fallback=0.1)
                
                # Read custom pagination patterns if any
                custom_patterns = pagination_config.get('CustomPatterns', fallback='')
                if custom_patterns.strip():
                    custom_pagination_patterns = [p.strip() for p in custom_patterns.split('\n') if p.strip()]
                
                log_debug(f"Pagination config: Enabled={pagination_enabled}, Delay={pagination_delay}, CustomPatterns={len(custom_pagination_patterns)}")
        except ValueError as e:
            log_warning(f"Invalid pagination configuration, using defaults: {e}")
            pagination_enabled = True
            pagination_delay = 0.1
            custom_pagination_patterns = []

        # Parse Playbook configuration from external file
        try:
            # Use override playbook file if provided, otherwise use config setting
            if playbook_file_override:
                playbook_file = playbook_file_override
                log_info(f"Using command-line specified playbook: {playbook_file}")
            else:
                playbook_config = config['Playbook']
                playbook_file = playbook_config.get('PlaybookFile', 'playbook.txt')
                log_debug(f"Using config-specified playbook: {playbook_file}")
            
            # Handle relative and absolute paths
            if not os.path.isabs(playbook_file):
                # If relative path, make it relative to the config file directory
                config_dir = os.path.dirname(os.path.abspath(config_file))
                playbook_file = os.path.join(config_dir, playbook_file)
            
            # Read the playbook file
            try:
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    playbook_script = f.read()
                log_debug(f"Loaded playbook from: {playbook_file}")
            except FileNotFoundError:
                raise ValueError(f"Playbook file not found: {playbook_file}")
            except Exception as e:
                raise ValueError(f"Error reading playbook file '{playbook_file}': {e}")
                
            if not playbook_script.strip():
                raise ValueError(f"The playbook file '{playbook_file}' is empty.")
                
        except KeyError:
            # Only raise this error if no override was provided
            if not playbook_file_override:
                raise ValueError("Missing required [Playbook] section in config file.")
            # If override was provided but config section is missing, that's okay
        
        playbook_steps = []
        success_message = None # To store the custom success message
        lines = playbook_script.strip().split('\n')
        
        for i, original_line in enumerate(lines, 1):
            try:
                # Strip leading and trailing whitespace to allow flexible formatting
                line = original_line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Remove any leading/trailing whitespace and normalize
                line = line.strip()
                
                parts = line.split(' ', 1)
                if len(parts) == 1:
                    # Handle commands without values (like empty SEND)
                    action = parts[0].upper()
                    value = ""
                elif len(parts) == 2:
                    action, value = parts[0].upper(), parts[1].strip()
                    # Remove surrounding quotes if present
                    if len(value) >= 2 and ((value.startswith('"') and value.endswith('"')) or 
                                          (value.startswith("'") and value.endswith("'"))):
                        value = value[1:-1]
                else:
                    raise ValueError(f"Malformed playbook line #{i}: '{line}'. Expected 'ACTION [value]'.")
                
                if action == 'SEND':
                    playbook_steps.append(('send', value))  # Use 'send' for SEND commands
                elif action == 'PAUSE':
                    try:
                        pause_time = float(value)
                        if pause_time < 0:
                            raise ValueError(f"Pause time cannot be negative: {pause_time}")
                        playbook_steps.append(('pause', pause_time))
                    except ValueError as e:
                        raise ValueError(f"Invalid pause value on line #{i}: {e}")
                elif action == 'WAIT':
                    # Keep 'PROMPT' as-is for runtime resolution, don't substitute here!
                    playbook_steps.append(('wait', value))
                elif action == 'IF_CONTAINS':
                    playbook_steps.append(('if_contains', value))
                elif action == 'IF_CONTAINS_I':  # Case-insensitive variant
                    playbook_steps.append(('if_contains_i', value))
                elif action == 'IF_NOT_CONTAINS':
                    playbook_steps.append(('if_not_contains', value))
                elif action == 'IF_NOT_CONTAINS_I':  # Case-insensitive variant
                    playbook_steps.append(('if_not_contains_i', value))
                elif action == 'IF_REGEX':
                    playbook_steps.append(('if_regex', value))
                elif action == 'ELIF_CONTAINS':
                    playbook_steps.append(('elif_contains', value))
                elif action == 'ELIF_CONTAINS_I':  # Case-insensitive variant
                    playbook_steps.append(('elif_contains_i', value))
                elif action == 'ELIF_NOT_CONTAINS':
                    playbook_steps.append(('elif_not_contains', value))
                elif action == 'ELIF_NOT_CONTAINS_I':  # Case-insensitive variant
                    playbook_steps.append(('elif_not_contains_i', value))
                elif action == 'ELIF_REGEX':
                    playbook_steps.append(('elif_regex', value))
                elif action == 'ELSE':
                    playbook_steps.append(('else', ''))
                elif action == 'ENDIF':
                    playbook_steps.append(('endif', ''))
                elif action == 'SUCCESS':
                    success_message = value # Capture the success message
                else:
                    raise ValueError(f"Unknown action '{action}' on playbook line #{i}.")
            except ValueError as e:
                log_error(f"Playbook parsing error: {e}")
                raise

        log_success(f"Parsed {len(playbook_steps)} playbook steps successfully")
        return baud_rate, timeout, playbook_steps, success_message, prompt_symbol, pagination_enabled, pagination_delay, custom_pagination_patterns

    except (configparser.Error, KeyError, FileNotFoundError, ValueError) as e:
        log_error(f"Error processing config file: {e}")
        return None, None, None, None, None, None, None, None
    except Exception as e:
        log_error(f"Unexpected error parsing config file: {e}")
        return None, None, None, None, None, None, None, None

def select_com_port():
    """Lists available COM ports and prompts the user to select one."""
    try:
        available_ports = serial.tools.list_ports.comports()
        if not available_ports:
            log_error("No serial ports found. Please connect a device and try again.")
            return None

        if VERBOSE_MODE:
            log_section("Available COM Ports")
        else:
            print(f"\n{Colors.BOLD}Available COM Ports:{Colors.END}")
            
        for i, port in enumerate(available_ports):
            print(f"  {i + 1}: {port.device} - {port.description}")

        while True:
            try:
                choice_str = input("\nPlease select a port (enter the number): ")
                if not choice_str: # Handle empty input from user pressing Enter
                    continue
                choice = int(choice_str)
                if 1 <= choice <= len(available_ports):
                    selected_port = available_ports[choice - 1].device
                    log_success(f"Selected port: {selected_port}")
                    return selected_port
                else:
                    log_warning("Invalid number. Please try again.")
            except ValueError:
                log_warning("Invalid input. Please enter a number.")
            except (KeyboardInterrupt, EOFError):
                log_info("Selection cancelled. Exiting.")
                return None
    except Exception as e:
        log_error(f"Error listing COM ports: {e}")
        return None


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Mellanox Device Updater - Automated serial communication tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 serial_communicator.py                           # Run with progress bar
  python3 serial_communicator.py --verbose                 # Run with detailed logging
  python3 serial_communicator.py -v                        # Short form for verbose
  python3 serial_communicator.py --playbook custom.txt     # Use custom playbook file
  python3 serial_communicator.py -p examples/example1.txt  # Use example playbook
        """
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose mode with detailed logging (default: show progress bar)'
    )
    
    parser.add_argument(
        '--config',
        default='config.ini',
        help='Path to configuration file (default: config.ini)'
    )
    
    parser.add_argument(
        '-p', '--playbook',
        help='Path to playbook file (overrides PlaybookFile setting in config)'
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        if args.verbose:
            log_section("Mellanox Device Updater - Verbose Mode")
            log_info(f"Loading configuration from {args.config}")
            if args.playbook:
                log_info(f"Using custom playbook: {args.playbook}")
        else:
            print(f"{Colors.BOLD}{Colors.WHITE}Mellanox Device Updater{Colors.END}")
            if args.playbook:
                print(f"Using custom playbook: {args.playbook}")
        
        result = parse_config_and_playbook(args.config, args.playbook)
        baud_rate, timeout, playbook_steps, success_message, prompt_symbol, pagination_enabled, pagination_delay, custom_pagination_patterns = result
        
        # Exit if the config file had errors.
        if baud_rate is None:
            log_error("Configuration loading failed. Exiting.")
            sys.exit(1)

        # Exit if the playbook contains no valid steps.
        if not playbook_steps:
            log_error("No valid steps found in the [Playbook] script. Please check config.ini.")
            sys.exit(1)
        
        log_success(f"Configuration loaded successfully: {len(playbook_steps)} steps found")

        serial_port = select_com_port()
        if not serial_port:
            log_error("No serial port selected. Exiting.")
            sys.exit(1)

        # The playbook execution now uses all config settings including verbose mode
        success = execute_playbook(
            serial_port, baud_rate, playbook_steps, timeout, prompt_symbol, 
            pagination_enabled, pagination_delay, custom_pagination_patterns, 
            verbose=args.verbose
        )

        if success:
            # If a custom success message was defined, use it. Otherwise, use a default.
            if success_message:
                log_success(success_message)
            else:
                log_success("Playbook completed successfully!")
        else:
            log_error("Playbook execution failed. Please check the above logs for errors.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        log_info("Program interrupted by user. Exiting.")
        if PROGRESS_BAR:
            PROGRESS_BAR.close()
        sys.exit(0)
    except Exception as e:
        log_error(f"Unexpected error in main: {e}")
        if PROGRESS_BAR:
            PROGRESS_BAR.close()
        sys.exit(1)