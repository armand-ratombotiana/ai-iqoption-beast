"""
Comprehensive System Test Suite for IQOption Trading Bot
Tests all APIs and n8n node functionality with real credentials
"""
import sys
import time
import json
import requests
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, '/app/app/KAEL/KAEL/src')

# Test configuration
EMAIL = "tombokael4@gmail.com"
PASSWORD = "tombokael04"
API_URL = "http://localhost:5000"

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def test_iqoption_direct():
    """Test 1: Direct IQOption API Connection"""
    print_header("TEST 1: Direct IQOption API Connection")

    try:
        from iqoptionapi.stable_api import IQ_Option

        print_info("Attempting to connect to IQ Option...")
        api = IQ_Option(EMAIL, PASSWORD)
        check, reason = api.connect()

        if not check:
            print_error(f"Connection failed: {reason}")
            return False

        print_success(f"Connected successfully: {reason}")

        # Check connection stability
        print_info("Checking connection stability...")
        if not api.check_connect():
            print_error("Connection check failed")
            return False

        print_success("Connection is stable")

        # Get account balance
        print_info("Retrieving account balance...")
        balance = api.get_balance()
        print_success(f"Practice Balance: ${balance:.2f}")

        # Get profile info
        print_info("Retrieving profile information...")
        profile = api.get_profile_ansyc()
        if profile:
            print_success(f"Profile retrieved - Name: {profile.get('name', 'N/A')}")

        # Check market status
        print_info("Checking market status...")
        open_times = api.get_all_open_time()

        if 'binary' in open_times:
            open_markets = [pair for pair, status in open_times['binary'].items()
                          if status.get('open', False)]
            print_success(f"Found {len(open_markets)} open markets")
            print_info(f"Sample open markets: {', '.join(open_markets[:5])}")

        return True

    except Exception as e:
        print_error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_health():
    """Test 2: API Health Check"""
    print_header("TEST 2: Flask API Health Check")

    try:
        print_info(f"Checking health endpoint: {API_URL}/health")
        response = requests.get(f"{API_URL}/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_success(f"API is healthy - Status: {data.get('status')}")
            print_info(f"Timestamp: {data.get('timestamp')}")
            return True
        else:
            print_error(f"Health check failed with status code: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is the Flask server running?")
        print_warning("Start the server with: python3 trading_api.py")
        return False
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False

def test_api_status():
    """Test 3: Trading Status Endpoint"""
    print_header("TEST 3: Trading Status Endpoint")

    try:
        print_info("Fetching trading status...")
        response = requests.get(f"{API_URL}/status", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_success("Status retrieved successfully")

            state = data.get('tradingState', {})
            config = data.get('config', {})

            print_info("Trading State:")
            print(f"  Daily Profit: ${state.get('daily_profit', 0):.2f}")
            print(f"  Daily Loss: ${state.get('daily_loss', 0):.2f}")
            print(f"  Consecutive Losses: {state.get('consecutive_losses', 0)}")
            print(f"  Martingale Level: {state.get('martingale_level', 0)}")
            print(f"  Trades Today: {state.get('trades_today', 0)}")

            print_info("Risk Management Config:")
            print(f"  Max Daily Loss: ${config.get('MAX_DAILY_LOSS', 0):.2f}")
            print(f"  Max Daily Profit: ${config.get('MAX_DAILY_PROFIT', 0):.2f}")
            print(f"  Max Consecutive Losses: {config.get('MAX_CONSECUTIVE_LOSSES', 0)}")
            print(f"  Min Confidence: {config.get('MIN_CONFIDENCE_THRESHOLD', 0)}%")

            return True
        else:
            print_error(f"Request failed with status code: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False

def test_api_trade_execution():
    """Test 4: Trade Execution via API"""
    print_header("TEST 4: Trade Execution (Demo Mode)")

    try:
        print_warning("This test will execute a REAL demo trade and wait for results")
        print_warning("Expected duration: ~1-2 minutes")

        payload = {
            "email": EMAIL,
            "password": PASSWORD,
            "action": "call",
            "pair": "EURUSD",
            "confidence": 75,
            "accountType": "demo"
        }

        print_info(f"Executing CALL trade on EURUSD with 75% confidence...")
        print_info("Trade parameters will be auto-calculated based on confidence")

        start_time = time.time()
        response = requests.post(
            f"{API_URL}/trade",
            json=payload,
            timeout=300  # 5 minute timeout
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print_success(f"Trade executed successfully in {elapsed:.1f}s")

            print_info("Trade Details:")
            print(f"  Order ID: {data.get('orderId')}")
            print(f"  Action: {data.get('action', '').upper()}")
            print(f"  Pair: {data.get('pair')}")
            print(f"  Amount: ${data.get('amount'):.2f}")
            print(f"  Duration: {data.get('duration')} minute(s)")
            print(f"  Confidence: {data.get('confidence')}%")

            print_info("Results:")
            result = data.get('result', '')
            profit = data.get('profit', 0)

            if result == 'win':
                print_success(f"Result: WIN - Profit: ${profit:.2f}")
            else:
                print_warning(f"Result: LOSS - Loss: ${abs(profit):.2f}")

            print_info("Balance:")
            print(f"  Old: ${data.get('oldBalance', 0):.2f}")
            print(f"  New: ${data.get('newBalance', 0):.2f}")
            print(f"  Change: ${data.get('balanceChange', 0):.2f}")

            state = data.get('tradingState', {})
            print_info("Updated Trading State:")
            print(f"  Daily P/L: +${state.get('dailyProfit', 0):.2f} / -${state.get('dailyLoss', 0):.2f}")
            print(f"  Martingale Level: {state.get('martingaleLevel', 0)}")
            print(f"  Consecutive Losses: {state.get('consecutiveLosses', 0)}")
            print(f"  Trades Today: {state.get('tradesToday', 0)}")

            return True
        else:
            print_error(f"Trade failed with status code: {response.status_code}")
            error_data = response.json()
            print_error(f"Error: {error_data.get('error')}")
            return False

    except requests.exceptions.Timeout:
        print_error("Request timed out. Trade may still be processing.")
        return False
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_reset():
    """Test 5: State Reset Endpoint"""
    print_header("TEST 5: State Reset Endpoint")

    try:
        print_info("Testing daily stats reset...")
        response = requests.post(
            f"{API_URL}/reset",
            json={"type": "daily"},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Reset successful: {data.get('message')}")

            state = data.get('tradingState', {})
            print_info("Trading State After Reset:")
            print(f"  Daily Profit: ${state.get('daily_profit', 0):.2f}")
            print(f"  Daily Loss: ${state.get('daily_loss', 0):.2f}")
            print(f"  Trades Today: {state.get('trades_today', 0)}")

            return True
        else:
            print_error(f"Reset failed with status code: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False

def test_risk_management():
    """Test 6: Risk Management Validation"""
    print_header("TEST 6: Risk Management Validation")

    try:
        # Test 1: Low confidence rejection
        print_info("Test 6a: Low confidence signal rejection")
        payload = {
            "email": EMAIL,
            "password": PASSWORD,
            "action": "call",
            "pair": "EURUSD",
            "confidence": 50,  # Below threshold
            "accountType": "demo"
        }

        response = requests.post(f"{API_URL}/trade", json=payload, timeout=10)

        if response.status_code == 400:
            error_data = response.json()
            if "confidence" in error_data.get('error', '').lower():
                print_success("Low confidence correctly rejected")
            else:
                print_warning(f"Rejected but different reason: {error_data.get('error')}")
        else:
            print_error("Low confidence signal was not rejected")
            return False

        # Test 2: Invalid signal rejection
        print_info("Test 6b: Invalid signal rejection")
        payload = {
            "email": EMAIL,
            "password": PASSWORD,
            "action": "invalid",  # Invalid action
            "pair": "EURUSD",
            "confidence": 75,
            "accountType": "demo"
        }

        response = requests.post(f"{API_URL}/trade", json=payload, timeout=10)

        if response.status_code == 400:
            print_success("Invalid signal correctly rejected")
        else:
            print_error("Invalid signal was not rejected")
            return False

        print_success("All risk management validations passed")
        return True

    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False

def test_n8n_node():
    """Test 7: n8n Node Structure"""
    print_header("TEST 7: n8n Node Structure Validation")

    try:
        print_info("Checking n8n node file...")

        import os
        node_path = "/app/app/KAEL/KAEL/n8n-nodes-trading/nodes/Trading/Trading.node.js"

        if not os.path.exists(node_path):
            print_error(f"Node file not found at: {node_path}")
            return False

        print_success("Node file exists")

        # Read and validate structure
        with open(node_path, 'r') as f:
            content = f.read()

        required_elements = [
            "class Trading",
            "execute()",
            "operation === 'trade'",
            "operation === 'status'",
            "operation === 'reset'",
            "axios.post",
            "axios.get"
        ]

        print_info("Validating node structure...")
        all_present = True
        for element in required_elements:
            if element in content:
                print_success(f"Found: {element}")
            else:
                print_error(f"Missing: {element}")
                all_present = False

        if all_present:
            print_success("n8n node structure is valid")
            print_info("Node supports: Execute Trade, Get Status, Reset State")
            return True
        else:
            print_error("n8n node structure validation failed")
            return False

    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and generate report"""
    print_header("COMPREHENSIVE SYSTEM TEST SUITE")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Testing with account: {EMAIL}")
    print_warning("All trades will use DEMO account for safety")

    tests = [
        ("Direct IQOption API Connection", test_iqoption_direct, True),
        ("Flask API Health Check", test_api_health, True),
        ("Trading Status Endpoint", test_api_status, True),
        ("Trade Execution", test_api_trade_execution, False),  # Optional - takes time
        ("State Reset Endpoint", test_api_reset, True),
        ("Risk Management Validation", test_risk_management, True),
        ("n8n Node Structure", test_n8n_node, True)
    ]

    results = []

    for name, test_func, required in tests:
        try:
            result = test_func()
            results.append((name, result, required))

            if not result and required:
                print_error(f"Critical test '{name}' failed. Stopping tests.")
                break

        except Exception as e:
            print_error(f"Test '{name}' crashed: {str(e)}")
            results.append((name, False, required))
            if required:
                break

        time.sleep(1)  # Brief pause between tests

    # Print summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result, _ in results if result)
    total = len(results)

    for name, result, required in results:
        status = f"{Colors.OKGREEN}PASS{Colors.ENDC}" if result else f"{Colors.FAIL}FAIL{Colors.ENDC}"
        req_marker = " (required)" if required else " (optional)"
        print(f"{status} - {name}{req_marker}")

    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.ENDC}")

    if passed == total:
        print_success("All tests passed! System is fully operational.")
        return 0
    elif passed >= len([r for r in results if r[2]]):  # All required tests passed
        print_warning("All required tests passed. Some optional tests failed.")
        return 0
    else:
        print_error("Critical tests failed. System needs attention.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
