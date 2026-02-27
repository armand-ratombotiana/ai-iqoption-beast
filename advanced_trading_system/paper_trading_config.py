"""
Paper Trading Configuration
Settings for automated demo trading with validation and monitoring

This configuration is optimized for:
- Safe demo account testing
- Comprehensive metrics collection
- Signal validation against TradingView
- Win rate measurement
"""

import os

# ============================================================================
# PAPER TRADING SETTINGS
# ============================================================================

PAPER_TRADING_CONFIG = {
    # Safety Settings
    'ACCOUNT_TYPE': 'demo',  # CRITICAL: Always use demo for paper trading
    'MAX_DAILY_TRADES': 50,  # Limit trades per day for testing
    'MAX_CONCURRENT_TRADES': 3,  # Maximum open positions at once

    # Trading Parameters
    'TRADE_AMOUNT': 2.0,  # $2 per trade (conservative)
    'TRADE_DURATION': 1,  # 1 minute (most common for binary options)

    # Risk Management
    'MAX_DAILY_LOSS': 20.0,  # Stop trading after $20 loss
    'MAX_DAILY_PROFIT': 100.0,  # Stop trading after $100 profit (take profits)
    'MAX_CONSECUTIVE_LOSSES': 3,  # Pause after 3 losses in a row

    # Signal Requirements (Conservative)
    'MIN_CONFIDENCE': 70,  # Minimum 70% confidence to trade
    'REQUIRE_MULTIPLE_INDICATORS': True,  # Need 2+ indicators to agree
    'MIN_INDICATOR_AGREEMENT': 2,  # At least 2 indicators must agree

    # Validation Settings
    'COMPARE_WITH_TRADINGVIEW': True,  # Compare our signals with TradingView
    'LOG_ALL_SIGNALS': True,  # Log even signals we don't trade
    'TRACK_INDICATOR_ACCURACY': True,  # Track which indicators perform best

    # Monitoring
    'ENABLE_DASHBOARD': True,  # Real-time monitoring dashboard
    'DASHBOARD_UPDATE_INTERVAL': 5,  # Update every 5 seconds
    'SAVE_TRADE_HISTORY': True,  # Save all trades to database

    # Testing Duration
    'TARGET_TRADE_COUNT': 100,  # Stop after 100 trades
    'MAX_TESTING_DAYS': 7,  # Maximum 7 days of testing
}

# ============================================================================
# CURRENCY PAIRS FOR TESTING
# ============================================================================

# Start with most liquid pairs (best spreads, most predictable)
TESTING_PAIRS = [
    'EURUSD-OTC',  # Most liquid forex pair
    'GBPUSD-OTC',  # Second most liquid
    'USDJPY-OTC',  # Major pair with good volatility
]

# Add more pairs after validating with top 3
ADDITIONAL_PAIRS = [
    'AUDUSD-OTC',
    'USDCAD-OTC',
    'EURJPY-OTC',
    'GBPJPY-OTC',
]

# ============================================================================
# INDICATOR SETTINGS (Using TA-Lib)
# ============================================================================

INDICATOR_CONFIG = {
    'RSI': {
        'period': 14,
        'overbought': 70,
        'oversold': 30,
        'weight': 1.0,  # Indicator weight in consensus
    },
    'MACD': {
        'fast': 12,
        'slow': 26,
        'signal': 9,
        'weight': 1.2,  # Slightly higher weight (reliable)
    },
    'STOCHASTIC': {
        'k_period': 14,
        'd_period': 3,
        'overbought': 80,
        'oversold': 20,
        'weight': 0.9,
    },
    'ADX': {
        'period': 14,
        'min_trend_strength': 25,  # Only trade when ADX > 25
        'weight': 1.1,
    },
    'BOLLINGER_BANDS': {
        'period': 20,
        'std_dev': 2,
        'weight': 1.0,
    },
}

# ============================================================================
# SIGNAL GENERATION RULES
# ============================================================================

SIGNAL_RULES = {
    # RSI Rules
    'RSI_OVERSOLD_CALL': {
        'condition': 'RSI < 30',
        'signal': 'CALL',
        'confidence_boost': 10,
    },
    'RSI_OVERBOUGHT_PUT': {
        'condition': 'RSI > 70',
        'signal': 'PUT',
        'confidence_boost': 10,
    },

    # MACD Rules
    'MACD_BULLISH_CROSS': {
        'condition': 'MACD crosses above Signal',
        'signal': 'CALL',
        'confidence_boost': 15,
    },
    'MACD_BEARISH_CROSS': {
        'condition': 'MACD crosses below Signal',
        'signal': 'PUT',
        'confidence_boost': 15,
    },

    # Trend Confirmation
    'ADX_STRONG_TREND': {
        'condition': 'ADX > 25',
        'confidence_boost': 10,  # Boost any signal in strong trend
    },
    'ADX_WEAK_TREND': {
        'condition': 'ADX < 20',
        'confidence_penalty': 20,  # Reduce confidence in ranging market
    },

    # Bollinger Bands
    'BB_LOWER_BAND_CALL': {
        'condition': 'Price at lower band',
        'signal': 'CALL',
        'confidence_boost': 8,
    },
    'BB_UPPER_BAND_PUT': {
        'condition': 'Price at upper band',
        'signal': 'PUT',
        'confidence_boost': 8,
    },
}

# ============================================================================
# LOGGING AND REPORTING
# ============================================================================

LOGGING_CONFIG = {
    'LOG_FILE': 'logs/paper_trading.log',
    'LOG_LEVEL': 'INFO',
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    # Database for trade history
    'DB_PATH': 'data/paper_trading.db',

    # CSV exports for analysis
    'EXPORT_CSV': True,
    'CSV_PATH': 'data/paper_trades.csv',

    # Screenshots of signals (optional)
    'SAVE_SCREENSHOTS': False,
}

# ============================================================================
# METRICS TO TRACK
# ============================================================================

METRICS_CONFIG = {
    'track': [
        'total_trades',
        'winning_trades',
        'losing_trades',
        'win_rate',
        'profit_loss',
        'roi_percentage',
        'avg_profit_per_trade',
        'max_consecutive_wins',
        'max_consecutive_losses',
        'max_drawdown',
        'sharpe_ratio',

        # Per-indicator metrics
        'rsi_accuracy',
        'macd_accuracy',
        'stochastic_accuracy',
        'adx_accuracy',

        # Per-pair metrics
        'eurusd_win_rate',
        'gbpusd_win_rate',
        'usdjpy_win_rate',

        # Time-based metrics
        'best_hour',
        'worst_hour',
        'best_day',
        'worst_day',
    ],

    # Report generation
    'GENERATE_DAILY_REPORT': True,
    'GENERATE_FINAL_REPORT': True,
    'REPORT_PATH': 'reports/paper_trading/',
}

# ============================================================================
# VALIDATION CRITERIA
# ============================================================================

VALIDATION_CRITERIA = {
    # Minimum success thresholds
    'MIN_WIN_RATE': 55.0,  # Must achieve 55%+ win rate (profitable at 80% payout)
    'MIN_TRADES': 100,  # At least 100 trades for statistical significance
    'MAX_DRAWDOWN': 30.0,  # Maximum $30 drawdown allowed

    # Indicator validation
    'MIN_INDICATOR_ACCURACY': 50.0,  # Each indicator should be >50% accurate

    # Consistency requirements
    'MAX_VARIANCE': 10.0,  # Win rate shouldn't vary more than 10% between pairs

    # Signal quality
    'MIN_SIGNALS_PER_DAY': 10,  # Should generate at least 10 signals daily
    'MAX_SIGNALS_PER_DAY': 100,  # But not too many (avoid overtrading)
}

# ============================================================================
# SAFETY LIMITS
# ============================================================================

SAFETY_LIMITS = {
    # Emergency stops
    'EMERGENCY_STOP_LOSS': 50.0,  # Hard stop at $50 loss
    'EMERGENCY_STOP_ENABLED': True,

    # Connection monitoring
    'MAX_CONNECTION_FAILURES': 3,  # Stop after 3 connection failures
    'CONNECTION_TIMEOUT': 30,  # 30 seconds timeout

    # Data validation
    'REQUIRE_MINIMUM_CANDLES': 100,  # Need at least 100 candles for analysis
    'MAX_DATA_AGE': 60,  # Data must be less than 60 seconds old

    # Trading hours (optional)
    'TRADING_HOURS_START': None,  # 24/7 testing (or set to hour, e.g., 8)
    'TRADING_HOURS_END': None,  # 24/7 testing (or set to hour, e.g., 18)
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_config():
    """Get complete paper trading configuration"""
    return {
        'trading': PAPER_TRADING_CONFIG,
        'pairs': TESTING_PAIRS,
        'indicators': INDICATOR_CONFIG,
        'signal_rules': SIGNAL_RULES,
        'logging': LOGGING_CONFIG,
        'metrics': METRICS_CONFIG,
        'validation': VALIDATION_CRITERIA,
        'safety': SAFETY_LIMITS,
    }

def validate_config():
    """Validate configuration is safe for paper trading"""
    # Check account type
    if PAPER_TRADING_CONFIG['ACCOUNT_TYPE'] != 'demo':
        print("ERROR: Paper trading must use 'demo' account!")
        return False

    # Check trade amount is reasonable
    if PAPER_TRADING_CONFIG['TRADE_AMOUNT'] > 10.0:
        print("WARNING: Trade amount > $10 is high for paper trading")

    # Check safety limits are enabled
    if not SAFETY_LIMITS['EMERGENCY_STOP_ENABLED']:
        print("WARNING: Emergency stop is disabled!")

    return True

def get_testing_summary():
    """Get summary of testing configuration"""
    monitoring = 'Enabled' if PAPER_TRADING_CONFIG['ENABLE_DASHBOARD'] else 'Disabled'
    return """
Paper Trading Configuration Summary:
=====================================
Account Type: %s
Trade Amount: $%.2f
Duration: %d minute(s)
Target Trades: %d
Testing Pairs: %d (%s)

Risk Management:
- Max Daily Loss: $%.2f
- Max Daily Profit: $%.2f
- Max Consecutive Losses: %d

Validation Criteria:
- Minimum Win Rate: %.1f%%
- Minimum Trades: %d
- Max Drawdown: $%.2f

Indicators: RSI, MACD, Stochastic, ADX, Bollinger Bands (TA-Lib)
Monitoring: %s
""" % (
        PAPER_TRADING_CONFIG['ACCOUNT_TYPE'],
        PAPER_TRADING_CONFIG['TRADE_AMOUNT'],
        PAPER_TRADING_CONFIG['TRADE_DURATION'],
        PAPER_TRADING_CONFIG['TARGET_TRADE_COUNT'],
        len(TESTING_PAIRS),
        ', '.join(TESTING_PAIRS),
        PAPER_TRADING_CONFIG['MAX_DAILY_LOSS'],
        PAPER_TRADING_CONFIG['MAX_DAILY_PROFIT'],
        PAPER_TRADING_CONFIG['MAX_CONSECUTIVE_LOSSES'],
        VALIDATION_CRITERIA['MIN_WIN_RATE'],
        VALIDATION_CRITERIA['MIN_TRADES'],
        VALIDATION_CRITERIA['MAX_DRAWDOWN'],
        monitoring
    )


if __name__ == '__main__':
    print("="*70)
    print("PAPER TRADING CONFIGURATION")
    print("="*70)

    # Validate config
    if validate_config():
        print("Configuration validated successfully!")
        print(get_testing_summary())
    else:
        print("Configuration validation FAILED!")

    print("="*70)
