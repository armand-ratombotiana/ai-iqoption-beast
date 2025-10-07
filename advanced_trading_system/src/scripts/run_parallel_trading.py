#!/usr/bin/env python3
"""
Parallel Trading System - Production Entry Point
Trades multiple pairs simultaneously with real IQOption integration

Usage:
    python scripts/run_parallel_trading.py --mode demo
    python scripts/run_parallel_trading.py --mode live --confirm
    python scripts/run_parallel_trading.py --test-pairs
"""
import asyncio
import os
import sys
import argparse
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import concurrent.futures

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Core imports
try:
    from iqoptionapi.stable_api import IQ_Option
except ImportError:
    print("❌ IQOption API not found. Please ensure it's installed.")
    sys.exit(1)

from config.settings import TradingConfig
from database.trade_storage import TradeDatabase
from analysis.technical_indicators import TechnicalIndicators

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/parallel_trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


class ParallelTradingSystem:
    """
    Parallel trading system with real IQOption integration
    """
    
    def __init__(self, config: TradingConfig, dry_run: bool = True):
        self.config = config
        self.dry_run = dry_run
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.api = None
        self.db = TradeDatabase(config.DB_PATH)
        self.technical_indicators = TechnicalIndicators()
        
        # Parallel trading settings
        self.max_concurrent_pairs = 5
        self.min_payout_threshold = 0.75
        self.balance_allocation_per_trade = 0.02  # 2% per trade
        self.total_risk_budget = 0.10  # 10% total risk
        
        # Session tracking
        self.active_trades = {}
        self.session_stats = {
            'trades_executed': 0,
            'trades_won': 0,
            'trades_lost': 0,
            'total_profit': 0.0,
            'pairs_traded': set(),
            'start_time': datetime.now(),
            'errors': []
        }
        
        self.logger.info(f"Parallel Trading System initialized (DRY RUN: {dry_run})")

    async def connect_to_iqoption(self) -> bool:
        """Connect to IQOption with async wrapper"""
        try:
            self.logger.info("Connecting to IQOption...")
            
            if not self.config.EMAIL or not self.config.PASSWORD:
                raise ValueError("IQOption credentials not set")
            
            # Run connection in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                self.api = await loop.run_in_executor(
                    executor, 
                    lambda: IQ_Option(self.config.EMAIL, self.config.PASSWORD)
                )
                
                check, reason = await loop.run_in_executor(
                    executor,
                    self.api.connect
                )
            
            if not check:
                raise ConnectionError(f"Connection failed: {reason}")
            
            # Set account type
            account_type = 'PRACTICE' if self.dry_run or self.config.ACCOUNT_TYPE.lower() == 'demo' else 'REAL'
            await loop.run_in_executor(executor, self.api.change_balance, account_type)
            await asyncio.sleep(1)
            
            # Verify connection
            balance = await loop.run_in_executor(executor, self.api.get_balance)
            if balance is None:
                raise ConnectionError("Could not retrieve balance")
            
            self.logger.info(f"✅ Connected to IQOption")
            self.logger.info(f"Account Type: {account_type}")
            self.logger.info(f"Balance: ${balance:.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Connection failed: {e}")
            return False

    async def get_available_pairs(self) -> List[Dict]:
        """Get available pairs with payouts"""
        try:
            if self.dry_run:
                # Return simulated pairs for testing
                return [
                    {'pair': 'EURUSD-OTC', 'payout': 0.85, 'is_open': True, 'category': 'forex'},
                    {'pair': 'GBPUSD-OTC', 'payout': 0.82, 'is_open': True, 'category': 'forex'},
                    {'pair': 'AUDCHF-OTC', 'payout': 0.80, 'is_open': True, 'category': 'forex'},
                    {'pair': 'USDJPY-OTC', 'payout': 0.78, 'is_open': True, 'category': 'forex'},
                    {'pair': 'EURJPY-OTC', 'payout': 0.76, 'is_open': True, 'category': 'forex'},
                ]
            
            # Get real pairs from IQOption
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Get all open times
                open_times = await loop.run_in_executor(
                    executor,
                    self.api.get_all_open_time
                )
            
            available_pairs = []
            
            # Process turbo options (1-5 minutes)
            turbo_pairs = open_times.get('turbo', {})
            for pair, times in turbo_pairs.items():
                if times.get('open', False):
                    # Get payout
                    try:
                        payout = await loop.run_in_executor(
                            executor,
                            self.api.get_payout,
                            pair,
                            1  # 1 minute
                        )
                        
                        if payout and payout >= self.min_payout_threshold:
                            available_pairs.append({
                                'pair': pair,
                                'payout': payout,
                                'is_open': True,
                                'category': 'forex'
                            })
                    except Exception as e:
                        self.logger.debug(f"Could not get payout for {pair}: {e}")
                        continue
            
            # Sort by payout (highest first)
            available_pairs.sort(key=lambda x: x['payout'], reverse=True)
            
            self.logger.info(f"📊 Found {len(available_pairs)} available pairs")
            return available_pairs[:self.max_concurrent_pairs * 2]  # Get more than we need
            
        except Exception as e:
            self.logger.error(f"❌ Error getting available pairs: {e}")
            return []

    async def get_market_data_parallel(self, pairs: List[str]) -> Dict[str, Dict]:
        """Get market data for multiple pairs in parallel"""
        try:
            if self.dry_run:
                # Simulate market data
                market_data = {}
                for pair in pairs:
                    market_data[pair] = self._simulate_market_data(pair)
                return market_data
            
            # Get real market data in parallel
            loop = asyncio.get_event_loop()
            
            async def get_single_pair_data(pair: str) -> tuple:
                try:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        current_time = int(time.time())
                        candles = await loop.run_in_executor(
                            executor,
                            self.api.get_candles,
                            pair, 60, 100, current_time
                        )
                    
                    if not candles or len(candles) < 20:
                        return pair, None
                    
                    # Calculate indicators
                    market_data = {
                        'pair': pair,
                        'current_price': candles[-1]['close'],
                        'rsi_14': self.technical_indicators.rsi(candles, 14),
                        'trend': self.technical_indicators.identify_trend(candles),
                        'volatility': self.technical_indicators.calculate_volatility(candles)[0],
                        'bb_position': self.technical_indicators.bollinger_bands(candles)['position'],
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    return pair, market_data
                    
                except Exception as e:
                    self.logger.error(f"Error getting data for {pair}: {e}")
                    return pair, None
            
            # Execute all requests in parallel
            tasks = [get_single_pair_data(pair) for pair in pairs]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            market_data = {}
            for result in results:
                if isinstance(result, Exception):
                    continue
                pair, data = result
                if data:
                    market_data[pair] = data
            
            self.logger.info(f"📊 Retrieved market data for {len(market_data)} pairs")
            return market_data
            
        except Exception as e:
            self.logger.error(f"❌ Error getting parallel market data: {e}")
            return {}

    def _simulate_market_data(self, pair: str) -> Dict:
        """Simulate market data for testing"""
        import random
        
        base_price = 0.5685 if 'AUD' in pair else 1.0850
        
        return {
            'pair': pair,
            'current_price': base_price + random.uniform(-0.001, 0.001),
            'rsi_14': random.uniform(30, 70),
            'trend': random.choice(['uptrend', 'downtrend', 'sideways']),
            'volatility': random.choice(['low', 'medium', 'high']),
            'bb_position': random.uniform(0.2, 0.8),
            'timestamp': datetime.now().isoformat()
        }

    def analyze_trading_opportunities(self, market_data: Dict[str, Dict], 
                                    available_pairs: List[Dict]) -> List[Dict]:
        """Analyze and rank trading opportunities"""
        opportunities = []
        
        for pair_info in available_pairs:
            pair = pair_info['pair']
            
            if pair not in market_data:
                continue
            
            data = market_data[pair]
            
            # Simple signal generation
            signal, confidence = self._generate_signal(data)
            
            if signal and confidence >= self.config.MIN_CONFIDENCE:
                opportunities.append({
                    'pair': pair,
                    'signal': signal,
                    'confidence': confidence,
                    'payout': pair_info['payout'],
                    'expected_value': confidence * pair_info['payout'],
                    'market_data': data
                })
        
        # Sort by expected value
        opportunities.sort(key=lambda x: x['expected_value'], reverse=True)
        
        # Limit to max concurrent pairs
        return opportunities[:self.max_concurrent_pairs]

    def _generate_signal(self, market_data: Dict) -> tuple:
        """Generate trading signal from market data"""
        try:
            rsi = market_data.get('rsi_14', 50)
            trend = market_data.get('trend', 'sideways')
            bb_position = market_data.get('bb_position', 0.5)
            
            # Signal logic
            if rsi < 30 and trend != 'downtrend':
                return 'CALL', 75
            elif rsi > 70 and trend != 'uptrend':
                return 'PUT', 75
            elif bb_position < 0.2 and trend == 'uptrend':
                return 'CALL', 70
            elif bb_position > 0.8 and trend == 'downtrend':
                return 'PUT', 70
            elif trend == 'uptrend' and rsi < 50:
                return 'CALL', 65
            elif trend == 'downtrend' and rsi > 50:
                return 'PUT', 65
            else:
                return None, 0
                
        except Exception as e:
            self.logger.error(f"Signal generation error: {e}")
            return None, 0

    async def execute_trades_parallel(self, opportunities: List[Dict]) -> List[Dict]:
        """Execute multiple trades in parallel"""
        if not opportunities:
            return []
        
        self.logger.info(f"🚀 Executing {len(opportunities)} trades in parallel...")
        
        # Calculate position sizes
        balance = await self._get_balance()
        max_trade_amount = balance * self.balance_allocation_per_trade
        
        async def execute_single_trade(opportunity: Dict) -> Dict:
            try:
                pair = opportunity['pair']
                signal = opportunity['signal']
                confidence = opportunity['confidence']
                
                # Position sizing based on confidence
                amount = max_trade_amount * (confidence / 100)
                amount = max(self.config.MIN_AMOUNT, min(amount, self.config.MAX_AMOUNT))
                
                self.logger.info(f"📈 Executing {signal} on {pair} - ${amount:.2f}")
                
                if self.dry_run:
                    # Simulate trade
                    import random
                    order_id = f"SIM_{pair}_{int(time.time())}"
                    
                    # Simulate result
                    await asyncio.sleep(1)  # Simulate execution time
                    is_win = random.random() < (confidence / 100)
                    profit = amount * opportunity['payout'] if is_win else -amount
                    
                    result = {
                        'success': True,
                        'order_id': order_id,
                        'pair': pair,
                        'signal': signal,
                        'amount': amount,
                        'profit': profit,
                        'result': 'WIN' if is_win else 'LOSS',
                        'simulated': True
                    }
                else:
                    # Real trade execution
                    loop = asyncio.get_event_loop()
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        status, order_id = await loop.run_in_executor(
                            executor,
                            self.api.buy,
                            amount, pair, signal.lower(), 1
                        )
                    
                    if status and order_id:
                        result = {
                            'success': True,
                            'order_id': str(order_id),
                            'pair': pair,
                            'signal': signal,
                            'amount': amount,
                            'simulated': False
                        }
                    else:
                        result = {
                            'success': False,
                            'error': 'Trade execution failed',
                            'pair': pair
                        }
                
                # Store in database
                if result.get('success'):
                    trade_data = {
                        'trade_id': result['order_id'],
                        'timestamp': datetime.now().isoformat(),
                        'pair': pair,
                        'direction': signal,
                        'amount': amount,
                        'duration': 1,
                        'result': 'PENDING' if not result.get('simulated') else result.get('result'),
                        'ai_signal_confidence': int(confidence),
                        'payout_rate': opportunity['payout'],
                        'strategy_version': 'parallel_v2.0'
                    }
                    
                    if result.get('simulated'):
                        trade_data['result'] = result['result']
                        trade_data['profit'] = result['profit']
                    
                    self.db.insert_trade(trade_data)
                
                return result
                
            except Exception as e:
                self.logger.error(f"❌ Error executing trade for {opportunity['pair']}: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'pair': opportunity['pair']
                }
        
        # Execute all trades concurrently
        tasks = [execute_single_trade(opp) for opp in opportunities]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_trades = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"❌ Trade execution exception: {result}")
                continue
            
            if result.get('success'):
                successful_trades.append(result)
                self.session_stats['trades_executed'] += 1
                self.session_stats['pairs_traded'].add(result['pair'])
                
                # Update stats for simulated trades
                if result.get('simulated'):
                    if result['result'] == 'WIN':
                        self.session_stats['trades_won'] += 1
                    else:
                        self.session_stats['trades_lost'] += 1
                    self.session_stats['total_profit'] += result.get('profit', 0)
                
                self.logger.info(f"✅ Trade executed: {result['pair']} {result['signal']}")
        
        self.logger.info(f"✅ Successfully executed {len(successful_trades)} trades")
        return successful_trades

    async def _get_balance(self) -> float:
        """Get current account balance"""
        try:
            if self.dry_run:
                return 10000.0  # Simulated balance
            
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                balance = await loop.run_in_executor(
                    executor,
                    self.api.get_balance
                )
                return balance if balance is not None else 0.0
                
        except Exception as e:
            self.logger.error(f"❌ Error getting balance: {e}")
            return 0.0

    async def run_parallel_trading_session(self, duration_minutes: int = 60) -> Dict:
        """Run the complete parallel trading session"""
        try:
            self.logger.info(f"🚀 Starting parallel trading session for {duration_minutes} minutes...")
            
            # Connect to IQOption
            if not await self.connect_to_iqoption():
                self.logger.error("❌ Failed to connect to IQOption")
                return {'success': False, 'error': 'Connection failed'}
            
            # Get available pairs
            available_pairs = await self.get_available_pairs()
            if not available_pairs:
                self.logger.warning("⚠️ No available pairs found")
                return {'success': False, 'error': 'No available pairs'}
            
            # Get market data
            market_data = await self.get_market_data_parallel([pair['pair'] for pair in available_pairs])
            
            # Analyze opportunities
            opportunities = self.analyze_trading_opportunities(market_data, available_pairs)
            
            if not opportunities:
                self.logger.warning("⚠️ No trading opportunities found")
                return {'success': False, 'error': 'No opportunities'}
            
            # Execute trades
            results = await self.execute_trades_parallel(opportunities)
            
            # Final session stats
            self.session_stats['end_time'] = datetime.now()
            self.session_stats['duration'] = (self.session_stats['end_time'] - self.session_stats['start_time']).total_seconds() / 60
            
            self.logger.info(f"📊 Session completed! {self.session_stats['trades_executed']} trades executed")
            
            return {
                'success': True,
                'trades_executed': self.session_stats['trades_executed'],
                'trades_won': self.session_stats['trades_won'],
                'trades_lost': self.session_stats['trades_lost'],
                'total_profit': self.session_stats['total_profit'],
                'pairs_traded': list(self.session_stats['pairs_traded']),
                'session_duration': self.session_stats['duration'],
                'session_stats': self.session_stats
            }
            
        except Exception as e:
            self.logger.error(f"❌ Session error: {e}")
            return {'success': False, 'error': str(e)}

    async def cleanup(self):
        """Cleanup resources"""
        if self.api:
            try:
                await self.api.disconnect()
            except:
                pass

    async def get_session_stats(self) -> Dict:
        """Get current session statistics"""
        return self.session_stats.copy()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Parallel Trading System")
    parser.add_argument('--mode', choices=['demo', 'live'], default='demo', help='Trading mode')
    parser.add_argument('--confirm', action='store_true', help='Confirm live trading')
    parser.add_argument('--test-pairs', action='store_true', help='Test with specific pairs')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    
    # Validate configuration
    try:
        TradingConfig.validate()
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return
    
    # Initialize system
    system = ParallelTradingSystem(TradingConfig, dry_run=args.mode == 'demo')
    
    try:
        # Run session
        results = asyncio.run(system.run_parallel_trading_session(duration_minutes=60))
        
        if results['success']:
            logger.info(f"✅ Session completed successfully!")
            logger.info(f"📊 Final stats: {results['trades_executed']} trades, ${results['total_profit']:.2f} profit")
        else:
            logger.error(f"❌ Session failed: {results['error']}")
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ Session interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        # Cleanup
        asyncio.run(system.cleanup())


if __name__ == "__main__":
    main()