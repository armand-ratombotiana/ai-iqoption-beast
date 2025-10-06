"""
Enhanced Configuration System
Production-ready configuration with validation, environment support, and secrets management
"""
import os
import yaml
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from pathlib import Path
import hvac  # HashiCorp Vault client


class DatabaseConfig(BaseModel):
    """Database configuration"""
    type: str = Field(default="sqlite", description="Database type: sqlite, postgresql")
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(default="trading_db", description="Database name")
    username: Optional[str] = Field(default=None, description="Database username")
    password: Optional[str] = Field(default=None, description="Database password")
    sqlite_path: str = Field(default="data/trades_enhanced.db", description="SQLite file path")
    pool_size: int = Field(default=10, description="Connection pool size")
    max_overflow: int = Field(default=20, description="Max pool overflow")
    
    @property
    def connection_string(self) -> str:
        """Generate database connection string"""
        if self.type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        elif self.type == "postgresql":
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"
        else:
            raise ValueError(f"Unsupported database type: {self.type}")


class RedisConfig(BaseModel):
    """Redis configuration"""
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    password: Optional[str] = Field(default=None, description="Redis password")
    db: int = Field(default=0, description="Redis database number")
    max_connections: int = Field(default=10, description="Max connections in pool")
    
    @property
    def connection_string(self) -> str:
        """Generate Redis connection string"""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class AIModelConfig(BaseModel):
    """AI Model configuration"""
    enabled: bool = Field(default=True, description="Enable this model")
    model_name: str = Field(description="Model name/version")
    api_key: Optional[str] = Field(default=None, description="API key")
    weight: float = Field(default=1.0, ge=0.1, le=5.0, description="Model weight in consensus")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    rate_limit: int = Field(default=60, description="Requests per minute")


class TradingConfig(BaseModel):
    """Trading configuration"""
    base_amount: float = Field(default=2.0, gt=0, description="Base trade amount")
    min_amount: float = Field(default=1.0, gt=0, description="Minimum trade amount")
    max_amount: float = Field(default=20.0, gt=0, description="Maximum trade amount")
    default_duration: int = Field(default=1, ge=1, le=5, description="Default trade duration in minutes")
    payout_ratio: float = Field(default=0.8, gt=0, le=2.0, description="Payout ratio for wins")
    
    @validator('max_amount')
    def max_amount_must_be_greater_than_min(cls, v, values):
        if 'min_amount' in values and v <= values['min_amount']:
            raise ValueError('max_amount must be greater than min_amount')
        return v


class RiskManagementConfig(BaseModel):
    """Risk management configuration"""
    max_daily_loss: float = Field(default=50.0, gt=0, description="Maximum daily loss")
    max_daily_profit: float = Field(default=200.0, gt=0, description="Maximum daily profit")
    max_consecutive_losses: int = Field(default=3, ge=1, description="Max consecutive losses before pause")
    min_account_balance: float = Field(default=50.0, gt=0, description="Minimum account balance")
    position_size_method: str = Field(default="kelly", description="Position sizing method: fixed, kelly, confidence")
    kelly_fraction: float = Field(default=0.25, gt=0, le=1.0, description="Fraction of Kelly criterion to use")


class ConsensusConfig(BaseModel):
    """AI Consensus configuration"""
    threshold: float = Field(default=0.66, ge=0.5, le=1.0, description="Consensus threshold (66%)")
    min_confidence: int = Field(default=65, ge=0, le=100, description="Minimum confidence to trade")
    min_models: int = Field(default=2, ge=1, description="Minimum models required for consensus")
    exploration_rate: float = Field(default=0.1, ge=0, le=0.5, description="Exploration rate for multi-armed bandit")


class MonitoringConfig(BaseModel):
    """Monitoring and logging configuration"""
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/trading.log", description="Log file path")
    enable_prometheus: bool = Field(default=False, description="Enable Prometheus metrics")
    prometheus_port: int = Field(default=8000, description="Prometheus metrics port")
    enable_sentry: bool = Field(default=False, description="Enable Sentry error tracking")
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")


class SecurityConfig(BaseModel):
    """Security configuration"""
    use_vault: bool = Field(default=False, description="Use HashiCorp Vault for secrets")
    vault_url: Optional[str] = Field(default=None, description="Vault server URL")
    vault_token: Optional[str] = Field(default=None, description="Vault token")
    vault_path: str = Field(default="secret/trading", description="Vault secret path")
    encrypt_database: bool = Field(default=False, description="Encrypt database")
    api_key_rotation_days: int = Field(default=90, description="API key rotation period")


class EnhancedTradingConfig(BaseModel):
    """Enhanced trading system configuration"""
    
    # Environment
    environment: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Account settings
    account_type: str = Field(default="demo", description="Account type: demo, real")
    email: Optional[str] = Field(default=None, description="Trading account email")
    password: Optional[str] = Field(default=None, description="Trading account password")
    
    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    trading: TradingConfig = Field(default_factory=TradingConfig)
    risk_management: RiskManagementConfig = Field(default_factory=RiskManagementConfig)
    consensus: ConsensusConfig = Field(default_factory=ConsensusConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    # AI Models
    ai_models: Dict[str, AIModelConfig] = Field(default_factory=dict)
    
    # Data providers
    data_providers: List[str] = Field(default_factory=lambda: ["iqoption"])
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @classmethod
    def load_from_file(cls, config_path: str) -> 'EnhancedTradingConfig':
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            print(f"⚠️ Config file {config_path} not found, using defaults")
            return cls()
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)

    @classmethod
    def load_from_env(cls) -> 'EnhancedTradingConfig':
        """Load configuration from environment variables"""
        config = cls()
        
        # Load from environment variables with prefix
        env_mapping = {
            'TRADING_ENVIRONMENT': 'environment',
            'TRADING_DEBUG': 'debug',
            'TRADING_ACCOUNT_TYPE': 'account_type',
            'IQOPTION_EMAIL': 'email',
            'IQOPTION_PASSWORD': 'password',
            
            # Database
            'DB_TYPE': 'database.type',
            'DB_HOST': 'database.host',
            'DB_PORT': 'database.port',
            'DB_NAME': 'database.name',
            'DB_USERNAME': 'database.username',
            'DB_PASSWORD': 'database.password',
            
            # Redis
            'REDIS_HOST': 'redis.host',
            'REDIS_PORT': 'redis.port',
            'REDIS_PASSWORD': 'redis.password',
            
            # AI Models
            'OPENAI_API_KEY': 'ai_models.openai.api_key',
            'ANTHROPIC_API_KEY': 'ai_models.claude.api_key',
            'DEEPSEEK_API_KEY': 'ai_models.deepseek.api_key',
        }
        
        for env_var, config_path in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                cls._set_nested_value(config, config_path, value)
        
        return config

    @staticmethod
    def _set_nested_value(obj: Any, path: str, value: Any):
        """Set nested configuration value"""
        keys = path.split('.')
        current = obj
        
        for key in keys[:-1]:
            if not hasattr(current, key):
                setattr(current, key, type('Config', (), {})())
            current = getattr(current, key)
        
        # Convert string values to appropriate types
        if isinstance(value, str):
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                value = float(value)
        
        setattr(current, keys[-1], value)

    def setup_ai_models(self):
        """Setup default AI model configurations"""
        default_models = {
            'openai': AIModelConfig(
                enabled=True,
                model_name='gpt-4o-mini',
                weight=1.2,
                api_key=os.getenv('OPENAI_API_KEY')
            ),
            'claude': AIModelConfig(
                enabled=True,
                model_name='claude-3-5-haiku-20241022',
                weight=1.0,
                api_key=os.getenv('ANTHROPIC_API_KEY')
            ),
            'deepseek': AIModelConfig(
                enabled=True,
                model_name='deepseek-chat',
                weight=1.0,
                api_key=os.getenv('DEEPSEEK_API_KEY')
            ),
            'gemini': AIModelConfig(
                enabled=bool(os.getenv('GOOGLE_API_KEY')),
                model_name='gemini-pro',
                weight=1.1,
                api_key=os.getenv('GOOGLE_API_KEY')
            ),
            'mistral': AIModelConfig(
                enabled=bool(os.getenv('MISTRAL_API_KEY')),
                model_name='mistral-large-latest',
                weight=1.2,
                api_key=os.getenv('MISTRAL_API_KEY')
            )
        }
        
        for name, config in default_models.items():
            if name not in self.ai_models:
                self.ai_models[name] = config

    def get_secret(self, key: str) -> Optional[str]:
        """Get secret from Vault or environment"""
        if self.security.use_vault and self.security.vault_url:
            try:
                client = hvac.Client(
                    url=self.security.vault_url,
                    token=self.security.vault_token
                )
                
                if client.is_authenticated():
                    secret = client.secrets.kv.v2.read_secret_version(
                        path=self.security.vault_path
                    )
                    return secret['data']['data'].get(key)
            except Exception as e:
                print(f"⚠️ Vault error: {e}")
        
        # Fallback to environment variable
        return os.getenv(key)

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate required fields
        if not self.email:
            errors.append("Trading account email is required")
        
        if not self.password:
            errors.append("Trading account password is required")
        
        # Validate AI models
        enabled_models = [name for name, config in self.ai_models.items() if config.enabled]
        if len(enabled_models) < self.consensus.min_models:
            errors.append(f"At least {self.consensus.min_models} AI models must be enabled")
        
        # Check API keys for enabled models
        for name, config in self.ai_models.items():
            if config.enabled and not config.api_key:
                errors.append(f"API key required for enabled model: {name}")
        
        # Validate database configuration
        if self.database.type == "postgresql":
            if not all([self.database.username, self.database.password, self.database.host]):
                errors.append("PostgreSQL requires username, password, and host")
        
        return errors

    def save_to_file(self, config_path: str):
        """Save configuration to YAML file"""
        config_dict = self.dict()
        
        # Remove sensitive data
        if 'password' in config_dict:
            config_dict['password'] = '***HIDDEN***'
        
        for model_config in config_dict.get('ai_models', {}).values():
            if 'api_key' in model_config:
                model_config['api_key'] = '***HIDDEN***'
        
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        print(f"📝 Configuration saved to {config_path}")

    def display(self):
        """Display current configuration (without sensitive data)"""
        print("\n" + "=" * 80)
        print("⚙️ ENHANCED TRADING SYSTEM CONFIGURATION")
        print("=" * 80)
        
        print(f"\n🌍 Environment: {self.environment.upper()}")
        print(f"🔧 Debug Mode: {'✅' if self.debug else '❌'}")
        print(f"📧 Account: {self.account_type.upper()} ({self.email})")
        
        print(f"\n💾 Database:")
        print(f"   Type: {self.database.type}")
        if self.database.type == "postgresql":
            print(f"   Host: {self.database.host}:{self.database.port}")
            print(f"   Database: {self.database.name}")
        else:
            print(f"   Path: {self.database.sqlite_path}")
        
        print(f"\n🔄 Redis:")
        print(f"   Host: {self.redis.host}:{self.redis.port}")
        print(f"   Database: {self.redis.db}")
        
        print(f"\n🤖 AI Models:")
        for name, config in self.ai_models.items():
            status = "✅" if config.enabled else "❌"
            api_status = "🔑" if config.api_key else "❌"
            print(f"   {status} {name}: {config.model_name} (weight: {config.weight}) {api_status}")
        
        print(f"\n💰 Trading:")
        print(f"   Base Amount: ${self.trading.base_amount}")
        print(f"   Range: ${self.trading.min_amount} - ${self.trading.max_amount}")
        print(f"   Duration: {self.trading.default_duration}m")
        print(f"   Payout Ratio: {self.trading.payout_ratio}")
        
        print(f"\n🛡️ Risk Management:")
        print(f"   Max Daily Loss: ${self.risk_management.max_daily_loss}")
        print(f"   Max Consecutive Losses: {self.risk_management.max_consecutive_losses}")
        print(f"   Position Sizing: {self.risk_management.position_size_method}")
        
        print(f"\n🎯 Consensus:")
        print(f"   Threshold: {self.consensus.threshold * 100:.0f}%")
        print(f"   Min Confidence: {self.consensus.min_confidence}%")
        print(f"   Min Models: {self.consensus.min_models}")
        
        print(f"\n📊 Monitoring:")
        print(f"   Log Level: {self.monitoring.log_level}")
        print(f"   Prometheus: {'✅' if self.monitoring.enable_prometheus else '❌'}")
        print(f"   Sentry: {'✅' if self.monitoring.enable_sentry else '❌'}")
        
        print(f"\n🔒 Security:")
        print(f"   Vault: {'✅' if self.security.use_vault else '❌'}")
        print(f"   Database Encryption: {'✅' if self.security.encrypt_database else '❌'}")
        
        print("\n" + "=" * 80)

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == 'production'

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment.lower() == 'development'


# Global configuration instance
config = EnhancedTradingConfig()


def load_config(config_path: str = None) -> EnhancedTradingConfig:
    """Load configuration from file or environment"""
    global config
    
    if config_path:
        config = EnhancedTradingConfig.load_from_file(config_path)
    else:
        config = EnhancedTradingConfig.load_from_env()
    
    # Setup default AI models
    config.setup_ai_models()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   • {error}")
        if config.is_production:
            raise ValueError("Configuration validation failed in production")
    
    return config


def get_config() -> EnhancedTradingConfig:
    """Get current configuration"""
    return config