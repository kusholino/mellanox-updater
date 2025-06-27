# SerialLink

A practical tool for automating serial communication with network devices, switches, and servers. Instead of manually typing commands into a terminal session, you write a simple playbook that defines what commands to run and SerialLink handles the rest.

Perfect for network administrators, system engineers, and anyone who needs to run the same commands on multiple devices repeatedly.

## What It Does

SerialLink connects to devices via serial port and automatically:
- Logs into devices using your credentials
- Runs your commands in sequence
- Waits for responses and handles prompts
- Makes decisions based on device output
- Reports progress and results

Think of it as scripting for serial console sessions.

## Features

### Core Automation
- **Serial Port Management**: Automatically detects available serial ports and manages connections
- **Smart Prompt Detection**: Recognizes common device prompts (>, #, hostname>, user@host#)
- **Automatic Pagination Handling**: Responds to "More" prompts and paged output automatically
- **Command Sequencing**: Executes commands in precise order with configurable timing
- **Login State Detection**: Checks if already logged in and skips unnecessary login steps

### Conditional Logic
- **IF_CONTAINS/IF_NOT_CONTAINS**: Make decisions based on command output
- **Case-Sensitive and Case-Insensitive**: Both `IF_CONTAINS` and `IF_CONTAINS_I` variants
- **Regular Expression Support**: `IF_REGEX` and `IF_NOT_REGEX` for pattern matching
- **ELIF and ELSE**: Complete conditional logic with multiple branches
- **Nested Conditionals**: Support for complex, multi-level conditional blocks

### Playbook Commands
- **SEND**: Send a command to the device
- **WAIT**: Wait for specific text in the output
- **PAUSE**: Wait for a specific number of seconds
- **IF_CONTAINS**: Execute commands only if output contains text
- **IF_NOT_CONTAINS**: Execute commands only if output doesn't contain text
- **SUCCESS**: Set a custom completion message
- **Comments**: Lines starting with # are ignored

### Device Support
- **Multi-Vendor Compatibility**: Works with any device that uses serial console
- **Flexible Serial Settings**: Configurable baud rates, timeouts, and connection parameters
- **Cross-Platform**: Runs on Linux, macOS, and Windows
- **Smart Initialization**: Handles device connection and initial output processing

### User Experience
- **Zero-Configuration Setup**: Single command setup with automatic environment creation
- **Smart Installation**: Only installs missing components, preserves existing setup
- **Comprehensive Validation**: Built-in testing and verification of all components
- **Rich Progress Feedback**: Real-time status updates with colored output
- **Verbose Mode**: Detailed logging for troubleshooting and development

### Configuration Management
- **Template System**: Pre-configured templates for common scenarios
- **Command-Line Overrides**: Override any configuration setting from command line
- **Multiple Profiles**: Different configurations for different environments
- **Environment Detection**: Automatically handles different Python environments

### Output Processing
- **Intelligent Buffering**: Handles large command outputs efficiently
- **Automatic Cleanup**: Strips pagination prompts and control characters
- **Real-time Display**: Live output streaming with proper formatting
- **Output Capture**: Full output available for conditional logic evaluation

## Quick Start

Get up and running in under 2 minutes:

```bash
# Get SerialLink ready (handles everything automatically)
./setup.sh

# Verify everything works
./setup.sh validate

# Start using it immediately
./seriallink --help
```

That's it. No manual configuration, no complex setup steps, no environment tweaking.

## Basic Usage

### 1. Connect Your Device
Plug in your serial cable and find the port:
```bash
# On Linux, usually /dev/ttyUSB0 or /dev/ttyS0
# On macOS, usually /dev/cu.usbserial*
ls /dev/tty*
```

### 2. Set Your Connection Details
Edit `config.ini` with your device info:
```ini
[serial]
port = /dev/ttyUSB0
baudrate = 115200
timeout = 10

[playbook]
file = playbook.txt

[timing]
command_delay = 1.0
response_timeout = 30
```

### 3. Create a Playbook
Write your commands in `playbook.txt`:
```
# Login to device
WAIT login:
SEND admin
WAIT Password:
SEND your_password
WAIT PROMPT

# Run commands
SEND show version
WAIT PROMPT
SUCCESS Done!
```

### 4. Run It
```bash
./seriallink --verbose
```

Watch as SerialLink connects to your device and runs all commands automatically.

## Real-World Examples

### Router Configuration Backup
```
# Login sequence
WAIT login:
SEND admin
WAIT Password:
SEND admin_password
WAIT PROMPT

# Get configuration
SEND show running-config
PAUSE 5
WAIT PROMPT
SEND show startup-config
PAUSE 5
WAIT PROMPT
SUCCESS Backup completed
```

### Conditional Logic Based on Device Type
```
# Login first
WAIT login:
SEND admin
WAIT Password:
SEND admin_password
WAIT PROMPT

# Check device type
SEND show version
WAIT PROMPT

# Run device-specific commands
IF_CONTAINS "Cisco"
    SEND show ip interface brief
    WAIT PROMPT
ENDIF

IF_CONTAINS "Juniper"
    SEND show interfaces terse
    WAIT PROMPT
ENDIF

SUCCESS Device check completed
```

### Server Health Check
```
# Login to server
WAIT login:
SEND root
WAIT Password:
SEND root_password
WAIT PROMPT

# Check system health
SEND uptime
WAIT PROMPT
SEND df -h
WAIT PROMPT
SEND free -h
WAIT PROMPT
SUCCESS Health check done
```

## Command Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `WAIT <text>` | Wait for specific text | `WAIT login:` |
| `SEND <command>` | Send command | `SEND show version` |
| `PAUSE <seconds>` | Wait for time | `PAUSE 5` |
| `IF_CONTAINS "<text>"` | Conditional execution | `IF_CONTAINS "Cisco"` |
| `IF_NOT_CONTAINS "<text>"` | Negative condition | `IF_NOT_CONTAINS "Error"` |
| `IF_CONTAINS_I "<text>"` | Case-insensitive condition | `IF_CONTAINS_I "cisco"` |
| `IF_REGEX "<pattern>"` | Regex pattern matching | `IF_REGEX "Version [0-9]+"` |
| `ELIF_CONTAINS "<text>"` | Else-if condition | `ELIF_CONTAINS "Juniper"` |
| `ELSE` | Default condition | `ELSE` |
| `ENDIF` | End conditional block | `ENDIF` |
| `SUCCESS <message>` | Mark completion | `SUCCESS All done!` |
| `# comment` | Add comments | `# This is a comment` |

## Configuration Options

Edit `config.ini` to customize behavior:

```ini
[serial]
port = /dev/ttyUSB0          # Your serial port
baudrate = 115200            # Communication speed
timeout = 10                 # Connection timeout

[playbook]
file = playbook.txt          # Which playbook to run

[timing]
command_delay = 1.0          # Wait between commands
response_timeout = 30        # How long to wait for responses

[logging]
level = INFO                 # Logging level (DEBUG, INFO, WARNING, ERROR)
```

## Command Line Options

```bash
# Basic usage
./seriallink

# With verbose output
./seriallink --verbose

# Override settings
./seriallink --baudrate 9600 --username admin --password secret

# Use different config file
./seriallink --config my_device.ini

# Use different playbook
./seriallink --playbook backup_commands.txt

# Override prompt symbol
./seriallink --prompt-symbol "#"

# Disable features
./seriallink --no-color --no-pagination
```

## Troubleshooting

### Connection Issues

**Permission denied on serial port:**
```bash
sudo usermod -a -G dialout $USER
# Then log out and back in
```

**Can't find serial port:**
```bash
# List available ports
ls /dev/tty*
# On Linux, try /dev/ttyUSB0, /dev/ttyS0
# On macOS, try /dev/cu.usbserial*
```

**Device not responding:**
- Check cable connections
- Verify baudrate matches device settings
- Try different timeout values
- Use `--verbose` to see detailed communication

### Playbook Issues

**Commands not working:**
- Check for typos in WAIT statements
- Make sure your device prompt is properly detected
- Add PAUSE commands if device is slow to respond
- Use `--verbose` to see detailed communication
- Check that expected text exactly matches device output

**Conditional logic not working:**
- Text matching is case-sensitive (use `IF_CONTAINS_I` for case-insensitive)
- Use exact text from device output
- Check for extra spaces or characters
- Try `IF_REGEX` for complex pattern matching

### Setup Problems

**Python version issues:**
```bash
# Setup script will find compatible Python automatically
./setup.sh --python python3.11
```

**Dependencies not installing:**
```bash
# Clean and retry
./setup.sh clean
./setup.sh --force
```

**Environment broken:**
```bash
# Reset everything
./setup.sh clean
./setup.sh
```

## Error Codes

If setup fails, you'll get a specific error code:

| Code | Issue | Solution |
|------|-------|----------|
| 1 | Python not found | Install Python 3.8+ |
| 2 | Python too old | Upgrade to Python 3.8+ |
| 3 | venv module missing | Install python3-venv package |
| 4 | Can't create environment | Check disk space and permissions |
| 5 | Dependencies failed | Check internet connection |

## Advanced Features

### Multiple Devices
Create separate config files for each device:
```bash
./seriallink --config router1.ini
./seriallink --config switch1.ini
./seriallink --config server1.ini
```

### Complex Conditionals
Chain multiple conditions with ELIF and ELSE:
```
SEND show version
WAIT PROMPT

IF_CONTAINS "Version 15.2"
    SEND show license
    WAIT PROMPT
ELIF_CONTAINS "Version 16.0"
    SEND show platform
    WAIT PROMPT
ELSE
    SEND show inventory
    WAIT PROMPT
ENDIF
```

### Case-Insensitive Matching
```
SEND show version
WAIT PROMPT

IF_CONTAINS_I "cisco"
    # Matches "Cisco", "CISCO", "cisco", etc.
    SEND show ip route
    WAIT PROMPT
ENDIF
```

### Regular Expression Matching
```
SEND show version
WAIT PROMPT

IF_REGEX "Version [0-9]+\.[0-9]+"
    SEND show running-config
    WAIT PROMPT
ENDIF
```

### Output Processing
Save command output by using verbose mode and redirecting output:
```bash
./seriallink --verbose > device_output.log 2>&1
```

## Getting Help

### Check Setup
```bash
# Validate your installation
./setup.sh validate

# See all available options
./seriallink --help
```

### Debug Issues
```bash
# See detailed communication
./seriallink --verbose

# Test connection manually
./seriallink --verbose --playbook simple_test.txt
```

### Example Playbooks
Check the `examples/` directory for ready-to-use playbooks:
- Basic device login
- Router configuration backup
- Switch port configuration  
- Server health checks
- Firewall rule management

## Tips for Success

1. **Start Simple**: Begin with basic login and one command
2. **Use Verbose Mode**: Always use `--verbose` when testing new playbooks
3. **Check Your Output**: Device output must exactly match your WAIT conditions
4. **Add Delays**: Some devices need time between commands - use PAUSE
5. **Test Incrementally**: Add commands one at a time to playbooks
6. **Use Comments**: Document your playbooks with # comments
7. **Check Conditionals**: Use exact text matching or try case-insensitive variants

SerialLink makes serial device automation straightforward. No complex scripting languages, no intricate setup procedures - just simple commands that work.