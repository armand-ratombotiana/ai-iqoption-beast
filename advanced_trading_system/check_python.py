# -*- coding: utf-8 -*-
"""
Python Version Checker
Checks if the correct Python version is installed
Compatible with Python 2.7 and 3.x
"""

from __future__ import print_function
import sys

def check_python_version():
    """Check Python version and provide guidance"""
    
    print("\n" + "="*70)
    print("PYTHON VERSION CHECK")
    print("="*70)
    
    # Get current version
    major = sys.version_info[0]
    minor = sys.version_info[1]
    patch = sys.version_info[2]
    
    print("\nCurrent Python Version: {0}.{1}.{2}".format(major, minor, patch))
    print("Full Version: {0}".format(sys.version))
    print("Executable: {0}".format(sys.executable))
    
    # Check if version is compatible
    if major < 3:
        print("\nERROR: Python 2.x detected!")
        print("\nKAEL AI Agents System requires Python 3.7 or higher")
        print("\nSOLUTION:")
        print("\n   Option 1: Install Python 3.9+ (Recommended)")
        print("   -----------------------------------------")
        print("   Windows:")
        print("   1. Download from: https://www.python.org/downloads/")
        print("   2. Run installer (check 'Add Python to PATH')")
        print("   3. Restart terminal")
        print("   4. Run: python3 check_python.py")
        print("\n   Linux/Mac:")
        print("   sudo apt-get install python3.9  # Ubuntu/Debian")
        print("   brew install python@3.9         # macOS")
        print("\n   Option 2: Use Python Virtual Environment")
        print("   -----------------------------------------")
        print("   1. Install Python 3.9+")
        print("   2. Create venv: python3 -m venv kael_env")
        print("   3. Activate:")
        print("      Windows: kael_env\\Scripts\\activate")
        print("      Linux/Mac: source kael_env/bin/activate")
        print("   4. Run tests: python test_comprehensive_agents.py")
        
        print("\n" + "="*70)
        return False
    
    elif major == 3 and minor < 7:
        print("\nWARNING: Python {0}.{1} detected".format(major, minor))
        print("Minimum required: Python 3.7")
        print("Recommended: Python 3.9+")
        print("\nPlease upgrade Python to 3.7 or higher")
        print("\n" + "="*70)
        return False
    
    else:
        print("\nSUCCESS: Python {0}.{1} is compatible!".format(major, minor))
        
        if minor >= 9:
            print("Excellent! Python 3.9+ detected")
        elif minor >= 7:
            print("Good! Python 3.7+ detected")
        
        print("\nNext Steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Configure: cp .env.example .env")
        print("   3. Run tests: python test_comprehensive_agents.py")
        
        print("\n" + "="*70)
        return True

if __name__ == "__main__":
    try:
        is_compatible = check_python_version()
        sys.exit(0 if is_compatible else 1)
    except Exception as e:
        print("\nError checking Python version: {0}".format(e))
        sys.exit(1)