"""
Test script to verify the Flask API
"""
import requests
import json

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        print(f"✅ Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_trade():
    """Test trade execution"""
    print("\nTesting trade execution...")

    payload = {
        "email": "tombokael4@gmail.com",
        "password": "tombokael04",
        "action": "call",
        "pair": "EURUSD",
        "amount": 1,
        "duration": 1,
        "accountType": "demo"
    }

    print(f"Sending request: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            'http://localhost:5000/trade',
            json=payload,
            timeout=120  # 2 minutes timeout
        )

        result = response.json()
        print(f"\n📊 Response:")
        print(json.dumps(result, indent=2))

        if result.get('success'):
            print("\n✅ Trade executed successfully!")
        else:
            print(f"\n❌ Trade failed: {result.get('error')}")

        return result.get('success', False)
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("API TEST SUITE")
    print("=" * 60)

    # Test health
    if test_health():
        print("\n" + "=" * 60)

        # Test trade (only if health check passes)
        user_input = input("\nDo you want to test trade execution? (yes/no): ")
        if user_input.lower() in ['yes', 'y']:
            test_trade()

    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)
