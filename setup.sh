#!/bin/bash
# SerialLink - Complete Setup & Validation Script
#
# This single script handles EVERYTHING for SerialLink:
# - Python environment validation & setup
# - Virtual environment creation & management
# - Dependency installation & verification
# - Configuration setup & validation
# - Comprehensive system testing
# - User guidance & troubleshooting
#
# Generated Scripts:
# - seriallink: Main launcher (auto-uses venv, no manual activation needed) - KEPT AFTER SETUP
# - activate_env.sh: Manual venv activation helper (for development) - REMOVED AFTER SETUP
# NOTE: Only the launcher script remains for convenient one-command usage
#
# Usage:
#     ./setup.sh [command] [options]
#
# Commands:
#     setup       Complete setup process (default)
#     validate    Run validation only
#     clean       Clean/reset environment and temporary files
#
# Options:
#     --force         Force recreate virtual environment
#     --python CMD    Specify Python command (default: python3)
#     --no-test       Skip comprehensive testing  
#     --minimal       Minimal setup (no extras)
#     --help          Show this help

# Change to script directory
cd "$(dirname "$0")"

# Configuration
VENV_NAME="seriallink-env"
PYTHON_CMD="python3"
FORCE_SETUP=false
SKIP_TESTING=false
MINIMAL_SETUP=false
COMMAND="setup"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YIGHLIGHT='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Error codes
readonly ERROR_PYTHON_NOT_FOUND=1
readonly ERROR_PYTHON_VERSION=2
readonly ERROR_VENV_MODULE=3
readonly ERROR_VENV_CREATION=4
readonly ERROR_DEPENDENCY_INSTALL=5
readonly ERROR_PROJECT_STRUCTURE=6
readonly ERROR_CONFIG_INVALID=7
readonly ERROR_MODULE_IMPORT=8
readonly ERROR_UNKNOWN_COMMAND=9
readonly ERROR_INVALID_ARGUMENT=10

# Status tracking
ERRORS=0
WARNINGS=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} ${BOLD}$1${NC}"
    [ -n "$2" ] && echo -e "${DIM}  $2${NC}"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} ${BOLD}$1${NC}"
    [ -n "$2" ] && echo -e "${DIM}  $2${NC}"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} ${BOLD}$1${NC}"
    [ -n "$2" ] && echo -e "${DIM}  $2${NC}"
    WARNINGS=$((WARNINGS + 1))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} ${BOLD}$1${NC}"
    [ -n "$2" ] && echo -e "${DIM}  $2${NC}"
    ERRORS=$((ERRORS + 1))
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Parse arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            setup|validate|clean)
                COMMAND="$1"
                shift
                ;;
            --force)
                FORCE_SETUP=true
                shift
                ;;
            --python)
                PYTHON_CMD="$2"
                shift 2
                ;;
            --no-test)
                SKIP_TESTING=true
                shift
                ;;
            --minimal)
                MINIMAL_SETUP=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit $ERROR_INVALID_ARGUMENT
                ;;
        esac
    done
}

show_help() {
    cat << 'EOF'
SerialLink - Smart Setup & Validation Script

This script intelligently checks what's needed and only installs missing components:
[OK] Python environment validation & setup
[OK] Virtual environment creation (only if missing/broken)
[OK] Dependency installation (only what's missing)
[OK] Configuration setup (only if missing)
[OK] Launcher script creation (only if missing/outdated)
[OK] Comprehensive system testing
[OK] User guidance & troubleshooting

Usage: ./setup.sh [command] [options]

Commands:
  setup       Smart setup - only install what's missing (default)
  validate    Run validation only  
  clean       Clean environment and temporary files

Options:
  --force         Force recreate virtual environment even if working
  --python CMD    Specify Python command (default: python3)
  --no-test       Skip comprehensive testing
  --minimal       Minimal setup (no extras)
  --help          Show this help

Examples:
  ./setup.sh                    # Smart setup (only missing components)
  ./setup.sh setup --force      # Force recreate environment
  ./setup.sh validate           # Validate existing setup
  ./setup.sh clean              # Clean environment and temp files
  ./setup.sh --python python3.11 # Use specific Python

After setup:
  ./seriallink --help           # Use SerialLink (launcher auto-handles venv)
  ./setup.sh validate           # Validate anytime
EOF
}

# Validation functions
validate_python() {
    log_info "Checking Python installation..."
    
    if ! command_exists "$PYTHON_CMD"; then
        log_warning "Python command '$PYTHON_CMD' not found, trying alternatives..."
        
        for cmd in python python3.12 python3.11 python3.10 python3.9 python3.8; do
            if command_exists "$cmd"; then
                PYTHON_CMD="$cmd"
                log_success "Found Python: $PYTHON_CMD"
                break
            fi
        done
        
        if ! command_exists "$PYTHON_CMD"; then
            log_error "No suitable Python installation found" "Install Python 3.8+ and try again"
            exit $ERROR_PYTHON_NOT_FOUND
        fi
    else
        log_success "Python command found: $PYTHON_CMD"
    fi
    
    # Check version
    log_info "Validating Python version..."
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    VERSION_CHECK=$($PYTHON_CMD -c "import sys; print(1 if sys.version_info >= (3, 8) else 0)" 2>/dev/null)
    
    if [ "$VERSION_CHECK" != "1" ]; then
        log_error "Python 3.8+ required" "Found: $PYTHON_VERSION"
        exit $ERROR_PYTHON_VERSION
    fi
    log_success "Python version compatible: $PYTHON_VERSION"
    
    # Check venv module
    log_info "Checking virtual environment support..."
    if ! $PYTHON_CMD -m venv --help >/dev/null 2>&1; then
        log_error "venv module not available" "Install python3-venv package"
        exit $ERROR_VENV_MODULE
    fi
    log_success "Virtual environment module available"
    
    return 0
}

validate_environment() {
    log_info "Validating virtual environment..."
    
    if [ ! -d "$VENV_NAME" ]; then
        log_error "Virtual environment not found" "Run: ./setup.sh setup"
        return 1
    fi
    
    if [ ! -f "$VENV_NAME/bin/python" ]; then
        log_error "Virtual environment Python not found" "Recreate with: ./setup.sh setup --force"
        return 1
    fi
    
    log_success "Virtual environment exists: $VENV_NAME"
    
    # Test activation
    local venv_version=$("$VENV_NAME/bin/python" --version 2>&1)
    log_success "Virtual environment Python: $venv_version"
    
    return 0
}

validate_dependencies() {
    log_info "Validating dependencies..."
    
    # Check requirements.txt
    if [ ! -f "requirements.txt" ]; then
        log_warning "requirements.txt not found" "Will use basic requirements"
    else
        log_success "requirements.txt found"
    fi
    
    # Test critical imports
    local import_errors=0
    
    if ! "$VENV_NAME/bin/python" -c "import serial" 2>/dev/null; then
        log_error "PySerial not available" "Install with: pip install pyserial"
        import_errors=$((import_errors + 1))
    else
        local serial_version=$("$VENV_NAME/bin/python" -c "import serial; print(serial.__version__)" 2>/dev/null)
        log_success "PySerial available: v$serial_version"
    fi
    
    if ! "$VENV_NAME/bin/python" -c "import tqdm" 2>/dev/null; then
        log_error "TQDM not available" "Install with: pip install tqdm"
        import_errors=$((import_errors + 1))
    else
        local tqdm_version=$("$VENV_NAME/bin/python" -c "import tqdm; print(tqdm.__version__)" 2>/dev/null)
        log_success "TQDM available: v$tqdm_version"
    fi
    
    return $import_errors
}

validate_project_structure() {
    log_info "Validating project structure..."
    
    local missing_files=0
    local required_files=("main.py" "config.ini.template")
    local required_dirs=("core" "utils" "config")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Required file missing: $file"
            missing_files=$((missing_files + 1))
        else
            log_success "Found: $file"
        fi
    done
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            log_error "Required directory missing: $dir"
            missing_files=$((missing_files + 1))
        else
            local py_files=$(find "$dir" -name "*.py" 2>/dev/null | wc -l)
            log_success "Found: $dir/ ($py_files Python files)"
        fi
    done
    
    return $missing_files
}

validate_configuration() {
    log_info "Validating configuration..."
    
    if [ ! -f "config.ini" ]; then
        if [ -f "config.ini.template" ]; then
            log_warning "config.ini not found" "Copy from config.ini.template"
        else
            log_error "No configuration files found" "config.ini.template missing"
            return 1
        fi
    else
        log_success "Configuration file exists: config.ini"
        
        # Test configuration loading
        if "$VENV_NAME/bin/python" -c "
import sys
sys.path.insert(0, '.')
try:
    from config.config_manager import ConfigManager
    from utils.logger import Logger
    logger = Logger(verbose=False, use_colors=False)
    config_manager = ConfigManager(logger)
    if config_manager.load_config('config.ini'):
        print('Configuration loaded successfully')
    else:
        sys.exit(1)
except Exception as e:
    print(f'Configuration error: {e}')
    sys.exit(1)
" 2>/dev/null; then
            log_success "Configuration loads correctly"
        else
            log_error "Configuration file invalid" "Check config.ini syntax"
            return 1
        fi
    fi
    
    return 0
}

validate_seriallink_modules() {
    log_info "Validating SerialLink modules..."
    
    local module_errors=0
    local modules=(
        "utils.logger:Logger"
        "utils.pagination:PaginationHandler" 
        "utils.output_processor:OutputProcessor"
        "core.prompt_detector:PromptDetector"
        "core.conditional_logic:ConditionalProcessor"
        "core.serial_handler:SerialHandler"
        "core.playbook_executor:PlaybookExecutor"
        "config.config_manager:ConfigManager"
    )
    
    for module_info in "${modules[@]}"; do
        local module_name="${module_info%:*}"
        local class_name="${module_info#*:}"
        
        if "$VENV_NAME/bin/python" -c "
import sys
sys.path.insert(0, '.')
try:
    module = __import__('$module_name', fromlist=['$class_name'])
    getattr(module, '$class_name')
except Exception as e:
    sys.exit(1)
" 2>/dev/null; then
            log_success "Module OK: $module_name"
        else
            log_error "Module failed: $module_name"
            module_errors=$((module_errors + 1))
        fi
    done
    
    return $module_errors
}

# Setup functions
setup_environment() {
    log_info "Checking virtual environment..."
    
    # Check if environment exists and is functional
    if [ -d "$VENV_NAME" ] && [ -f "$VENV_NAME/bin/python" ]; then
        # Test if the environment is working
        if "$VENV_NAME/bin/python" -c "import sys" 2>/dev/null; then
            local venv_version=$("$VENV_NAME/bin/python" --version 2>&1)
            if [ "$FORCE_SETUP" = true ]; then
                log_info "Removing existing virtual environment (--force used)..."
                rm -rf "$VENV_NAME"
                log_success "Existing environment removed"
            else
                log_success "Virtual environment already exists and working: $venv_version"
                return 0
            fi
        else
            log_warning "Virtual environment exists but is broken, recreating..."
            rm -rf "$VENV_NAME"
        fi
    fi
    
    # Create new environment only if needed
    log_info "Creating virtual environment '$VENV_NAME'..."
    if $PYTHON_CMD -m venv "$VENV_NAME" 2>&1; then
        log_success "Virtual environment created"
    else
        log_error "Failed to create virtual environment"
        exit $ERROR_VENV_CREATION
    fi
    
    # Upgrade pip
    log_info "Upgrading pip..."
    if "$VENV_NAME/bin/python" -m pip install --upgrade pip >/dev/null 2>&1; then
        log_success "pip upgraded"
    else
        log_warning "pip upgrade failed" "Continuing anyway"
    fi
    
    return 0
}

setup_dependencies() {
    log_info "Checking dependencies..."
    
    # Create requirements.txt if missing
    if [ ! -f "requirements.txt" ]; then
        log_info "Creating requirements.txt..."
        cat > requirements.txt << 'EOF'
pyserial>=3.5
tqdm>=4.60.0
EOF
        log_success "Basic requirements.txt created"
    fi
    
    # Check if dependencies are already installed and working
    local need_install=false
    
    # Make sure we have a working Python in venv first
    if [ ! -f "$VENV_NAME/bin/python" ]; then
        log_error "Virtual environment Python not found"
        exit $ERROR_VENV_CREATION
    fi
    
    if ! "$VENV_NAME/bin/python" -c "import serial" 2>/dev/null; then
        log_info "PySerial not found, will install"
        need_install=true
    else
        local serial_version=$("$VENV_NAME/bin/python" -c "import serial; print(serial.__version__)" 2>/dev/null)
        log_success "PySerial already available: v$serial_version"
    fi
    
    if ! "$VENV_NAME/bin/python" -c "import tqdm" 2>/dev/null; then
        log_info "TQDM not found, will install"
        need_install=true
    else
        local tqdm_version=$("$VENV_NAME/bin/python" -c "import tqdm; print(tqdm.__version__)" 2>/dev/null)
        log_success "TQDM already available: v$tqdm_version"
    fi
    
    # Only install if something is missing
    if [ "$need_install" = true ]; then
        log_info "Installing missing dependencies (this may take a moment)..."
        if "$VENV_NAME/bin/python" -m pip install -r requirements.txt >/dev/null 2>&1; then
            log_success "Dependencies installed"
        else
            log_error "Failed to install dependencies"
            exit $ERROR_DEPENDENCY_INSTALL
        fi
    else
        log_success "All dependencies already satisfied"
    fi
    
    return 0
}

setup_configuration() {
    log_info "Setting up configuration..."
    
    if [ ! -f "config.ini" ]; then
        if [ -f "config.ini.template" ]; then
            cp config.ini.template config.ini
            log_success "Configuration created from template"
        else
            log_warning "No template found, creating basic config"
            cat > config.ini << 'EOF'
[DEFAULT]
port = 
baudrate = 115200
username = 
password = 
playbook_file = playbook.txt
prompt_symbol = >
timeout = 10
enable_colors = true
enable_pagination = true

[LOGGING]
verbose = false
log_file = 

[ADVANCED]
initialization_delay = 2
command_delay = 1
success_message = SerialLink execution completed successfully!
EOF
            log_success "Basic configuration created"
        fi
    else
        log_success "Configuration file already exists"
    fi
    
    # Set permissions automatically - no manual intervention needed
    if chmod 600 config.ini 2>/dev/null; then
        log_success "Configuration permissions set securely"
    else
        log_warning "Could not set secure permissions on config.ini" "File is still usable"
    fi
    
    return 0
}

setup_scripts() {
    log_info "Checking launcher scripts..."
    
    local need_create=false
    
    # Check if main seriallink launcher exists and is correct
    if [ ! -f "seriallink" ] || ! grep -q "seriallink-env/bin/python main.py" seriallink 2>/dev/null; then
        need_create=true
        log_info "SerialLink launcher missing or outdated"
    else
        log_success "SerialLink launcher already exists"
    fi
    
    # Check if activation helper exists
    if [ ! -f "activate_env.sh" ] || ! grep -q "source seriallink-env/bin/activate" activate_env.sh 2>/dev/null; then
        need_create=true
        log_info "Activation helper missing or outdated"
    else
        log_success "Activation helper already exists"
    fi
    
    # Only create scripts if needed
    if [ "$need_create" = true ]; then
        log_info "Creating/updating launcher scripts..."
        
        # Main seriallink launcher
        cat > seriallink << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
if [ -d "seriallink-env" ] && [ -f "seriallink-env/bin/python" ]; then
    exec seriallink-env/bin/python main.py "$@"
else
    echo "Error: Environment not ready. Run: ./setup.sh setup"
    exit 1
fi
EOF
        if chmod +x seriallink 2>/dev/null; then
            log_success "SerialLink launcher created with execute permissions"
        else
            log_warning "Created SerialLink launcher but could not set execute permissions"
        fi
        
        # Environment activation helper
        cat > activate_env.sh << 'EOF'
#!/bin/bash
if [ -d "seriallink-env" ]; then
    source seriallink-env/bin/activate
    echo "SerialLink virtual environment activated"
    echo "Python: $(which python)"
    echo "To deactivate: deactivate"
else
    echo "Error: Environment not found. Run: ./setup.sh setup"
fi
EOF
        if chmod +x activate_env.sh 2>/dev/null; then
            log_success "Activation helper created with execute permissions"
        else
            log_warning "Created activation helper but could not set execute permissions"
        fi
        
        log_success "Launcher scripts created/updated"
    else
        log_success "All launcher scripts already up to date"
    fi
    
    return 0
}

# Cleanup function
cleanup_temporary_files() {
    local remove_generated_scripts="${1:-false}"
    log_info "Cleaning up temporary files..."
    
    local cleaned_count=0
    
    # Remove Python cache files
    if find . -name "__pycache__" -type d 2>/dev/null | grep -q .; then
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        log_success "Removed Python cache directories"
        cleaned_count=$((cleaned_count + 1))
    fi
    
    if find . -name "*.pyc" -type f 2>/dev/null | grep -q .; then
        find . -name "*.pyc" -type f -delete 2>/dev/null || true
        log_success "Removed Python compiled files (.pyc)"
        cleaned_count=$((cleaned_count + 1))
    fi
    
    if find . -name "*.pyo" -type f 2>/dev/null | grep -q .; then
        find . -name "*.pyo" -type f -delete 2>/dev/null || true
        log_success "Removed Python optimized files (.pyo)"
        cleaned_count=$((cleaned_count + 1))
    fi
    
    # Remove temporary files
    local temp_patterns=("*.tmp" "*.temp" "*~" ".DS_Store" "Thumbs.db" "*.log" "*.bak" "*.swp" "*.swo" "*.orig" "*.rej" ".*.swp" ".*.swo")
    for pattern in "${temp_patterns[@]}"; do
        if find . -name "$pattern" -type f 2>/dev/null | grep -q .; then
            find . -name "$pattern" -type f -delete 2>/dev/null || true
            log_success "Removed temporary files: $pattern"
            cleaned_count=$((cleaned_count + 1))
        fi
    done
    
    # Remove IDE and editor temporary files
    local ide_patterns=(".vscode/settings.json.bak" ".idea/*.tmp" "*.sublime-workspace" ".project" ".pydevproject")
    for pattern in "${ide_patterns[@]}"; do
        if find . -path "*$pattern" -type f 2>/dev/null | grep -q .; then
            find . -path "*$pattern" -type f -delete 2>/dev/null || true
            log_success "Removed IDE temporary files: $pattern"
            cleaned_count=$((cleaned_count + 1))
        fi
    done
    
    # Remove old setup/validation scripts that might exist (but keep useful generated scripts)
    local old_files=("validate" "test_setup.py" "run_tests.sh" "setup_env.sh" "update_shebangs.sh" "cleanup_old_scripts.sh" "setup_old.sh")
    for file in "${old_files[@]}"; do
        if [ -f "$file" ]; then
            rm -f "$file"
            log_success "Removed old script: $file"
            cleaned_count=$((cleaned_count + 1))
        fi
    done
    
    # Remove generated scripts if requested (only activate_env.sh for post-setup cleanup)
    if [ "$remove_generated_scripts" = true ]; then
        # Keep seriallink launcher but remove activation helper
        if [ -f "activate_env.sh" ]; then
            rm -f "activate_env.sh"
            log_success "Removed temporary script: activate_env.sh"
            cleaned_count=$((cleaned_count + 1))
        fi
        log_info "Launcher script preserved for convenient usage"
    fi
    
    # Clean up pip cache in virtual environment
    if [ -f "$VENV_NAME/bin/python" ]; then
        "$VENV_NAME/bin/python" -m pip cache purge >/dev/null 2>&1 || true
        log_success "Cleaned pip cache"
        cleaned_count=$((cleaned_count + 1))
    fi
    
    # Remove empty directories (except important ones)
    local protected_dirs=("core" "utils" "config" "docs" "examples" "tests" "$VENV_NAME")
    find . -type d -empty 2>/dev/null | while read -r empty_dir; do
        local should_keep=false
        for protected in "${protected_dirs[@]}"; do
            if [[ "$empty_dir" == *"$protected"* ]]; then
                should_keep=true
                break
            fi
        done
        if [ "$should_keep" = false ] && [ "$empty_dir" != "." ]; then
            rmdir "$empty_dir" 2>/dev/null || true
        fi
    done
    
    if [ $cleaned_count -eq 0 ]; then
        log_success "Workspace already clean"
    else
        log_success "Workspace cleanup complete ($cleaned_count items cleaned)"
    fi
    
    # Show protected directories and preserved files
    if [ "$remove_generated_scripts" = true ]; then
        log_info "Protected directories: core/, utils/, config/, docs/, tests/, $VENV_NAME/"
        log_info "Launcher script preserved - activation helper removed"
    else
        log_info "Protected: core/, utils/, config/, docs/, tests/, $VENV_NAME/"
        log_info "All generated scripts preserved"
    fi
    
    return 0
}

# Main command functions
cmd_setup() {
    echo -e "${CYAN}${BOLD}============================================================${NC}"
    echo -e "${CYAN}${BOLD}           SerialLink Smart Setup${NC}"
    echo -e "${CYAN}${BOLD}============================================================${NC}"
    echo -e "${DIM}Only installing/creating what's missing or broken${NC}"
    echo
    
    # Validate Python first
    validate_python || exit 1
    
    # Setup environment (only if needed)
    setup_environment || exit 1
    
    # Install dependencies (only if missing)
    setup_dependencies || exit 1
    
    # Setup configuration (only if missing)
    setup_configuration || exit 1
    
    # Create scripts (only if missing/outdated)
    setup_scripts || exit 1
    
    # Run validation unless skipped
    if [ "$SKIP_TESTING" != true ]; then
        echo
        log_info "Running comprehensive validation..."
        echo -e "${CYAN}===========================================${NC}"
        cmd_validate_internal
        echo -e "${CYAN}===========================================${NC}"
    fi
    
    # Cleanup workspace - remove ALL generated scripts and temporary files after setup
    echo
    cleanup_temporary_files true
    
    # Show final status
    show_final_status
}

cmd_validate() {
    echo -e "${CYAN}${BOLD}============================================================${NC}"
    echo -e "${CYAN}${BOLD}           SerialLink Validation${NC}"
    echo -e "${CYAN}${BOLD}============================================================${NC}"
    echo
    
    cmd_validate_internal
    show_final_status
}

cmd_validate_internal() {
    validate_python || return 1
    validate_environment || return 1  
    validate_dependencies || return 1
    validate_project_structure || return 1
    validate_configuration || return 1
    validate_seriallink_modules || return 1
    return 0
}

cmd_clean() {
    echo -e "${CYAN}${BOLD}============================================================${NC}"
    echo -e "${CYAN}${BOLD}           SerialLink Environment Cleanup${NC}"
    echo -e "${CYAN}${BOLD}============================================================${NC}"
    echo
    
    log_info "Cleaning SerialLink environment..."
    
    # Remove virtual environment
    if [ -d "$VENV_NAME" ]; then
        rm -rf "$VENV_NAME"
        log_success "Virtual environment removed"
    else
        log_info "No virtual environment to remove"
    fi
    
    # Remove generated scripts
    local scripts=("seriallink" "activate_env.sh")
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            rm -f "$script"
            log_success "Removed: $script"
        fi
    done
    
    # Remove any old test/validation scripts
    local old_scripts=("validate" "test_setup.py" "run_tests.sh" "setup_env.sh" "update_shebangs.sh" "cleanup_old_scripts.sh")
    for script in "${old_scripts[@]}"; do
        if [ -f "$script" ]; then
            rm -f "$script"
            log_success "Removed old script: $script"
        fi
    done
    
    log_success "Environment cleaned"
    
    # Also cleanup temporary files
    echo
    cleanup_temporary_files false
    
    echo
    echo -e "${GREEN}${BOLD}Environment and workspace cleanup complete!${NC}"
    echo -e "${DIM}Project is now clean and optimized${NC}"
    echo
    echo -e "${YELLOW}To set up again: ./setup.sh setup${NC}"
}

show_final_status() {
    echo
    echo -e "${BOLD}============================================================${NC}"
    
    # Status summary
    if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}${BOLD}Status: EXCELLENT${NC}"
    elif [ $ERRORS -eq 0 ]; then
        echo -e "${YELLOW}${BOLD}Status: GOOD${NC}"
        echo -e "SerialLink is functional with $WARNINGS warnings"
    fi
    
    echo -e "${BOLD}============================================================${NC}"
    echo
    
    if [ $ERRORS -eq 0 ]; then
        echo -e "${CYAN}${BOLD}Quick Commands:${NC}"
        echo -e "  • ${BOLD}Use SerialLink:${NC} ./seriallink --help"
        echo -e "  • ${BOLD}Validate setup:${NC} ./setup.sh validate"
        echo
        
        echo -e "${CYAN}${BOLD}Next Steps:${NC}"
        echo -e "  1. SerialLink is ready to use immediately!"
        echo -e "  2. Edit config.ini to set your device settings (port, username, etc.)"
        echo -e "  3. Connect your serial device"
        echo -e "  4. Create a playbook with your commands"
        echo -e "  5. Run: ./seriallink -u username --verbose"
        echo
    else
        echo -e "${YELLOW}${BOLD}Troubleshooting:${NC}"
        echo -e "  • Fix errors listed above"
        echo -e "  • Run: ./setup.sh validate"
        echo -e "  • Clean and retry: ./setup.sh clean && ./setup.sh setup"
        echo
    fi
}

# Main execution
main() {
    parse_arguments "$@"
    
    case "$COMMAND" in
        setup)
            cmd_setup
            ;;
        validate)
            cmd_validate
            ;;
        clean)
            cmd_clean
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            show_help
            exit $ERROR_UNKNOWN_COMMAND
            ;;
    esac
    
    exit $ERRORS
}

# Run main with all arguments
main "$@"
