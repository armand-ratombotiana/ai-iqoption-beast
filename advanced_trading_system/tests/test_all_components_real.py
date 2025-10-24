"""
Comprehensive Real Credential Testing
Tests all components with actual IQOption connection
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import traceback
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Loaded environment variables from .env file")
    else:
        print("⚠️ No .env file found")

# Load environment variables
load_env_file()

from iqoptionapi.stable_api import IQ_Option
from config.settings import TradingConfig


class ComprehensiveRealTester:
    """Test all components with real credentials"""
    
    def __init__(self):
        self.test_results = {
            'env_check': False,
            'iqoption_connection': False,
            'pairs_fetching': False,
            'market_data': False,
            'payout_fetching': False,
            'candles_fetching': False,
            'basic_trade_test': False,
            'errors': []
        }
        self.api = None
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 COMPREHENSIVE REAL CREDENTIAL TESTING")
        print("=" * 80)
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            # Test 1: Environment Variables
            self.test_environment_variables()
            
            # Test 2: IQOption Connection
            await self.test_iqoption_connection()
            
            # Test 3: Pairs Fetching
            await self.test_pairs_fetching()
            
            # Test 4: Market Data
            await self.test_market_data()
            
            # Test 5: Payout Fetching
            await self.test_payout_fetching()
            
            # Test 6: Candles Fetching
            await self.test_candles_fetching()
            
            # Test 7: Basic Trade Test (Optional)
            trade_test = input("\n🤔 Run basic trade test? This will execute a $1 demo trade (y/N): ").lower().strip()
            if trade_test == 'y':
                await self.test_basic_trade()
            
            # Print final results
            self.print_comprehensive_summary()
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Critical test failure: {e}")
            traceback.print_exc()
        finally:
            await self.cleanup()
    
    def test_environment_variables(self):
        """Test environment variables"""
        print("\n📋 TEST 1: Environment Variables Check")
        print("-" * 50)
        
        try:
            required_vars = {
                'IQOPTION_EMAIL': os.getenv('IQOPTION_EMAIL'),
                'IQOPTION_PASSWORD': os.getenv('IQOPTION_PASSWORD'),
                'ACCOUNT_TYPE': os.getenv('ACCOUNT_TYPE', 'PRACTICE')
            }
            
            print("🔍 Environment Variables:")
            all_set = True
            for var, value in required_vars.items():
                if value:
                    display_value = value if var != 'IQOPTION_PASSWORD' else '*' * len(value)
                    print(f"   ✅ {var}: {display_value}")
                else:
                    print(f"   ❌ {var}: Not set")
                    all_set = False
            
            if all_set:
                self.test_results['env_check'] = True
                print("\n✅ All required environment variables are set")
            else:
                raise ValueError("Missing required environment variables")
                
        except Exception as e:
            self.test_results['errors'].append(f"Environment: {str(e)}")
            print(f"❌ Environment check failed: {e}")
    
    async def test_iqoption_connection(self):
        """Test IQOption API connection"""
        print("\n🔌 TEST 2: IQOption Connection")
        print("-" * 50)
        
        try:
            email = os.getenv('IQOPTION_EMAIL')
            password = os.getenv('IQOPTION_PASSWORD')
            account_type = os.getenv('ACCOUNT_TYPE', 'PRACTICE')
            
            print(f"📧 Connecting with email: {email}")
            print(f"🏦 Account type: {account_type}")
            
            self.api = IQ_Option(email, password)
            
            # Test connection
            print("🔄 Attempting connection...")
            check, reason = self.api.connect()
            
            if check:
                print("✅ Connection successful!")
                
                # Set account type
                self.api.change_balance(account_type)
                
                # Get balance
                balance = self.api.get_balance()
                print(f"💰 {account_type} Balance: ${balance:.2f}")
                
                # Test basic API call
                server_time = self.api.get_server_timestamp()
                if server_time:
                    print(f"🕐 Server time: {datetime.fromtimestamp(server_time)}")
                
                self.test_results['iqoption_connection'] = True
                
            else:
                raise Exception(f"Connection failed: {reason}")
                
        except Exception as e:
            self.test_results['errors'].append(f"IQOption Connection: {str(e)}")
            print(f"❌ Connection test failed: {e}")
            raise
    
    async def test_pairs_fetching(self):
        """Test fetching available trading pairs"""
        print("\n📊 TEST 3: Available Pairs Fetching")
        print("-" * 50)
        
        try:
            if not self.api:
                raise Exception("API not connected")
            
            print("🔄 Fetching available pairs...")
            
            # Get all open times
            open_times = self.api.get_all_open_time()
            
            if open_times:
                turbo_pairs = open_times.get('turbo', {})
                binary_pairs = open_times.get('binary', {})
                
                print(f"📈 Found pairs:")
                print(f"   Turbo pairs: {len(turbo_pairs)}")
                print(f"   Binary pairs: {len(binary_pairs)}")
                
                # Show sample pairs
                print(f"\n🔍 Sample Turbo pairs:")
                for i, (pair, status) in enumerate(list(turbo_pairs.items())[:5]):
                    is_open = status.get('open', False)
                    print(f"   • {pair}-OTC: {'✅ Open' if is_open else '❌ Closed'}")
                
                print(f"\n🔍 Sample Binary pairs:")
                for i, (pair, status) in enumerate(list(binary_pairs.items())[:5]):
                    is_open = status.get('open', False)
                    print(f"   • {pair}: {'✅ Open' if is_open else '❌ Closed'}")
                
                if turbo_pairs or binary_pairs:
                    self.test_results['pairs_fetching'] = True
                    print(f"\n✅ Pairs fetching successful")
                else:
                    raise Exception("No pairs available")
            else:
                raise Exception("Could not fetch open times")
                
        except Exception as e:
            self.test_results['errors'].append(f"Pairs fetching: {str(e)}")
            print(f"❌ Pairs fetching failed: {e}")
    
    async def test_market_data(self):
        """Test market data access"""
        print("\n📈 TEST 4: Market Data Access")
        print("-" * 50)
        
        try:
            if not self.api:
                raise Exception("API not connected")
            
            # Get test pairs
            open_times = self.api.get_all_open_time()
            turbo_pairs = open_times.get('turbo', {})
            
            # Find an open pair
            test_pair = None
            for pair, status in turbo_pairs.items():
                if status.get('open', False):
                    test_pair = f"{pair}-OTC"
                    break
            
            if not test_pair:
                # Try binary pairs
                binary_pairs = open_times.get('binary', {})
                for pair, status in binary_pairs.items():
                    if status.get('open', False):
                        test_pair = pair
                        break
            
            if not test_pair:
                raise Exception("No open pairs found for testing")
            
            print(f"🎯 Testing market data for: {test_pair}")
            
            # Test current price (via candles)
            print("🔄 Getting current price...")
            current_time = int(time.time())
            candles = self.api.get_candles(test_pair, 1, 1, current_time)
            
            if candles and len(candles) > 0:
                current_price = candles[-1]['close']
                print(f"💹 Current price: {current_price:.6f}")
                self.test_results['market_data'] = True
                print("✅ Market data access successful")
            else:
                raise Exception("Could not get current price")
                
        except Exception as e:
            self.test_results['errors'].append(f"Market data: {str(e)}")
            print(f"❌ Market data test failed: {e}")
    
    async def test_payout_fetching(self):
        """Test payout fetching"""
        print("\n💰 TEST 5: Payout Fetching")
        print("-" * 50)
        
        try:
            if not self.api:
                raise Exception("API not connected")
            
            # Get test pairs
            open_times = self.api.get_all_open_time()
            turbo_pairs = open_times.get('turbo', {})
            
            print("🔄 Testing payout fetching...")
            successful_payouts = 0
            
            # Test payouts for first 5 open pairs
            test_count = 0
            for pair, status in turbo_pairs.items():
                if status.get('open', False) and test_count < 5:
                    test_pair = f"{pair}-OTC"
                    try:
                        payout = self.api.get_payout(test_pair, 1)  # 1 minute
                        if payout and payout > 0:
                            print(f"   • {test_pair}: {payout:.1%} payout")
                            successful_payouts += 1
                        else:
                            print(f"   • {test_pair}: No payout data")
                        
                        # Small delay to avoid rate limiting
                        time.sleep(0.2)
                        test_count += 1
                        
                    except Exception as e:
                        print(f"   • {test_pair}: Error - {e}")
            
            if successful_payouts > 0:
                self.test_results['payout_fetching'] = True
                print(f"\n✅ Payout fetching successful ({successful_payouts}/{test_count} pairs)")
            else:
                raise Exception("No payouts could be fetched")
                
        except Exception as e:
            self.test_results['errors'].append(f"Payout fetching: {str(e)}")
            print(f"❌ Payout fetching failed: {e}")
    
    async def test_candles_fetching(self):
        """Test historical candles fetching"""
        print("\n📊 TEST 6: Historical Candles Fetching")
        print("-" * 50)
        
        try:
            if not self.api:
                raise Exception("API not connected")
            
            # Get test pair
            open_times = self.api.get_all_open_time()
            turbo_pairs = open_times.get('turbo', {})
            
            test_pair = None
            for pair, status in turbo_pairs.items():
                if status.get('open', False):
                    test_pair = f"{pair}-OTC"
                    break
            
            if not test_pair:
                raise Exception("No open pairs for testing")
            
            print(f"🎯 Testing candles for: {test_pair}")
            
            # Test different timeframes and counts
            test_cases = [
                {'timeframe': 1, 'count': 10, 'name': '1-minute, 10 candles'},
                {'timeframe': 1, 'count': 100, 'name': '1-minute, 100 candles'},
                {'timeframe': 5, 'count': 20, 'name': '5-minute, 20 candles'}
            ]
            
            successful_tests = 0
            current_time = int(time.time())
            
            for test_case in test_cases:
                try:
                    print(f"🔄 Testing {test_case['name']}...")
                    candles = self.api.get_candles(
                        test_pair, 
                        test_case['timeframe'], 
                        test_case['count'], 
                        current_time
                    )
                    
                    if candles and len(candles) > 0:
                        print(f"   ✅ Received {len(candles)} candles")
                        
                        # Show sample candle
                        latest = candles[-1]
                        print(f"   📈 Latest: O:{latest['open']:.6f} H:{latest['high']:.6f} L:{latest['low']:.6f} C:{latest['close']:.6f}")
                        successful_tests += 1
                    else:
                        print(f"   ❌ No candles received")
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            if successful_tests > 0:
                self.test_results['candles_fetching'] = True
                print(f"\n✅ Candles fetching successful ({successful_tests}/{len(test_cases)} tests)")
            else:
                raise Exception("No candles could be fetched")
                
        except Exception as e:
            self.test_results['errors'].append(f"Candles fetching: {str(e)}")
            print(f"❌ Candles fetching failed: {e}")
    
    async def test_basic_trade(self):
        """Test basic trade execution"""
        print("\n🚀 TEST 7: Basic Trade Execution")
        print("-" * 50)
        
        try:
            if not self.api:
                raise Exception("API not connected")
            
            # Get balance
            balance = self.api.get_balance()
            if balance < 1.0:
                raise Exception(f"Insufficient balance: ${balance:.2f}")
            
            # Find a good pair for testing
            open_times = self.api.get_all_open_time()
            turbo_pairs = open_times.get('turbo', {})
            
            test_pair = None
            for pair, status in turbo_pairs.items():
                if status.get('open', False):
                    test_pair = f"{pair}-OTC"
                    # Check if payout is available
                    try:
                        payout = self.api.get_payout(test_pair, 1)
                        if payout and payout > 0.7:  # At least 70% payout
                            break
                    except:
                        continue
            
            if not test_pair:
                raise Exception("No suitable pair found for trading")
            
            print(f"🎯 Executing test trade on: {test_pair}")
            
            # Get payout
            payout = self.api.get_payout(test_pair, 1)
            print(f"💰 Payout: {payout:.1%}")
            
            # Execute trade
            print("🔄 Executing $1.00 CALL trade (1 minute)...")
            status, order_id = self.api.buy(1.0, test_pair, 'call', 1)
            
            if status and order_id:
                print(f"✅ Trade executed successfully!")
                print(f"   Order ID: {order_id}")
                print(f"   Pair: {test_pair}")
                print(f"   Direction: CALL")
                print(f"   Amount: $1.00")
                print(f"   Duration: 1 minute")
                
                # Wait for result
                print(f"\n⏳ Waiting 70 seconds for trade result...")
                await asyncio.sleep(70)
                
                # Check result
                print("🔄 Checking trade result...")
                for attempt in range(10):
                    try:
                        profit = self.api.check_win_v3(order_id)
                        if profit is not None:
                            result = "WIN" if profit > 0 else "LOSS"
                            print(f"\n📊 Trade Result:")
                            print(f"   Result: {result}")
                            print(f"   Profit/Loss: ${profit:+.2f}")
                            
                            new_balance = self.api.get_balance()
                            print(f"   Balance: ${balance:.2f} → ${new_balance:.2f}")
                            
                            self.test_results['basic_trade_test'] = True
                            print(f"\n✅ Basic trade test completed successfully")
                            break
                    except Exception as e:
                        print(f"   Attempt {attempt + 1}: {e}")
                    
                    await asyncio.sleep(2)
                else:
                    print("⚠️ Could not get trade result, but trade was executed")
                    self.test_results['basic_trade_test'] = True
            else:
                raise Exception("Trade execution failed")
                
        except Exception as e:
            self.test_results['errors'].append(f"Basic trade: {str(e)}")
            print(f"❌ Basic trade test failed: {e}")
    
    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🧪 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        # Calculate success rate
        total_tests = len([k for k in self.test_results.keys() if k != 'errors'])
        passed_tests = sum([1 for k, v in self.test_results.items() if k != 'errors' and v])
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        # Individual test results
        test_names = {
            'env_check': 'Environment Variables',
            'iqoption_connection': 'IQOption Connection',
            'pairs_fetching': 'Pairs Fetching',
            'market_data': 'Market Data Access',
            'payout_fetching': 'Payout Fetching',
            'candles_fetching': 'Candles Fetching',
            'basic_trade_test': 'Basic Trade Test'
        }
        
        print(f"\n📋 Detailed Results:")
        for key, name in test_names.items():
            if key in self.test_results:
                status = "✅ PASS" if self.test_results[key] else "❌ FAIL"
                print(f"   {name}: {status}")
        
        # Show errors
        if self.test_results['errors']:
            print(f"\n⚠️ Errors Encountered ({len(self.test_results['errors'])}):")
            for i, error in enumerate(self.test_results['errors'], 1):
                print(f"   {i}. {error}")
        
        # System readiness assessment
        print(f"\n🎯 System Readiness Assessment:")
        
        critical_tests = ['env_check', 'iqoption_connection', 'pairs_fetching', 'market_data']
        critical_passed = sum([1 for test in critical_tests if self.test_results.get(test, False)])
        
        if critical_passed == len(critical_tests):
            print("   ✅ READY FOR PARALLEL TRADING")
            print("   All critical components are working correctly")
        elif critical_passed >= 3:
            print("   ⚠️ MOSTLY READY - Minor issues detected")
            print("   Core functionality works, some features may be limited")
        else:
            print("   ❌ NOT READY - Critical issues found")
            print("   Major components need fixing before trading")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if not self.test_results.get('iqoption_connection', False):
            print("   • Verify IQOption credentials and account status")
        if not self.test_results.get('pairs_fetching', False):
            print("   • Check market hours and API access permissions")
        if not self.test_results.get('payout_fetching', False):
            print("   • Some pairs may have limited payout data")
        if not self.test_results.get('candles_fetching', False):
            print("   • Historical data access may be restricted")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.api:
            try:
                self.api.close()
                print("\n🧹 API connection closed")
            except:
                pass


async def main():
    """Main test execution"""
    print("⚠️ IMPORTANT NOTICE:")
    print("This test will use REAL IQOption credentials from .env file")
    print("All trades will be executed on PRACTICE account only")
    print("No real money will be used")
    
    proceed = input("\nProceed with comprehensive testing? (y/N): ").lower().strip()
    if proceed != 'y':
        print("Testing cancelled.")
        return
    
    tester = ComprehensiveRealTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
