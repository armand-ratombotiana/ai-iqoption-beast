#!/usr/bin/env python3
"""
Production Trading System - Main Entry Point
Integrates all modules and components for live trading

Usage:
    python run_trading_system.py --mode demo
    python run_trading_system.py --mode live --confirm
"""

import sys
import os
import argparse
import time
from datetime import datetime
from typing import Optional
import logging

# IQOption API
from iqoptionapi.stable_api import IQ_Option

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TradingSystemConfig:
    """Consolidated Trading System Configuration"""

    # Account Configuration
    EMAIL = os.getenv('IQOPTION_EMAIL', 'tombokael4@gmail.com')
    PASSWORD = os.getenv('IQOPTION_PASSWORD', 'tombokael04')
    ACCOUNT_TYPE = os.getenv('ACCOUNT_TYPE', 'PRACTICE')  # PRACTICE or REAL

    # Risk Management
    RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', '0.02'))  # 2%
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '0.10'))  # 10%
    MAX_CONCURRENT_TRADES = int(os.getenv('MAX_CONCURRENT_TRADES', '3'))
    MIN_ACCOUNT_BALANCE = float(os.getenv('MIN_ACCOUNT_BALANCE', '50'))

    # Trade Parameters
    BASE_TRADE_AMOUNT = float(os.getenv('BASE_TRADE_AMOUNT', '2.0'))
    MAX_TRADE_AMOUNT = float(os.getenv('MAX_TRADE_AMOUNT', '20.0'))
    MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', '60'))

    # Martingale
    MARTINGALE_ENABLED = os.getenv('MARTINGALE_ENABLED', 'True').lower() == 'true'
    MARTINGALE_MULTIPLIER = float(os.getenv('MARTINGALE_MULTIPLIER', '1.5'))
    MAX_MARTINGALE_LEVEL = int(os.getenv('MAX_MARTINGALE_LEVEL', '3'))

    # Assets to Trade
    TRADING_ASSETS = os.getenv('TRADING_ASSETS', 'EURUSD,GBPUSD,USDJPY').split(',')

    # Parallel Processing
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '3'))


class RiskManager:
    """Risk Management System"""

    def __init__(self, config: TradingSystemConfig):
        self.config = config
        self.daily_profit = 0.0
        self.daily_loss = 0.0
        self.consecutive_losses = 0
        self.consecutive_wins = 0
        self.current_martingale_level = 0
        self.trades_today = []

        logger.info("Risk Manager initialized")

    def can_trade(self, balance: float) -> tuple[bool, str]:
        """Check if trading is allowed"""

        # Check minimum balance
        if balance < self.config.MIN_ACCOUNT_BALANCE:
            return False, f"Balance ${balance:.2f} below minimum ${self.config.MIN_ACCOUNT_BALANCE}"

        # Check daily loss limit
        if abs(self.daily_loss) >= self.config.MAX_DAILY_LOSS * balance:
            return False, f"Daily loss limit reached: ${abs(self.daily_loss):.2f}"

        # Check daily profit target
        max_profit = self.config.MAX_DAILY_LOSS * balance * 2  # 2x max loss
        if self.daily_profit >= max_profit:
            return False, f"Daily profit target reached: ${self.daily_profit:.2f}"

        # Check consecutive losses
        if self.consecutive_losses >= 3:
            return False, f"Too many consecutive losses: {self.consecutive_losses}"

        return True, "OK"

    def calculate_position_size(self, balance: float, confidence: float) -> float:
        """Calculate position size based on risk and confidence"""

        # Base position size
        base_size = balance * self.config.RISK_PER_TRADE

        # Adjust for confidence
        confidence_factor = confidence / 100.0
        adjusted_size = base_size * confidence_factor

        # Apply Martingale if enabled
        if self.config.MARTINGALE_ENABLED and self.consecutive_losses > 0:
            martingale_multiplier = self.config.MARTINGALE_MULTIPLIER ** min(
                self.consecutive_losses,
                self.config.MAX_MARTINGALE_LEVEL
            )
            adjusted_size *= martingale_multiplier

        # Enforce limits
        final_size = max(1.0, min(adjusted_size, self.config.MAX_TRADE_AMOUNT))

        logger.info(f"Position size: ${final_size:.2f} (confidence: {confidence}%, losses: {self.consecutive_losses})")
        return final_size

    def record_trade(self, profit: float):
        """Record trade result"""
        self.trades_today.append(profit)

        if profit > 0:
            self.daily_profit += profit
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            logger.info(f"✅ WIN: +${profit:.2f} (Streak: {self.consecutive_wins})")
        else:
            self.daily_loss += abs(profit)
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            logger.info(f"❌ LOSS: -${abs(profit):.2f} (Streak: {self.consecutive_losses})")


class SignalGenerator:
    """Signal Generation System"""

    def __init__(self, api: IQ_Option):
        self.api = api
        logger.info("Signal Generator initialized")

    def generate_signal(self, asset: str, timeframe: int = 60) -> Optional[dict]:
        """Generate trading signal for asset"""

        try:
            # Get candles
            self.api.start_candles_stream(asset, timeframe, 50)
            time.sleep(2)
            candles = self.api.get_realtime_candles(asset, timeframe)
            self.api.stop_candles_stream(asset, timeframe)

            if not candles or len(candles) < 20:
                return None

            # Convert to list
            candle_list = list(candles.values())

            # Simple trend analysis
            recent_closes = [c['close'] for c in candle_list[-10:]]
            older_closes = [c['close'] for c in candle_list[-20:-10]]

            recent_avg = sum(recent_closes) / len(recent_closes)
            older_avg = sum(older_closes) / len(older_closes)

            # Determine direction
            if recent_avg > older_avg * 1.0001:  # 0.01% threshold
                action = 'call'
                confidence = min(70 + (recent_avg - older_avg) / older_avg * 10000, 85)
            elif recent_avg < older_avg * 0.9999:
                action = 'put'
                confidence = min(70 + (older_avg - recent_avg) / older_avg * 10000, 85)
            else:
                action = 'hold'
                confidence = 50

            signal = {
                'asset': asset,
                'action': action,
                'confidence': confidence,
                'current_price': candle_list[-1]['close'],
                'timestamp': datetime.now()
            }

            logger.info(f"Signal: {asset} - {action.upper()} @ {confidence:.1f}%")
            return signal

        except Exception as e:
            logger.error(f"Error generating signal for {asset}: {e}")
            return None


class TradingEngine:
    """Main Trading Engine"""

    def __init__(self, config: TradingSystemConfig, dry_run: bool = True):
        self.config = config
        self.dry_run = dry_run
        self.api = None
        self.risk_manager = RiskManager(config)
        self.signal_generator = None
        self.running = False

        logger.info(f"Trading Engine initialized (DRY RUN: {dry_run})")

    def connect(self) -> bool:
        """Connect to IQOption API"""
        try:
            logger.info("Connecting to IQOption...")
            self.api = IQ_Option(self.config.EMAIL, self.config.PASSWORD)
            check, reason = self.api.connect()

            if check:
                self.api.change_balance(self.config.ACCOUNT_TYPE)
                time.sleep(1)

                balance = self.api.get_balance()
                logger.info(f"✅ Connected successfully")
                logger.info(f"Account: {self.config.ACCOUNT_TYPE}")
                logger.info(f"Balance: ${balance}")

                self.signal_generator = SignalGenerator(self.api)
                return True
            else:
                logger.error(f"Connection failed: {reason}")
                return False

        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def check_market_open(self, asset: str) -> bool:
        """Check if market is open for asset"""
        try:
            self.api.start_candles_stream(asset, 60, 10)
            time.sleep(1)
            candles = self.api.get_realtime_candles(asset, 60)
            self.api.stop_candles_stream(asset, 60)

            if candles and len(candles) > 0:
                latest = list(candles.values())[-1]
                time_diff = time.time() - latest.get('from', 0)
                return time_diff < 300  # Less than 5 minutes

            return False
        except:
            return False

    def execute_trade(self, signal: dict, amount: float) -> Optional[dict]:
        """Execute trade based on signal"""

        if signal['action'] == 'hold':
            logger.info("Signal is HOLD - skipping trade")
            return None

        asset = signal['asset']
        action = signal['action']

        logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Executing {action.upper()} on {asset} for ${amount:.2f}")

        if self.dry_run:
            # Simulate trade result (random for demo)
            import random
            result = {
                'success': True,
                'profit': amount * 0.85 if random.random() > 0.5 else -amount,
                'asset': asset,
                'action': action,
                'amount': amount,
                'simulated': True
            }
            time.sleep(2)  # Simulate trade duration
        else:
            # Real trade execution
            try:
                duration = 1  # 1 minute

                # Place the trade
                check, trade_id = self.api.buy(
                    amount,
                    asset,
                    action,
                    duration
                )

                if not check:
                    logger.error(f"Trade failed to execute")
                    return None

                logger.info(f"Trade placed: ID {trade_id}")

                # Wait for result
                time.sleep(duration * 60 + 5)

                # Get result (simplified - actual implementation would check via API)
                result = {
                    'success': True,
                    'profit': 0,  # Would get actual result from API
                    'asset': asset,
                    'action': action,
                    'amount': amount,
                    'trade_id': trade_id
                }

            except Exception as e:
                logger.error(f"Trade execution error: {e}")
                return None

        return result

    def run(self, max_trades: Optional[int] = None):
        """Run trading system"""

        if not self.connect():
            logger.error("Failed to connect - exiting")
            return

        self.running = True
        trade_count = 0

        logger.info("="*70)
        logger.info("TRADING SYSTEM STARTED")
        logger.info("="*70)
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE TRADING'}")
        logger.info(f"Assets: {', '.join(self.config.TRADING_ASSETS)}")
        logger.info(f"Max trades: {max_trades if max_trades else 'Unlimited'}")
        logger.info("="*70)

        try:
            while self.running:
                # Check if we should continue
                if max_trades and trade_count >= max_trades:
                    logger.info(f"Reached max trades limit ({max_trades})")
                    break

                balance = self.api.get_balance()

                # Check risk limits
                can_trade, reason = self.risk_manager.can_trade(balance)
                if not can_trade:
                    logger.warning(f"Trading halted: {reason}")
                    break

                # Scan assets for signals
                for asset in self.config.TRADING_ASSETS:
                    if not self.check_market_open(asset):
                        logger.debug(f"{asset} market closed")
                        continue

                    # Generate signal
                    signal = self.signal_generator.generate_signal(asset)

                    if not signal or signal['confidence'] < self.config.MIN_CONFIDENCE:
                        continue

                    # Calculate position size
                    amount = self.risk_manager.calculate_position_size(
                        balance,
                        signal['confidence']
                    )

                    # Execute trade
                    result = self.execute_trade(signal, amount)

                    if result and result['success']:
                        trade_count += 1
                        self.risk_manager.record_trade(result['profit'])

                        # Log summary
                        logger.info(f"Trade #{trade_count} complete")
                        logger.info(f"Daily P/L: ${self.risk_manager.daily_profit - self.risk_manager.daily_loss:.2f}")
                        logger.info(f"Win rate: {self.risk_manager.consecutive_wins}/{trade_count}")

                    time.sleep(5)  # Prevent rapid trading

                # Wait before next scan
                time.sleep(30)

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"System error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown trading system"""
        self.running = False
        logger.info("="*70)
        logger.info("TRADING SYSTEM SHUTDOWN")
        logger.info(f"Total trades: {len(self.risk_manager.trades_today)}")
        logger.info(f"Daily profit: ${self.risk_manager.daily_profit:.2f}")
        logger.info(f"Daily loss: ${self.risk_manager.daily_loss:.2f}")
        logger.info(f"Net P/L: ${self.risk_manager.daily_profit - self.risk_manager.daily_loss:.2f}")
        logger.info("="*70)


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(description='IQOption Trading System')
    parser.add_argument('--mode', choices=['demo', 'live'], default='demo',
                        help='Trading mode (demo=dry run, live=real trading)')
    parser.add_argument('--max-trades', type=int, default=None,
                        help='Maximum number of trades to execute')
    parser.add_argument('--confirm', action='store_true',
                        help='Required confirmation for live trading')

    args = parser.parse_args()

    # Safety check for live trading
    if args.mode == 'live' and not args.confirm:
        print("ERROR: Live trading requires --confirm flag")
        print("Example: python run_trading_system.py --mode live --confirm")
        sys.exit(1)

    if args.mode == 'live':
        print("\n" + "!"*70)
        print("WARNING: LIVE TRADING MODE")
        print("!"*70)
        response = input("Are you sure you want to trade with real money? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted")
            sys.exit(0)

    # Create logs directory
    os.makedirs('logs', exist_ok=True)

    # Initialize system
    config = TradingSystemConfig()
    engine = TradingEngine(config, dry_run=(args.mode == 'demo'))

    # Run
    engine.run(max_trades=args.max_trades)


if __name__ == "__main__":
    main()
