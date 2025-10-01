#!/usr/bin/env python3
"""
Test script for the Trading API
Tests all endpoints without making real trades
"""

import requests
import json

API_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("\n[TEST] Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_status():
    """Test status endpoint"""
    print("\n[TEST] Get Status")
    print("=" * 60)
    try:
        response = requests.get(f"{API_URL}/status", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_trade_validation():
    """Test trade validation (should fail without credentials)"""
    print("\n[TEST] Trade Validation (Missing Fields)")
    print("=" * 60)
    try:
        response = requests.post(f"{API_URL}/trade", json={}, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("TRADING API TEST SUITE")
    print("=" * 60)
    print("\nNOTE: Start API with: python3 trading_api.py")
    
    tests = [
        ("Health Check", test_health),
        ("Get Status", test_status),
        ("Trade Validation", test_trade_validation),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' crashed: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\n{passed}/{total} tests passed\n")

if __name__ == "__main__":
    main()
