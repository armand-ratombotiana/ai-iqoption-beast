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
#!/usr/bin/env python3
"""
Unified Trading System Entry Point
Single entry point for all trading modes with comprehensive testing

Usage:
    python run_trading_system.py --help
    python run_trading_system.py --mode basic --demo
    python run_trading_system.py --mode enhanced --demo
    python run_trading_system.py --mode parallel --demo
    python run_trading_system.py --test-all
    python run_trading_system.py --mode enhanced --live --confirm
"""
import os
import sys
import argparse
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Core imports
from config.settings import TradingConfig

# Setup logging
def setup_logging(mode: str):
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    log_file = f'logs/unified_trading_{mode}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


class UnifiedTradingSystem:
    """
    Unified entry point for all trading systems
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.available_modes = {
            'basic': 'Basic Trading System (Single pair, simple AI)',
            'enhanced': 'Enhanced Trading System (Multi-AI, advanced features)',
            'parallel': 'Parallel Trading System (Multiple pairs simultaneously)'
        }
    
    def display_welcome(self):
        """Display welcome message and available modes"""
        print("\n" + "=" * 80)
        print("🚀 UNIFIED BINARY OPTIONS TRADING SYSTEM")
        print("=" * 80)
        
        print(f"\n📋 Available Trading Modes:")
        for mode, description in self.available_modes.items():
            print(f"   • {mode.upper()}: {description}")
        
        print(f"\n⚙️  Configuration Status:")
        try:
            TradingConfig.validate()
            print("   ✅ Configuration valid")
        except ValueError as e:
            print(f"   ❌ Configuration error: {e}")
            return False
        
        # Check API keys
        api_keys = {
            'IQOption': bool(os.getenv('IQOPTION_EMAIL') and os.getenv('IQOPTION_PASSWORD')),
            'OpenAI': bool(os.getenv('OPENAI_API_KEY')),
            'Claude': bool(os.getenv('ANTHROPIC_API_KEY')),
            'DeepSeek': bool(os.getenv('DEEPSEEK_API_KEY'))
        }
        
        print(f"\n🔑 API Keys Status:")
        for service, available in api_keys.items():
            status = "✅" if available else "❌"
            print(f"   {status} {service}")
        
        if not api_keys['IQOption']:
            print("\n⚠️  WARNING: IQOption credentials not set!")
            print("   Set IQOPTION_EMAIL and IQOPTION_PASSWORD environment variables")
        
        print("\n" + "=" * 80)
        return True
    
    async def run_basic_trading(self, demo: bool = True, **kwargs) -> Dict:
        """Run basic trading system"""
        try:
            from src.scripts.run_trading import AdvancedTradingSystem

            self.logger.info("🔄 Starting Basic Trading System...")

            system = AdvancedTradingSystem(TradingConfig)

            # Execute single trade
            result = system.execute_trade(
                pair=kwargs.get('pair', 'AUDCHF-OTC'),
                duration=kwargs.get('duration', 1)
            )

            if result:
                self.logger.info("✅ Basic trading completed successfully")
                return {'success': True, 'result': result}
            else:
                self.logger.error("❌ Basic trading failed")
                return {'success': False, 'error': 'Trade execution failed'}

        except Exception as e:
            self.logger.error(f"❌ Basic trading error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_enhanced_trading(self, demo: bool = True, **kwargs) -> Dict:
        """Run enhanced trading system"""
        try:
            # Import enhanced system
            from src.scripts.run_enhanced_trading import EnhancedTradingSystem

            self.logger.info("🔄 Starting Enhanced Trading System...")

            system = EnhancedTradingSystem(TradingConfig, dry_run=demo)

            # Run trading session
            result = system.run_trading_session(
                max_trades=kwargs.get('max_trades', 3),
                pairs=kwargs.get('pairs', ['EURUSD-OTC', 'GBPUSD-OTC'])
            )

            return result

        except Exception as e:
            self.logger.error(f"❌ Enhanced trading error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_parallel_trading(self, demo: bool = True, **kwargs) -> Dict:
        """Run parallel trading system"""
        try:
            # Import parallel system
            from src.scripts.run_parallel_trading import ParallelTradingSystem

            self.logger.info("🔄 Starting Parallel Trading System...")

            system = ParallelTradingSystem(TradingConfig, dry_run=demo)

            # Run parallel session
            result = await system.run_parallel_trading_session(
                duration_minutes=kwargs.get('duration', 30)
            )

            return result

        except Exception as e:
            self.logger.error(f"❌ Parallel trading error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def test_all_systems(self) -> Dict:
        """Test all trading systems"""
        self.logger.info("🧪 Testing All Trading Systems...")
        
        test_results = {
            'basic': {'tested': False, 'success': False, 'error': None},
            'enhanced': {'tested': False, 'success': False, 'error': None},
            'parallel': {'tested': False, 'success': False, 'error': None}
        }
        
        # Test Basic System
        try:
            self.logger.info("Testing Basic Trading System...")
            result = await self.run_basic_trading(demo=True, pair='EURUSD-OTC')
            test_results['basic'] = {
                'tested': True,
                'success': result.get('success', False),
                'error': result.get('error')
            }
        except Exception as e:
            test_results['basic'] = {
                'tested': True,
                'success': False,
                'error': str(e)
            }
        
        # Test Enhanced System
        try:
            self.logger.info("Testing Enhanced Trading System...")
            result = await self.run_enhanced_trading(demo=True, max_trades=1)
            test_results['enhanced'] = {
                'tested': True,
                'success': result.get('success', False),
                'error': result.get('error')
            }
        except Exception as e:
            test_results['enhanced'] = {
                'tested': True,
                'success': False,
                'error': str(e)
            }
        
        # Test Parallel System
        try:
            self.logger.info("Testing Parallel Trading System...")
            result = await self.run_parallel_trading(demo=True, duration=5)
            test_results['parallel'] = {
                'tested': True,
                'success': result.get('success', False),
                'error': result.get('error')
            }
        except Exception as e:
            test_results['parallel'] = {
                'tested': True,
                'success': False,
                'error': str(e)
            }
        
        # Print test summary
        self._print_test_summary(test_results)
        
        return test_results
    
    def _print_test_summary(self, results: Dict):
        """Print test results summary"""
        print("\n" + "=" * 80)
        print("🧪 SYSTEM TEST RESULTS")
        print("=" * 80)
        
        for system, result in results.items():
            if result['tested']:
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                print(f"\n{system.upper()} System: {status}")
                if result['error']:
                    print(f"   Error: {result['error']}")
            else:
                print(f"\n{system.upper()} System: ⚠️ NOT TESTED")
        
        # Overall summary
        total_tested = sum(1 for r in results.values() if r['tested'])
        total_passed = sum(1 for r in results.values() if r['success'])
        
        print(f"\n📊 Summary: {total_passed}/{total_tested} systems passed")
        print("=" * 80)
    
    async def run_system(self, mode: str, demo: bool = True, **kwargs) -> Dict:
        """Run specified trading system"""
        if mode not in self.available_modes:
            raise ValueError(f"Unknown mode: {mode}. Available: {list(self.available_modes.keys())}")
        
        if mode == 'basic':
            return await self.run_basic_trading(demo=demo, **kwargs)
        elif mode == 'enhanced':
            return await self.run_enhanced_trading(demo=demo, **kwargs)
        elif mode == 'parallel':
            return await self.run_parallel_trading(demo=demo, **kwargs)


async def main():
    """Main async entry point"""
    parser = argparse.ArgumentParser(
        description='Unified Binary Options Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_trading_system.py --mode basic --demo
  python run_trading_system.py --mode enhanced --demo --max-trades 5
  python run_trading_system.py --mode parallel --demo --duration 30
  python run_trading_system.py --test-all
  python run_trading_system.py --mode enhanced --live --confirm
        """
    )
    
    parser.add_argument('--mode', choices=['basic', 'enhanced', 'parallel'],
                        help='Trading system mode')
    parser.add_argument('--demo', action='store_true', default=True,
                        help='Run in demo mode (default)')
    parser.add_argument('--live', action='store_true',
                        help='Run in live trading mode')
    parser.add_argument('--confirm', action='store_true',
                        help='Required confirmation for live trading')
    parser.add_argument('--test-all', action='store_true',
                        help='Test all trading systems')
    
    # Mode-specific arguments
    parser.add_argument('--pair', default='EURUSD-OTC',
                        help='Trading pair for basic mode')
    parser.add_argument('--max-trades', type=int, default=3,
                        help='Maximum trades for enhanced mode')
    parser.add_argument('--duration', type=int, default=30,
                        help='Session duration in minutes for parallel mode')
    
    args = parser.parse_args()
    
    # Determine demo/live mode
    if args.live:
        demo_mode = False
        if not args.confirm:
            print("❌ ERROR: Live trading requires --confirm flag")
            sys.exit(1)
    else:
        demo_mode = True
    
    # Setup logging
    mode_name = args.mode if args.mode else 'test'
    logger = setup_logging(mode_name)
    
    # Create directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    try:
        # Initialize unified system
        unified_system = UnifiedTradingSystem()
        
        # Display welcome
        if not unified_system.display_welcome():
            sys.exit(1)
        
        # Safety check for live trading
        if not demo_mode:
            print("\n" + "!" * 80)
            print("⚠️  WARNING: LIVE TRADING MODE")
            print("!" * 80)
            response = input("Are you sure you want to trade with real money? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted")
                sys.exit(0)
        
        # Run requested operation
        if args.test_all:
            results = await unified_system.test_all_systems()
            # Exit with error code if any tests failed
            failed_tests = sum(1 for r in results.values() if r['tested'] and not r['success'])
            sys.exit(failed_tests)
        
        elif args.mode:
            result = await unified_system.run_system(
                mode=args.mode,
                demo=demo_mode,
                pair=args.pair,
                max_trades=args.max_trades,
                duration=args.duration
            )
            
            if result['success']:
                logger.info(f"✅ {args.mode.upper()} trading completed successfully!")
            else:
                logger.error(f"❌ {args.mode.upper()} trading failed: {result.get('error')}")
                sys.exit(1)
        
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⚠️ Operation interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())#!/usr/bin/env python3
"""
🚀 UNIFIED BINARY OPTIONS TRADING SYSTEM - 24/7 DOCKER READY
Production-grade trading system with robust error handling and monitoring

Features:
- Automatic reconnection on failures
- Health monitoring
- Graceful shutdown
- Connection pooling
- Error recovery
- 24/7 operation ready
"""

import os
import sys
import argparse
import time
import json
import asyncio
import logging
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Core imports
try:
    from iqoptionapi.stable_api import IQ_Option
except ImportError:
    print("❌ IQOption API not installed. Run: pip install iqoptionapi")
    sys.exit(1)

from config.settings import TradingConfig
from database.trade_storage import TradeDatabase
from analysis.technical_indicators import TechnicalIndicators
from analysis.market_context import MarketContextAnalyzer

# AI Models (optional)
AI_MODELS = {}
try:
    from ai_models.openai_model import OpenAIModel
    AI_MODELS['openai'] = OpenAIModel
except ImportError:
    pass

try:
    from ai_models.claude_model import ClaudeModel
    AI_MODELS['claude'] = ClaudeModel
except ImportError:
    pass

try:
    from ai_models.deepseek_model import DeepSeekModel
    AI_MODELS['deepseek'] = DeepSeekModel
except ImportError:
    pass

try:
    from ai_models.free_ai_model import FreeAIModel
    AI_MODELS['free_ai'] = FreeAIModel
except ImportError:
    pass

try:
    from ai_models.consensus_engine import AIConsensusEngine
except ImportError:
    AIConsensusEngine = None


# Global flag for graceful shutdown
SHUTDOWN_FLAG = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global SHUTDOWN_FLAG
    SHUTDOWN_FLAG = True
    print("\n⚠️  Shutdown signal received. Finishing current trade...")

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# Setup logging
def setup_logging(mode: str):
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    log_file = f'logs/unified_{mode}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


class RobustTradingSystem:
    """
    Production-grade trading system with 24/7 operation capabilities
    """
    
    def __init__(self, config: TradingConfig, mode: str = 'basic'):
        self.config = config
        self.mode = mode
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Connection management
        self.api = None
        self.connection_retries = 0
        self.max_retries = 5
        self.retry_delay = 10  # seconds
        
        # Core components
        self.db = TradeDatabase(config.DB_PATH)
        self.technical_indicators = TechnicalIndicators()
        self.market_analyzer = MarketContextAnalyzer()
        
        # AI Components
        if AIConsensusEngine and len(AI_MODELS) > 0:
            self.consensus_engine = AIConsensusEngine(config.CONSENSUS_THRESHOLD)
            self._setup_ai_models()
        else:
            self.consensus_engine = None
            self.logger.warning("⚠️  AI models not available, using technical analysis only")
        
        # Health monitoring
        self.health_status = {
            'api_connected': False,
            'last_successful_trade': None,
            'consecutive_errors': 0,
            'total_trades': 0,
            'uptime_start': datetime.now()
        }
        
        # Session stats
        self.session_stats = {
            'trades_executed': 0,
            'trades_won': 0,
            'trades_lost': 0,
            'total_profit': 0.0,
            'start_time': datetime.now(),
            'errors': 0,
            'reconnections': 0
        }
    
    def _setup_ai_models(self):
        """Initialize AI models with error handling"""
        self.logger.info("🤖 Initializing AI Models...")
        
        models_loaded = 0
        
        if self.config.USE_OPENAI and 'openai' in AI_MODELS and os.getenv('OPENAI_API_KEY'):
            try:
                model = AI_MODELS['openai'](self.config.OPENAI_MODEL)
                self.consensus_engine.add_model(model, weight=self.config.OPENAI_WEIGHT)
                models_loaded += 1
                self.logger.info(f"✅ OpenAI loaded")
            except Exception as e:
                self.logger.error(f"❌ OpenAI failed: {e}")
        
        if self.config.USE_CLAUDE and 'claude' in AI_MODELS and os.getenv('ANTHROPIC_API_KEY'):
            try:
                model = AI_MODELS['claude'](self.config.CLAUDE_MODEL)
                self.consensus_engine.add_model(model, weight=self.config.CLAUDE_WEIGHT)
                models_loaded += 1
                self.logger.info(f"✅ Claude loaded")
            except Exception as e:
                self.logger.error(f"❌ Claude failed: {e}")
        
        if self.config.USE_DEEPSEEK and 'deepseek' in AI_MODELS and os.getenv('DEEPSEEK_API_KEY'):
            try:
                model = AI_MODELS['deepseek'](self.config.DEEPSEEK_MODEL)
                self.consensus_engine.add_model(model, weight=self.config.DEEPSEEK_WEIGHT)
                models_loaded += 1
                self.logger.info(f"✅ DeepSeek loaded")
            except Exception as e:
                self.logger.error(f"❌ DeepSeek failed: {e}")
        
        if self.config.USE_FREE_AI and 'free_ai' in AI_MODELS:
            try:
                model = AI_MODELS['free_ai'](self.config.FREE_AI_TYPE)
                self.consensus_engine.add_model(model, weight=self.config.FREE_AI_WEIGHT)
                models_loaded += 1
                self.logger.info(f"✅ Free AI loaded (type: {self.config.FREE_AI_TYPE})")
            except Exception as e:
                self.logger.error(f"❌ Free AI failed: {e}")
        
        self.logger.info(f"📊 {models_loaded} AI models active")
    
    def connect_to_iqoption(self, force_reconnect: bool = False) -> bool:
        """
        Connect to IQOption with retry logic and connection pooling
        """
        if self.api and self.health_status['api_connected'] and not force_reconnect:
            # Connection exists and is healthy
            return True
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"🔌 Connecting to IQOption (attempt {attempt}/{self.max_retries})...")
                
                if not self.config.EMAIL or not self.config.PASSWORD:
                    raise ValueError("IQOption credentials not set")
                
                # Create new API instance
                self.api = IQ_Option(self.config.EMAIL, self.config.PASSWORD)
                check, reason = self.api.connect()
                
                if not check:
                    raise ConnectionError(f"Connection failed: {reason}")
                
                # Set account type
                account_type = 'PRACTICE' if self.config.ACCOUNT_TYPE.lower() == 'demo' else 'REAL'
                self.api.change_balance(account_type)
                time.sleep(1)
                
                # Verify connection
                balance = self.api.get_balance()
                if balance is None:
                    raise ConnectionError("Could not retrieve balance")
                
                self.logger.info(f"✅ Connected - {account_type} - Balance: ${balance:.2f}")
                self.health_status['api_connected'] = True
                self.connection_retries = 0
                
                if force_reconnect:
                    self.session_stats['reconnections'] += 1
                
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Connection attempt {attempt} failed: {e}")
                self.health_status['api_connected'] = False
                self.connection_retries += 1
                
                if attempt < self.max_retries:
                    self.logger.info(f"⏳ Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"❌ Max retries ({self.max_retries}) reached")
                    return False
        
        return False
    
    def check_connection_health(self) -> bool:
        """Check if connection is healthy"""
        try:
            if not self.api:
                return False
            
            # Try to get balance as health check
            balance = self.api.get_balance()
            return balance is not None
        except:
            return False
    
    def get_market_data(self, pair: str) -> Optional[Dict]:
        """
        Get market data with retry logic and error handling
        """
        for attempt in range(3):
            try:
                self.logger.info(f"📊 Getting market data for {pair}...")
                
                # Check connection health
                if not self.check_connection_health():
                    self.logger.warning("⚠️  Connection unhealthy, reconnecting...")
                    if not self.connect_to_iqoption(force_reconnect=True):
                        return None
                
                # Get candles using safe method
                candles = self.market_analyzer._get_candles_safe(self.api, pair, '1m', 100)
                
                if not candles or len(candles) < 20:
                    self.logger.warning(f"Insufficient candle data (attempt {attempt + 1}/3)")
                    time.sleep(2)
                    continue
                
                # Calculate indicators
                market_data = {
                    'pair': pair,
                    'current_price': candles[-1]['close'],
                    'timestamp': datetime.now().isoformat(),
                    'rsi_14': self.technical_indicators.rsi(candles, 14),
                    'rsi_7': self.technical_indicators.rsi(candles, 7),
                    'macd': self.technical_indicators.macd(candles),
                    'macd_histogram': self.technical_indicators.macd(candles)['histogram'],
                    'bb_position': self.technical_indicators.bollinger_bands(candles)['position'],
                    'stochastic': self.technical_indicators.stochastic(candles),
                    'adx': self.technical_indicators.adx(candles),
                    'atr': self.technical_indicators.atr(candles),
                    'trend': self.technical_indicators.identify_trend(candles),
                    'volatility': self.technical_indicators.calculate_volatility(candles)[0],
                    'support': self.technical_indicators.find_support_resistance(candles)[0],
                    'resistance': self.technical_indicators.find_support_resistance(candles)[1],
                }
                
                self.logger.info(f"   Price: ${market_data['current_price']:.6f}")
                self.logger.info(f"   Trend: {market_data['trend']}, RSI: {market_data['rsi_14']:.1f}")
                
                return market_data
                
            except Exception as e:
                self.logger.error(f"❌ Error getting market data (attempt {attempt + 1}/3): {e}")
                if attempt < 2:
                    time.sleep(2)
                else:
                    self.session_stats['errors'] += 1
        
        return None
    
    def generate_signal(self, market_data: Dict) -> tuple:
        """Generate trading signal with fallback logic"""
        try:
            # Try AI consensus first
            if self.consensus_engine and hasattr(self.consensus_engine, 'models') and len(self.consensus_engine.models) > 0:
                consensus = self.consensus_engine.get_consensus_signal(market_data)
                
                if consensus.get('consensus_reached') and consensus['confidence'] >= self.config.MIN_CONFIDENCE:
                    self.logger.info(f"🤖 AI Signal: {consensus['signal']} ({consensus['confidence']:.1f}%)")
                    return consensus['signal'], consensus['confidence']
            
            # Fallback to technical analysis
            return self._technical_signal(market_data)
            
        except Exception as e:
            self.logger.error(f"❌ Signal generation error: {e}")
            # Last resort fallback
            return self._technical_signal(market_data)
    
    def _technical_signal(self, market_data: Dict) -> tuple:
        """Generate signal using technical analysis"""
        rsi = market_data.get('rsi_14', 50)
        trend = market_data.get('trend', 'sideways')
        bb_position = market_data.get('bb_position', 0.5)
        
        # Enhanced signal logic
        if rsi < 30:
            return 'CALL', 80
        elif rsi > 70:
            return 'PUT', 80
        elif rsi < 40 and trend == 'downtrend':
            return 'CALL', 75
        elif rsi > 60 and trend == 'uptrend':
            return 'PUT', 75
        elif bb_position < 0.2:
            return 'CALL', 70
        elif bb_position > 0.8:
            return 'PUT', 70
        elif trend == 'uptrend' and rsi < 55:
            return 'CALL', 65
        elif trend == 'downtrend' and rsi > 45:
            return 'PUT', 65
        else:
            return None, 0
    
    def execute_trade(self, pair: str, duration: int = 1) -> Optional[Dict]:
        """
        Execute trade with comprehensive error handling
        """
        global SHUTDOWN_FLAG
        
        if SHUTDOWN_FLAG:
            self.logger.info("⚠️  Shutdown in progress, skipping trade")
            return {'success': False, 'error': 'Shutdown requested'}
        
        try:
            self.logger.info(f"\n{'='*70}")
            self.logger.info(f"🚀 Executing trade on {pair}")
            
            # Get market data
            market_data = self.get_market_data(pair)
            if not market_data:
                return {'success': False, 'error': 'Market data unavailable'}
            
            # Generate signal
            signal, confidence = self.generate_signal(market_data)
            if not signal:
                self.logger.warning("❌ No trading signal generated")
                return {'success': False, 'error': 'No signal'}
            
            # Calculate position size
            balance = self.api.get_balance()
            amount = self.config.BASE_AMOUNT * (confidence / 100)
            amount = max(self.config.MIN_AMOUNT, min(amount, self.config.MAX_AMOUNT))
            amount = round(amount, 2)
            
            self.logger.info(f"💵 Position size: ${amount}")
            
            # Execute trade
            self.logger.info(f"📈 Executing {signal} trade...")
            status, order_id = self.api.buy(amount, pair, signal.lower(), duration)
            
            if not status or not order_id:
                self.logger.error("❌ Trade execution failed")
                self.session_stats['errors'] += 1
                return {'success': False, 'error': 'Execution failed'}
            
            self.logger.info(f"✅ Trade executed! Order ID: {order_id}")
            
            # Store in database
            trade_data = {
                'trade_id': str(order_id),
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
                'strategy_version': f'{self.mode}_v4.0_robust'
            }
            
            self.db.insert_trade(trade_data)
            self.session_stats['trades_executed'] += 1
            self.health_status['total_trades'] += 1
            
            # Wait for result
            self.logger.info(f"⏳ Waiting for result ({duration} min)...")
            time.sleep(duration * 60 + 10)
            
            # Check shutdown flag
            if SHUTDOWN_FLAG:
                self.logger.info("⚠️  Shutdown requested, finishing current trade...")
            
            # Get result
            profit = None
            for attempt in range(20):
                try:
                    profit = self.api.check_win_v3(order_id)
                    if profit is not None:
                        break
                except:
                    pass
                time.sleep(0.5)
            
            if profit is not None:
                result = 'WIN' if profit > 0 else 'LOSS'
                self.db.update_trade(str(order_id), {'result': result, 'profit': profit})
                
                if profit > 0:
                    self.session_stats['trades_won'] += 1
                    self.logger.info(f"✅ WIN! Profit: +${profit:.2f}")
                else:
                    self.session_stats['trades_lost'] += 1
                    self.logger.info(f"❌ LOSS! Loss: ${abs(profit):.2f}")
                
                self.session_stats['total_profit'] += profit
                self.health_status['last_successful_trade'] = datetime.now()
                self.health_status['consecutive_errors'] = 0
                
                return {
                    'success': True,
                    'order_id': order_id,
                    'signal': signal,
                    'result': result,
                    'profit': profit
                }
            else:
                self.logger.warning("⚠️  Result not available")
                return {'success': False, 'error': 'Result not available'}
                
        except Exception as e:
            self.logger.error(f"❌ Trade execution error: {e}")
            self.session_stats['errors'] += 1
            self.health_status['consecutive_errors'] += 1
            
            # If too many consecutive errors, try reconnecting
            if self.health_status['consecutive_errors'] >= 3:
                self.logger.warning("⚠️  Too many consecutive errors, reconnecting...")
                self.connect_to_iqoption(force_reconnect=True)
            
            return {'success': False, 'error': str(e)}
    
    def run_basic_mode(self, pair: str, duration: int = 1) -> Dict:
        """Basic mode with error recovery"""
        self.logger.info(f"\n🎯 BASIC MODE - Single Trade")
        
        if not self.connect_to_iqoption():
            return {'success': False, 'error': 'Connection failed'}
        
        result = self.execute_trade(pair, duration)
        
        return result if result else {'success': False}
    
    def print_health_status(self):
        """Print system health status"""
        uptime = (datetime.now() - self.health_status['uptime_start']).seconds / 60
        
        print("\n" + "="*70)
        print("🏥 SYSTEM HEALTH STATUS")
        print("="*70)
        print(f"⏱️  Uptime: {uptime:.1f} minutes")
        print(f"🔌 API Connected: {'✅' if self.health_status['api_connected'] else '❌'}")
        print(f"📊 Total Trades: {self.health_status['total_trades']}")
        print(f"❌ Consecutive Errors: {self.health_status['consecutive_errors']}")
        print(f"🔄 Reconnections: {self.session_stats['reconnections']}")
        if self.health_status['last_successful_trade']:
            print(f"✅ Last Trade: {self.health_status['last_successful_trade'].strftime('%H:%M:%S')}")
        print("="*70)
    
    def print_summary(self):
        """Print session summary"""
        duration = (datetime.now() - self.session_stats['start_time']).seconds / 60
        
        print("\n" + "="*70)
        print("📊 SESSION SUMMARY")
        print("="*70)
        print(f"\n⏱️  Duration: {duration:.1f} minutes")
        print(f"📈 Trades: {self.session_stats['trades_executed']}")
        print(f"✅ Wins: {self.session_stats['trades_won']}")
        print(f"❌ Losses: {self.session_stats['trades_lost']}")
        
        if self.session_stats['trades_executed'] > 0:
            win_rate = self.session_stats['trades_won'] / self.session_stats['trades_executed'] * 100
            print(f"🎯 Win Rate: {win_rate:.1f}%")
        
        print(f"💰 Total P/L: ${self.session_stats['total_profit']:+.2f}")
        print(f"⚠️  Errors: {self.session_stats['errors']}")
        print(f"🔄 Reconnections: {self.session_stats['reconnections']}")
        print(f"\n📁 Database: {self.config.DB_PATH}")
        print("="*70)


def main():
    """Main entry point with robust error handling"""
    parser = argparse.ArgumentParser(
        description='Robust 24/7 Binary Options Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--mode', choices=['basic', 'enhanced', 'parallel'], default='basic')
    parser.add_argument('--pair', default='EURUSD-OTC')
    parser.add_argument('--duration', type=int, default=1)
    parser.add_argument('--loop', action='store_true')
    parser.add_argument('--loop-interval', type=int, default=5)
    parser.add_argument('--max-iterations', type=int, default=None)
    parser.add_argument('--test-connection', action='store_true')
    parser.add_argument('--health-check-interval', type=int, default=10, 
                        help='Health check every N iterations')
    
    args = parser.parse_args()
    
    # Setup
    logger = setup_logging(args.mode)
    os.makedirs('data', exist_ok=True)
    
    global SHUTDOWN_FLAG
    
    try:
        # Validate config
        TradingConfig.validate()
        TradingConfig.display()
        
        # Create robust system
        system = RobustTradingSystem(TradingConfig, mode=args.mode)
        
        print("\n" + "="*70)
        print("🚀 ROBUST 24/7 TRADING SYSTEM - DOCKER READY")
        print("="*70)
        print(f"\nMode: {args.mode.upper()}")
        print(f"Account: {TradingConfig.ACCOUNT_TYPE}")
        print(f"Health Checks: Every {args.health_check_interval} iterations")
        
        # Test connection if requested
        if args.test_connection:
            success = system.connect_to_iqoption()
            system.print_health_status()
            sys.exit(0 if success else 1)
        
        # Loop mode or single execution
        if args.loop:
            logger.info(f"\n🔄 24/7 LOOP MODE: Trading every {args.loop_interval} minutes")
            if args.max_iterations:
                logger.info(f"   Max iterations: {args.max_iterations}")
            else:
                logger.info(f"   Running indefinitely (send SIGTERM to stop)")
            
            iteration = 0
            while not SHUTDOWN_FLAG:
                iteration += 1
                
                # Check max iterations
                if args.max_iterations and iteration > args.max_iterations:
                    logger.info(f"\n✅ Reached max iterations ({args.max_iterations})")
                    break
                
                logger.info(f"\n{'='*70}")
                logger.info(f"🔄 ITERATION {iteration}")
                logger.info(f"{'='*70}")
                
                try:
                    # Run trading
                    result = system.run_basic_mode(args.pair, args.duration)
                    
                    if result and result.get('success'):
                        logger.info(f"✅ Iteration {iteration} completed")
                    else:
                        logger.warning(f"⚠️  Iteration {iteration} had issues")
                
                except Exception as e:
                    logger.error(f"❌ Iteration {iteration} error: {e}")
                    system.session_stats['errors'] += 1
                
                # Health check
                if iteration % args.health_check_interval == 0:
                    system.print_health_status()
                
                # Check shutdown
                if SHUTDOWN_FLAG or (args.max_iterations and iteration >= args.max_iterations):
                    break
                
                # Wait for next iteration
                logger.info(f"\n⏳ Waiting {args.loop_interval} minutes until next trade...")
                next_time = datetime.now() + timedelta(minutes=args.loop_interval)
                logger.info(f"   Next trade at: {next_time.strftime('%H:%M:%S')}")
                
                # Sleep with periodic checks for shutdown
                for _ in range(args.loop_interval * 60):
                    if SHUTDOWN_FLAG:
                        break
                    time.sleep(1)
        else:
            # Single execution
            result = system.run_basic_mode(args.pair, args.duration)
            
            if result.get('success'):
                logger.info("✅ Session completed successfully!")
            else:
                logger.error(f"❌ Session failed: {result.get('error')}")
                sys.exit(1)
        
        # Print final summaries
        system.print_health_status()
        system.print_summary()
        
        logger.info("\n✅ System shutdown gracefully")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Keyboard interrupt received")
        if 'system' in locals():
            system.print_health_status()
            system.print_summary()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()