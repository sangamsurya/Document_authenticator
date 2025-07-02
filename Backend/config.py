import os
from typing import Dict, Any, Optional
from pathlib import Path
import json
from logger import logger

class Config:
    """
    Configuration manager for the steganography application.
    Handles settings from environment variables, config files, and defaults.
    """
    
    # Default configuration
    DEFAULT_CONFIG = {
        # Application settings
        "APP_NAME": "Steganography API",
        "APP_VERSION": "1.0.0",
        "DEBUG": False,
        "HOST": "0.0.0.0",
        "PORT": 5000,
        
        # File settings
        "MAX_FILE_SIZE": 10 * 1024 * 1024,  # 10MB
        "ALLOWED_IMAGE_EXTENSIONS": {"png", "jpg", "jpeg"},
        "ALLOWED_AUDIO_EXTENSIONS": {"wav"},
        "UPLOAD_FOLDER": "uploads",
        "OUTPUT_FOLDER": "output",
        
        # Database settings
        "MONGODB_URI": "mongodb://localhost:27017/",
        "DB_NAME": "steganography_db",
        "COLLECTION_NAME": "audio_fingerprints",
        
        # Audio settings
        "MIN_FRAME_RATE": 8000,
        "MAX_FRAME_RATE": 48000,
        "MAX_AUDIO_DURATION": 300,  # seconds
        
        # Logging settings
        "LOG_LEVEL": "INFO",
        "LOG_DIR": "logs",
        "LOG_MAX_BYTES": 10 * 1024 * 1024,  # 10MB
        "LOG_BACKUP_COUNT": 5,
        
        # Security settings
        "SECRET_KEY": "your-secret-key-here",
        "API_KEY_HEADER": "X-API-Key",
        "RATE_LIMIT": "100 per minute",
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_file = config_file
        
        # Load configuration from file if provided
        if config_file:
            self.load_config_file(config_file)
        
        # Override with environment variables
        self.load_environment_variables()
        
        # Create necessary directories
        self._create_directories()
        
        # Validate configuration
        self.validate()

    def load_config_file(self, config_file: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                self.config.update(file_config)
            logger.info(f"Loaded configuration from {config_file}")
        except FileNotFoundError:
            logger.warning(f"Configuration file {config_file} not found, using defaults")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing configuration file: {str(e)}")
            raise ValueError(f"Invalid configuration file format: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading configuration file: {str(e)}")
            raise Exception(f"Failed to load configuration file: {str(e)}")

    def load_environment_variables(self) -> None:
        """
        Load configuration from environment variables.
        Environment variables should be prefixed with 'STEGO_'.
        """
        for key in self.config:
            env_key = f"STEGO_{key}"
            if env_key in os.environ:
                value = os.environ[env_key]
                # Convert string values to appropriate types
                if key in {"DEBUG", "MAX_FILE_SIZE", "MIN_FRAME_RATE", 
                          "MAX_FRAME_RATE", "MAX_AUDIO_DURATION", "PORT",
                          "LOG_MAX_BYTES", "LOG_BACKUP_COUNT"}:
                    value = int(value)
                elif key in {"ALLOWED_IMAGE_EXTENSIONS", "ALLOWED_AUDIO_EXTENSIONS"}:
                    value = set(value.split(","))
                self.config[key] = value
                logger.debug(f"Loaded {key} from environment variable")

    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.config["UPLOAD_FOLDER"],
            self.config["OUTPUT_FOLDER"],
            self.config["LOG_DIR"]
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")

    def validate(self) -> None:
        """Validate the configuration."""
        try:
            # Validate file paths
            for path in [self.config["UPLOAD_FOLDER"], 
                        self.config["OUTPUT_FOLDER"], 
                        self.config["LOG_DIR"]]:
                if not os.path.exists(path):
                    raise ValueError(f"Directory does not exist: {path}")
            
            # Validate numeric values
            if self.config["MAX_FILE_SIZE"] <= 0:
                raise ValueError("MAX_FILE_SIZE must be positive")
            if self.config["MIN_FRAME_RATE"] <= 0:
                raise ValueError("MIN_FRAME_RATE must be positive")
            if self.config["MAX_FRAME_RATE"] <= self.config["MIN_FRAME_RATE"]:
                raise ValueError("MAX_FRAME_RATE must be greater than MIN_FRAME_RATE")
            if self.config["MAX_AUDIO_DURATION"] <= 0:
                raise ValueError("MAX_AUDIO_DURATION must be positive")
            
            # Validate file extensions
            if not self.config["ALLOWED_IMAGE_EXTENSIONS"]:
                raise ValueError("ALLOWED_IMAGE_EXTENSIONS cannot be empty")
            if not self.config["ALLOWED_AUDIO_EXTENSIONS"]:
                raise ValueError("ALLOWED_AUDIO_EXTENSIONS cannot be empty")
            
            logger.info("Configuration validation successful")
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise ValueError(f"Invalid configuration: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        logger.debug(f"Set configuration {key} = {value}")

    def save(self, config_file: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config_file: Path to save configuration (optional)
        """
        if config_file is None:
            config_file = self.config_file
        if config_file is None:
            raise ValueError("No configuration file specified")
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Saved configuration to {config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            raise Exception(f"Failed to save configuration: {str(e)}")

    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dictionary syntax."""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value using dictionary syntax."""
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        """Check if configuration key exists."""
        return key in self.config

# Create a global configuration instance
config = Config() 