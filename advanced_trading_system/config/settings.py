"""
Trading Configuration Settings
Centralized configuration for the trading system
"""
import os


class TradingConfig:
    """Trading system configuration"""

    # ========================================================================
    # Account Settings
    # ========================================================================
    # SECURITY: Credentials must be set via environment variables
    EMAIL = os.getenv('IQOPTION_EMAIL')
    PASSWORD = os.getenv('IQOPTION_PASSWORD')
    ACCOUNT_TYPE = os.getenv('ACCOUNT_TYPE', 'demo')  # 'demo' or 'real'

    # ========================================================================
    # AI Model Settings
    # ========================================================================
    USE_OPENAI = os.getenv('USE_OPENAI', 'true').lower() == 'true'
    USE_CLAUDE = os.getenv('USE_CLAUDE', 'true').lower() == 'true'
    USE_DEEPSEEK = os.getenv('USE_DEEPSEEK', 'true').lower() == 'true'

    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-haiku-20241022')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

    # AI Model Weights (can be adjusted based on performance)
    OPENAI_WEIGHT = float(os.getenv('OPENAI_WEIGHT', '1.2'))
    CLAUDE_WEIGHT = float(os.getenv('CLAUDE_WEIGHT', '1.0'))
    DEEPSEEK_WEIGHT = float(os.getenv('DEEPSEEK_WEIGHT', '1.0'))

    # ========================================================================
    # Consensus Settings
    # ========================================================================
    CONSENSUS_THRESHOLD = float(os.getenv('CONSENSUS_THRESHOLD', '0.66'))  # 66%
    MIN_CONFIDENCE = int(os.getenv('MIN_CONFIDENCE', '65'))  # Minimum 65%

    # ========================================================================
    # Trading Parameters
    # ========================================================================
    BASE_AMOUNT = float(os.getenv('BASE_AMOUNT', '2.0'))
    MIN_AMOUNT = float(os.getenv('MIN_AMOUNT', '1.0'))
    MAX_AMOUNT = float(os.getenv('MAX_AMOUNT', '20.0'))

    # Trade Duration (minutes)
    DEFAULT_DURATION = int(os.getenv('DEFAULT_DURATION', '1'))
    MIN_DURATION = 1
    MAX_DURATION = 5

    # ========================================================================
    # Risk Management
    # ========================================================================
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '50.0'))
    MAX_DAILY_PROFIT = float(os.getenv('MAX_DAILY_PROFIT', '200.0'))
    MAX_CONSECUTIVE_LOSSES = int(os.getenv('MAX_CONSECUTIVE_LOSSES', '3'))
    MIN_ACCOUNT_BALANCE = float(os.getenv('MIN_ACCOUNT_BALANCE', '50.0'))

    # ========================================================================
    # Database Settings
    # ========================================================================
    DB_PATH = os.getenv('DB_PATH', 'data/trades_advanced.db')

    # ========================================================================
    # Logging Settings
    # ========================================================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/trading.log')

    # ========================================================================
    # Market Analysis Settings
    # ========================================================================
    CANDLE_COUNT = int(os.getenv('CANDLE_COUNT', '100'))
    TIMEFRAME = os.getenv('TIMEFRAME', '1m')

    # Technical Indicators
    RSI_PERIOD_14 = 14
    RSI_PERIOD_7 = 7
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BB_PERIOD = 20
    BB_STD = 2

    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []

        # Critical: Validate required credentials
        if not cls.EMAIL:
            errors.append("IQOPTION_EMAIL environment variable is required")
        if not cls.PASSWORD:
            errors.append("IQOPTION_PASSWORD environment variable is required")

        if cls.CONSENSUS_THRESHOLD < 0.5 or cls.CONSENSUS_THRESHOLD > 1.0:
            errors.append("CONSENSUS_THRESHOLD must be between 0.5 and 1.0")

        if cls.MIN_CONFIDENCE < 0 or cls.MIN_CONFIDENCE > 100:
            errors.append("MIN_CONFIDENCE must be between 0 and 100")

        if cls.BASE_AMOUNT < cls.MIN_AMOUNT:
            errors.append("BASE_AMOUNT must be >= MIN_AMOUNT")

        if cls.MAX_AMOUNT < cls.BASE_AMOUNT:
            errors.append("MAX_AMOUNT must be >= BASE_AMOUNT")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(errors))

        return True

    @classmethod
    def display(cls):
        """Display current configuration"""
        print("\n" + "=" * 70)
        print("⚙️  TRADING SYSTEM CONFIGURATION")
        print("=" * 70)

        print(f"\n📧 Account:")
        print(f"   Type: {cls.ACCOUNT_TYPE.upper()}")
        print(f"   Email: {cls.EMAIL}")

        print(f"\n🤖 AI Models:")
        print(f"   OpenAI: {'✅' if cls.USE_OPENAI else '❌'} (weight: {cls.OPENAI_WEIGHT})")
        print(f"   Claude: {'✅' if cls.USE_CLAUDE else '❌'} (weight: {cls.CLAUDE_WEIGHT})")
        print(f"   DeepSeek: {'✅' if cls.USE_DEEPSEEK else '❌'} (weight: {cls.DEEPSEEK_WEIGHT})")

        print(f"\n🎯 Consensus:")
        print(f"   Threshold: {cls.CONSENSUS_THRESHOLD * 100:.0f}%")
        print(f"   Min Confidence: {cls.MIN_CONFIDENCE}%")

        print(f"\n💰 Trading:")
        print(f"   Base Amount: ${cls.BASE_AMOUNT}")
        print(f"   Range: ${cls.MIN_AMOUNT} - ${cls.MAX_AMOUNT}")
        print(f"   Default Duration: {cls.DEFAULT_DURATION}m")

        print(f"\n🛡️  Risk Management:")
        print(f"   Max Daily Loss: ${cls.MAX_DAILY_LOSS}")
        print(f"   Max Daily Profit: ${cls.MAX_DAILY_PROFIT}")
        print(f"   Max Consecutive Losses: {cls.MAX_CONSECUTIVE_LOSSES}")

        print(f"\n💾 Database:")
        print(f"   Path: {cls.DB_PATH}")

        print("\n" + "=" * 70)
