#!/usr/bin/env python3
"""
Comprehensive Testing Script for All Trading Systems
Tests all components with real credentials (demo mode)
"""
import os
import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import TradingConfig


class TradingSystemTester:
    """Comprehensive tester for all trading systems"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.test_results = {}
    
    async def test_configuration(self) -> bool:
        """Test system configuration"""
        print("\n🔧 Testing Configuration...")
        
        try:
            TradingConfig.validate()
            print("✅ Configuration validation passed")
            
            # Check required environment variables
            required_vars = ['IQOPTION_EMAIL', 'IQOPTION_PASSWORD']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
                return False
            
            print("✅ Required credentials found")
            return True
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return False
    
    async def test_iqoption_connection(self) -> bool:
        """Test IQOption connection"""
        print("\n🔌 Testing IQOption Connection...")
        
        try:
            from iqoptionapi.stable_api import IQ_Option
            
            api = IQ_Option(TradingConfig.EMAIL, TradingConfig.PASSWORD)
            check, reason = api.connect()
            
            if not check:
                print(f"❌ Connection failed: {reason}")
                return False
            
            api.change_balance('PRACTICE')
            balance = api.get_balance()
            
            if balance is None:
                print("❌ Could not retrieve balance")
                return False
            
            print(f"✅ Connection successful, Demo balance: ${balance:.2f}")
            api.close()
            return True
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    async def test_market_data(self) -> bool:
        """Test market data retrieval"""
        print("\n📊 Testing Market Data Retrieval...")
        
        try:
            from iqoptionapi.stable_api import IQ_Option
            from analysis.technical_indicators import TechnicalIndicators
            import time
            
            api = IQ_Option(TradingConfig.EMAIL, TradingConfig.PASSWORD)
            check, reason = api.connect()
            
            if not check:
                print(f"❌ Connection failed: {reason}")
                return False
            
            # Test candle data
            current_time = int(time.time())
            candles = api.get_candles('EURUSD-OTC', 60, 100, current_time)
            
            if not candles or len(candles) < 20:
                print("❌ Insufficient candle data")
                api.close()
                return False
            
            print(f"✅ Retrieved {len(candles)} candles")
            
            # Test technical indicators
            indicators = TechnicalIndicators()
            rsi = indicators.rsi(candles, 14)
            macd = indicators.macd(candles)
            
            print(f"✅ Technical indicators calculated (RSI: {rsi:.1f})")
            
            api.close()
            return True
            
        except Exception as e:
            print(f"❌ Market data test failed: {e}")
            return False
    
    async def test_ai_models(self) -> bool:
        """Test AI model initialization"""
        print("\n🤖 Testing AI Models...")
        
        ai_results = {}
        
        # Test OpenAI
        if os.getenv('OPENAI_API_KEY'):
            try:
                from ai_models.openai_model import OpenAIModel
                model = OpenAIModel()
                ai_results['OpenAI'] = True
                print("✅ OpenAI model initialized")
            except Exception as e:
                ai_results['OpenAI'] = False
                print(f"❌ OpenAI model failed: {e}")
        else:
            print("⚠️ OpenAI API key not set")
        
        # Test Claude
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                from ai_models.claude_model import ClaudeModel
                model = ClaudeModel()
                ai_results['Claude'] = True
                print("✅ Claude model initialized")
            except Exception as e:
                ai_results['Claude'] = False
                print(f"❌ Claude model failed: {e}")
        else:
            print("⚠️ Claude API key not set")
        
        # Test DeepSeek
        if os.getenv('DEEPSEEK_API_KEY'):
            try:
                from ai_models.deepseek_model import DeepSeekModel
                model = DeepSeekModel()
                ai_results['DeepSeek'] = True
                print("✅ DeepSeek model initialized")
            except Exception as e:
                ai_results['DeepSeek'] = False
                print(f"❌ DeepSeek model failed: {e}")
        else:
            print("⚠️ DeepSeek API key not set")
        
        # At least one AI model should work
        working_models = sum(ai_results.values())
        print(f"📊 {working_models} AI models working")
        
        return working_models > 0
    
    async def test_database(self) -> bool:
        """Test database operations"""
        print("\n💾 Testing Database Operations...")
        
        try:
            from database.trade_storage import TradeDatabase
            
            # Test database initialization
            db = TradeDatabase('data/test_trades.db')
            
            # Test trade insertion
            test_trade = {
                'trade_id': f'TEST_{int(datetime.now().timestamp())}',
                'timestamp': datetime.now().isoformat(),
                'pair': 'EURUSD-OTC',
                'direction': 'CALL',
                'amount': 10.0,
                'duration': 1,
                'result': 'WIN',
                'profit': 8.0,
                'ai_signal_confidence': 75,
                'strategy_version': 'test_v1.0'
            }
            
            success = db.insert_trade(test_trade)
            if not success:
                print("❌ Trade insertion failed")
                return False
            
            # Test trade retrieval
            retrieved_trade = db.get_trade(test_trade['trade_id'])
            if not retrieved_trade:
                print("❌ Trade retrieval failed")
                return False
            
            print("✅ Database operations successful")
            
            # Cleanup test data
            os.remove('data/test_trades.db')
            return True
            
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict:
        """Run all tests"""
        print("🧪 COMPREHENSIVE TRADING SYSTEM TESTS")
        print("=" * 80)
        
        tests = [
            ('Configuration', self.test_configuration),
            ('IQOption Connection', self.test_iqoption_connection),
            ('Market Data', self.test_market_data),
            ('AI Models', self.test_ai_models),
            ('Database', self.test_database)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
                results[test_name] = False
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! System is ready for trading.")
        else:
            print("⚠️ Some tests failed. Please fix issues before trading.")
        
        return results


async def main():
    """Main test runner"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Run tests
    tester = TradingSystemTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    failed_tests = sum(1 for result in results.values() if not result)
    sys.exit(failed_tests)


if __name__ == "__main__":
    asyncio.run(main())
