#!/usr/bin/env python3
"""
KAEL Trading System - Main Entry Point
Reorganized production-ready automated trading system

Usage:
    python main.py --mode demo --trades 5
    python main.py --mode live --trades 10 --confirm
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to Python path for clean imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
load_dotenv()

# Configure logging
def setup_logging():
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'trading.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Import trading modules
try:
    from core import RiskManager, PositionSizer, TradeExecutor
    from analysis import TechnicalIndicators
    from data import ConnectionManager, DataValidator
    logger.info("✅ Core modules loaded from reorganized src/")
except ImportError as e:
    logger.error(f"❌ Failed to import modules: {e}")
    sys.exit(1)


class KAELTradingSystem:
    """
    Main trading system interface
    Entry point for all trading operations
    """
    
    def __init__(self):
        self.logger = logger
        self.config = self._load_config()
        
    def _load_config(self):
        """Load configuration from environment"""
        return {
            'mode': os.getenv('ACCOUNT_TYPE', 'demo'),
            'email': os.getenv('IQOPTION_EMAIL'),
            'password': os.getenv('IQOPTION_PASSWORD'),
            'risk_per_trade': float(os.getenv('RISK_PER_TRADE', '0.02')),
            'max_daily_loss': float(os.getenv('MAX_DAILY_LOSS', '50.0')),
        }
    
    def run_trading(self, mode: str, trades: int = None, live: bool = False):
        """
        Main trading method
        
        Args:
            mode: 'demo' or 'live'
            trades: Maximum trades to execute
            live: Whether to trade with real money
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info(f"🚀 KAEL Trading System v2.0 - {mode.upper()} Mode")
            self.logger.info("=" * 80)
            
            # Validate configuration
            if not self.config['email'] or not self.config['password']:
                self.logger.error("❌ IQOption credentials not configured")
                return False
            
            # Live trading confirmation
            if live and mode == 'live':
                response = input("⚠️  REAL MONEY trading. Continue? (yes/no): ")
                if response.lower() != 'yes':
                    self.logger.warning("❌ Live trading cancelled by user")
                    return False
            
            self.logger.info(f"✅ Configuration valid - Mode: {mode}")
            self.logger.info(f"✅ Risk per trade: {self.config['risk_per_trade']*100:.1f}%")
            self.logger.info(f"✅ Max daily loss: ${self.config['max_daily_loss']:.2f}")
            
            if trades:
                self.logger.info(f"✅ Max trades: {trades}")
            
            self.logger.info("\n🎯 System ready for trading!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='KAEL Automated Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Demo trading (safe):
    python main.py --mode demo --trades 5

  Live trading (real money):
    python main.py --mode live --trades 10 --confirm

  Continuous trading:
    python main.py --mode demo --continuous
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['demo', 'live'],
        default='demo',
        help='Trading mode (default: demo)'
    )
    
    parser.add_argument(
        '--trades',
        type=int,
        default=None,
        help='Maximum number of trades'
    )
    
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Confirm live trading (required for live mode)'
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuously'
    )
    
    args = parser.parse_args()
    
    # Initialize system
    system = KAELTradingSystem()
    
    # Run trading
    success = system.run_trading(
        mode=args.mode,
        trades=args.trades,
        live=args.confirm and args.mode == 'live'
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
