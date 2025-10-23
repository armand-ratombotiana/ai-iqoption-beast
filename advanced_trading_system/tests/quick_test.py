"""
Quick test script to identify immediate issues
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from iqoptionapi.stable_api import IQ_Option


async def quick_connection_test():
    """Quick test of basic IQOption connection"""
    print("🔍 Quick Connection Test")
    print("-" * 30)
    
    # Check environment variables
    email = os.getenv('IQOPTION_EMAIL')
    password = os.getenv('IQOPTION_PASSWORD')
    
    if not email or not password:
        print("❌ Missing credentials:")
        print("   Set IQOPTION_EMAIL and IQOPTION_PASSWORD environment variables")
        return False
    
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {'*' * len(password)}")
    
    try:
        # Test basic connection
        print("\n🔌 Connecting to IQOption...")
        api = IQ_Option(email, password)
        check, reason = api.connect()
        
        if check:
            print("✅ Connection successful!")
            
            # Test basic operations
            api.change_balance('PRACTICE')
            balance = api.get_balance()
            print(f"💰 Practice Balance: ${balance:.2f}")
            
            # Test getting pairs
            print("\n📊 Testing pairs access...")
            open_time = api.get_all_open_time()
            if open_time:
                turbo_pairs = open_time.get('turbo', {})
                binary_pairs = open_time.get('binary', {})
                print(f"   Turbo pairs: {len(turbo_pairs)}")
                print(f"   Binary pairs: {len(binary_pairs)}")
                
                # Test a specific pair
                if turbo_pairs:
                    test_pair = list(turbo_pairs.keys())[0] + '-OTC'
                    print(f"\n🧪 Testing pair: {test_pair}")
                    
                    try:
                        payout = api.get_payout(test_pair, 1)
                        print(f"   Payout: {payout:.1%}" if payout else "   Payout: Not available")
                    except Exception as e:
                        print(f"   Payout error: {e}")
                    
                    try:
                        candles = api.get_candles(test_pair, 1, 5, int(time.time()))
                        print(f"   Candles: {len(candles) if candles else 0} received")
                    except Exception as e:
                        print(f"   Candles error: {e}")
            
            api.close()
            return True
            
        else:
            print(f"❌ Connection failed: {reason}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import time
    asyncio.run(quick_connection_test())
