"""
Utility functions for the EDI service.
"""

import os
import logging
from typing import Optional


def setup_logging(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Set up logging for a module.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (defaults to EDI_LOG_LEVEL env var or INFO)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Set log level
        log_level = level or os.getenv("EDI_LOG_LEVEL", "INFO")
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(logger.level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get boolean value from environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        
    Returns:
        Boolean value
    """
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """
    Get integer value from environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        
    Returns:
        Integer value
    """
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_str(key: str, default: str = "") -> str:
    """
    Get string value from environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        
    Returns:
        String value
    """
    return os.getenv(key, default)
