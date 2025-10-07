#!/usr/bin/env python3
"""
Enhanced AI Trading System - Production Entry Point
Multi-AI consensus with advanced features and real IQOption integration

Usage:
    python scripts/run_enhanced_trading.py --mode demo
    python scripts/run_enhanced_trading.py --mode live --confirm
    python scripts/run_enhanced_trading.py --test-connection
"""
import os
import sys
import argparse
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

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
from analysis.market_context import MarketContextAnalyzer

# AI Models
from ai_models.base_model import BaseAIModel
from ai_models.consensus_engine import AIConsensusEngine

# Try to import optional AI models
AI_MODELS_AVAILABLE = {}

try:
    from ai_models.openai_model import OpenAIModel
    AI_MODELS_AVAILABLE['openai'] = OpenAIModel
except ImportError:
    print("⚠️ OpenAI model not available")

try:
    from ai_models.claude_model import ClaudeModel
    AI_MODELS_AVAILABLE['claude'] = ClaudeModel
except ImportError:
    print("⚠️ Claude model not available")

try:
    from ai_models.deepseek_model import DeepSeekModel
    AI_MODELS_AVAILABLE['deepseek'] = DeepSeekModel
except ImportError:
    print("⚠️ DeepSeek model not available")

# Enhanced features (optional)
try:
    from ai_models.enhanced_consensus import EnhancedConsensusEngine
    from ai_models.kelly_position_sizer import KellyPositionSizer
    from ai_models.explainability import ExplainabilityEngine
    ENHANCED_FEATURES = True
except ImportError:
    print("⚠️ Enhanced features not available, using basic consensus")
    ENHANCED_FEATURES = False

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/enhanced_trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


class EnhancedTradingSystem:
    """
    Production-ready enhanced trading system with real IQOption integration
    """

    def __init__(self, config: TradingConfig, dry_run: bool = True):
        self.config = config
        self.dry_run = dry_run
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.api = None
        self.db = TradeDatabase(config.DB_PATH)
        self.market_analyzer = MarketContextAnalyzer()
        self.technical_indicators = TechnicalIndicators()
        
        # AI Components
        if ENHANCED_FEATURES:
            self.consensus_engine = EnhancedConsensusEngine(config.CONSENSUS_THRESHOLD)
            self.position_sizer = KellyPositionSizer(config.__dict__)
            self.explainability = ExplainabilityEngine()
        else:
            self.consensus_engine = AIConsensusEngine(config.CONSENSUS_THRESHOLD)
            self.position_sizer = None
            self.explainability = None
        
        # Performance tracking
        self.session_stats = {
            'trades_executed': 0,
            'trades_won': 0,
            'trades_lost': 0,
            'total_profit': 0.0,
            'start_time': datetime.now(),
            'errors': []
        }
        
        self.logger.info(f"Enhanced Trading System initialized (DRY RUN: {dry_run})")

    def connect_to_iqoption(self) -> bool:
        """Connect to IQOption with proper error handling"""
        try:
            self.logger.info("Connecting to IQOption...")
            
            if not self.config.EMAIL or not self.config.PASSWORD:
                raise ValueError("IQOption credentials not set. Please set IQOPTION_EMAIL and IQOPTION_PASSWORD environment variables.")
            
            self.api = IQ_Option(self.config.EMAIL, self.config.PASSWORD)
            check, reason = self.api.connect()
            
            if not check:
                raise ConnectionError(f"IQOption connection failed: {reason}")
            
            # Set account type
            account_type = 'PRACTICE' if self.dry_run or self.config.ACCOUNT_TYPE.lower() == 'demo' else 'REAL'
            self.api.change_balance(account_type)
            time.sleep(1)
            
            # Verify connection
            balance = self.api.get_balance()
            if balance is None:
                raise ConnectionError("Could not retrieve balance")
            
            self.logger.info(f"✅ Connected to IQOption")
            self.logger.info(f"Account Type: {account_type}")
            self.logger.info(f"Balance: ${balance:.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Connection failed: {e}")
            return False

    def initialize_ai_models(self):
        """Initialize available AI models"""
        models_loaded = 0
        
        # Load OpenAI model
        if self.config.USE_OPENAI and 'openai' in AI_MODELS_AVAILABLE:
            try:
                if os.getenv('OPENAI_API_KEY'):
                    openai_model = AI_MODELS_AVAILABLE['openai'](self.config.OPENAI_MODEL)
                    self.consensus_engine.add_model(openai_model, weight=self.config.OPENAI_WEIGHT)
                    models_loaded += 1
                    self.logger.info(f"✅ OpenAI model loaded: {self.config.OPENAI_MODEL}")
                else:
                    self.logger.warning("⚠️ OPENAI_API_KEY not set")
            except Exception as e:
                self.logger.error(f"❌ OpenAI model failed: {e}")
        
        # Load Claude model
        if self.config.USE_CLAUDE and 'claude' in AI_MODELS_AVAILABLE:
            try:
                if os.getenv('ANTHROPIC_API_KEY'):
                    claude_model = AI_MODELS_AVAILABLE['claude'](self.config.CLAUDE_MODEL)
                    self.consensus_engine.add_model(claude_model, weight=self.config.CLAUDE_WEIGHT)
                    models_loaded += 1
                    self.logger.info(f"✅ Claude model loaded: {self.config.CLAUDE_MODEL}")
                else:
                    self.logger.warning("⚠️ ANTHROPIC_API_KEY not set")
            except Exception as e:
                self.logger.error(f"❌ Claude model failed: {e}")
        
        # Load DeepSeek model
        if self.config.USE_DEEPSEEK and 'deepseek' in AI_MODELS_AVAILABLE:
            try:
                if os.getenv('DEEPSEEK_API_KEY'):
                    deepseek_model = AI_MODELS_AVAILABLE['deepseek'](self.config.DEEPSEEK_MODEL)
                    self.consensus_engine.add_model(deepseek_model, weight=self.config.DEEPSEEK_WEIGHT)
                    models_loaded += 1
                    self.logger.info(f"✅ DeepSeek model loaded: {self.config.DEEPSEEK_MODEL}")
                else:
                    self.logger.warning("⚠️ DEEPSEEK_API_KEY not set")
            except Exception as e:
                self.logger.error(f"❌ DeepSeek model failed: {e}")
        
        if models_loaded == 0:
            self.logger.warning("⚠️ No AI models loaded! Using fallback technical analysis.")
            return False
        
        self.logger.info(f"📊 Loaded {models_loaded} AI models")
        return True

    def get_market_data(self, pair: str) -> Optional[Dict]:
        """Get real market data from IQOption"""
        try:
            if self.dry_run:
                # Simulate market data for testing
                return self._simulate_market_data(pair)
            
            # Get real candles from IQOption
            current_time = int(time.time())
            candles = self.api.get_candles(pair, 60, self.config.CANDLE_COUNT, current_time)
            
            if not candles or len(candles) < 20:
                self.logger.warning(f"Insufficient candle data for {pair}")
                return None
            
            # Calculate technical indicators
            market_data = {
                'pair': pair,
                'current_price': candles[-1]['close'],
                'timestamp': datetime.now().isoformat(),
                
                # Technical indicators
                'rsi_14': self.technical_indicators.rsi(candles, 14),
                'rsi_7': self.technical_indicators.rsi(candles, 7),
                'macd': self.technical_indicators.macd(candles),
                'bb_position': self.technical_indicators.bollinger_bands(candles)['position'],
                'stochastic': self.technical_indicators.stochastic(candles),
                'adx': self.technical_indicators.adx(candles),
                'atr': self.technical_indicators.atr(candles),
                'cci': self.technical_indicators.cci(candles),
                'williams_r': self.technical_indicators.williams_r(candles),
                
                # Market analysis
                'trend': self.technical_indicators.identify_trend(candles),
                'volatility': self.technical_indicators.calculate_volatility(candles)[0],
                'volatility_value': self.technical_indicators.calculate_volatility(candles)[1],
                'support': self.technical_indicators.find_support_resistance(candles)[0],
                'resistance': self.technical_indicators.find_support_resistance(candles)[1],
                'candlestick_pattern': self.technical_indicators.detect_candlestick_pattern(candles),
                
                # Time context
                'hour': datetime.now().hour,
                'day_of_week': datetime.now().weekday()
            }
            
            self.logger.info(f"📊 Market data retrieved for {pair}")
            self.logger.info(f"   Price: ${market_data['current_price']:.6f}")
            self.logger.info(f"   Trend: {market_data['trend']}")
            self.logger.info(f"   RSI(14): {market_data['rsi_14']:.1f}")
            self.logger.info(f"   Volatility: {market_data['volatility']}")
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"❌ Error getting market data for {pair}: {e}")
            return None

    def _simulate_market_data(self, pair: str) -> Dict:
        """Simulate market data for testing"""
        import random
        
        base_price = 0.5685 if 'AUD' in pair else 1.0850
        
        return {
            'pair': pair,
            'current_price': base_price + random.uniform(-0.001, 0.001),
            'timestamp': datetime.now().isoformat(),
            'rsi_14': random.uniform(30, 70),
            'rsi_7': random.uniform(25, 75),
            'macd': {'macd': random.uniform(-0.0001, 0.0001), 'signal': random.uniform(-0.0001, 0.0001), 'histogram': random.uniform(-0.0001, 0.0001)},
            'bb_position': random.uniform(0.2, 0.8),
            'stochastic': {'k': random.uniform(20, 80), 'd': random.uniform(20, 80)},
            'adx': random.uniform(15, 35),
            'atr': random.uniform(0.0001, 0.0005),
            'cci': random.uniform(-100, 100),
            'williams_r': random.uniform(-80, -20),
            'trend': random.choice(['uptrend', 'downtrend', 'sideways']),
            'volatility': random.choice(['low', 'medium', 'high']),
            'volatility_value': random.uniform(0.5, 2.0),
            'support': base_price - random.uniform(0.001, 0.003),
            'resistance': base_price + random.uniform(0.001, 0.003),
            'candlestick_pattern': random.choice(['doji', 'hammer', 'none']),
            'hour': datetime.now().hour,
            'day_of_week': datetime.now().weekday()
        }

    def execute_trade(self, pair: str, duration: int = 1) -> Optional[Dict]:
        """Execute a complete trade with AI analysis"""
        try:
            self.logger.info(f"\n🚀 Executing trade on {pair}")
            
            # Step 1: Get market data
            market_data = self.get_market_data(pair)
            if not market_data:
                return None
            
            # Step 2: Get AI consensus
            if hasattr(self.consensus_engine, 'models') and len(self.consensus_engine.models) > 0:
                consensus = self.consensus_engine.get_consensus_signal(market_data)
                
                # Print consensus summary
                if hasattr(self.consensus_engine, 'print_consensus_summary'):
                    self.consensus_engine.print_consensus_summary(consensus)
                else:
                    self.logger.info(f"AI Consensus: {consensus['signal']} ({consensus['confidence']:.1f}%)")
                
                # Check consensus
                if not consensus.get('consensus_reached', False):
                    self.logger.warning("❌ No AI consensus reached")
                    return None
                
                confidence_key = 'confidence_calibrated' if 'confidence_calibrated' in consensus else 'confidence'
                if consensus[confidence_key] < self.config.MIN_CONFIDENCE:
                    self.logger.warning(f"❌ Confidence {consensus[confidence_key]:.1f}% below threshold {self.config.MIN_CONFIDENCE}%")
                    return None
                
                signal = consensus['signal']
                confidence = consensus[confidence_key]
                
            else:
                # Fallback to simple technical analysis
                self.logger.warning("Using fallback technical analysis")
                signal, confidence = self._fallback_signal_generation(market_data)
                if not signal:
                    return None
            
            # Step 3: Calculate position size
            if self.position_sizer and ENHANCED_FEATURES:
                recent_trades = self.db.get_recent_trades(100)
                historical_performance = self._calculate_historical_performance(recent_trades)
                
                position_info = self.position_sizer.calculate_position(
                    confidence=confidence,
                    balance=self.api.get_balance() if self.api else 10000,
                    ai_consensus={'confidence_calibrated': confidence},
                    historical_performance=historical_performance
                )
                amount = position_info['amount']
                self.logger.info(f"💵 Kelly position size: ${amount:.2f}")
            else:
                # Simple position sizing
                balance = self.api.get_balance() if self.api else 10000
                amount = min(self.config.BASE_AMOUNT * (confidence / 100), self.config.MAX_AMOUNT)
                amount = max(self.config.MIN_AMOUNT, amount)
                self.logger.info(f"💵 Simple position size: ${amount:.2f}")
            
            # Step 4: Execute trade
            trade_result = self._execute_trade_order(pair, signal, amount, duration)
            
            if trade_result and trade_result.get('success'):
                # Store trade in database
                trade_data = {
                    'trade_id': trade_result['order_id'],
                    'timestamp': datetime.now().isoformat(),
                    'pair': pair,
                    'direction': signal,
                    'amount': amount,
                    'duration': duration,
                    'result': 'PENDING',
                    'ai_signal_confidence': int(confidence),
                    'entry_price': market_data['current_price'],
                    'rsi_14': market_data['rsi_14'],
                    'trend': market_data['trend'],
                    'volatility': market_data['volatility'],
                    'strategy_version': 'enhanced_v2.0'
                }
                
                self.db.insert_trade(trade_data)
                self.session_stats['trades_executed'] += 1
                
                self.logger.info(f"✅ Trade executed: {signal} ${amount:.2f}")
                return trade_result
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Trade execution error: {e}")
            self.session_stats['errors'].append(str(e))
            return None

    def _fallback_signal_generation(self, market_data: Dict) -> tuple:
        """Fallback signal generation using technical analysis"""
        try:
            rsi = market_data.get('rsi_14', 50)
            trend = market_data.get('trend', 'sideways')
            bb_position = market_data.get('bb_position', 0.5)
            
            # Simple signal logic
            if rsi < 30 and trend != 'downtrend':
                return 'CALL', 70
            elif rsi > 70 and trend != 'uptrend':
                return 'PUT', 70
            elif bb_position < 0.2 and trend == 'uptrend':
                return 'CALL', 65
            elif bb_position > 0.8 and trend == 'downtrend':
                return 'PUT', 65
            else:
                return None, 0
                
        except Exception as e:
            self.logger.error(f"Fallback signal generation error: {e}")
            return None, 0

    def _execute_trade_order(self, pair: str, signal: str, amount: float, duration: int) -> Optional[Dict]:
        """Execute the actual trade order"""
        try:
            if self.dry_run:
                # Simulate trade execution
                import random
                order_id = f"SIM_{int(time.time())}"
                success = True
                self.logger.info(f"[SIMULATED] {signal} trade on {pair} for ${amount:.2f}")
                
                # Simulate trade result after duration
                time.sleep(2)  # Quick simulation
                is_win = random.random() < 0.6  # 60% win rate for simulation
                profit = amount * 0.8 if is_win else -amount
                
                return {
                    'success': success,
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
                status, order_id = self.api.buy(amount, pair, signal.lower(), duration)
                
                if status and order_id:
                    self.logger.info(f"✅ Real trade executed: Order ID {order_id}")
                    return {
                        'success': True,
                        'order_id': str(order_id),
                        'pair': pair,
                        'signal': signal,
                        'amount': amount,
                        'simulated': False
                    }
                else:
                    self.logger.error("❌ Trade execution failed")
                    return None
                    
        except Exception as e:
            self.logger.error(f"❌ Trade order execution error: {e}")
            return None

    def _calculate_historical_performance(self, trades: List[Dict]) -> Dict:
        """Calculate historical performance metrics"""
        if not trades:
            return {'win_rate': 0.55, 'avg_payout': 1.8}
        
        wins = sum(1 for t in trades if t.get('result') == 'WIN')
        total = len(trades)
        win_rate = wins / total if total > 0 else 0.55
        
        return {
            'win_rate': win_rate,
            'avg_payout': 1.8,
            'total_trades': total,
            'wins': wins,
            'losses': total - wins
        }

    def run_trading_session(self, max_trades: int = 5, pairs: List[str] = None) -> Dict:
        """Run a complete trading session"""
        if not pairs:
            pairs = ['EURUSD-OTC', 'GBPUSD-OTC', 'AUDCHF-OTC']
        
        self.logger.info(f"\n🚀 Starting Enhanced Trading Session")
        self.logger.info(f"Max trades: {max_trades}")
        self.logger.info(f"Pairs: {', '.join(pairs)}")
        self.logger.info(f"Mode: {'SIMULATION' if self.dry_run else 'LIVE TRADING'}")
        
        try:
            # Connect to IQOption
            if not self.connect_to_iqoption():
                return {'success': False, 'error': 'Connection failed'}
            
            # Initialize AI models
            self.initialize_ai_models()
            
            # Execute trades
            for i in range(max_trades):
                for pair in pairs:
                    if self.session_stats['trades_executed'] >= max_trades:
                        break
                    
                    self.logger.info(f"\n--- Trade {self.session_stats['trades_executed'] + 1}/{max_trades} ---")
                    
                    result = self.execute_trade(pair)
                    
                    if result and result.get('success'):
                        # Update session stats
                        if result.get('simulated'):
                            if result['result'] == 'WIN':
                                self.session_stats['trades_won'] += 1
                            else:
                                self.session_stats['trades_lost'] += 1
                            self.session_stats['total_profit'] += result.get('profit', 0)
                    
                    # Wait between trades
                    time.sleep(5)
                
                if self.session_stats['trades_executed'] >= max_trades:
                    break
            
            # Print session summary
            self._print_session_summary()
            
            return {
                'success': True,
                'stats': self.session_stats
            }
            
        except Exception as e:
            self.logger.error(f"❌ Session error: {e}")
            return {'success': False, 'error': str(e)}

    def _print_session_summary(self):
        """Print trading session summary"""
        duration = (datetime.now() - self.session_stats['start_time']).seconds / 60
        
        print("\n" + "=" * 80)
        print("📊 ENHANCED TRADING SESSION SUMMARY")
        print("=" * 80)
        
        print(f"\n⏱️  Duration: {duration:.1f} minutes")
        print(f"📈 Trades Executed: {self.session_stats['trades_executed']}")
        print(f"✅ Wins: {self.session_stats['trades_won']}")
        print(f"❌ Losses: {self.session_stats['trades_lost']}")
        
        if self.session_stats['trades_executed'] > 0:
            win_rate = self.session_stats['trades_won'] / self.session_stats['trades_executed'] * 100
            print(f"🎯 Win Rate: {win_rate:.1f}%")
        
        print(f"💰 Total P/L: ${self.session_stats['total_profit']:+.2f}")
        
        if self.session_stats['errors']:
            print(f"\n⚠️  Errors: {len(self.session_stats['errors'])}")
            for error in self.session_stats['errors'][:3]:
                print(f"   • {error}")
        
        print(f"\n📁 Database: {self.config.DB_PATH}")
        print("\n" + "=" * 80)

    def test_connection(self) -> bool:
        """Test IQOption connection"""
        print("\n🔍 Testing IQOption Connection...")
        
        if self.connect_to_iqoption():
            print("✅ Connection test successful!")
            
            # Test market data
            print("\n📊 Testing market data retrieval...")
            market_data = self.get_market_data('EURUSD-OTC')
            if market_data:
                print("✅ Market data test successful!")
                print(f"   Current price: ${market_data['current_price']:.6f}")
                print(f"   RSI(14): {market_data['rsi_14']:.1f}")
                return True
            else:
                print("❌ Market data test failed!")
                return False
        else:
            print("❌ Connection test failed!")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Enhanced AI Trading System')
    parser.add_argument('--mode', choices=['demo', 'live'], default='demo',
                        help='Trading mode (demo=simulation, live=real trading)')
    parser.add_argument('--max-trades', type=int, default=5,
                        help='Maximum number of trades to execute')
    parser.add_argument('--pairs', nargs='+', default=['EURUSD-OTC', 'GBPUSD-OTC'],
                        help='Trading pairs to use')
    parser.add_argument('--test-connection', action='store_true',
                        help='Test connection and exit')
    parser.add_argument('--confirm', action='store_true',
                        help='Required confirmation for live trading')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    
    # Safety check for live trading
    if args.mode == 'live' and not args.confirm:
        print("❌ ERROR: Live trading requires --confirm flag")
        print("Example: python scripts/run_enhanced_trading.py --mode live --confirm")
        sys.exit(1)
    
    if args.mode == 'live':
        print("\n" + "!" * 80)
        print("⚠️  WARNING: LIVE TRADING MODE")
        print("!" * 80)
        response = input("Are you sure you want to trade with real money? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted")
            sys.exit(0)
    
    # Create directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    try:
        # Validate configuration
        TradingConfig.validate()
        TradingConfig.display()
        
        # Initialize system
        system = EnhancedTradingSystem(TradingConfig, dry_run=(args.mode == 'demo'))
        
        # Test connection if requested
        if args.test_connection:
            success = system.test_connection()
            sys.exit(0 if success else 1)
        
        # Run trading session
        result = system.run_trading_session(
            max_trades=args.max_trades,
            pairs=args.pairs
        )
        
        if result['success']:
            logger.info("✅ Trading session completed successfully!")
        else:
            logger.error(f"❌ Trading session failed: {result.get('error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⚠️ Session interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()