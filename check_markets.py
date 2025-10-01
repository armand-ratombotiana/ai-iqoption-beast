"""
Check available markets and their status
"""
from iqoptionapi.stable_api import IQ_Option
import time

def check_available_markets(email, password):
    """Check what markets are currently open"""
    print("Connecting to IQ Option...")
    api = IQ_Option(email, password)
    check, reason = api.connect()

    if not check:
        print(f"❌ Connection failed: {reason}")
        return

    print(f"✅ Connected successfully!")
    api.change_balance('PRACTICE')

    # Get open markets
    print("\n" + "="*60)
    print("CHECKING BINARY OPTIONS MARKETS")
    print("="*60)

    open_times = api.get_all_open_time()

    if 'binary' in open_times:
        binary_markets = []
        for pair, info in open_times['binary'].items():
            is_open = info.get('open', False)
            if is_open:
                binary_markets.append(pair)

        print(f"\n✅ Found {len(binary_markets)} open binary markets:")
        for i, pair in enumerate(sorted(binary_markets)[:20], 1):  # Show first 20
            print(f"   {i}. {pair}")

    # Check digital markets
    print("\n" + "="*60)
    print("CHECKING DIGITAL OPTIONS MARKETS")
    print("="*60)

    if 'digital' in open_times:
        digital_markets = []
        for pair, info in open_times['digital'].items():
            is_open = info.get('open', False)
            if is_open:
                digital_markets.append(pair)

        print(f"\n✅ Found {len(digital_markets)} open digital markets:")
        for i, pair in enumerate(sorted(digital_markets)[:20], 1):  # Show first 20
            print(f"   {i}. {pair}")

    # Get balance
    balance = api.get_balance()
    print(f"\n" + "="*60)
    print(f"Current Demo Balance: ${balance}")
    print("="*60)

if __name__ == '__main__':
    EMAIL = "tombokael4@gmail.com"
    PASSWORD = "tombokael04"

    check_available_markets(EMAIL, PASSWORD)
