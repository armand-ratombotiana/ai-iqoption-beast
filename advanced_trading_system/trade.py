#!/usr/bin/env python3
"""
IQOption Trading System - Main Entry Point
Complete integrated trading system with all modules

Usage:
    python trade.py --mode demo --trades 5
    python trade.py --mode live --trades 10 --confirm
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
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

logger = logging.getLogger(__name__)

# Import trading system (will be created)
try:
    from run_trading_system import TradingEngine, TradingSystemConfig
    logger.info("✅ Trading modules loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import trading modules: {e}")
    logger.info("Using standalone version...")
    TradingEngine = None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='IQOption Automated Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Demo trading (safe):
    python trade.py --mode demo --trades 5

  Live trading (real money - careful!):
    python trade.py --mode live --trades 10 --confirm

  Continuous trading:
    python trade.py --mode demo
        """
    )

    parser.add_argument(
        '--mode',
        choices=['demo', 'live'],
        default='demo',
        help='Trading mode: demo (simulated) or live (real money)'
    )

    parser.add_argument(
        '--trades',
        type=int,
        default=None,
        help='Maximum number of trades to execute (default: unlimited)'
    )

    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Required confirmation flag for live trading'
    )

    parser.add_argument(
        '--assets',
        type=str,
        default=None,
        help='Comma-separated list of assets to trade (e.g., EURUSD,GBPUSD)'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='.env',
        help='Configuration file path (default: .env)'
    )

    args = parser.parse_args()

    # Safety check for live trading
    if args.mode == 'live':
        if not args.confirm:
            print("\n" + "="*70)
            print("ERROR: Live trading requires --confirm flag for safety")
            print("="*70)
            print("\nExample:")
            print("  python trade.py --mode live --trades 10 --confirm")
            print("\nThis ensures you understand you're trading with REAL MONEY.")
            sys.exit(1)

        print("\n" + "!"*70)
        print("⚠️  WARNING: LIVE TRADING MODE - REAL MONEY AT RISK")
        print("!"*70)
        print("\nYou are about to trade with REAL MONEY.")
        print("You can LOSE your entire investment.")
        response = input("\nType 'YES' in capital letters to confirm: ")

        if response != 'YES':
            print("\nAborted. Trading cancelled.")
            sys.exit(0)

    # Banner
    print("\n" + "="*70)
    print("  IQOption Automated Trading System")
    print("="*70)
    print(f"  Mode: {args.mode.upper()}")
    print(f"  Max trades: {args.trades if args.trades else 'Unlimited'}")
    if args.assets:
        print(f"  Assets: {args.assets}")
    print("="*70 + "\n")

    # Check if trading engine is available
    if TradingEngine is None:
        print("ERROR: Trading engine not found")
        print("Please ensure run_trading_system.py is in the project root")
        sys.exit(1)

    # Create and run trading system
    try:
        config = TradingSystemConfig()

        # Override config with command line args
        if args.assets:
            config.TRADING_ASSETS = args.assets.split(',')

        # Create engine
        engine = TradingEngine(
            config=config,
            dry_run=(args.mode == 'demo')
        )

        # Run trading
        logger.info("Starting trading system...")
        engine.run(max_trades=args.trades)

    except KeyboardInterrupt:
        logger.info("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info("Trading system stopped")


if __name__ == '__main__':
    main()
