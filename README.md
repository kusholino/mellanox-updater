# Mellanox Device Updater

A professional Python tool for automated serial communication with Mellanox switches and network devices. Features robust error handling, automatic pagination, dynamic prompt detection, and flexible playbook management.

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
- **`WAIT text`** - Wait for specific text to appear
- **`WAIT PROMPT`** - Wait for command prompt (auto-detected)
- **`SEND command`** - Send a command to the device
- **`PAUSE seconds`** - Wait for a fixed number of seconds
- **`SUCCESS message`** - Custom success message when completed

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

### Custom Config File
```bash
python3 serial_communicator.py --config my_config.ini
```

### Multiple Playbooks
Create different playbook files for different tasks:
```bash
# Edit config.ini to point to different playbooks
PlaybookFile = basic_setup.txt
PlaybookFile = firmware_update.txt
PlaybookFile = configuration_backup.txt
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

## 📁 File Structure

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
