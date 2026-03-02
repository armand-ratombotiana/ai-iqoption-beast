"""
Trading Configuration Settings
Centralized configuration for the trading system with secure secrets management
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from utils.secrets_manager import SecretsManager, get_secrets_manager

# Load .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try loading from current directory
    load_dotenv()

# Initialize secrets manager
_secrets = get_secrets_manager(environment=os.getenv('ENVIRONMENT', 'production'))


class TradingConfig:
    """Trading system configuration"""

    # ========================================================================
    # Account Settings
    # ========================================================================
    # SECURITY: Credentials managed by SecretsManager
    EMAIL = _secrets.get_credential('IQOPTION_EMAIL')
    PASSWORD = _secrets.get_credential('IQOPTION_PASSWORD')
    ACCOUNT_TYPE = _secrets.get_credential('ACCOUNT_TYPE', 'demo')  # 'demo' or 'real'

    # ========================================================================
    # AI Model Settings
    # ========================================================================
    USE_OPENAI = os.getenv('USE_OPENAI', 'false').lower() == 'true'
    USE_CLAUDE = os.getenv('USE_CLAUDE', 'false').lower() == 'true'
    USE_DEEPSEEK = os.getenv('USE_DEEPSEEK', 'false').lower() == 'true'
    USE_FREE_AI = os.getenv('USE_FREE_AI', 'true').lower() == 'true'  # FREE AI enabled by default

    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-haiku-20241022')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    FREE_AI_TYPE = os.getenv('FREE_AI_TYPE', 'rule-based')  # 'rule-based' or 'huggingface'

    # AI Model Weights (can be adjusted based on performance)
    OPENAI_WEIGHT = float(os.getenv('OPENAI_WEIGHT', '1.2'))
    CLAUDE_WEIGHT = float(os.getenv('CLAUDE_WEIGHT', '1.0'))
    DEEPSEEK_WEIGHT = float(os.getenv('DEEPSEEK_WEIGHT', '1.0'))
    FREE_AI_WEIGHT = float(os.getenv('FREE_AI_WEIGHT', '1.5'))  # Higher weight for free AI

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
        """Validate configuration with secrets manager"""
        errors = []

        # Use SecretsManager for credential validation
        try:
            is_valid, validation_errors = _secrets.validate_credentials(raise_on_error=False)
            if not is_valid:
                errors.extend(validation_errors)
        except Exception as e:
            errors.append(f"Secrets validation error: {str(e)}")

        # Validate trading parameters
        if cls.CONSENSUS_THRESHOLD < 0.5 or cls.CONSENSUS_THRESHOLD > 1.0:
            errors.append("CONSENSUS_THRESHOLD must be between 0.5 and 1.0")

        if cls.MIN_CONFIDENCE < 0 or cls.MIN_CONFIDENCE > 100:
            errors.append("MIN_CONFIDENCE must be between 0 and 100")

        if cls.BASE_AMOUNT < cls.MIN_AMOUNT:
            errors.append("BASE_AMOUNT must be >= MIN_AMOUNT")

        if cls.MAX_AMOUNT < cls.BASE_AMOUNT:
            errors.append("MAX_AMOUNT must be >= BASE_AMOUNT")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        return True

    @classmethod
    def display(cls):
        """Display current configuration with masked credentials"""
        print("\n" + "=" * 70)
        print("TRADING SYSTEM CONFIGURATION")
        print("=" * 70)

        # Display account info with masked credentials
        print(f"\nAccount:")
        print(f"   Type: {cls.ACCOUNT_TYPE.upper()}")
        masked_email = _secrets.mask_for_logging(cls.EMAIL) if cls.EMAIL else "NOT SET"
        print(f"   Email: {masked_email}")

        print(f"\nAI Models:")
        print(f"   Free AI: {'ENABLED' if cls.USE_FREE_AI else 'DISABLED'} (weight: {cls.FREE_AI_WEIGHT}) - {cls.FREE_AI_TYPE}")
        print(f"   OpenAI: {'ENABLED' if cls.USE_OPENAI else 'DISABLED'} (weight: {cls.OPENAI_WEIGHT})")
        print(f"   Claude: {'ENABLED' if cls.USE_CLAUDE else 'DISABLED'} (weight: {cls.CLAUDE_WEIGHT})")
        print(f"   DeepSeek: {'ENABLED' if cls.USE_DEEPSEEK else 'DISABLED'} (weight: {cls.DEEPSEEK_WEIGHT})")

        print(f"\nConsensus:")
        print(f"   Threshold: {cls.CONSENSUS_THRESHOLD * 100:.0f}%")
        print(f"   Min Confidence: {cls.MIN_CONFIDENCE}%")

        print(f"\nTrading:")
        print(f"   Base Amount: ${cls.BASE_AMOUNT}")
        print(f"   Range: ${cls.MIN_AMOUNT} - ${cls.MAX_AMOUNT}")
        print(f"   Default Duration: {cls.DEFAULT_DURATION}m")

        print(f"\nRisk Management:")
        print(f"   Max Daily Loss: ${cls.MAX_DAILY_LOSS}")
        print(f"   Max Daily Profit: ${cls.MAX_DAILY_PROFIT}")
        print(f"   Max Consecutive Losses: {cls.MAX_CONSECUTIVE_LOSSES}")

        print(f"\nDatabase:")
        print(f"   Path: {cls.DB_PATH}")

        print("\n" + "=" * 70)

    @classmethod
    def get_secrets_manager(cls) -> SecretsManager:
        """Get the secrets manager instance"""
        return _secrets
