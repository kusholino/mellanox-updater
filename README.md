# Mellanox Device Updater

A Python tool for automating serial communication with Mellanox switches and network devices using configurable playbooks.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Line Options](#command-line-options)
- [Configuration](#configuration)
- [Playbook Format](#playbook-format)
- [Conditional Logic](#conditional-logic)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Overview

This tool automates device configuration tasks that typically require manual intervention. Instead of manually typing commands into a terminal session, you create a playbook (text file) that defines the sequence of commands to execute.

The tool provides:
- Automated serial port detection and communication
- Progress tracking with meaningful descriptions
- Conditional command execution based on device responses
- Automatic pagination handling
- Comprehensive error handling and logging

## Installation

### Requirements
- Python 3.8 or higher
- Serial port access permissions

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy configuration template
cp config.ini.template config.ini

# Edit configuration as needed
nano config.ini
```

## Quick Start

1. **Basic execution with default settings:**
   ```bash
   python main.py
   ```

2. **Specify credentials:**
   ```bash
   python main.py -u admin --password your_password
   ```

3. **Use verbose logging:**
   ```bash
   python main.py --verbose
   ```

4. **Specify serial port and baudrate:**
   ```bash
   python main.py -p /dev/ttyUSB0 -b 115200
   ```

## Command Line Options

```
Usage: python main.py [options]

Serial Communication:
  -p, --port PORT          Serial port (e.g., COM3, /dev/ttyUSB0)
  -b, --baudrate RATE      Baud rate (default: 115200)

Configuration:
  -c, --config FILE        Configuration file (default: config.ini)
  --playbook FILE          Playbook file (overrides config setting)

Authentication:
  -u, --username USER      Username for device login
  --password PASS          Password for device login

Output Control:
  -v, --verbose            Enable verbose logging
  --no-color               Disable colored output
  --no-pagination          Disable automatic pagination handling
  --prompt-symbol SYMBOL   Override prompt symbol (default: >)

Help:
  -h, --help               Show help message
```

## Configuration

### config.ini Structure

```ini
[Serial]
port = /dev/ttyUSB0
baudrate = 115200
timeout = 30

[Playbook]
file = playbook.txt

[Logging]
verbose = false
```

### Configuration Priority

Settings are applied in this order (highest to lowest priority):
1. Command line arguments
2. Configuration file
3. Built-in defaults

## Playbook Format

Playbooks use simple command syntax:

### Basic Commands

```plaintext
# Send command to device
SEND show version

# Wait for specific text
WAIT login:

# Wait for command prompt
WAIT PROMPT

# Pause execution
PAUSE 5
```

### Login Sequence Example

```plaintext
WAIT login:
SEND admin
WAIT Password:
SEND your_password
WAIT PROMPT
```

### Command Execution Example

```plaintext
SEND show system
WAIT PROMPT
SEND show interfaces
WAIT PROMPT
```

## Conditional Logic

Execute commands based on device responses:

### Basic Conditionals

```plaintext
SEND show version
WAIT PROMPT
IF_CONTAINS: Version 2.1
  SEND show license
  WAIT PROMPT
ENDIF
```

### Multiple Conditions

```plaintext
SEND show system
WAIT PROMPT
IF_CONTAINS: Temperature: OK
  SEND show interfaces
  WAIT PROMPT
ELIF_CONTAINS: Temperature: WARNING
  SEND show thermal-status
  WAIT PROMPT
ELSE
  SEND show critical-alerts
  WAIT PROMPT
ENDIF
```

### Supported Conditional Types

- `IF_CONTAINS: text` - Execute if output contains text
- `IF_NOT_CONTAINS: text` - Execute if output doesn't contain text
- `ELIF_CONTAINS: text` - Else-if contains text
- `ELSE` - Execute if no conditions met
- `ENDIF` - End conditional block

## Examples

### Firmware Update Check

```plaintext
# Check current firmware version
SEND show version
WAIT PROMPT

# Update if old version detected
IF_CONTAINS: firmware-1.0
  SEND copy tftp://192.168.1.100/firmware-2.0 flash:
  WAIT PROMPT
  SEND reload
  WAIT PROMPT
ENDIF
```

### Configuration Backup

```plaintext
# Login sequence
WAIT login:
SEND admin
WAIT Password:
SEND backup123
WAIT PROMPT

# Backup configuration
SEND show configuration
WAIT PROMPT
SEND copy running-config tftp://192.168.1.100/backup.conf
WAIT PROMPT
```

### Health Check

```plaintext
SEND show system-health
WAIT PROMPT

IF_CONTAINS: Status: OK
  SEND show brief-status
  WAIT PROMPT
ELSE
  SEND show detailed-diagnostics
  WAIT PROMPT
  SEND show error-logs
  WAIT PROMPT
ENDIF
```

## Troubleshooting

### Common Issues

**Serial Port Access Denied**
```bash
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
# Then logout and login again

# Check port permissions
ls -l /dev/ttyUSB0
```

**Device Not Responding**
- Verify cable connections
- Check baudrate settings
- Ensure device is powered on
- Try different serial port

**Commands Not Executing**
- Enable verbose mode: `python main.py --verbose`
- Check playbook syntax
- Verify conditional logic
- Ensure proper line endings in playbook file

**Progress Bar Stuck**
- Check for pagination prompts in device output
- Use `--no-pagination` if automatic handling fails
- Verify timeout settings in config.ini

### Debug Mode

Enable verbose logging for detailed information:

```bash
python main.py --verbose
```

This shows:
- Each command sent to device
- Device responses
- Progress tracking details
- Conditional logic evaluation
- Error messages with context

### Log Analysis

The tool provides detailed error messages:
- Line numbers for playbook syntax errors
- Specific timeout information
- Serial communication status
- Conditional evaluation results

## Advanced Usage

### Custom Prompt Detection

Override automatic prompt detection:

```bash
python main.py --prompt-symbol "#"
```

### Pagination Handling

Disable automatic pagination if needed:

```bash
python main.py --no-pagination
```

### Multiple Device Types

Use different playbooks for different devices:

```bash
python main.py --playbook cisco_commands.txt
python main.py --playbook juniper_commands.txt
```

### Batch Operations

Create device-specific configuration files:

```bash
# Device 1
python main.py -c device1_config.ini

# Device 2  
python main.py -c device2_config.ini
```

### Integration Scripts

Embed in shell scripts for automation:

```bash
#!/bin/bash
echo "Starting device configuration..."
python main.py -u admin --password $DEVICE_PASSWORD
if [ $? -eq 0 ]; then
    echo "Configuration successful"
else
    echo "Configuration failed"
    exit 1
fi
```

---

For additional help or bug reports, refer to the project documentation or contact the development team.

# 2. Run with interactive port selection
python main.py

# 3. Enter your credentials when prompted
# Username: admin
# Password: [your password]

# 4. Watch the magic happen!
```

That's it! The tool will:
- Auto-detect your serial ports
- Let you choose the correct one
- Execute the default playbook
- Show progress with friendly descriptions

---

## 🔧 Installation

### **System Requirements**
- Python 3.7 or higher
- Serial port access (USB-to-Serial adapter or built-in serial port)
- Operating System: Windows, macOS, or Linux

### **Step 1: Get the Code**
```bash
git clone <repository-url>
cd mellanox-updater
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

The tool only requires two dependencies:
- `pyserial==3.5` - For serial communication
- `tqdm>=4.64.0` - For beautiful progress bars

### **Step 3: Set Up Configuration (Optional)**
```bash
cp config.ini.template config.ini
```

Edit `config.ini` to set default values:
```ini
[Serial]
Port = COM3                    # Your serial port (auto-detected if not found)
BaudRate = 115200             # Communication speed
Timeout = 60                  # Seconds to wait for responses
PromptSymbol = >              # Your device's command prompt symbol

[Playbook]
PlaybookFile = playbook.txt   # Path to your command sequence file
```

---

## 📱 Running the Tool

### **Basic Usage**
```bash
# Run with default settings
python main.py

# Run with specific username
python main.py -u admin

# Run with username and password (not recommended for security)
python main.py -u admin --password mypassword

# Run in verbose mode (shows detailed logs)
python main.py --verbose

# Use custom configuration file
python main.py -c my_config.ini
```

### **All Command Line Options**
```bash
Options:
  -h, --help                    Show detailed help message
  -b, --baudrate RATE          Serial baud rate (default: 115200)
  -c, --config FILE            Configuration file path (default: config.ini)
  -p, --playbook FILE          Playbook file path (overrides config setting)
  -v, --verbose                Enable detailed logging and debug output
  -u, --username USER          Device username (prompted if not provided)
  --password PASS              Device password (prompted if not provided - SAFER)
  --no-color                   Disable colored output (useful for scripts)
  --no-pagination              Disable automatic page handling
  --prompt-symbol SYMBOL       Override command prompt detection
  --legacy-mode                Use older compatibility mode
```

### **Interactive vs Non-Interactive Usage**

**Interactive (Recommended for Manual Use):**
```bash
python main.py -v
# Tool will prompt for:
# - Serial port selection (if multiple found)
# - Username (if not in config)
# - Password (if not in config)
```

**Non-Interactive (For Scripts/Automation):**
```bash
python main.py -u admin --password secret --no-color
# All parameters provided, no prompts
```

---

## ⚙️ Configuration

### **Understanding config.ini**

The configuration file controls default behavior. Here's what each setting does:

```ini
[Serial]
# Serial port - can be:
# Windows: COM1, COM2, COM3, etc.
# Linux: /dev/ttyUSB0, /dev/ttyS0, etc.  
# macOS: /dev/tty.usbserial-*, etc.
Port = COM3

# Communication speed - common values:
# 9600, 19200, 38400, 57600, 115200, 230400
BaudRate = 115200

# How long to wait for device responses (seconds)
# Increase for slow devices, decrease for faster execution
Timeout = 60

# Character(s) that indicate command prompt is ready
# Common values: >, #, $, %, switch>
PromptSymbol = >

[Playbook]  
# Path to file containing command sequence
# Can be relative path or absolute path
PlaybookFile = playbook.txt
```

### **Configuration Priority Order**
1. **Command line arguments** (highest priority)
2. **config.ini file settings**
3. **Built-in defaults** (lowest priority)

Example:
```bash
# This overrides config.ini BaudRate setting
python main.py -b 9600

# This overrides config.ini PlaybookFile setting  
python main.py -p custom_commands.txt
```

---

## 📝 Creating Playbooks

Playbooks are simple text files that define the sequence of commands to execute. Think of them as "scripts" for device interaction.

### **Basic Playbook Structure**

```plaintext
# Comments start with # and are ignored
# Blank lines are ignored

# Step 1: Wait for login prompt and send username
WAIT login:
SEND admin

# Step 2: Wait for password prompt and send password  
WAIT Password:
SEND mypassword

# Step 3: Wait for command prompt
WAIT PROMPT

# Step 4: Execute a command and wait for prompt
SEND show version
WAIT PROMPT

# Step 5: Show success message
SUCCESS Configuration complete!
```

### **All Playbook Commands**

| Command | Purpose | Example | Notes |
|---------|---------|---------|-------|
| `SEND` | Send text to device | `SEND show version` | Automatically adds newline |
| `WAIT` | Wait for specific text | `WAIT login:` | Case-sensitive match |
| `WAIT PROMPT` | Wait for command prompt | `WAIT PROMPT` | Uses PromptSymbol from config |
| `PAUSE` | Wait for X seconds | `PAUSE 10` | Useful for slow operations |
| `SUCCESS` | Show success message | `SUCCESS Done!` | Optional, shown in green |
| `#` | Comment line | `# This is a comment` | Ignored during execution |

### **Real-World Playbook Examples**

**Example 1: Simple Version Check**
```plaintext
# Login sequence
WAIT login:
SEND admin
WAIT Password:
SEND mypassword
WAIT PROMPT

# Get device information
SEND show version
WAIT PROMPT
SEND show system-info
WAIT PROMPT

SUCCESS Version check complete!
```

**Example 2: Configuration Backup**
```plaintext
# Login
WAIT login:
SEND admin  
WAIT Password:
SEND mypassword
WAIT PROMPT

# Create backup
SEND configuration write
WAIT PROMPT
PAUSE 5
SEND show running-config
WAIT PROMPT

SUCCESS Backup complete!
```

**Example 3: Multiple Device Commands**
```plaintext
# Login
WAIT login:
SEND admin
WAIT Password:
SEND mypassword  
WAIT PROMPT

# Check interface status
SEND show interfaces brief
WAIT PROMPT

# Check routing table
SEND show ip route
WAIT PROMPT

# Check system status
SEND show system status
WAIT PROMPT

SUCCESS System check complete!
```

---

## 🔄 Conditional Logic

Conditional logic allows your playbooks to make decisions based on device responses. This is powerful for handling different device types, versions, or configurations.

### **Basic Conditional Structure**

```plaintext
SEND show version
WAIT PROMPT

IF_CONTAINS "Version 3.8"
    # Commands to run if version is 3.8
    SEND enable advanced-features
    WAIT PROMPT
ENDIF
```

### **All Conditional Commands**

| Command | Purpose | Example |
|---------|---------|---------|
| `IF_CONTAINS "text"` | Check if output contains text | `IF_CONTAINS "Version 3.8"` |
| `IF_NOT_CONTAINS "text"` | Check if output does NOT contain text | `IF_NOT_CONTAINS "Error"` |
| `IF "text"` | Alias for IF_CONTAINS | `IF "Ready"` |
| `ELIF_CONTAINS "text"` | Else-if with contains check | `ELIF_CONTAINS "Version 3.7"` |
| `ELIF_NOT_CONTAINS "text"` | Else-if with not-contains check | `ELIF_NOT_CONTAINS "Warning"` |
| `ELSE` | Default case if no conditions match | `ELSE` |
| `ENDIF` | End of conditional block | `ENDIF` |

### **Advanced Conditional Examples**

**Example 1: Version-Specific Commands**
```plaintext
SEND show version
WAIT PROMPT

IF_CONTAINS "Version 3.8"
    SEND license install advanced
    WAIT PROMPT
    SEND enable feature-set advanced  
    WAIT PROMPT
ELIF_CONTAINS "Version 3.7"
    SEND license install basic
    WAIT PROMPT
    SEND enable feature-set basic
    WAIT PROMPT
ELSE
    SEND show help
    WAIT PROMPT
    SUCCESS Unsupported version detected
ENDIF

SUCCESS Version-specific configuration complete!
```

**Example 2: Error Handling**
```plaintext
SEND configure
WAIT PROMPT

SEND interface ethernet 1/1
WAIT PROMPT

# Check if interface exists
IF_NOT_CONTAINS "Invalid interface"
    SEND no shutdown
    WAIT PROMPT
    SEND description "Uplink Port"
    WAIT PROMPT
    SUCCESS Interface configured successfully
ELSE
    SEND exit
    WAIT PROMPT
    SUCCESS Interface not found, skipping configuration
ENDIF
```

**Example 3: Nested Conditions**
```plaintext
SEND show system
WAIT PROMPT

IF_CONTAINS "System Ready"
    SEND show interfaces
    WAIT PROMPT
    
    IF_CONTAINS "Ethernet1/1"
        SEND configure
        WAIT PROMPT
        SEND interface ethernet 1/1
        WAIT PROMPT
        SEND no shutdown
        WAIT PROMPT
        SEND exit
        WAIT PROMPT
        SUCCESS Interface Ethernet1/1 enabled
    ELSE
        SUCCESS Interface Ethernet1/1 not found
    ENDIF
ELSE
    SUCCESS System not ready, skipping interface configuration
ENDIF
```

---

## 🎯 Command Reference

### **Running the Tool**

```bash
# Basic execution
python main.py

# With custom configuration
python main.py -c /path/to/config.ini

# With custom playbook
python main.py -p /path/to/playbook.txt

# Verbose mode (recommended for troubleshooting)
python main.py --verbose

# Quiet mode (no colors, minimal output)
python main.py --no-color

# Override serial settings
python main.py -b 9600 --prompt-symbol "#"

# Full example with all options
python main.py -c custom.ini -p commands.txt -u admin --verbose --no-pagination
```

### **Playbook Command Syntax**

```plaintext
# Send commands (automatically adds newline)
SEND command_here
SEND show version
SEND configure terminal

# Wait for specific text (case-sensitive)
WAIT Expected Text Here
WAIT login:
WAIT Password:
WAIT (config)#

# Wait for command prompt (uses PromptSymbol from config)
WAIT PROMPT

# Pause execution for X seconds
PAUSE 5
PAUSE 30

# Conditional logic
IF_CONTAINS "text to search for"
    # commands here
ELIF_CONTAINS "other text" 
    # other commands
ELSE
    # default commands
ENDIF

# Success message (optional, shown in green)
SUCCESS Operation completed successfully!

# Comments (ignored)
# This is a comment
# TODO: Add more commands here
```

---

## 🛠️ Troubleshooting

### **Common Issues & Solutions**

#### 🔌 **Serial Port Problems**

**Problem: "Serial port not found" or "Permission denied"**

**Solutions:**
```bash
# On Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
# Then logout and login again

# Check available ports
python -m serial.tools.list_ports

# Run without specifying port to see available options
python main.py
```

**Problem: "Device not responding"**

**Solutions:**
1. Check physical connections
2. Verify baud rate: `python main.py -b 9600`
3. Try different prompt symbol: `python main.py --prompt-symbol "#"`
4. Use verbose mode: `python main.py --verbose`

#### 🔐 **Login Issues**

**Problem: "Login failed" or "Authentication error"**

**Solutions:**
```bash  
# Test with verbose logging
python main.py --verbose -u admin

# Check if already logged in (tool will skip login)
python main.py --verbose
```

**Problem: "Password prompt not detected"**

**Solutions:**
1. Update playbook to use exact text:
```plaintext
# Instead of:
WAIT Password:

# Try:
WAIT password:
# or:
WAIT Enter password:
```

#### ⚡ **Execution Problems**

**Problem: "Command timeout" or "Hanging on command"**

**Solutions:**
```bash
# Increase timeout
python main.py -c config.ini  # Edit Timeout in config

# Add pauses in playbook
SEND slow_command_here
PAUSE 10
WAIT PROMPT
```

**Problem: "Conditional logic not working"**

**Solutions:**
1. Use verbose mode to see exact device output:
```bash
python main.py --verbose
```

2. Check exact text matching:
```plaintext
# Case-sensitive matching
IF_CONTAINS "Version 3.8.1"  # Must match exactly
```

#### 📊 **Progress Display Issues**

**Problem: "Progress bar shows technical details"**

**Solution:** Update to latest version - this has been fixed to show user-friendly descriptions like "Logging in" and "Executing: show version"

**Problem: "No progress bar visible"**

**Solutions:**
```bash
# Ensure tqdm is installed
pip install tqdm>=4.64.0

# Run without --no-color
python main.py --verbose
```

### **Debugging Steps**

1. **Start with verbose mode:**
```bash
python main.py --verbose
```

2. **Check configuration:**
```bash
# Verify config.ini exists and is readable
cat config.ini

# Test with minimal playbook
echo "SEND show version" > test.txt
echo "WAIT PROMPT" >> test.txt  
python main.py -p test.txt --verbose
```

3. **Test serial connection:**
```bash
# List available ports
python -c "import serial.tools.list_ports; [print(p) for p in serial.tools.list_ports.comports()]"
```

4. **Validate playbook syntax:**
```plaintext
# Check for common errors:
# - Missing WAIT PROMPT after SEND commands
# - Unmatched IF/ENDIF blocks
# - Incorrect text in WAIT commands
```

---

## 📊 Understanding Progress Output

The tool provides real-time feedback about execution progress. Here's how to interpret what you see:

### **Normal Mode Output**
```
Logging in:  29%|████████▊                        | 4/14 [00:02<00:05]
```
- **"Logging in"**: Current operation being performed
- **29%**: Percentage complete
- **4/14**: Current step out of total steps
- **[00:02<00:05]**: 2 seconds elapsed, 5 seconds estimated remaining

### **Verbose Mode Output**
```
[INFO] Connecting to serial port COM3 at 115200 baud
[INFO] Waiting for login prompt...
[DEBUG] Received: "Welcome to Mellanox Switch"
[DEBUG] Received: "login: "
[INFO] Sending username: admin
[DEBUG] Sent: "admin\n"
Logging in:  29%|████████▊                        | 4/14 [00:02<00:05]
```

### **Progress Descriptions**
- **"Logging in"**: Authenticating with device
- **"Executing: [command]"**: Running specific command  
- **"Conditional: [condition]"**: Evaluating IF/ELIF/ELSE logic
- **"Waiting for: [text]"**: Waiting for specific device response
- **"Pausing: [X] seconds"**: Deliberate delay in execution

### **Success/Error Messages**
```bash
✅ SUCCESS: Configuration complete!
❌ ERROR: Login failed - check credentials  
⚠️  WARNING: Command timeout - device may be slow
ℹ️  INFO: Already logged in, skipping login sequence
```

---

## 🔐 Security & Best Practices

### **Credential Management**

**❌ AVOID:**
```bash
# Don't put passwords in command line (visible in process list)
python main.py --password mypassword

# Don't put passwords in config.ini (visible in plain text)
```

**✅ RECOMMENDED:**
```bash
# Let tool prompt for password (secure input)
python main.py -u admin

# Use environment variables
export DEVICE_USERNAME=admin
export DEVICE_PASSWORD=mypassword
python main.py -u $DEVICE_USERNAME --password $DEVICE_PASSWORD
```

### **File Permissions**

```bash
# Secure your configuration files
chmod 600 config.ini
chmod 600 *.txt

# Create dedicated directory
mkdir ~/mellanox-configs
chmod 700 ~/mellanox-configs
```

### **Network Security**

- **Use serial connections** when possible (more secure than network)
- **Limit physical access** to serial ports
- **Monitor logs** for unauthorized access attempts
- **Use strong passwords** for device authentication

---

## 📚 Examples & Use Cases

### **Use Case 1: Daily Health Checks**

**Scenario:** Check system status every morning

**Playbook: daily_health.txt**
```plaintext
# Daily system health check
WAIT login:
SEND admin
WAIT Password:
SEND mypassword
WAIT PROMPT

# Check system resources
SEND show system resources
WAIT PROMPT

# Check interface status
SEND show interfaces brief
WAIT PROMPT

# Check for errors
SEND show log
WAIT PROMPT

IF_CONTAINS "ERROR"
    SUCCESS ⚠️ Warnings found in system log - please review
ELSE
    SUCCESS ✅ All systems healthy
ENDIF
```

**Usage:**
```bash
python main.py -p daily_health.txt --verbose
```

### **Use Case 2: Firmware Upgrade Validation**

**Scenario:** Verify firmware upgrade was successful

**Playbook: upgrade_check.txt**
```plaintext
# Post-upgrade validation
WAIT login:
SEND admin
WAIT Password:
SEND mypassword
WAIT PROMPT

# Check new firmware version  
SEND show version
WAIT PROMPT

IF_CONTAINS "Version 4.2.1"
    # New version detected - run post-upgrade tasks
    SEND show license
    WAIT PROMPT
    
    SEND test connectivity
    WAIT PROMPT
    
    IF_CONTAINS "Test passed"
        SUCCESS ✅ Firmware upgrade successful and validated
    ELSE
        SUCCESS ⚠️ Firmware upgraded but connectivity test failed
    ENDIF
ELSE
    SUCCESS ❌ Firmware upgrade failed - still on old version
ENDIF
```

### **Use Case 3: Multi-Device Configuration**

**Scenario:** Configure multiple switches with same settings

**Playbook: switch_config.txt**
```plaintext
# Standard switch configuration
WAIT login:
SEND admin
WAIT Password:
SEND mypassword
WAIT PROMPT

# Enter configuration mode
SEND configure
WAIT PROMPT

# Set hostname based on current device
SEND show system hostname
WAIT PROMPT

IF_CONTAINS "switch01"
    SEND hostname "PROD-SW-01"
    WAIT PROMPT
ELIF_CONTAINS "switch02"  
    SEND hostname "PROD-SW-02"
    WAIT PROMPT
ELSE
    SEND hostname "UNKNOWN-SWITCH"
    WAIT PROMPT
ENDIF

# Apply common configuration
SEND interface ethernet 1/1
WAIT PROMPT
SEND description "Uplink to Core"
WAIT PROMPT
SEND no shutdown
WAIT PROMPT

# Save configuration
SEND exit
WAIT PROMPT
SEND configuration save
WAIT PROMPT

SUCCESS ✅ Switch configuration complete
```

**Usage:**
```bash
# Run on multiple devices
python main.py -p switch_config.txt --verbose
# Disconnect, connect to next switch, repeat
```

### **Use Case 4: Automated Testing**

**Scenario:** Run automated tests after configuration changes

**Playbook: system_test.txt**
```plaintext
# Automated system testing
WAIT login:
SEND admin
WAIT Password:
SEND mypassword
WAIT PROMPT

# Test 1: Interface connectivity
SEND ping 192.168.1.1
WAIT PROMPT

IF_CONTAINS "Success rate is 100"
    SUCCESS ✅ Test 1 PASSED: Network connectivity OK
ELSE
    SUCCESS ❌ Test 1 FAILED: Network connectivity issues
ENDIF

# Test 2: VLAN configuration
SEND show vlan brief
WAIT PROMPT

IF_CONTAINS "VLAN100"
    IF_CONTAINS "active"
        SUCCESS ✅ Test 2 PASSED: VLAN100 active
    ELSE
        SUCCESS ❌ Test 2 FAILED: VLAN100 not active
    ENDIF
ELSE
    SUCCESS ❌ Test 2 FAILED: VLAN100 not found
ENDIF

# Test 3: License status
SEND show license
WAIT PROMPT

IF_NOT_CONTAINS "expired"
    SUCCESS ✅ Test 3 PASSED: License valid
ELSE
    SUCCESS ❌ Test 3 FAILED: License expired
ENDIF

SUCCESS 🎉 Automated testing complete
```

---

## 🏗️ Advanced Features

### **Legacy Mode**
For compatibility with older devices or original script behavior:
```bash
python main.py --legacy-mode
```

### **Custom Prompt Symbols**  
For devices with non-standard prompts:
```bash
python main.py --prompt-symbol "#"
python main.py --prompt-symbol "switch>"
```

### **Batch Processing**
Process multiple playbooks:
```bash
python main.py -p config1.txt --verbose && \
python main.py -p config2.txt --verbose && \
python main.py -p config3.txt --verbose
```

### **Integration with Scripts**
```bash
#!/bin/bash
# Automated device management script

DEVICES=("switch01" "switch02" "switch03")
PLAYBOOK="daily_check.txt"

for device in "${DEVICES[@]}"; do
    echo "Processing $device..."
    # Connect to device serial port and run playbook
    python main.py -p $PLAYBOOK --no-color
    echo "Completed $device"
done
```

---

## 🔧 Developer Information

- **Developer Documentation**: See [DEVELOPER.md](DEVELOPER.md) for architecture details
- **Source Code**: Modular Python codebase with comprehensive documentation
- **Testing**: Extensive test suite included in `tests/` directory
- **Contributing**: Fork, create feature branch, add tests, submit pull request

---

## 📄 License & Support

- **License**: MIT License - free for personal and commercial use
- **Documentation**: This README + DEVELOPER.md + inline code comments
- **Issues**: Create GitHub issues for bug reports or feature requests

---

**🎉 That's it! You're now ready to automate your Mellanox device management like a pro!**

*Remember: Start simple with basic playbooks, then gradually add conditional logic as you become more comfortable with the tool.*
