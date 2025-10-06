"""
Multi-Data Provider System
Integrates multiple data sources for robust market data
"""

from .base_provider import BaseDataProvider
from .iqoption_provider import IQOptionProvider
from .multi_provider import MultiDataProvider

__all__ = [
    'BaseDataProvider',
    'IQOptionProvider', 
    'MultiDataProvider'
]