"""
Logging and output formatting utilities for the Mellanox device updater.

This module provides comprehensive logging functionality including:
- Colored console output with different message types
- Progress tracking and status reporting
- Verbose and non-verbose modes
- Background progress bar support with tqdm
"""

import sys
from typing import Optional

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class Colors:
    """ANSI color codes for console output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class Logger:
    """Handles all logging and output formatting for the application."""
    
    def __init__(self, verbose: bool = False, use_colors: bool = True):
        """
        Initialize the logger.
        
        Args:
            verbose: Whether to run in verbose mode
            use_colors: Whether to use colored output
        """
        self.verbose_mode = verbose
        self.use_colors = use_colors
        self.colors = Colors() if use_colors else self._create_no_color_class()
        self.progress_bar = None
        
    def _create_no_color_class(self):
        """Create a no-color version of the Colors class."""
        class NoColors:
            GREEN = RED = YELLOW = BLUE = CYAN = WHITE = BOLD = END = ''
        return NoColors()
    
    def _write_above_progress_bar(self, message: str):
        """Write a message above the progress bar in verbose mode."""
        if self.progress_bar and self.verbose_mode:
            # Clear the progress bar, write message on new line, then refresh
            self.progress_bar.clear()
            print(message)
            sys.stdout.flush()
            self.progress_bar.refresh()
        else:
            print(message, flush=True)
    
    def log_info(self, message: str):
        """Print an informational message in blue."""
        if self.verbose_mode:
            msg = f"{self.colors.BLUE}[INFO]{self.colors.END} {message}"
            self._write_above_progress_bar(msg)
    
    def log_success(self, message: str):
        """Print a success message in green."""
        if self.verbose_mode:
            msg = f"{self.colors.GREEN}[OK]{self.colors.END} {message}"
            self._write_above_progress_bar(msg)
        # In non-verbose mode, only show critical success messages
        elif any(key in message for key in ["Serial port opened successfully", 
                                          "Playbook completed successfully", 
                                          "Configuration loaded successfully"]):
            if self.progress_bar:
                self.progress_bar.write(f"{self.colors.GREEN}[OK]{self.colors.END} {message}")
            else:
                print(f"{self.colors.GREEN}[OK]{self.colors.END} {message}")
    
    def log_warning(self, message: str):
        """Print a warning message in yellow."""
        if self.verbose_mode:
            msg = f"{self.colors.YELLOW}[WARN]{self.colors.END} {message}"
            self._write_above_progress_bar(msg)
        # In non-verbose mode, always show warnings as they might be important
        elif self.progress_bar:
            self.progress_bar.write(f"{self.colors.YELLOW}[WARN]{self.colors.END} {message}")
        else:
            print(f"{self.colors.YELLOW}[WARN]{self.colors.END} {message}")
    
    def log_error(self, message: str):
        """Print an error message in red."""
        # Always show errors regardless of mode
        msg = f"{self.colors.RED}[ERROR]{self.colors.END} {message}"
        if self.progress_bar:
            self.progress_bar.write(msg)
        else:
            print(msg)
    
    def log_debug(self, message: str):
        """Print a debug message in cyan."""
        if self.verbose_mode:
            msg = f"{self.colors.CYAN}[DEBUG]{self.colors.END} {message}"
            self._write_above_progress_bar(msg)
    
    def log_section(self, message: str):
        """Print a section header."""
        if self.verbose_mode:
            section_msg = f"\n{self.colors.BOLD}{self.colors.WHITE}[SECTION]{self.colors.END} {message}"
            divider = "-" * (len(message) + 10)
            self._write_above_progress_bar(section_msg)
            self._write_above_progress_bar(divider)
    
    def log_command_execution(self, action: str, command: str = "", step_num: int = 0):
        """Log command execution with clean formatting."""
        if self.verbose_mode:
            if command:
                msg = f"{self.colors.CYAN}[CMD]{self.colors.END} {action}: {command}"
            else:
                msg = f"{self.colors.CYAN}[ACTION]{self.colors.END} {action}"
            self._write_above_progress_bar(msg)
        else:
            # Non-verbose: Update progress bar description to show current action
            if self.progress_bar:
                self.progress_bar.set_description(action)
    
    def log_command_success(self, action: str, command: str = ""):
        """Log successful command/action completion."""
        if self.verbose_mode:
            if command:
                msg = f"{self.colors.GREEN}[OK]{self.colors.END} {action}: {command}"
            else:
                msg = f"{self.colors.GREEN}[OK]{self.colors.END} {action}"
            self._write_above_progress_bar(msg)
        # In non-verbose mode: Don't show individual command success messages
        # The progress bar will show overall progress
    
    def log_output(self, output: str):
        """Log command output."""
        if self.verbose_mode and output.strip():
            output_msg = f"{self.colors.WHITE}Output:{self.colors.END}"
            self._write_above_progress_bar(output_msg)
            for line in output.split('\n'):
                if line.strip():
                    self._write_above_progress_bar(f"  {line}")
            self._write_above_progress_bar("")  # Add spacing after output
    
    def create_progress_bar(self, total: int, description: str = "Processing") -> Optional[object]:
        """Create and return a progress bar instance."""
        if TQDM_AVAILABLE:
            self.progress_bar = tqdm(
                total=total,
                desc=description,
                unit="step",
                bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]',
                ncols=80,
                leave=True,
                file=sys.stdout,
                dynamic_ncols=False,
                position=0,  # Ensure progress bar stays at bottom
                ascii=False  # Use unicode characters for better display
            )
            return self.progress_bar
        return None
    
    def update_progress(self, description: Optional[str] = None):
        """Update progress bar with optional description."""
        if self.progress_bar:
            if description:
                self.progress_bar.set_description(description)
            self.progress_bar.update(1)
    
    def update_progress_description(self, description: str):
        """Update just the progress bar description."""
        if self.progress_bar:
            self.progress_bar.set_description(description)
    
    def show_progress(self, current: int, total: int, description: str = "Processing"):
        """Show or update progress display."""
        if not self.progress_bar and TQDM_AVAILABLE:
            self.create_progress_bar(total, description)
        elif self.progress_bar:
            self.progress_bar.set_description(description)
            # Update to current position if behind
            if current > self.progress_bar.n:
                self.progress_bar.update(current - self.progress_bar.n)
    
    def close_progress_bar(self):
        """Close the progress bar if it exists."""
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None
    
    def set_progress_bar(self, progress_bar):
        """Set the progress bar instance for coordinated output."""
        self.progress_bar = progress_bar


# Legacy function support for backward compatibility
_global_logger = None

def get_global_logger():
    """Get or create the global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger()
    return _global_logger

def set_verbose_mode(verbose: bool):
    """Set verbose mode on the global logger."""
    logger = get_global_logger()
    logger.verbose_mode = verbose

def log_info(message: str):
    """Legacy function - use Logger class instead."""
    get_global_logger().log_info(message)

def log_success(message: str):
    """Legacy function - use Logger class instead."""
    get_global_logger().log_success(message)

def log_warning(message: str):
    """Legacy function - use Logger class instead."""
    get_global_logger().log_warning(message)

def log_error(message: str):
    """Legacy function - use Logger class instead."""
    get_global_logger().log_error(message)

def log_debug(message: str):
    """Legacy function - use Logger class instead."""
    get_global_logger().log_debug(message)

def log_section(message: str):
    """Legacy function - use Logger class instead."""
    get_global_logger().log_section(message)
