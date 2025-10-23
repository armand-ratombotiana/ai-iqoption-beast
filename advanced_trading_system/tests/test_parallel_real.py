"""
Real Credential Testing for Parallel Trading System
Tests all components with actual IQOption connection
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import traceback

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import TradingConfig
from data_providers.iqoption_provider import IQOptionProvider
from trading.parallel_trading_engine import ParallelTradingEngine


class RealCredentialTester:
    """Test parallel trading system with real credentials"""
    
    def __init__(self):
        self.test_results = {
            'connection': False,
            'pairs_fetch': False,
            'pair_filtering': False,
            'market_data': False,
            'ai_analysis': False,
            'trade_execution': False,
            'errors': []
        }
        self.provider = None
        self.engine = None
    
    async def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🧪 REAL CREDENTIAL TESTING - PARALLEL TRADING SYSTEM")
        print("=" * 80)
        
        try:
            # Test 1: Configuration validation
            await self.test_configuration()
            
            # Test 2: IQOption connection
            await self.test_connection()
            
            # Test 3: Fetch available pairs
            await self.test_pairs_fetching()
            
            # Test 4: Pair filtering
            await self.test_pair_filtering()
            
            # Test 5: Market data fetching
            await self.test_market_data()
            
            # Test 6: AI analysis (without execution)
            await self.test_ai_analysis()
            
            # Test 7: Demo trade execution (if requested)
            demo_trade = input("\n🤔 Execute demo trade? (y/N): ").lower().strip()
            if demo_trade == 'y':
                await self.test_trade_execution()
            
            # Print final results
            self.print_test_summary()
            
        except Exception as e:
            print(f"❌ Critical test failure: {e}")
            traceback.print_exc()
        finally:
            await self.cleanup()
    
    async def test_configuration(self):
        """Test configuration validation"""
        print("\n📋 TEST 1: Configuration Validation")
        print("-" * 50)
        
        try:
            # Check required environment variables
            required_vars = ['IQOPTION_EMAIL', 'IQOPTION_PASSWORD']
            missing_vars = []
            
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
            
            # Validate configuration
            TradingConfig.validate()
            TradingConfig.display()
            
            print("✅ Configuration validation passed")
            
        except Exception as e:
            self.test_results['errors'].append(f"Configuration: {str(e)}")
            print(f"❌ Configuration validation failed: {e}")
            raise
    
    async def test_connection(self):
        """Test IQOption connection"""
        print("\n🔌 TEST 2: IQOption Connection")
        print("-" * 50)
        
        try:
            self.provider = IQOptionProvider(
                email=os.getenv('IQOPTION_EMAIL'),
                password=os.getenv('IQOPTION_PASSWORD'),
                account_type='PRACTICE'  # Always use practice for testing
            )
            
            success = await self.provider.connect()
            
            if success:
                balance = self.provider.get_balance()
                print(f"✅ Connected successfully")
                print(f"💰 Practice Balance: ${balance:.2f}")
                self.test_results['connection'] = True
            else:
                raise Exception("Connection failed")
                
        except Exception as e:
            self.test_results['errors'].append(f"Connection: {str(e)}")
            print(f"❌ Connection failed: {e}")
            raise
    
    async def test_pairs_fetching(self):
        """Test fetching available pairs"""
        print("\n📊 TEST 3: Fetching Available Pairs")
        print("-" * 50)
        
        try:
            if not self.provider:
                raise Exception("Provider not initialized")
            
            # Update available pairs
            pairs = await self.provider.update_available_pairs()
            
            if pairs:
                print(f"✅ Fetched {len(pairs)} pairs")
                
                # Show sample pairs
                sample_pairs = list(pairs.items())[:5]
                print("\n📋 Sample pairs:")
                for pair_name, pair_info in sample_pairs:
                    payout = pair_info.get('payout', 0)
                    is_open = pair_info.get('is_open', False)
                    category = pair_info.get('category', 'unknown')
                    print(f"   • {pair_name}: {payout:.1%} payout, {'Open' if is_open else 'Closed'} ({category})")
                
                # Get pairs summary
                summary = self.provider.get_pairs_summary()
                print(f"\n📈 Pairs Summary:")
                print(f"   Total: {summary['total_pairs']}")
                print(f"   High payout (>85%): {summary['payout_ranges']['high']}")
                print(f"   Medium payout (75-85%): {summary['payout_ranges']['medium']}")
                print(f"   Low payout (<75%): {summary['payout_ranges']['low']}")
                
                self.test_results['pairs_fetch'] = True
            else:
                raise Exception("No pairs fetched")
                
        except Exception as e:
            self.test_results['errors'].append(f"Pairs fetching: {str(e)}")
            print(f"❌ Pairs fetching failed: {e}")
    
    async def test_pair_filtering(self):
        """Test pair filtering functionality"""
        print("\n🔍 TEST 4: Pair Filtering")
        print("-" * 50)
        
        try:
            if not self.provider:
                raise Exception("Provider not initialized")
            
            # Test different filter criteria
            filter_tests = [
                {'min_payout': 0.75, 'max_pairs': 10, 'name': 'Standard Filter'},
                {'min_payout': 0.85, 'max_pairs': 5, 'name': 'High Payout Filter'},
                {'min_payout': 0.70, 'max_pairs': 20, 'categories': ['forex'], 'name': 'Forex Only Filter'}
            ]
            
            for filter_test in filter_tests:
                name = filter_test.pop('name')
                filtered_pairs = await self.provider.get_filtered_pairs(**filter_test)
                
                print(f"\n🎯 {name}:")
                print(f"   Found {len(filtered_pairs)} pairs")
                
                if filtered_pairs:
                    for pair in filtered_pairs[:3]:  # Show top 3
                        print(f"   • {pair['pair']}: {pair['payout']:.1%} ({pair['category']})")
            
            self.test_results['pair_filtering'] = True
            print("\n✅ Pair filtering tests passed")
            
        except Exception as e:
            self.test_results['errors'].append(f"Pair filtering: {str(e)}")
            print(f"❌ Pair filtering failed: {e}")
    
    async def test_market_data(self):
        """Test market data fetching"""
        print("\n📈 TEST 5: Market Data Fetching")
        print("-" * 50)
        
        try:
            if not self.provider:
                raise Exception("Provider not initialized")
            
            # Get a few pairs to test
            filtered_pairs = await self.provider.get_filtered_pairs(min_payout=0.75, max_pairs=3)
            
            if not filtered_pairs:
                raise Exception("No pairs available for testing")
            
            for pair_info in filtered_pairs:
                pair_name = pair_info['pair']
                print(f"\n📊 Testing {pair_name}:")
                
                # Test current price
                price = await self.provider.get_current_price(pair_name)
                if price:
                    print(f"   Current Price: {price:.6f}")
                else:
                    print(f"   ⚠️ Could not get current price")
                
                # Test candles
                candles = await self.provider.get_candles(pair_name, '1m', 10)
                if candles and len(candles) > 0:
                    print(f"   Candles: {len(candles)} received")
                    latest = candles[-1]
                    print(f"   Latest: O:{latest['open']:.6f} H:{latest['high']:.6f} L:{latest['low']:.6f} C:{latest['close']:.6f}")
                else:
                    print(f"   ⚠️ Could not get candles")
            
            self.test_results['market_data'] = True
            print("\n✅ Market data tests passed")
            
        except Exception as e:
            self.test_results['errors'].append(f"Market data: {str(e)}")
            print(f"❌ Market data test failed: {e}")
    
    async def test_ai_analysis(self):
        """Test AI analysis without execution"""
        print("\n🤖 TEST 6: AI Analysis")
        print("-" * 50)
        
        try:
            # Initialize parallel engine for AI testing
            config = TradingConfig()
            self.engine = ParallelTradingEngine(config)
            
            # Get test pairs
            filtered_pairs = await self.provider.get_filtered_pairs(min_payout=0.75, max_pairs=2)
            
            if not filtered_pairs:
                raise Exception("No pairs for AI analysis")
            
            print(f"🔍 Analyzing {len(filtered_pairs)} pairs...")
            
            # Test parallel analysis
            analysis_results = await self.engine._analyze_pairs_parallel(filtered_pairs)
            
            print(f"\n📊 Analysis Results:")
            for result in analysis_results:
                if result:
                    print(f"   • {result['pair']}: {result['signal']} ({result['confidence']:.1f}% confidence)")
                    print(f"     Payout: {result['payout']:.1%}")
            
            self.test_results['ai_analysis'] = True
            print("\n✅ AI analysis tests passed")
            
        except Exception as e:
            self.test_results['errors'].append(f"AI analysis: {str(e)}")
            print(f"❌ AI analysis test failed: {e}")
    
    async def test_trade_execution(self):
        """Test actual trade execution (demo only)"""
        print("\n🚀 TEST 7: Demo Trade Execution")
        print("-" * 50)
        
        try:
            if not self.provider:
                raise Exception("Provider not initialized")
            
            # Get one good pair for testing
            filtered_pairs = await self.provider.get_filtered_pairs(min_payout=0.80, max_pairs=1)
            
            if not filtered_pairs:
                raise Exception("No suitable pairs for trade test")
            
            test_pair = filtered_pairs[0]
            pair_name = test_pair['pair']
            
            print(f"🎯 Testing trade execution on {pair_name}")
            print(f"   Payout: {test_pair['payout']:.1%}")
            
            # Execute small demo trade
            trade_result = await self.provider.execute_trade(
                pair=pair_name,
                direction='CALL',  # Fixed direction for test
                amount=1.0,  # Minimum amount
                duration=1
            )
            
            if trade_result and trade_result.get('success'):
                order_id = trade_result['order_id']
                print(f"✅ Trade executed successfully!")
                print(f"   Order ID: {order_id}")
                print(f"   Pair: {pair_name}")
                print(f"   Direction: CALL")
                print(f"   Amount: $1.00")
                
                # Wait a bit and check result
                print(f"\n⏳ Waiting 70 seconds for result...")
                await asyncio.sleep(70)
                
                result = await self.provider.check_trade_result(order_id)
                if result:
                    print(f"\n📊 Trade Result:")
                    print(f"   Result: {result['result']}")
                    print(f"   Profit/Loss: ${result['profit']:+.2f}")
                else:
                    print(f"⚠️ Could not get trade result")
                
                self.test_results['trade_execution'] = True
            else:
                error = trade_result.get('error', 'Unknown error') if trade_result else 'No result'
                raise Exception(f"Trade execution failed: {error}")
            
        except Exception as e:
            self.test_results['errors'].append(f"Trade execution: {str(e)}")
            print(f"❌ Trade execution test failed: {e}")
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🧪 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len([k for k in self.test_results.keys() if k != 'errors'])
        passed_tests = sum([1 for k, v in self.test_results.items() if k != 'errors' and v])
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        
        # Individual test results
        test_names = {
            'connection': 'IQOption Connection',
            'pairs_fetch': 'Pairs Fetching',
            'pair_filtering': 'Pair Filtering',
            'market_data': 'Market Data',
            'ai_analysis': 'AI Analysis',
            'trade_execution': 'Trade Execution'
        }
        
        print(f"\n📋 Detailed Results:")
        for key, name in test_names.items():
            status = "✅ PASS" if self.test_results[key] else "❌ FAIL"
            print(f"   {name}: {status}")
        
        # Show errors
        if self.test_results['errors']:
            print(f"\n⚠️ Errors Encountered:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if not self.test_results['connection']:
            print("   • Check IQOption credentials and network connection")
        if not self.test_results['pairs_fetch']:
            print("   • Verify IQOption API access and account status")
        if not self.test_results['market_data']:
            print("   • Check if pairs are available during current market hours")
        if not self.test_results['ai_analysis']:
            print("   • Verify AI model API keys are set correctly")
        
        print("\n" + "=" * 80)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.provider:
            await self.provider.disconnect()
        if self.engine:
            await self.engine.cleanup()


async def main():
    """Main testing function"""
    print("⚠️ IMPORTANT: This will test with REAL credentials on PRACTICE account")
    print("Make sure you have set the following environment variables:")
    print("- IQOPTION_EMAIL")
    print("- IQOPTION_PASSWORD")
    print("- OPENAI_API_KEY (optional)")
    print("- ANTHROPIC_API_KEY (optional)")
    print("- DEEPSEEK_API_KEY (optional)")
    
    proceed = input("\nProceed with testing? (y/N): ").lower().strip()
    if proceed != 'y':
        print("Testing cancelled.")
        return
    
    tester = RealCredentialTester()
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())
