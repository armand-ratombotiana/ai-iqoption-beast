#!/usr/bin/env python3
"""
Interactive script to set up .env file with real credentials for testing
"""
import os
import getpass
from pathlib import Path


def setup_credentials():
    """Interactive setup for .env file"""
    print("=" * 70)
    print("KAEL TRADING SYSTEM - CREDENTIAL SETUP")
    print("=" * 70)
    print()
    print("⚠️  SECURITY WARNING:")
    print("  - Your credentials will be stored in .env file")
    print("  - Never commit .env file to git!")
    print("  - Use DEMO mode for initial testing")
    print()

    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        response = input(".env file already exists. Overwrite? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Aborted. Existing .env file kept.")
            return

    # Collect credentials
    print("\n📧 IQ OPTION CREDENTIALS")
    print("-" * 70)
    iqoption_email = input("IQ Option Email: ").strip()
    iqoption_password = getpass.getpass("IQ Option Password: ")

    print("\n🤖 AI API KEYS")
    print("-" * 70)
    anthropic_key = getpass.getpass("Anthropic API Key (for Claude) [optional]: ").strip()
    openai_key = getpass.getpass("OpenAI API Key [optional]: ").strip()
    deepseek_key = getpass.getpass("DeepSeek API Key [optional]: ").strip()

    print("\n⚙️  TRADING CONFIGURATION")
    print("-" * 70)
    trading_mode = input("Trading Mode (demo/live) [default: demo]: ").strip() or "demo"

    # Create .env content
    env_content = f"""# =============================================================================
# KAEL TRADING SYSTEM - CREDENTIALS
# =============================================================================
# ⚠️  NEVER COMMIT THIS FILE TO GIT!
# Generated: {os.popen('date').read().strip()}

# =============================================================================
# IQ OPTION CREDENTIALS (REQUIRED)
# =============================================================================
IQOPTION_EMAIL={iqoption_email}
IQOPTION_PASSWORD={iqoption_password}

# =============================================================================
# TRADING MODE
# =============================================================================
# Options: 'demo' or 'live'
# ⚠️  ALWAYS start with 'demo' for testing!
TRADING_MODE={trading_mode}

# =============================================================================
# AI API KEYS (Optional but recommended)
# =============================================================================
ANTHROPIC_API_KEY={anthropic_key}
OPENAI_API_KEY={openai_key}
DEEPSEEK_API_KEY={deepseek_key}

# =============================================================================
# BINARY OPTIONS SETTINGS
# =============================================================================
BASE_TRADE_AMOUNT=1.0
MAX_TRADE_AMOUNT=10.0
TRADING_ASSETS=EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,NZDUSD,EURJPY,GBPJPY

# =============================================================================
# RISK MANAGEMENT
# =============================================================================
MAX_DAILY_LOSS=50
MAX_DAILY_PROFIT=100
MAX_CONSECUTIVE_LOSSES=5
MIN_BALANCE=50
MAX_TRADES_PER_HOUR=30
MAX_TRADES_PER_DAY=200

# =============================================================================
# MARTINGALE STRATEGY
# =============================================================================
ENABLE_MARTINGALE=true
MARTINGALE_MULTIPLIER=1.5
MAX_MARTINGALE_LEVEL=3

# =============================================================================
# AI SIGNAL REQUIREMENTS
# =============================================================================
MIN_AI_CONFIDENCE=65
MIN_CONSENSUS_AGREEMENT=0.7

# =============================================================================
# TIMING CONTROLS
# =============================================================================
MIN_SECONDS_BETWEEN_TRADES=70

# =============================================================================
# HEALTH MONITORING
# =============================================================================
ENABLE_HEALTH_API=true
HEALTH_API_PORT=5001

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL=INFO

# =============================================================================
# ADVANCED SETTINGS
# =============================================================================
AUTO_RESTART_ON_ERROR=true
MAX_RESTART_ATTEMPTS=100
RESTART_DELAY_SECONDS=60
CONNECTION_CHECK_INTERVAL=300
"""

    # Write .env file
    with open(".env", "w") as f:
        f.write(env_content)

    # Set permissions
    os.chmod(".env", 0o600)

    print("\n✅ SUCCESS!")
    print("=" * 70)
    print(f"  .env file created successfully")
    print(f"  Trading Mode: {trading_mode.upper()}")
    print(f"  File permissions: 600 (read/write for owner only)")
    print()
    print("📋 NEXT STEPS:")
    print("  1. Review .env file: cat .env")
    print("  2. Install dependencies: pip install -r requirements.txt")
    print("  3. Run connection test: python tests/integration/test_connection.py")
    print("  4. Run full test suite: pytest tests/")
    print()
    print("⚠️  IMPORTANT:")
    print("  - .env file contains sensitive credentials")
    print("  - Never commit to version control")
    print("  - Always use DEMO mode for testing first")
    print("=" * 70)


if __name__ == "__main__":
    try:
        setup_credentials()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Setup failed. Please try again.")
