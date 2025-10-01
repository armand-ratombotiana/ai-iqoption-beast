#!/usr/bin/env python3
"""
Main entry point for IQOption AI Trading Bot API
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.app import create_app
from src.utils.config import Config

if __name__ == '__main__':
    # Create application
    config = Config()
    app = create_app(config)

    # Run server
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'true').lower() == 'true'
    )
