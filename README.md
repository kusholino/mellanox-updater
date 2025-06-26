# Mellanox Device Updater

A professional Python tool for automated serial communication with Mellanox switches and network devices. Features robust error handling, automatic pagination, dynamic prompt detection, flexible playbook management, and **powerful conditional logic** for intelligent device automation.

## ✨ **NEW: Conditional Logic Support**
Execute different commands based on device output! Automatically adapt to different switch models, software versions, or configurations:

```
SEND show version
WAIT PROMPT
IF_CONTAINS "SN2700"
    SEND show interfaces ethernet brief
    WAIT PROMPT
ELSE
    SEND show interfaces status
    WAIT PROMPT  
ENDIF
```

## 🚀 Quick Start

### Prerequisites
- Python 3.6+
- Serial device connected via USB/COM port

### Installation
1. Clone or download this repository
2. Install required packages:
```bash
pip install pyserial tqdm
```

### Basic Usage
1. **Configure your device settings** in `config.ini`
2. **Write your commands** in `playbook.txt` (no indentation required!)
3. **Run the tool**:
```bash
# With progress bar (recommended for most users)
python3 serial_communicator.py

# With detailed logging (for troubleshooting)
python3 serial_communicator.py --verbose
```

## 📝 Creating Playbooks

Write your device commands in `playbook.txt` with **zero indentation required**:

```
# Simple example - no spaces needed!
WAIT login:
SEND admin
WAIT Password:
SEND mypassword
WAIT PROMPT
SEND show version
SEND configure terminal
SEND hostname new-switch-name
SEND exit
WAIT PROMPT
SEND exit
SUCCESS Configuration completed!
```

### Supported Commands

#### Basic Commands
- **`WAIT text`** - Wait for specific text to appear
- **`WAIT PROMPT`** - Wait for command prompt (auto-detected)
- **`SEND command`** - Send a command to the device
- **`PAUSE seconds`** - Wait for a fixed number of seconds
- **`SUCCESS message`** - Custom success message when completed

#### **NEW: Conditional Logic Commands**
Execute commands based on the output of previous commands:

**Case-Sensitive Matching:**
- **`IF_CONTAINS "text"`** - Execute block if output contains exact text
- **`IF_NOT_CONTAINS "text"`** - Execute block if output does NOT contain exact text
- **`ELIF_CONTAINS "text"`** - Alternative condition (case-sensitive)
- **`ELIF_NOT_CONTAINS "text"`** - Alternative condition (case-sensitive)

**Case-Insensitive Matching:**
- **`IF_CONTAINS_I "text"`** - Execute block if output contains text (ignoring case)
- **`IF_NOT_CONTAINS_I "text"`** - Execute block if output does NOT contain text (ignoring case)
- **`ELIF_CONTAINS_I "text"`** - Alternative condition (case-insensitive)
- **`ELIF_NOT_CONTAINS_I "text"`** - Alternative condition (case-insensitive)

**Advanced Pattern Matching:**
- **`IF_REGEX "pattern"`** - Execute block if regex pattern matches
- **`ELIF_REGEX "pattern"`** - Alternative regex condition

**Control Flow:**
- **`ELSE`** - Execute if no conditions matched
- **`ENDIF`** - End conditional block (required)

### Example Playbooks

**Basic Configuration:**
```
WAIT login:
SEND admin
WAIT Password:
SEND password123
WAIT PROMPT
SEND configure terminal
SEND hostname lab-switch-01
SEND interface ethernet 1/1
SEND description "Server Connection"
SEND no shutdown
SEND exit
SEND exit
WAIT PROMPT
SEND write memory
SUCCESS Switch configured successfully!
```

**Smart Device Detection with Conditionals:**
```
# Check device model and adapt commands accordingly
WAIT login:
SEND admin
WAIT Password:
SEND password123
WAIT PROMPT
SEND show version
WAIT PROMPT

# Different commands for different switch models
IF_CONTAINS "SN2700"
    SEND show interfaces ethernet brief
    WAIT PROMPT
    SEND show system temperature
    WAIT PROMPT
ELIF_CONTAINS "SN3700"
    SEND show interfaces status
    WAIT PROMPT
    SEND show environment power
    WAIT PROMPT
ELSE
    SEND show interfaces summary
    WAIT PROMPT
ENDIF

SUCCESS Device configuration completed based on model!
```

**Feature Detection and Configuration:**
```
WAIT PROMPT
SEND show features
WAIT PROMPT

# Only configure BGP if it's enabled
IF_NOT_CONTAINS "BGP: disabled"
    SEND configure terminal
    SEND router bgp 65001
    SEND neighbor 192.168.1.1 remote-as 65002
    SEND exit
    SEND exit
    WAIT PROMPT
ENDIF

# Check if VLAN feature is available
IF_CONTAINS_I "vlan"
    SEND show vlan brief
    WAIT PROMPT
ENDIF

SUCCESS Configuration applied based on available features!
```

**Information Gathering:**
```
WAIT login:
SEND admin
WAIT Password:
SEND password123
WAIT PROMPT
SEND show version
PAUSE 2
WAIT PROMPT
SEND show interfaces
PAUSE 2
WAIT PROMPT
SEND show configuration
PAUSE 5
WAIT PROMPT
SEND exit
SUCCESS Information collected successfully!
```

## ⚙️ Configuration

Edit `config.ini` to match your setup:

```ini
[Serial]
BaudRate = 115200
Timeout = 60
PromptSymbol = >

[Pagination]
Enabled = true
ResponseDelay = 0.1

[Playbook]
PlaybookFile = playbook.txt
```

### Configuration Options

**Serial Settings:**
- **BaudRate**: Serial communication speed (usually 115200)
- **Timeout**: Maximum wait time for each command (seconds)
- **PromptSymbol**: Fallback prompt if auto-detection fails

**Pagination Settings:**
- **Enabled**: Automatically handle "Press any key to continue" prompts
- **ResponseDelay**: Delay after responding to pagination (seconds)

**Playbook Settings:**
- **PlaybookFile**: Path to your playbook file (relative or absolute)

## 🎯 Key Features

### ✅ **Zero Indentation Required**
Write commands with any formatting you prefer:
```
WAIT login:
SEND admin
    WAIT Password:
        SEND password123
WAIT PROMPT
SEND show version
```

### ✅ **Automatic Pagination Handling**
Automatically responds to:
- `--More--` prompts
- `Press any key to continue`
- `Continue? [y/n]`
- And many more pagination patterns

### ✅ **Smart Prompt Detection**
Automatically detects device prompts like:
- `switch01>`
- `admin@switch01#`
- `switch01(config)#`

### ✅ **Professional Logging**
- **Progress bar mode**: Clean output for normal use
- **Verbose mode**: Detailed logging for troubleshooting
- **Color-coded messages**: Easy to read status updates

### ✅ **Robust Error Handling**
- Serial communication errors
- Timeout handling
- Invalid command detection
- File not found errors

### ✅ **Smart Pre-Login Detection**
- Automatically detects if already logged in
- Intelligently skips all login-related steps when already authenticated
- Preserves actual commands and configuration steps
- Handles complex login sequences with multiple prompts and credentials

### ✅ **Serial Port Protection**
- Detects if port is already in use
- Prevents conflicts with other applications
- Clear error messages for port access issues

### ✅ **Conditional Logic Support**
- **Smart decision making**: Execute different commands based on device output
- **Device model detection**: Automatic adaptation to different hardware
- **Feature detection**: Only run commands if features are available
- **Case-sensitive and case-insensitive text matching**
- **Regular expression pattern matching** for advanced conditions
- **Nested conditional blocks** with IF/ELIF/ELSE/ENDIF
- **Dynamic workflows** that adapt to device state

## 🔧 Usage Examples

### Standard Operation
```bash
python3 serial_communicator.py
```
Shows a clean progress bar and only critical information.

### Troubleshooting Mode
```bash
python3 serial_communicator.py --verbose
```
Shows detailed logging, command outputs, and debug information.

### Custom Playbook File
```bash
python3 serial_communicator.py --playbook my_custom_playbook.txt
```

### Using Conditional Examples
```bash
# Run the comprehensive conditional logic example
python3 serial_communicator.py --playbook examples/conditional_playbook_example.txt
```

## 🎯 **Conditional Logic Guide**

### Case Sensitivity Rules
- **Default behavior**: All text matching is **case-sensitive**
- **Case-insensitive**: Use commands ending with `_I` (e.g., `IF_CONTAINS_I`)
- **Regular expressions**: Case-insensitive by default

### Basic Conditional Structure
```
SEND some command
WAIT PROMPT
IF_CONTAINS "expected text"
    SEND conditional command 1
    WAIT PROMPT
    SEND conditional command 2
    WAIT PROMPT
ENDIF
```

### Advanced Conditional Structure
```
SEND show device info
WAIT PROMPT

IF_CONTAINS "Model: SN2700"
    SEND show interfaces ethernet brief
    WAIT PROMPT
ELIF_CONTAINS "Model: SN3700"
    SEND show interfaces status
    WAIT PROMPT
ELIF_REGEX "Model: SN[0-9]{4}"
    SEND show interfaces summary
    WAIT PROMPT
ELSE
    SEND show system
    WAIT PROMPT
ENDIF
```

### Real-World Examples

#### Device Model Detection
```
SEND show version
WAIT PROMPT
IF_CONTAINS "SN2700"
    # Commands specific to SN2700
    SEND show interfaces ethernet 1/1-1/32
    WAIT PROMPT
ELIF_CONTAINS "SN3700"
    # Commands specific to SN3700
    SEND show interfaces ethernet 1/1-1/64
    WAIT PROMPT
ENDIF
```

#### Software Version Adaptation
```
SEND show version
WAIT PROMPT
IF_REGEX "Version.*3\.[0-9]+"
    # Commands for version 3.x
    SEND show system resources
    WAIT PROMPT
ELIF_REGEX "Version.*4\.[0-9]+"
    # Commands for version 4.x
    SEND show platform resources
    WAIT PROMPT
ENDIF
```

#### Feature Availability Check
```
SEND show features
WAIT PROMPT
IF_NOT_CONTAINS_I "bgp.*disabled"
    SEND show ip bgp summary
    WAIT PROMPT
    IF_CONTAINS "neighbors"
        SEND show ip bgp neighbors
        WAIT PROMPT
    ENDIF
ENDIF
```
python3 serial_communicator.py --config my_config.ini
```

### Custom Playbook File
```bash
# Use a specific playbook file (overrides config setting)
python3 serial_communicator.py --playbook examples/example1_no_indent.txt

# Combine with verbose mode
python3 serial_communicator.py --verbose --playbook custom_commands.txt
```

### Multiple Playbooks
Create different playbook files for different tasks:
```bash
# Use different playbooks for different scenarios
python3 serial_communicator.py --playbook basic_setup.txt
python3 serial_communicator.py --playbook firmware_update.txt  
python3 serial_communicator.py --playbook configuration_backup.txt
```

## 📋 Typical Workflow

1. **Connect** your Mellanox device via serial cable
2. **Edit** `playbook.txt` with your desired commands
3. **Configure** `config.ini` if needed (usually defaults work)
4. **Run** the tool and select your COM port
5. **Monitor** progress - the tool handles everything automatically
6. **Review** results and any error messages

## 🚨 Troubleshooting

### Common Issues

**"No serial ports found"**
- Check device connection
- Install device drivers if needed
- Try different USB port

**"Permission denied" on Linux**
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

**"Timeout waiting for prompt"**
- Check baud rate in config.ini
- Verify device is powered on
- Try increasing timeout value

**"Config parsing errors"**
- Ensure playbook file exists
- Check file permissions
- Verify config.ini syntax

### Getting Help

1. **Run in verbose mode** to see detailed logs:
   ```bash
   python3 serial_communicator.py --verbose
   ```

2. **Check the logs** for specific error messages

3. **Verify your playbook** syntax and commands

4. **Test with a simple playbook** first

## � Troubleshooting

### Common Issues

**"Port is already in use" or "Permission denied"**
- Close other serial applications (PuTTY, minicom, etc.)
- On Linux, try: `sudo python3 serial_communicator.py`
- Check if another instance is running

**"Device requires login" when already logged in**
- The pre-login detection may have failed
- Manually add a `SEND \n` at the start of your playbook
- Check if device has unusual prompt formatting

**"Login steps not being skipped properly"**
- The improved login filtering should handle most cases automatically
- If login steps are still executed when already authenticated, check verbose logs
- Ensure your playbook uses standard login patterns (WAIT login:, SEND admin, etc.)
- Contact support if login filtering isn't working for your specific device

**Commands fail or timeout**
- Increase timeout in config.ini
- Use verbose mode to see actual device responses
- Verify commands work when typed manually

## �📁 File Structure

```
mellanox-updater/
├── config.ini              # Main configuration
├── playbook.txt            # Your command sequences
├── serial_communicator.py  # Main application
└── examples/               # Example playbooks
    ├── basic_config.txt
    ├── info_gathering.txt
    └── firmware_update.txt
```

## 💡 Tips & Best Practices

- **Start simple**: Test with basic commands first
- **Use comments**: Add `# comments` to document your playbooks
- **Check timeouts**: Increase timeout for slow operations
- **Test commands**: Verify commands work manually first
- **Backup configs**: Save working playbooks for reuse
- **Use verbose mode**: When developing or troubleshooting

## 🔒 Safety Notes

- **Test thoroughly** before using on production devices
- **Have console access** as backup
- **Save current configs** before making changes
- **Start with read-only commands** to verify connectivity
- **Use appropriate timeouts** to avoid hanging

---

**Happy automating! 🎉**

For detailed technical information, see `README_DEV.md`.

## 🔀 **NEW: Conditional Logic in Playbooks**

The playbook format now supports conditional statements based on command output:

### Basic Conditional Logic
```
SEND show version
WAIT PROMPT

IF_CONTAINS "SN2700"
    SEND show interfaces ethernet brief
    WAIT PROMPT
ELIF_CONTAINS "SN3700"
    SEND show interfaces status
    WAIT PROMPT
ELSE
    SEND show interfaces
    WAIT PROMPT
ENDIF
```

## 🛠️ **Troubleshooting**

### Common Issues

**1. Conditional logic not working as expected**
```bash
# Use verbose mode to see condition evaluation
python3 serial_communicator.py --verbose
```
This shows:
- What text is being matched against
- Whether conditions evaluate to true/false
- Which conditional blocks are being executed or skipped

**2. Case sensitivity problems**
```
# Instead of this (case-sensitive)
IF_CONTAINS "BGP"

# Use this for case-insensitive matching
IF_CONTAINS_I "BGP"
```

**3. Complex patterns not matching**
```
# Use regex for complex patterns
IF_REGEX "Temperature.*([0-9]+)C.*Normal"
```

**4. Serial port access denied**
```bash
# On Linux, add user to dialout group
sudo usermod -a -G dialout $USER
# Then logout and login again

# Or run with sudo (temporary solution)
sudo python3 serial_communicator.py
```

**5. Device not responding**
- Check cable connections
- Verify correct COM port selection
- Ensure device is powered on and accessible
- Try different baud rates (9600, 38400, 115200)

### Debug Mode
Always use `--verbose` when troubleshooting:
```bash
python3 serial_communicator.py --verbose
```

This provides:
- Detailed connection information
- Command execution status
- Output from each command
- Conditional logic evaluation details
- Error messages with context

## 📁 **Project Structure**
```
mellanox-updater/
├── serial_communicator.py      # Main automation script
├── config.ini                  # Configuration settings
├── playbook.txt                # Your command sequence
├── examples/
│   └── conditional_playbook_example.txt  # Advanced conditional examples
├── docs/
│   ├── CONDITIONAL_LOGIC_SPEC.md         # Detailed conditional logic spec
│   └── ...
└── README.md                   # This documentation
```

## 🤝 **Support**

### Getting Help
1. **Check verbose output**: Run with `--verbose` flag
2. **Review examples**: See `examples/` directory for working playbooks
3. **Check documentation**: See `docs/` directory for detailed specs

### Feature Requests
The conditional logic system is designed to be extensible. Current capabilities include:
- Text matching (case-sensitive and case-insensitive)
- Regular expression patterns
- Nested conditions with IF/ELIF/ELSE/ENDIF

## 📋 **Changelog**

### Latest Updates
- ✅ **Conditional Logic**: Full IF/ELIF/ELSE/ENDIF support
- ✅ **Case Sensitivity Control**: Both case-sensitive and case-insensitive matching
- ✅ **Regular Expression Support**: Advanced pattern matching with IF_REGEX
- ✅ **Improved Output Processing**: Clean command output without pagination artifacts
- ✅ **Enhanced Error Handling**: Better error messages and recovery
- ✅ **Smart Login Detection**: Automatically skip login steps when already authenticated
- ✅ **Flexible Playbook Formatting**: No indentation requirements
- ✅ **Professional Progress Display**: Clean progress bars and status updates

---

**🎉 The Mellanox Device Updater now supports intelligent, conditional automation - making your network device management smarter and more efficient!**
