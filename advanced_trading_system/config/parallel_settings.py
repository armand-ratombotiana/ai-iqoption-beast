"""
Parallel Trading Configuration
Extended settings for parallel trading operations
"""
import os
from config.settings import TradingConfig


class ParallelTradingConfig(TradingConfig):
    """Extended configuration for parallel trading"""
    
    # Parallel Trading Settings
    MAX_CONCURRENT_PAIRS = int(os.getenv('MAX_CONCURRENT_PAIRS', '5'))
    MIN_PAYOUT_THRESHOLD = float(os.getenv('MIN_PAYOUT_THRESHOLD', '0.75'))
    MAX_PAIRS_TO_ANALYZE = int(os.getenv('MAX_PAIRS_TO_ANALYZE', '20'))
    
    # Risk Management
    BALANCE_ALLOCATION_PER_TRADE = float(os.getenv('BALANCE_ALLOCATION_PER_TRADE', '0.02'))  # 2%
    TOTAL_RISK_BUDGET = float(os.getenv('TOTAL_RISK_BUDGET', '0.10'))  # 10%
    CORRELATION_THRESHOLD = float(os.getenv('CORRELATION_THRESHOLD', '0.7'))
    
    # Timing
    MIN_TIME_BETWEEN_TRADES = int(os.getenv('MIN_TIME_BETWEEN_TRADES', '30'))  # seconds
    PAIR_ANALYSIS_TIMEOUT = int(os.getenv('PAIR_ANALYSIS_TIMEOUT', '10'))  # seconds
    
    # Filtering
    PREFERRED_CATEGORIES = os.getenv('PREFERRED_CATEGORIES', 'forex,crypto').split(',')
    EXCLUDED_PAIRS = os.getenv('EXCLUDED_PAIRS', '').split(',') if os.getenv('EXCLUDED_PAIRS') else []
    
    @classmethod
    def display_parallel_config(cls):
        """Display parallel trading configuration"""
        print(f"\n🔄 Parallel Trading Configuration:")
        print(f"   Max Concurrent Pairs: {cls.MAX_CONCURRENT_PAIRS}")
        print(f"   Min Payout Threshold: {cls.MIN_PAYOUT_THRESHOLD:.1%}")
        print(f"   Balance Per Trade: {cls.BALANCE_ALLOCATION_PER_TRADE:.1%}")
        print(f"   Total Risk Budget: {cls.TOTAL_RISK_BUDGET:.1%}")
        print(f"   Preferred Categories: {', '.join(cls.PREFERRED_CATEGORIES)}")
