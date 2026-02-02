"""
EchoLog Configuration Module
============================
Manages all configuration settings for the application.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def get_app_root() -> Path:
    """
    Get the application root directory.
    Works both in development and when packaged with PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled/packaged executable
        # sys.executable is the path to the EXE file
        return Path(sys.executable).parent
    else:
        # Running in development
        return Path(__file__).parent


# Application root directory
APP_ROOT = get_app_root()

# Load environment variables from .env file
# Try to load from app root first (for packaged app)
env_path = APP_ROOT / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # Fall back to default behavior


# ========================================
# Environment Configuration
# ========================================
class Environment:
    """Environment settings"""
    CURRENT = os.getenv("ENVIRONMENT", "dev")
    IS_DEV = CURRENT == "dev"
    IS_TEST = CURRENT == "test"
    IS_PROD = CURRENT == "prod"


# ========================================
# API Configuration
# ========================================
class DeepgramConfig:
    """Deepgram API configuration"""
    API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
    
    # WebSocket endpoint
    WEBSOCKET_URL = "wss://api.deepgram.com/v1/listen"
    
    # Model settings
    MODEL = "nova-2"
    LANGUAGE = "zh"  # Chinese
    
    # Streaming options
    PUNCTUATE = True
    INTERIM_RESULTS = True
    ENDPOINTING = 300  # milliseconds
    
    @classmethod
    def get_ws_url(cls) -> str:
        """Build the WebSocket URL with query parameters"""
        params = [
            f"model={cls.MODEL}",
            f"language={cls.LANGUAGE}",
            f"punctuate={str(cls.PUNCTUATE).lower()}",
            f"interim_results={str(cls.INTERIM_RESULTS).lower()}",
            f"endpointing={cls.ENDPOINTING}",
            "encoding=linear16",
            f"sample_rate={AudioConfig.SAMPLE_RATE}",
            f"channels={AudioConfig.CHANNELS}",
        ]
        return f"{cls.WEBSOCKET_URL}?{'&'.join(params)}"


# ========================================
# Audio Configuration
# ========================================
class AudioConfig:
    """Audio capture configuration (as per PRD)"""
    SAMPLE_RATE = 16000      # Hz - required by Deepgram
    CHANNELS = 1             # Mono
    DTYPE = "int16"          # Linear16 format
    BLOCK_SIZE = 4000        # Samples per block (~250ms at 16kHz)
    

# ========================================
# File Output Configuration
# ========================================
class OutputConfig:
    """Output file configuration"""
    # Base directory for output files
    # Uses APP_ROOT to work correctly when packaged with PyInstaller
    OUTPUT_DIR = APP_ROOT / "output"
    
    # File naming
    FILE_PREFIX = "echolog"
    FILE_EXTENSION = ".md"
    
    # Timestamp format for filenames
    FILENAME_TIME_FORMAT = "%Y%m%d_%H%M%S"
    
    # Timestamp format for content (optional inline timestamps)
    CONTENT_TIME_FORMAT = "[%H:%M:%S]"
    
    # Whether to include timestamps in the output
    INCLUDE_TIMESTAMPS = True
    
    @classmethod
    def ensure_output_dir(cls) -> Path:
        """Ensure the output directory exists"""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return cls.OUTPUT_DIR


# ========================================
# GUI Configuration
# ========================================
class GUIConfig:
    """GUI appearance configuration"""
    WINDOW_TITLE = "EchoLog - 智能听写助手"
    WINDOW_SIZE = "800x600"
    MIN_WIDTH = 600
    MIN_HEIGHT = 400
    
    # Theme
    APPEARANCE_MODE = "dark"  # "dark", "light", or "system"
    COLOR_THEME = "blue"
    
    # Text display
    FONT_FAMILY = "Microsoft YaHei"  # 微软雅黑 for Chinese support
    FONT_SIZE = 14
    
    # Status colors
    COLOR_RECORDING = "#FF4444"   # Red when recording
    COLOR_IDLE = "#44FF44"        # Green when idle
    COLOR_INTERIM = "#888888"     # Gray for interim text


# ========================================
# Validation
# ========================================
def validate_config() -> bool:
    """
    Validate critical configuration.
    Returns True if valid, raises exception otherwise.
    """
    if not DeepgramConfig.API_KEY or DeepgramConfig.API_KEY == "your_deepgram_api_key_here":
        if Environment.IS_PROD:
            raise ValueError("DEEPGRAM_API_KEY is required in production!")
        else:
            print("⚠️ Warning: DEEPGRAM_API_KEY is not set. Please update your .env file.")
            return False
    return True


# Run validation on import (in non-test environments)
if not Environment.IS_TEST:
    validate_config()
