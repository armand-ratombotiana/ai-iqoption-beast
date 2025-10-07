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
    asyncio.run(main())