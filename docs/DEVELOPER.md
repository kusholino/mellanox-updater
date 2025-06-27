# SerialLink Developer Guide

## Project Overview

SerialLink is a Python-based tool for automating serial communication with network devices, servers, and switches. It uses configurable playbooks to execute command sequences with conditional logic and automatic response handling.

## Architecture

### Core Components

```
seriallink/
├── main.py              # Entry point and argument parsing
├── setup.sh             # Complete setup and validation script
├── config/
│   ├── config_manager.py    # Configuration file handling
│   └── __init__.py
├── core/
│   ├── serial_handler.py    # Serial port communication
│   ├── playbook_executor.py # Playbook parsing and execution
│   ├── prompt_detector.py   # Command prompt detection
│   ├── conditional_logic.py # IF/ENDIF statement processing
│   └── __init__.py
├── utils/
│   ├── logger.py           # Logging and output formatting
│   ├── output_processor.py # Command output processing
│   ├── pagination.py       # Automatic pagination handling
│   └── __init__.py
├── tests/              # Unit and integration tests
├── docs/               # Documentation
└── examples/           # Example playbooks
```

### Data Flow

1. **Configuration Loading**: `ConfigManager` loads settings from `config.ini`
2. **Serial Connection**: `SerialHandler` establishes device connection
3. **Playbook Parsing**: `PlaybookExecutor` reads and validates playbook syntax
4. **Command Execution**: Commands are sent via serial connection
5. **Response Processing**: `OutputProcessor` handles device responses
6. **Conditional Logic**: `ConditionalProcessor` evaluates IF/ENDIF statements
7. **Progress Tracking**: `Logger` provides real-time feedback

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Virtual environment support
- Serial port access permissions

### Quick Setup

```bash
# Clone repository
git clone <repository-url>
cd seriallink

# Run automated setup
./setup.sh

# Activate development environment
source seriallink-env/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt  # if exists
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv seriallink-env
source seriallink-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config.ini.template config.ini
```

## Code Structure

### Main Application (`main.py`)

Entry point that:
- Parses command line arguments
- Initializes logging
- Loads configuration
- Starts playbook execution

### Configuration (`config/config_manager.py`)

Handles:
- INI file parsing
- Default value management
- Configuration validation
- Runtime setting overrides

### Serial Communication (`core/serial_handler.py`)

Features:
- Cross-platform serial port handling
- Connection management and recovery
- Timeout handling
- Data encoding/decoding

### Playbook Execution (`core/playbook_executor.py`)

Processes:
- Playbook file parsing
- Command validation
- Execution flow control
- Error handling and recovery

### Conditional Logic (`core/conditional_logic.py`)

Supports:
- `IF_CONTAINS` / `IF_NOT_CONTAINS` statements
- Nested conditional blocks
- Regular expression matching
- Multiple condition evaluation

### Logging (`utils/logger.py`)

Provides:
- Colored console output
- File logging
- Progress indicators
- Error reporting

## Playbook Syntax

### Basic Commands

```
WAIT <text>         # Wait for specific text in output
SEND <command>      # Send command to device
PAUSE <seconds>     # Wait for specified time
SUCCESS <message>   # Mark successful completion
```

### Conditional Statements

```
IF_CONTAINS "<text>"
    # Commands to execute if text found
ENDIF

IF_NOT_CONTAINS "<text>"
    # Commands to execute if text not found
ENDIF
```

### Comments

```
# This is a comment
# Comments can appear anywhere in the playbook
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_serial_handler.py

# Run with coverage
python -m pytest --cov=core --cov=utils tests/
```

### Test Structure

```
tests/
├── test_serial_handler.py      # Serial communication tests
├── test_playbook_executor.py   # Playbook parsing tests
├── test_conditional_logic.py   # Conditional logic tests
├── test_config_manager.py      # Configuration tests
└── fixtures/                   # Test data and mocks
```

## Adding New Features

### New Playbook Commands

1. Add command parsing in `playbook_executor.py`
2. Implement command logic in relevant core module
3. Add tests for new functionality
4. Update documentation

### New Conditional Operations

1. Add operation type in `conditional_logic.py`
2. Implement evaluation logic
3. Add test cases
4. Update playbook examples

### New Output Processors

1. Create processor in `utils/output_processor.py`
2. Register processor in main execution flow
3. Add configuration options if needed
4. Test with various device types

## Configuration Options

### Core Settings

```ini
[DEFAULT]
port = /dev/ttyUSB0      # Serial port device
baudrate = 115200        # Communication speed
username = admin         # Default login username
password = password      # Default login password
playbook_file = playbook.txt  # Default playbook
prompt_symbol = >        # Command prompt indicator
timeout = 10             # Response timeout in seconds
```

### Advanced Settings

```ini
[ADVANCED]
initialization_delay = 2    # Delay after connection
command_delay = 1          # Delay between commands
max_retries = 3            # Connection retry attempts
buffer_size = 4096         # Serial buffer size
```

## Error Handling

### Common Error Patterns

- **Connection Issues**: Retry with exponential backoff
- **Timeout Errors**: Increase timeout or check device responsiveness
- **Parsing Errors**: Validate playbook syntax before execution
- **Permission Errors**: Check serial port access rights

### Error Codes

- `1`: Python not found
- `2`: Python version incompatible
- `3`: Virtual environment module unavailable
- `4`: Virtual environment creation failed
- `5`: Dependency installation failed
- `6`: Project structure invalid
- `7`: Configuration invalid
- `8`: Module import failed

## Debugging

### Verbose Logging

```bash
# Enable verbose output
./seriallink --verbose

# Log to file
./seriallink --verbose > execution.log 2>&1
```

### Serial Port Debugging

```bash
# List available ports
python -m serial.tools.list_ports

# Test port access
python -c "import serial; s=serial.Serial('/dev/ttyUSB0'); s.close()"
```

### Playbook Debugging

- Add `PAUSE` commands to slow execution
- Use `SUCCESS` messages for checkpoints
- Enable verbose logging for detailed output

## Contributing

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write descriptive docstrings
- Keep functions focused and small

### Pull Request Process

1. Create feature branch from main
2. Implement changes with tests
3. Update documentation
4. Ensure all tests pass
5. Submit pull request with description

### Commit Messages

Use clear, descriptive commit messages:
```
feat: add support for SSH connections
fix: resolve timeout handling in serial_handler
docs: update installation instructions
test: add unit tests for conditional logic
```

## Performance Considerations

### Serial Communication

- Use appropriate timeouts to avoid hanging
- Implement connection pooling for multiple devices
- Buffer large outputs to prevent memory issues

### Playbook Execution

- Validate playbooks before execution
- Use lazy loading for large playbooks
- Implement execution caching where appropriate

## Security Notes

### Configuration Files

- Store sensitive data in separate config files
- Use environment variables for passwords
- Set restrictive file permissions (600)

### Serial Communication

- Validate all input data
- Sanitize command strings
- Implement command whitelisting for production

## Troubleshooting

### Common Issues

**Permission Denied on Serial Port**
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

**Module Import Errors**
```bash
# Ensure virtual environment is activated
source seriallink-env/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

**Playbook Syntax Errors**
- Check for matching IF/ENDIF statements
- Verify command syntax
- Use verbose mode for detailed error messages

## Future Enhancements

### Planned Features

- SSH/Telnet support alongside serial
- Web interface for playbook management
- Device template system
- Parallel execution for multiple devices
- Integration with network management systems

### Architecture Improvements

- Plugin system for device types
- Configuration management API
- Real-time monitoring dashboard
- Automated testing framework
