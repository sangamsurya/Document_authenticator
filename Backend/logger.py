import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional
import sys

class Logger:
    """
    A custom logger class that provides advanced logging features including:
    - Log rotation
    - Different log levels for different environments
    - Custom log formatting
    - Console and file logging
    """
    
    def __init__(self, 
                 name: str = "steganography",
                 log_dir: str = "logs",
                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 level: int = logging.INFO):
        """
        Initialize the logger.
        
        Args:
            name: Name of the logger
            log_dir: Directory to store log files
            max_bytes: Maximum size of each log file
            backup_count: Number of backup files to keep
            level: Default logging level
        """
        self.name = name
        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.level = level
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add handlers
        self._add_console_handler()
        self._add_file_handler()
        
        # Set up exception hook
        sys.excepthook = self._handle_exception

    def _add_console_handler(self) -> None:
        """Add console handler with colored output."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        
        # Create formatter with colors
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self) -> None:
        """Add rotating file handler."""
        log_file = os.path.join(self.log_dir, f"{self.name}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        file_handler.setLevel(self.level)
        
        # Create formatter
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def _handle_exception(self, exc_type, exc_value, exc_traceback) -> None:
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        self.logger.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Log exception message."""
        self.logger.exception(message, *args, **kwargs)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[41m',  # Red background
        'RESET': '\033[0m'       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        # Add color to the level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

# Create a global logger instance
logger = Logger()

# Example usage:
if __name__ == "__main__":
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    try:
        1/0
    except Exception as e:
        logger.exception("This is an exception message") 