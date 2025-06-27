# Mellanox Device Updater

A professional Python tool for automated serial communication with Mellanox switches and network devices. Features a modern modular architecture, intelligent command block progress tracking, and comprehensive conditional logic support.

## 🚀 Key Features

- **🏗️ Modular Architecture**: Clean, maintainable codebase with dedicated modules
- **📊 Smart Progress Tracking**: User-friendly progress bars showing logical command blocks
- **🔄 Conditional Logic**: Advanced IF/ELIF/ELSE/ENDIF support with multiple conditions
- **🔧 Automatic Login Detection**: Skips login steps if already authenticated
- **📱 Interactive Port Selection**: Automatic serial port detection and selection
- **🎨 Rich Output Formatting**: Colored output with verbose/non-verbose modes
- **⚡ Robust Error Handling**: Comprehensive error detection and recovery
- **📄 Flexible Configuration**: INI-based configuration with command-line overrides

## 📋 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd mellanox-updater
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your device:**
   ```bash
   cp config.ini.template config.ini
   # Edit config.ini with your device settings
   ```

### Basic Usage

**Run with default configuration:**
```bash
python main.py
```

**Run with credentials:**
```bash
python main.py -u admin --password your_password
```

**Run in verbose mode:**
```bash
python main.py --verbose
```

**Use custom configuration:**
```bash
python main.py -c custom_config.ini --verbose
```

## 📖 Command Line Options

```
Options:
  -h, --help                    Show help message
  -b, --baudrate RATE          Baud rate (default: 115200)
  -c, --config FILE            Configuration file (default: config.ini)
  -p, --playbook FILE          Playbook file (overrides config setting)
  -v, --verbose                Enable verbose logging
  -u, --username USER          Username for device login
  --password PASS              Password for device login
  --no-color                   Disable colored output
  --no-pagination              Disable automatic pagination handling
  --prompt-symbol SYMBOL       Override prompt symbol (default: >)
  --legacy-mode                Run in legacy mode
```

## 🎯 Progress Bar Examples

The tool displays user-friendly progress descriptions showing what logical operation is being performed:

**Non-verbose mode:**
```
Logging in:  29%|████████▊                        | 4/14 [00:02<00:05]
Executing: show diag:  43%|█████████████▎         | 6/14 [00:03<00:04]  
Conditional: show license:  64%|████████████████▋  | 9/14 [00:05<00:02]
Executing: show configuration:  93%|███████████▌  | 13/14 [00:06<00:00]
```

**Verbose mode:**
Shows the same progress descriptions plus detailed logging above the progress bar.

## 📝 Playbook Format

Create playbooks using simple, intuitive commands:

```plaintext
# Login sequence
WAIT login:
SEND admin
WAIT Password:
SEND your_password
WAIT PROMPT

# Execute commands
SEND show version
WAIT PROMPT

# Conditional logic
IF_CONTAINS "specific_version"
    SEND show license
    WAIT PROMPT
ENDIF

# Pause and final commands
SEND show configuration
PAUSE 10
WAIT PROMPT

SUCCESS Playbook completed successfully!
```

## 🔄 Conditional Logic

The tool supports sophisticated conditional logic:

### Available Conditions
- `IF_CONTAINS "text"` - Check if output contains specific text
- `IF_NOT_CONTAINS "text"` - Check if output does NOT contain text
- `IF "text"` - Alias for IF_CONTAINS
- `ELIF_CONTAINS "text"` - Else-if with contains check
- `ELIF_NOT_CONTAINS "text"` - Else-if with not-contains check
- `ELSE` - Default case
- `ENDIF` - End conditional block

### Example Conditional Playbook
```plaintext
SEND show version
WAIT PROMPT

IF_CONTAINS "Version 3.8"
    SEND enable_feature_v38
    WAIT PROMPT
ELIF_CONTAINS "Version 3.7"
    SEND enable_feature_v37
    WAIT PROMPT
ELSE
    SEND show help
    WAIT PROMPT
ENDIF
```

## ⚙️ Configuration

### config.ini Structure
```ini
[DEFAULT]
port = /dev/ttyUSB0
baudrate = 115200
username = admin
password = your_password
playbook_file = playbook.txt
prompt_symbol = >
success_message = Configuration updated successfully!

[logging]
verbose = false
use_colors = true
use_pagination = true
```

### Playbook Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `SEND` | Send text to device | `SEND show version` |
| `WAIT` | Wait for specific text | `WAIT PROMPT` |
| `PAUSE` | Pause execution | `PAUSE 5` |
| `IF_CONTAINS` | Conditional execution | `IF_CONTAINS "text"` |
| `IF_NOT_CONTAINS` | Negative conditional | `IF_NOT_CONTAINS "error"` |
| `ELIF_CONTAINS` | Else-if condition | `ELIF_CONTAINS "other"` |
| `ELSE` | Default case | `ELSE` |
| `ENDIF` | End conditional | `ENDIF` |
| `SUCCESS` | Success message | `SUCCESS Done!` |

## 🏗️ Architecture

The tool uses a clean modular architecture:

```
mellanox-updater/
├── main.py                     # Application entry point
├── config/
│   └── config_manager.py       # Configuration and playbook management
├── core/
│   ├── playbook_executor.py    # Command execution and progress tracking
│   ├── serial_handler.py       # Serial communication
│   ├── prompt_detector.py      # Automatic prompt detection
│   └── conditional_logic.py    # IF/ELIF/ELSE logic processor
├── utils/
│   ├── logger.py               # Logging and output formatting
│   ├── output_processor.py     # Text processing and cleanup
│   └── pagination.py           # Automatic pagination handling
├── docs/                       # Documentation
├── examples/                   # Example configurations
└── tests/                      # Test suites
```

## 🔧 Troubleshooting

### Common Issues

**Serial port not found:**
- Run without `-p` option to see available ports
- Check device connections
- Verify user permissions for serial ports

**Login fails:**
- Verify credentials in config.ini
- Check if device is already logged in
- Use `--verbose` for detailed logging

**Commands not executing:**
- Check playbook syntax
- Verify prompt detection with `--verbose`
- Ensure proper WAIT commands after SEND

**Progress bar shows technical details:**
- This has been fixed in the latest version
- Both verbose and non-verbose modes now show user-friendly descriptions

### Verbose Mode Debugging

Use `--verbose` to see detailed execution logs:
```bash
python main.py --verbose
```

This shows:
- Detailed command execution logs
- Serial communication details
- Conditional logic evaluation
- Error details and stack traces

## 📚 Documentation

- [Developer Documentation](DEVELOPER.md) - Architecture and development guide
- [Conditional Logic Specification](docs/CONDITIONAL_LOGIC_SPEC.md) - Detailed conditional logic guide
- [Example Playbooks](examples/) - Sample configurations and playbooks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔄 Version History

### v2.0 - Modular Architecture & Smart Progress
- Complete modular refactor for maintainability
- Smart command block progress tracking
- Enhanced conditional logic support
- Improved error handling and logging
- Better user experience with intuitive progress bars

### v1.0 - Initial Release
- Basic serial communication
- Simple playbook execution
- Configuration file support
