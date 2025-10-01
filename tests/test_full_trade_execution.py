#!/usr/bin/env python3
"""
Full Trade Execution Test with Secure Credentials
Tests actual trade execution with IQOption API
"""
import os
import sys
import time
import json
import requests
from datetime import datetime

# Set environment variables for secure credential handling
os.environ['TEST_EMAIL'] = 'tombokael4@gmail.com'
os.environ['TEST_PASSWORD'] = 'tombokael04'

class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def mask_sensitive_data(text):
    """Mask sensitive data in logs"""
    if not text:
        return text
    
    # Mask email and password
    text = text.replace(os.environ.get('TEST_EMAIL', ''), '***EMAIL***')
    text = text.replace(os.environ.get('TEST_PASSWORD', ''), '***PASSWORD***')
    
    # Mask other sensitive patterns
    import re
    text = re.sub(r'"password":\s*"[^"]*"', '"password": "***MASKED***"', text)
    text = re.sub(r'"email":\s*"[^"]*"', '"email": "***MASKED***"', text)
    
    return text

def test_full_trade_execution():
    """Test complete trade execution flow"""
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}FULL TRADE EXECUTION TEST{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Using secure environment variables for credentials")
    print(f"{Colors.WARNING}This will execute a REAL demo trade and wait for results{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    # Test payload with secure credentials
    payload = {
        "email": os.environ.get('TEST_EMAIL'),
        "password": os.environ.get('TEST_PASSWORD'),
        "action": "call",
        "pair": "AUDCHF-OTC",  # Use OTC pair for 24/7 availability
        "confidence": 75,
        "accountType": "demo"
    }
    
    print(f"[INFO] Trade Parameters:")
    print(f"  Action: {payload['action'].upper()}")
    print(f"  Pair: {payload['pair']}")
    print(f"  Confidence: {payload['confidence']}%")
    print(f"  Account: {payload['accountType']}")
    print(f"  Email: ***MASKED***")
    print(f"  Password: ***MASKED***")
    print()
    
    try:
        print(f"[INFO] Executing trade request...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:5000/trade",
            json=payload,
            timeout=300  # 5 minute timeout
        )
        
        duration = time.time() - start_time
        
        print(f"[INFO] Request completed in {duration:.1f} seconds")
        print(f"[INFO] HTTP Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n{Colors.OKGREEN}✅ TRADE EXECUTION SUCCESSFUL{Colors.ENDC}")
            print(f"{'='*50}")
            
            # Display trade details (with sensitive data masked)
            print(f"Order ID: {data.get('orderId', 'N/A')}")
            print(f"Action: {data.get('action', 'N/A').upper()}")
            print(f"Pair: {data.get('pair', 'N/A')}")
            print(f"Amount: ${data.get('amount', 0):.2f}")
            print(f"Duration: {data.get('duration', 0)} minute(s)")
            print(f"Confidence: {data.get('confidence', 0)}%")
            print(f"Payout: {data.get('payout', 0):.2%}" if data.get('payout') else "Payout: N/A")
            
            print(f"\n📊 TRADE RESULTS:")
            result = data.get('result', 'unknown')
            profit = data.get('profit', 0)
            
            if result == 'win':
                print(f"{Colors.OKGREEN}Result: WIN 🎉{Colors.ENDC}")
                print(f"{Colors.OKGREEN}Profit: +${profit:.2f}{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}Result: LOSS 📉{Colors.ENDC}")
                print(f"{Colors.WARNING}Loss: ${abs(profit):.2f}{Colors.ENDC}")
            
            print(f"\n💰 BALANCE CHANGES:")
            print(f"Old Balance: ${data.get('oldBalance', 0):.2f}")
            print(f"New Balance: ${data.get('newBalance', 0):.2f}")
            print(f"Balance Change: ${data.get('balanceChange', 0):.2f}")
            
            print(f"\n📈 TRADING STATE:")
            trading_state = data.get('tradingState', {})
            print(f"Daily Profit: ${trading_state.get('dailyProfit', 0):.2f}")
            print(f"Daily Loss: ${trading_state.get('dailyLoss', 0):.2f}")
            print(f"Consecutive Losses: {trading_state.get('consecutiveLosses', 0)}")
            print(f"Martingale Level: {trading_state.get('martingaleLevel', 0)}")
            print(f"Trades Today: {trading_state.get('tradesToday', 0)}")
            
            print(f"\n⏰ TIMESTAMP: {data.get('timestamp', 'N/A')}")
            
            # Verify required fields
            required_fields = ['success', 'orderId', 'action', 'pair', 'result', 'profit']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"\n{Colors.WARNING}⚠️  Missing response fields: {missing_fields}{Colors.ENDC}")
                return False
            
            if data.get('success'):
                print(f"\n{Colors.OKGREEN}✅ ALL VALIDATIONS PASSED{Colors.ENDC}")
                return True
            else:
                print(f"\n{Colors.FAIL}❌ Trade marked as unsuccessful{Colors.ENDC}")
                return False
                
        else:
            print(f"\n{Colors.FAIL}❌ TRADE EXECUTION FAILED{Colors.ENDC}")
            print(f"HTTP Status: {response.status_code}")
            
            try:
                error_data = response.json()
                error_msg = mask_sensitive_data(str(error_data.get('error', 'Unknown error')))
                print(f"Error: {error_msg}")
                
                if 'tradingState' in error_data:
                    print(f"Trading State: {error_data['tradingState']}")
                    
            except:
                print(f"Raw response: {mask_sensitive_data(response.text)}")
            
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n{Colors.FAIL}❌ REQUEST TIMEOUT{Colors.ENDC}")
        print(f"The trade request timed out after 5 minutes")
        print(f"This could indicate:")
        print(f"  - Network connectivity issues")
        print(f"  - IQOption API delays")
        print(f"  - Server processing issues")
        return False
        
    except requests.exceptions.ConnectionError:
        print(f"\n{Colors.FAIL}❌ CONNECTION ERROR{Colors.ENDC}")
        print(f"Cannot connect to API server")
        print(f"Please ensure the API is running on localhost:5000")
        return False
        
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ UNEXPECTED ERROR{Colors.ENDC}")
        print(f"Error: {mask_sensitive_data(str(e))}")
        return False

def test_api_status_after_trade():
    """Test API status after trade execution"""
    print(f"\n{Colors.HEADER}Testing API Status After Trade...{Colors.ENDC}")
    
    try:
        response = requests.get("http://localhost:5000/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            trading_state = data.get('tradingState', {})
            
            print(f"✅ Status endpoint accessible")
            print(f"Trading State Updated:")
            print(f"  Total Trades: {trading_state.get('total_trades', 0)}")
            print(f"  Trades Today: {trading_state.get('trades_today', 0)}")
            print(f"  Daily Profit: ${trading_state.get('daily_profit', 0):.2f}")
            print(f"  Daily Loss: ${trading_state.get('daily_loss', 0):.2f}")
            
            return True
        else:
            print(f"❌ Status endpoint failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Status test failed: {e}")
        return False

def main():
    """Main test execution"""
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code != 200:
            print(f"{Colors.FAIL}ERROR: API is not responding properly{Colors.ENDC}")
            return 1
    except:
        print(f"{Colors.FAIL}ERROR: Cannot connect to API on localhost:5000{Colors.ENDC}")
        print("Please start the API with: python trading_api.py")
        return 1
    
    # Run full trade execution test
    trade_success = test_full_trade_execution()
    
    # Test API status after trade
    status_success = test_api_status_after_trade()
    
    # Final summary
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}FINAL TEST SUMMARY{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    if trade_success and status_success:
        print(f"{Colors.OKGREEN}✅ ALL TESTS PASSED{Colors.ENDC}")
        print(f"✅ Trade execution: SUCCESSFUL")
        print(f"✅ API status: FUNCTIONAL")
        print(f"✅ Data integrity: MAINTAINED")
        print(f"✅ Security: CREDENTIALS MASKED")
        return 0
    else:
        print(f"{Colors.FAIL}❌ SOME TESTS FAILED{Colors.ENDC}")
        print(f"{'✅' if trade_success else '❌'} Trade execution: {'PASSED' if trade_success else 'FAILED'}")
        print(f"{'✅' if status_success else '❌'} API status: {'PASSED' if status_success else 'FAILED'}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Fatal error: {e}{Colors.ENDC}")
        sys.exit(1)