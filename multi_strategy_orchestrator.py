#!/usr/bin/env python3
"""
Multi-Account Multi-Strategy Trading Orchestrator
Runs 5 accounts with different strategies in parallel
"""

import os
import sys
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

# Import components
from config.multi_account_config import get_account_manager, AccountConfig
from database.multi_account_logger import MultiAccountTradeLogger
from strategies.strategy_integrator import StrategyIntegrator
from strategies.strategy_config import StrategyConfig
from src.iqoptionapi.stable_api import IQ_Option

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler(f'logs/multi_strategy_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AccountTrader:
    """Individual account trader with strategy"""
    
    def __init__(self, account_config: AccountConfig, db_logger: MultiAccountTradeLogger):
        self.account_config = account_config
        self.db_logger = db_logger
        self.logger = logging.getLogger(f"AccountTrader-{account_config.account_id}")
        self.api = None
        self.strategy_integrator = None
        self.running = False
        self.balance = 0.0
        self.daily_pnl = 0.0
        self.trades_today = 0
        
    def connect(self) -> bool:
        """Connect to IQ Option"""
        try:
            self.logger.info(f"🔌 Connecting {self.account_config.email}...")
            
            self.api = IQ_Option(
                self.account_config.email,
                self.account_config.password
            )
            
            check, reason = self.api.connect()
            if not check:
                self.logger.error(f"❌ Connection failed: {reason}")
                self.db_logger.log_system_event(
                    self.account_config.account_id,
                    'connection_failed',
                    'ERROR',
                    f"Failed to connect: {reason}"
                )
                return False
            
            # Set trading mode
            if self.account_config.trading_mode == 'live':
                self.api.change_balance('REAL')
                self.logger.warning("⚠️ LIVE MODE")
            else:
                self.api.change_balance('PRACTICE')
                self.logger.info("✅ Demo mode")
            
            self.balance = self.api.get_balance()
            self.logger.info(f"💰 Balance: ${self.balance:.2f}")
            
            # Initialize strategy integrator
            strategy_config = self._create_strategy_config()
            self.strategy_integrator = StrategyIntegrator(strategy_config)
            
            # Update database
            self.db_logger.update_account_health(
                self.account_config.account_id,
                is_healthy=True,
                connection_failures=0
            )
            
            self.db_logger.log_system_event(
                self.account_config.account_id,
                'connection_success',
                'INFO',
                f"Connected successfully. Balance: ${self.balance:.2f}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Connection error: {e}")
            self.db_logger.log_system_event(
                self.account_config.account_id,
                'connection_error',
                'ERROR',
                str(e)
            )
            return False
    
    def _create_strategy_config(self) -> StrategyConfig:
        """Create strategy configuration from account profile"""
        account_manager = get_account_manager()
        profile_config = account_manager.get_strategy_config(self.account_config.account_id)
        
        return StrategyConfig(
            min_confidence=profile_config.get('min_confidence', 0.75),
            min_confluence=profile_config.get('min_confluence', 2),
            max_trade_amount=self.account_config.max_trade_amount,
            min_trade_amount=1.0,
            max_daily_loss=self.account_config.max_daily_loss,
            enabled_strategies=profile_config.get('enabled_strategies', [])
        )
    
    def trade_cycle(self):
        """Single trading cycle"""
        try:
            # Get available instruments
            instruments = self._get_available_instruments()
            if not instruments:
                return
            
            # Analyze each instrument
            for instrument in instruments[:5]:  # Limit to 5 instruments per cycle
                if not self.running:
                    break
                
                # Check if can trade
                if not self._can_trade():
                    break
                
                # Get candles
                candles = self.api.get_candles(instrument, 60, 100, time.time())
                if not candles or len(candles) < 50:
                    continue
                
                # Analyze with strategy
                direction, confidence, breakdown = self.strategy_integrator.analyze_instrument(candles)
                
                if direction == 'NEUTRAL':
                    continue
                
                # Calculate trade amount
                amount = self.strategy_integrator.get_trade_amount(
                    self.balance,
                    win_streak=0,
                    loss_streak=0
                )
                
                # Execute trade
                self._execute_trade(instrument, direction, amount, confidence, breakdown)
                
                # Wait between trades
                time.sleep(70)
                
        except Exception as e:
            self.logger.error(f"Trade cycle error: {e}")
    
    def _get_available_instruments(self) -> List[str]:
        """Get available trading instruments"""
        try:
            open_markets = self.api.get_all_open_time()
            if not open_markets or 'binary' not in open_markets:
                return []
            
            binary_markets = open_markets['binary']
            instruments = [
                'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD',
                'NZDUSD', 'EURJPY', 'GBPJPY', 'EURGBP', 'AUDJPY'
            ]
            
            available = []
            for inst in instruments:
                for suffix in ['', '-OTC']:
                    test_name = f"{inst}{suffix}"
                    if test_name in binary_markets and binary_markets[test_name].get('open', False):
                        available.append(test_name)
                        break
            
            return available
            
        except Exception as e:
            self.logger.error(f"Error getting instruments: {e}")
            return []
    
    def _can_trade(self) -> bool:
        """Check if can trade"""
        # Check daily loss limit
        if abs(self.daily_pnl) >= self.account_config.max_daily_loss and self.daily_pnl < 0:
            self.logger.warning("⚠️ Daily loss limit reached")
            return False
        
        # Check balance
        if self.balance < 1.0:
            self.logger.warning("⚠️ Insufficient balance")
            return False
        
        return True
    
    def _execute_trade(self, instrument: str, direction: str, amount: float,
                      confidence: float, breakdown: List[Dict]):
        """Execute a trade"""
        try:
            self.logger.info(f"📊 {instrument} {direction} ${amount:.2f} @ {confidence:.0%}")
            
            # Place order
            action = 'call' if direction == 'CALL' else 'put'
            success, order_id = self.api.buy(amount, instrument, action, 1)
            
            if not success:
                self.logger.error("❌ Trade failed")
                return
            
            # Log trade to database
            trade_data = {
                'trade_id': str(order_id),
                'instrument': instrument,
                'direction': direction,
                'amount': amount,
                'entry_time': datetime.now(),
                'expiration_seconds': 60,
                'selected_strategy': breakdown[0]['strategy'] if breakdown else 'unknown',
                'strategy_profile': self.account_config.strategy_profile,
                'confidence': int(confidence * 100),
                'strategy_breakdown': breakdown,
                'mode': self.account_config.trading_mode
            }
            
            db_trade_id = self.db_logger.log_trade(
                self.account_config.account_id,
                trade_data
            )
            
            # Wait for result
            time.sleep(65)
            
            # Check result
            result = self.api.check_win_v3(order_id)
            profit = result if isinstance(result, (int, float)) else 0
            
            won = profit > 0
            result_str = 'WIN' if won else 'LOSS'
            
            self.logger.info(f"{'✅' if won else '❌'} {result_str}: ${profit:.2f}")
            
            # Update database
            self.db_logger.update_trade_result(db_trade_id, result_str, profit)
            
            # Update stats
            self.daily_pnl += profit
            self.trades_today += 1
            self.balance = self.api.get_balance()
            
            # Update account manager
            account_manager = get_account_manager()
            account_manager.update_account_stats(
                self.account_config.account_id,
                self.daily_pnl,
                self.trades_today
            )
            
        except Exception as e:
            self.logger.error(f"Execute trade error: {e}")
    
    def run(self):
        """Main trading loop"""
        self.running = True
        
        while self.running:
            try:
                self.trade_cycle()
                time.sleep(5)
            except Exception as e:
                self.logger.error(f"Run error: {e}")
                time.sleep(30)
    
    def stop(self):
        """Stop trading"""
        self.running = False
        self.logger.info("🛑 Stopping...")


class MultiStrategyOrchestrator:
    """Orchestrates multiple accounts with different strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.account_manager = get_account_manager()
        self.db_logger = None
        self.traders: Dict[str, AccountTrader] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.running = False
        
        # Initialize database
        database_url = os.getenv('DATABASE_URL', 
                                'postgresql://postgres:postgres@localhost:5432/kael')
        try:
            self.db_logger = MultiAccountTradeLogger(database_url)
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            sys.exit(1)
    
    def initialize_traders(self):
        """Initialize all account traders"""
        self.logger.info("="*80)
        self.logger.info("🚀 MULTI-STRATEGY TRADING ORCHESTRATOR")
        self.logger.info("="*80)
        
        accounts = self.account_manager.get_healthy_accounts()
        self.logger.info(f"📊 Initializing {len(accounts)} accounts...")
        
        for account in accounts:
            trader = AccountTrader(account, self.db_logger)
            if trader.connect():
                self.traders[account.account_id] = trader
                self.logger.info(
                    f"✅ {account.account_id}: {account.strategy_profile} strategy"
                )
            else:
                self.logger.error(f"❌ Failed to initialize {account.account_id}")
        
        self.logger.info(f"✅ {len(self.traders)}/{len(accounts)} accounts ready")
        self.logger.info("="*80)
    
    def start(self):
        """Start all traders"""
        if not self.traders:
            self.logger.error("No traders initialized")
            return
        
        self.running = True
        self.logger.info("🎯 Starting all traders...")
        
        # Start each trader in separate thread
        futures = []
        for account_id, trader in self.traders.items():
            future = self.executor.submit(trader.run)
            futures.append((account_id, future))
        
        # Monitor traders
        try:
            while self.running:
                time.sleep(60)
                self._print_status()
                
                # Update daily performance
                self.db_logger.update_daily_performance()
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutdown requested...")
            self.stop()
    
    def stop(self):
        """Stop all traders"""
        self.running = False
        
        for trader in self.traders.values():
            trader.stop()
        
        self.executor.shutdown(wait=True)
        self.logger.info("✅ All traders stopped")
    
    def _print_status(self):
        """Print current status"""
        summary = self.account_manager.get_summary()
        
        self.logger.info("="*80)
        self.logger.info("📊 PORTFOLIO STATUS")
        self.logger.info(f"Active Accounts: {summary['healthy_accounts']}/{summary['total_accounts']}")
        self.logger.info(f"Total Trades: {summary['total_trades']}")
        self.logger.info(f"Daily P&L: ${summary['total_daily_pnl']:.2f}")
        
        for acc in summary['accounts']:
            self.logger.info(
                f"  {acc['account_id']}: {acc['strategy']} | "
                f"Trades: {acc['total_trades']} | P&L: ${acc['daily_pnl']:.2f}"
            )
        
        self.logger.info("="*80)


def main():
    """Main entry point"""
    orchestrator = MultiStrategyOrchestrator()
    orchestrator.initialize_traders()
    orchestrator.start()


if __name__ == '__main__':
    main()
