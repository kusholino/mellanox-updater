import serial
import time
import configparser
import sys
import serial.tools.list_ports

def execute_playbook(port, baudrate, playbook_steps, timeout):
    """
    Opens a serial port and executes a playbook of commands and waits.

    Args:
        port (str): The COM port to connect to.
        baudrate (int): The baud rate for the connection.
        playbook_steps (list): A list of (type, value) tuples for the playbook.
        timeout (int): The timeout in seconds for each wait operation.

    Returns:
        bool: True if the playbook completed successfully, False otherwise.
    """
    ser = None
    try:
        print(f"\n--- Opening port {port} at {baudrate} baud... ---")
        ser = serial.Serial(port, baudrate, timeout=1)
        print("--- Port opened successfully. ---")
        
        full_output_buffer = ""

        print("\n--- Sending initialization sequence (Enter, Ctrl+C, Enter) to ensure a clean state. ---")
        ser.write(b'\n')
        time.sleep(0.2)
        ser.write(b'\x03') # Ctrl+C
        time.sleep(0.2)
        ser.write(b'\n')
        time.sleep(1)

        def wait_for_output(expected_text, wait_timeout):
            """
            Waits for specific text in the serial output. Returns immediately upon match.
            This version does NOT use silence detection for faster execution.
            Returns a tuple: (bool_success, str_captured_output).
            """
            nonlocal full_output_buffer
            
            # First, check if the text is already in the buffer from a previous read
            if expected_text in full_output_buffer:
                print(f"--- Found expected text: '{expected_text}' (pre-existing) ---")
                match_index = full_output_buffer.find(expected_text)
                end_of_match = match_index + len(expected_text)
                
                captured_output = full_output_buffer[:end_of_match]
                full_output_buffer = full_output_buffer[end_of_match:] # Consume the matched part
                return True, captured_output

            # If not found, start the read loop
            start_time = time.time()
            while time.time() - start_time < wait_timeout:
                if ser.in_waiting > 0:
                    incoming_bytes = ser.read(ser.in_waiting)
                    incoming_text = incoming_bytes.decode('utf-8', errors='ignore')
                    full_output_buffer += incoming_text
                
                    # Check again after reading new data
                    if expected_text in full_output_buffer:
                        print(f"--- Found expected text: '{expected_text}' ---")
                        match_index = full_output_buffer.find(expected_text)
                        end_of_match = match_index + len(expected_text)
                        
                        captured_output = full_output_buffer[:end_of_match]
                        full_output_buffer = full_output_buffer[end_of_match:] # Consume the matched part
                        return True, captured_output

                time.sleep(0.1) # Small delay to prevent a busy-wait loop

            # This block is reached only on timeout
            print(f"\n--- TIMEOUT: Did not find '{expected_text}' within {wait_timeout} seconds. ---")
            captured_output = full_output_buffer
            full_output_buffer = "" # Clear buffer on timeout to prevent cascading errors
            return False, captured_output

        # Read initial output for 2 seconds to populate the buffer with any login prompt.
        # This ensures the first WAIT can find a pre-existing prompt.
        print("\n--- Reading initial output for 2 seconds... ---")
        start_time = time.time()
        while time.time() - start_time < 2:
            if ser.in_waiting > 0:
                full_output_buffer += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            time.sleep(0.1)
        
        for step_type, value in playbook_steps:
            if step_type == 'command':
                print(f"\n>>> Sending command: '{value}'")
                ser.write(value.encode('utf-8') + b'\n')
            elif step_type == 'pause':
                print(f"\n--- Pausing for {value} seconds... ---")
                time.sleep(value)
            elif step_type == 'wait':
                print(f"\n<<< Waiting for: '{value}' (timeout: {timeout}s)")
                success, captured_output = wait_for_output(value, timeout)
                if captured_output.strip():
                    print("\n--- Command Output ---")
                    print(captured_output.strip())
                    print("----------------------")
                if not success:
                    print("\n!!! Playbook failed at wait step. Aborting.")
                    return False

        print("\n✅ Playbook finished all steps.")
        return True

    except serial.SerialException as e:
        print(f"\n❌ Serial error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        return False
    finally:
        if ser and ser.is_open:
            ser.close()
            print("\n--- Port closed. ---")

def parse_config_and_playbook(config_file):
    """
    Reads and validates the config file.
    Returns playbook steps, settings, and a custom success message.
    """
    try:
        config = configparser.ConfigParser()
        if not config.read(config_file):
            raise FileNotFoundError(f"Config file '{config_file}' not found or is empty.")

        serial_config = config['Serial']
        baud_rate = serial_config.getint('BaudRate')
        timeout = serial_config.getint('Timeout', fallback=10)
        # Read the configurable prompt symbol. Default to '>' if not found.
        prompt_symbol = serial_config.get('PromptSymbol', fallback='>')

        playbook_config = config['Playbook']
        playbook_script = playbook_config.get('script')
        if not playbook_script:
            raise ValueError("The 'script' key in the [Playbook] section cannot be empty.")
        
        playbook_steps = []
        success_message = None # To store the custom success message
        lines = [line.strip() for line in playbook_script.strip().split('\n')]
        
        for i, line in enumerate(lines, 1):
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(' ', 1)
            if len(parts) != 2:
                raise ValueError(f"Malformed playbook line #{i}: '{line}'. Expected 'ACTION value'.")
            
            action, value = parts[0].upper(), parts[1].strip()
            
            if action == 'SEND':
                playbook_steps.append(('command', value))
            elif action == 'PAUSE':
                playbook_steps.append(('pause', float(value)))
            elif action == 'WAIT':
                # If waiting for 'PROMPT', substitute the configured symbol
                if value.upper() == 'PROMPT':
                    playbook_steps.append(('wait', prompt_symbol))
                else:
                    playbook_steps.append(('wait', value))
            elif action == 'SUCCESS':
                success_message = value # Capture the success message
            else:
                raise ValueError(f"Unknown action '{action}' on playbook line #{i}.")

        return baud_rate, timeout, playbook_steps, success_message

    except (configparser.Error, KeyError, FileNotFoundError, ValueError) as e:
        print(f"❌ Error processing config file: {e}")
        return None, None, None, None

def select_com_port():
    """Lists available COM ports and prompts the user to select one."""
    available_ports = serial.tools.list_ports.comports()
    if not available_ports:
        print("❌ Error: No serial ports found. Please connect a device and try again.")
        return None

    print("\nAvailable COM Ports:")
    for i, port in enumerate(available_ports):
        print(f"  {i + 1}: {port.device} - {port.description}")

    while True:
        try:
            choice_str = input("\nPlease select a port (enter the number): ")
            if not choice_str: # Handle empty input from user pressing Enter
                continue
            choice = int(choice_str)
            if 1 <= choice <= len(available_ports):
                return available_ports[choice - 1].device
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except (KeyboardInterrupt, EOFError):
            print("\nSelection cancelled. Exiting.")
            return None


if __name__ == "__main__":
    config_file = 'config.ini'
    
    baud_rate, timeout, playbook_steps, success_message = parse_config_and_playbook(config_file)
    
    # Exit if the config file had errors.
    if baud_rate is None:
        sys.exit(1)

    # NEW: Exit if the playbook contains no valid steps.
    if not playbook_steps:
        print("❌ Error: No valid steps found in the [Playbook] script. Please check config.ini.")
        sys.exit(1)

    serial_port = select_com_port()
    if not serial_port:
        sys.exit(1)

    # The playbook execution no longer needs to know about the success message.
    success = execute_playbook(serial_port, baud_rate, playbook_steps, timeout)

    if success:
        # If a custom success message was defined, use it. Otherwise, use a default.
        if success_message:
            print(f"\n🎉 {success_message} 🎉")
        else:
            print("\n🎉 Playbook completed successfully! 🎉")
    else:
        print("\n🔥 Playbook execution failed. Please check the above logs for errors.")