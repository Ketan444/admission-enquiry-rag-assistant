import logging
import sys
import os
from config.settings import settings

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter to colorize logs for CLI and file."""
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;20m"
    cyan = "\x1b[36;20m"
    reset = "\x1b[0m"
    format_str = "[%(asctime)s] %(levelname)-8s %(name)s:%(filename)s:%(lineno)d - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.format_str)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()
        
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # File Handler
    file_handler = logging.FileHandler(os.path.join("logs", "app.log"), encoding="utf-8")
    file_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s:%(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

# Root logger
app_logger = setup_logger("admission_assistant")
