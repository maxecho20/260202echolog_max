"""
EchoLog GUI - Windows Version
=============================
Windows-specific GUI implementation with proper font and path handling.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import and run main app
from main_gui import main

if __name__ == "__main__":
    main()
