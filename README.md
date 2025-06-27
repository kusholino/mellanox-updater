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
port = /dev/ttyUSB0
baudrate = 115200
username = admin
password = your_password
```

### 3. Create a Playbook
Write your commands in `playbook.txt`:
```
WAIT login:
SEND admin
WAIT Password:
SEND your_password
WAIT PROMPT
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
WAIT login:
SEND admin
WAIT Password:
SEND admin_password
WAIT PROMPT
SEND show running-config
PAUSE 10
WAIT PROMPT
SEND show startup-config
PAUSE 10
WAIT PROMPT
SUCCESS Backup completed
```

### Conditional Logic Based on Device Type
```
SEND show version
WAIT PROMPT

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
WAIT login:
SEND root
WAIT Password:
SEND root_password
WAIT PROMPT
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
| `ENDIF` | End conditional block | `ENDIF` |
| `SUCCESS <message>` | Mark completion | `SUCCESS All done!` |

## Configuration Options

Edit `config.ini` to customize behavior:

```ini
[DEFAULT]
port = /dev/ttyUSB0          # Your serial port
baudrate = 115200            # Communication speed
username = admin             # Login username
password = password          # Login password
playbook_file = playbook.txt # Which playbook to run
prompt_symbol = >            # What your prompt looks like
timeout = 10                 # How long to wait for responses

[LOGGING]
verbose = false              # Show detailed output
log_file =                   # Save log to file (optional)

[ADVANCED]
initialization_delay = 2     # Wait after connecting
command_delay = 1           # Wait between commands
```

## Command Line Options

```bash
# Basic usage
./seriallink

# With custom settings
./seriallink --username admin --password secret --verbose

# Use different config file
./seriallink --config my_device.ini

# Use different playbook
./seriallink --playbook backup_commands.txt

# Override prompt symbol
./seriallink --prompt-symbol "#"
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
- Make sure prompt_symbol matches your device
- Add PAUSE commands if device is slow
- Use `--verbose` to see what's happening

**Conditional logic not working:**
- Text matching is case-sensitive
- Use exact text from device output
- Check for extra spaces or characters

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
Chain multiple conditions:
```
IF_CONTAINS "Version 15.2"
    IF_CONTAINS "Advanced IP Services"
        SEND show license
        WAIT PROMPT
    ENDIF
ENDIF
```

### Output Processing
Save command output to files by using verbose mode:
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
2. **Use Verbose Mode**: Always use `--verbose` when testing
3. **Check Your Prompts**: Make sure prompt_symbol matches your device
4. **Add Delays**: Some devices need time between commands
5. **Test Incrementally**: Add commands one at a time to playbooks
6. **Save Configurations**: Keep separate config files for different devices

SerialLink makes serial device automation straightforward. No complex scripting languages, no intricate setup procedures - just simple commands that work.