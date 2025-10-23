#!/usr/bin/env python3
"""
Comprehensive Test Runner
Runs all tests with real credentials and generates detailed report
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print("\n" + "╔" + "═" * 78 + "╗")
    print(f"║{title.center(78)}║")
    print("╚" + "═" * 78 + "╝\n")

def run_test_file(test_file: str, description: str) -> bool:
    """Run a test file and return success status"""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    """Main test runner"""
    print_header("KAEL TRADING SYSTEM - COMPREHENSIVE TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}\n")
    
    # Check environment
    if not os.getenv('IQOPTION_EMAIL') or not os.getenv('IQOPTION_PASSWORD'):
        print("❌ ERROR: IQOption credentials not set in environment")
        print("Please set IQOPTION_EMAIL and IQOPTION_PASSWORD")
        return False
    
    print("✅ Environment credentials found\n")
    
    # Define test suite
    tests = [
        {
            'file': 'tests/test_data_ingestion.py',
            'description': 'Data Ingestion Layer Tests',
            'critical': True
        },
        {
            'file': 'tests/integration/test_all_components_real.py',
            'description': 'Component Integration Tests',
            'critical': True
        },
    ]
    
    results = {}
    
    # Run each test
    for test in tests:
        test_file = Path(test['file'])
        
        if not test_file.exists():
            print(f"⚠️  Test file not found: {test_file}")
            results[test['description']] = False
            continue
        
        success = run_test_file(str(test_file), test['description'])
        results[test['description']] = success
        
        if not success and test.get('critical', False):
            print(f"\n❌ Critical test failed: {test['description']}")
            print("Stopping test suite execution")
            break
    
    # Print summary
    print_header("TEST SUITE SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {percentage:.1f}%\n")
    
    print("Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
