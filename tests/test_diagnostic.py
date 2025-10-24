#!/usr/bin/env python3
"""
Diagnostic Test for API Issues
Provides detailed error information and debugging
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

def test_connection_only():
    """Test just the connection without executing trade"""
    print("=== TESTING CONNECTION ONLY ===")
    
    # First, let's test with a simple direct connection
    try:
        sys.path.insert(0, '/app/app/KAEL/KAEL/src')
        from iqoptionapi.stable_api import IQ_Option
        
        print("[INFO] Testing direct IQOption API connection...")
        api = IQ_Option(os.environ.get('TEST_EMAIL'), os.environ.get('TEST_PASSWORD'))
        check, reason = api.connect()
        
        if check:
            print(f"✅ Direct connection successful: {reason}")
            
            # Check balance
            balance = api.get_balance()
            print(f"✅ Balance retrieved: ${balance:.2f}")
            
            # Check market status
            open_times = api.get_all_open_time()
            if 'binary' in open_times:
                open_markets = [pair for pair, status in open_times['binary'].items() 
                              if status.get('open', False)]
                print(f"✅ Found {len(open_markets)} open markets")
                
                # Check specific pair
                if 'AUDCHF-OTC' in open_times['binary']:
                    is_open = open_times['binary']['AUDCHF-OTC'].get('open', False)
                    print(f"✅ AUDCHF-OTC market status: {'OPEN' if is_open else 'CLOSED'}")
                else:
                    print("⚠️  AUDCHF-OTC not found in market list")
                    
                # Show some available markets
                print(f"Available markets: {open_markets[:10]}")
            
            return True
        else:
            print(f"❌ Direct connection failed: {reason}")
            return False
            
    except Exception as e:
        print(f"❌ Direct connection test failed: {e}")
        return False

def test_api_with_detailed_error():
    """Test API with detailed error reporting"""
    print("\n=== TESTING API WITH DETAILED ERROR REPORTING ===")
    
    payload = {
        "email": os.environ.get('TEST_EMAIL'),
        "password": os.environ.get('TEST_PASSWORD'),
        "action": "call",
        "pair": "AUDCHF-OTC",
        "confidence": 75,
        "accountType": "demo"
    }
    
    try:
        print("[INFO] Sending request to API...")
        response = requests.post(
            "http://localhost:5000/trade",
            json=payload,
            timeout=30  # Shorter timeout for diagnostic
        )
        
        print(f"[INFO] Response status: {response.status_code}")
        print(f"[INFO] Response headers: {dict(response.headers)}")
        
        if response.content:
            try:
                data = response.json()
                print(f"[INFO] Response data: {mask_sensitive_data(json.dumps(data, indent=2))}")
                
                if 'error' in data:
                    print(f"[ERROR] API Error: {data['error']}")
                    
                if 'tradingState' in data:
                    print(f"[INFO] Trading State: {data['tradingState']}")
                    
            except json.JSONDecodeError:
                print(f"[ERROR] Invalid JSON response: {mask_sensitive_data(response.text)}")
        else:
            print("[ERROR] Empty response")
            
        return response.status_code == 200
        
    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def test_different_pairs():
    """Test with different trading pairs"""
    print("\n=== TESTING DIFFERENT TRADING PAIRS ===")
    
    pairs_to_test = [
        "EURUSD-OTC",
        "GBPUSD-OTC", 
        "USDJPY-OTC",
        "AUDCHF-OTC",
        "NZDUSD-OTC"
    ]
    
    for pair in pairs_to_test:
        print(f"\n[INFO] Testing pair: {pair}")
        
        payload = {
            "email": os.environ.get('TEST_EMAIL'),
            "password": os.environ.get('TEST_PASSWORD'),
            "action": "call",
            "pair": pair,
            "confidence": 75,
            "accountType": "demo"
        }
        
        try:
            response = requests.post(
                "http://localhost:5000/trade",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"✅ {pair}: SUCCESS")
                return True
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                    print(f"❌ {pair}: {error_msg}")
                except:
                    print(f"❌ {pair}: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"❌ {pair}: {e}")
    
    return False

def main():
    """Main diagnostic execution"""
    print("🔍 DIAGNOSTIC TEST SUITE")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test 1: Direct connection
    connection_ok = test_connection_only()
    
    # Test 2: API with detailed errors
    api_ok = test_api_with_detailed_error()
    
    # Test 3: Different pairs (only if API connection works)
    if not api_ok:
        pairs_ok = test_different_pairs()
    else:
        pairs_ok = True
    
    # Summary
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"Direct Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"API Connection: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"Alternative Pairs: {'✅ PASS' if pairs_ok else '❌ FAIL'}")
    
    if connection_ok and not api_ok:
        print("\n🔍 DIAGNOSIS:")
        print("- Direct IQOption connection works")
        print("- API wrapper has issues")
        print("- Check API server logs for detailed errors")
        print("- Possible issues: market closed, insufficient balance, API limits")
    elif not connection_ok:
        print("\n🔍 DIAGNOSIS:")
        print("- IQOption connection failed")
        print("- Check credentials and network connectivity")
        print("- IQOption servers might be down")
    elif api_ok:
        print("\n✅ ALL SYSTEMS OPERATIONAL")
    
    return 0 if (connection_ok and api_ok) else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)