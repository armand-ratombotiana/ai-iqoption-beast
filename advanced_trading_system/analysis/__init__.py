"""
Analysis module for technical indicators and market analysis

Updated to use TA-Lib (industry standard) for all technical indicators.
Maintains backward compatibility with existing code.
"""

# Try TA-Lib first (preferred), fallback to custom implementation
try:
    from .talib_indicators import TALibIndicators as TechnicalIndicators
    USING_TALIB = True
except ImportError:
    from .technical_indicators import TechnicalIndicators
    USING_TALIB = False

from .market_context import MarketContextAnalyzer

__all__ = ["TechnicalIndicators", "MarketContextAnalyzer", "USING_TALIB"]
