"""
Complete test suite for n8n node functionality
Tests the full workflow: n8n node → Flask API → IQ Option
"""
import requests
import json
import time

def test_health():
    """Test 1: Health check endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)

    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        result = response.json()

        if result.get('status') == 'ok':
            print("✅ PASSED - Health check successful")
            print(f"   Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print("❌ FAILED - Health check returned unexpected status")
            return False
    except Exception as e:
        print(f"❌ FAILED - Health check error: {e}")
        return False

def test_api_validation():
    """Test 2: API parameter validation"""
    print("\n" + "="*60)
    print("TEST 2: API Parameter Validation")
    print("="*60)

    # Test missing required field
    print("\n2.1: Testing missing required field...")
    try:
        response = requests.post(
            'http://localhost:5000/trade',
            json={"email": "test@test.com"},  # Missing other required fields
            timeout=5
        )

        if response.status_code == 400:
            error = response.json()
            print("✅ PASSED - Correctly rejected missing fields")
            print(f"   Error: {error.get('error')}")
        else:
            print("❌ FAILED - Should reject missing fields")
            return False
    except Exception as e:
        print(f"❌ FAILED - Validation test error: {e}")
        return False

    return True

def test_n8n_node_payload():
    """Test 3: Simulate n8n node request"""
    print("\n" + "="*60)
    print("TEST 3: Simulate n8n Node Request")
    print("="*60)

    # This simulates what the n8n node would send
    payload = {
        "email": "tombokael4@gmail.com",
        "password": "tombokael04",
        "action": "call",
        "pair": "AUDCHF-OTC",
        "amount": 1,
        "duration": 1,
        "accountType": "demo"
    }

    print("\n📤 Sending request to API...")
    print(f"   Payload: {json.dumps(payload, indent=2)}")

    try:
        print("\n⏳ Executing trade (this will take ~70 seconds)...")
        print("   [TRADE REQUEST] CALL AUDCHF-OTC $1 for 1min")

        response = requests.post(
            'http://localhost:5000/trade',
            json=payload,
            timeout=120  # 2 minutes timeout
        )

        result = response.json()

        print("\n📥 Response received:")
        print(json.dumps(result, indent=2))

        # Validate response structure
        required_fields = [
            'success', 'orderId', 'action', 'pair', 'amount',
            'duration', 'profit', 'result', 'oldBalance',
            'newBalance', 'balanceChange', 'timestamp'
        ]

        print("\n🔍 Validating response structure...")
        all_present = True
        for field in required_fields:
            if field in result:
                print(f"   ✅ {field}: {result[field]}")
            else:
                print(f"   ❌ Missing field: {field}")
                all_present = False

        if result.get('success') and all_present:
            print("\n✅ PASSED - n8n node simulation successful!")
            print(f"\n📊 Trade Summary:")
            print(f"   Order ID: {result.get('orderId')}")
            print(f"   Action: {result.get('action').upper()}")
            print(f"   Pair: {result.get('pair')}")
            print(f"   Result: {result.get('result').upper()}")
            print(f"   Profit/Loss: ${result.get('profit'):.2f}")
            print(f"   Balance Change: ${result.get('balanceChange'):.2f}")
            return True
        else:
            print(f"\n❌ FAILED - {result.get('error', 'Unknown error')}")
            return False

    except requests.Timeout:
        print("❌ FAILED - Request timeout (trade took too long)")
        return False
    except Exception as e:
        print(f"❌ FAILED - Trade simulation error: {e}")
        return False

def test_node_structure():
    """Test 4: Verify n8n node files exist"""
    print("\n" + "="*60)
    print("TEST 4: Verify n8n Node Structure")
    print("="*60)

    import os

    files_to_check = [
        'n8n-nodes-trading/package.json',
        'n8n-nodes-trading/nodes/Trading/Trading.node.js',
        'n8n-nodes-trading/nodes/Trading/trading.svg',
    ]

    all_exist = True
    for file_path in files_to_check:
        full_path = os.path.join('/app/app/KAEL/KAEL', file_path)
        if os.path.exists(full_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ Missing: {file_path}")
            all_exist = False

    if all_exist:
        print("\n✅ PASSED - All n8n node files present")
        return True
    else:
        print("\n❌ FAILED - Some files missing")
        return False

def test_node_configuration():
    """Test 5: Verify n8n node configuration"""
    print("\n" + "="*60)
    print("TEST 5: Verify n8n Node Configuration")
    print("="*60)

    try:
        with open('/app/app/KAEL/KAEL/n8n-nodes-trading/package.json', 'r') as f:
            package = json.load(f)

        print("\n📦 Package Information:")
        print(f"   Name: {package.get('name')}")
        print(f"   Version: {package.get('version')}")
        print(f"   Description: {package.get('description')}")

        if 'n8n' in package and 'nodes' in package['n8n']:
            nodes = package['n8n']['nodes']
            print(f"\n📋 Registered Nodes:")
            for node in nodes:
                print(f"   ✅ {node}")

            print("\n✅ PASSED - Node configuration valid")
            return True
        else:
            print("\n❌ FAILED - Invalid n8n configuration")
            return False

    except Exception as e:
        print(f"❌ FAILED - Configuration check error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "N8N NODE TEST SUITE" + " "*23 + "║")
    print("╚" + "="*58 + "╝")

    tests = [
        ("Health Check", test_health),
        ("API Validation", test_api_validation),
        ("Node Structure", test_node_structure),
        ("Node Configuration", test_node_configuration),
        ("n8n Node Simulation", test_n8n_node_payload),  # Run this last (takes time)
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")

    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! n8n node is ready to use!")
        print("\n📝 Next Steps:")
        print("   1. Install node in n8n: cd n8n-nodes-trading && npm link")
        print("   2. Restart n8n to load the new node")
        print("   3. Add 'Trading Bot' node to your workflow")
        print("   4. Configure with your credentials and trade!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")

    return passed == total

if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
