"""
Multi-Account Configuration Manager
Handles 5 separate IQOption accounts with strategy assignments
"""

import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import threading


@dataclass
class AccountConfig:
    """Configuration for a single trading account"""
    account_id: str
    email: str
    password: str
    strategy_profile: str  # 'conservative', 'moderate', 'aggressive', 'scalping', 'trend_following'
    enabled: bool = True
    max_daily_loss: float = 10.0
    max_trade_amount: float = 2.0
    trading_mode: str = 'demo'  # 'demo' or 'live'
    
    # Health tracking
    last_connection: Optional[datetime] = None
    connection_failures: int = 0
    is_healthy: bool = True
    total_trades: int = 0
    daily_pnl: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        if self.last_connection:
            data['last_connection'] = self.last_connection.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AccountConfig':
        """Create from dictionary"""
        if 'last_connection' in data and data['last_connection']:
            data['last_connection'] = datetime.fromisoformat(data['last_connection'])
        return cls(**data)


class MultiAccountManager:
    """
    Manages multiple trading accounts with strategy assignments
    Thread-safe operations for concurrent account management
    """
    
    def __init__(self, config_file: str = 'config/accounts.json'):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_file = Path(config_file)
        self.accounts: Dict[str, AccountConfig] = {}
        self.lock = threading.Lock()
        
        # Strategy profiles mapping
        self.strategy_profiles = {
            'conservative': {
                'min_confidence': 0.85,
                'min_confluence': 3,
                'max_trade_amount': 1.5,
                'max_daily_loss': 5.0,
                'enabled_strategies': ['bollinger_rsi_combo', 'rsi_divergence', 'trend_alignment']
            },
            'moderate': {
                'min_confidence': 0.78,
                'min_confluence': 2,
                'max_trade_amount': 2.0,
                'max_daily_loss': 8.0,
                'enabled_strategies': ['enhanced_candle_count', 'bollinger_rsi_combo', 'macd_momentum', 'trend_alignment']
            },
            'aggressive': {
                'min_confidence': 0.70,
                'min_confluence': 2,
                'max_trade_amount': 3.0,
                'max_daily_loss': 15.0,
                'enabled_strategies': ['enhanced_candle_count', 'macd_momentum', 'stochastic', 'support_resistance']
            },
            'scalping': {
                'min_confidence': 0.75,
                'min_confluence': 2,
                'max_trade_amount': 2.5,
                'max_daily_loss': 10.0,
                'enabled_strategies': ['enhanced_candle_count', 'stochastic', 'support_resistance']
            },
            'trend_following': {
                'min_confidence': 0.80,
                'min_confluence': 2,
                'max_trade_amount': 2.5,
                'max_daily_loss': 10.0,
                'enabled_strategies': ['trend_alignment', 'macd_momentum', 'enhanced_candle_count']
            }
        }
        
        self._load_or_create_config()
    
    def _load_or_create_config(self):
        """Load existing config or create default"""
        if self.config_file.exists():
            self._load_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration with 5 accounts"""
        self.logger.info("Creating default multi-account configuration...")
        
        # Default accounts with different strategies
        default_accounts = [
            AccountConfig(
                account_id='account_1',
                email='tombonirinakaej@gmail.com',
                password='tombokael04',
                strategy_profile='conservative',
                max_daily_loss=5.0,
                max_trade_amount=2
            ),
            AccountConfig(
                account_id='account_2',
                email='tombokael4@gmail.com',
                password='tombokael04',
                strategy_profile='moderate',
                max_daily_loss=8.0,
                max_trade_amount=2.0
            ),
            AccountConfig(
                account_id='account_3',
                email='ruslantombofitiavana@gmail.com',
                password='tombokael04',
                strategy_profile='aggressive',
                max_daily_loss=15.0,
                max_trade_amount=3.0
            ),
            AccountConfig(
                account_id='account_4',
                email='tombofifalianakimi@gmail.com',
                password='tombokael04',
                strategy_profile='scalping',
                max_daily_loss=10.0,
                max_trade_amount=2.5
            ),
            AccountConfig(
                account_id='account_5',
                email='dinokamisy@gmail.com',
                password='tombokael04',
                strategy_profile='trend_following',
                max_daily_loss=10.0,
                max_trade_amount=2.5
            )
        ]
        
        for account in default_accounts:
            self.accounts[account.account_id] = account
        
        self._save_config()
        self.logger.info(f"✅ Created configuration for {len(self.accounts)} accounts")
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            self.accounts = {
                acc_id: AccountConfig.from_dict(acc_data)
                for acc_id, acc_data in data.get('accounts', {}).items()
            }
            
            self.logger.info(f"✅ Loaded configuration for {len(self.accounts)} accounts")
        except Exception as e:
            self.logger.error(f"❌ Failed to load config: {e}")
            self._create_default_config()
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'accounts': {
                    acc_id: acc.to_dict()
                    for acc_id, acc in self.accounts.items()
                },
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.debug("Configuration saved")
        except Exception as e:
            self.logger.error(f"❌ Failed to save config: {e}")
    
    def get_account(self, account_id: str) -> Optional[AccountConfig]:
        """Get account configuration"""
        with self.lock:
            return self.accounts.get(account_id)
    
    def get_all_accounts(self) -> List[AccountConfig]:
        """Get all account configurations"""
        with self.lock:
            return list(self.accounts.values())
    
    def get_enabled_accounts(self) -> List[AccountConfig]:
        """Get only enabled accounts"""
        with self.lock:
            return [acc for acc in self.accounts.values() if acc.enabled]
    
    def get_healthy_accounts(self) -> List[AccountConfig]:
        """Get only healthy and enabled accounts"""
        with self.lock:
            return [
                acc for acc in self.accounts.values()
                if acc.enabled and acc.is_healthy
            ]
    
    def update_account_health(self, account_id: str, is_healthy: bool, 
                            connection_success: bool = True):
        """Update account health status"""
        with self.lock:
            account = self.accounts.get(account_id)
            if not account:
                return
            
            account.is_healthy = is_healthy
            account.last_connection = datetime.now()
            
            if connection_success:
                account.connection_failures = 0
            else:
                account.connection_failures += 1
                
                # Disable account after 3 consecutive failures
                if account.connection_failures >= 3:
                    account.enabled = False
                    self.logger.warning(
                        f"⚠️ Account {account_id} disabled after 3 connection failures"
                    )
            
            self._save_config()
    
    def update_account_stats(self, account_id: str, daily_pnl: float, 
                           total_trades: int):
        """Update account trading statistics"""
        with self.lock:
            account = self.accounts.get(account_id)
            if not account:
                return
            
            account.daily_pnl = daily_pnl
            account.total_trades = total_trades
            
            # Check if daily loss limit reached
            if abs(daily_pnl) >= account.max_daily_loss and daily_pnl < 0:
                account.enabled = False
                self.logger.warning(
                    f"⚠️ Account {account_id} disabled: daily loss limit reached"
                )
            
            self._save_config()
    
    def get_strategy_config(self, account_id: str) -> Dict:
        """Get strategy configuration for account"""
        account = self.get_account(account_id)
        if not account:
            return {}
        
        return self.strategy_profiles.get(account.strategy_profile, {})
    
    def enable_account(self, account_id: str):
        """Enable an account"""
        with self.lock:
            account = self.accounts.get(account_id)
            if account:
                account.enabled = True
                account.connection_failures = 0
                self._save_config()
                self.logger.info(f"✅ Account {account_id} enabled")
    
    def disable_account(self, account_id: str):
        """Disable an account"""
        with self.lock:
            account = self.accounts.get(account_id)
            if account:
                account.enabled = False
                self._save_config()
                self.logger.info(f"⚠️ Account {account_id} disabled")
    
    def reset_daily_stats(self):
        """Reset daily statistics for all accounts"""
        with self.lock:
            for account in self.accounts.values():
                account.daily_pnl = 0.0
                # Re-enable accounts that were disabled due to daily loss
                if not account.enabled and account.connection_failures < 3:
                    account.enabled = True
            
            self._save_config()
            self.logger.info("✅ Daily stats reset for all accounts")
    
    def get_summary(self) -> Dict:
        """Get summary of all accounts"""
        with self.lock:
            total_accounts = len(self.accounts)
            enabled_accounts = sum(1 for acc in self.accounts.values() if acc.enabled)
            healthy_accounts = sum(
                1 for acc in self.accounts.values() 
                if acc.enabled and acc.is_healthy
            )
            total_pnl = sum(acc.daily_pnl for acc in self.accounts.values())
            total_trades = sum(acc.total_trades for acc in self.accounts.values())
            
            return {
                'total_accounts': total_accounts,
                'enabled_accounts': enabled_accounts,
                'healthy_accounts': healthy_accounts,
                'total_daily_pnl': round(total_pnl, 2),
                'total_trades': total_trades,
                'accounts': [
                    {
                        'account_id': acc.account_id,
                        'email': acc.email,
                        'strategy': acc.strategy_profile,
                        'enabled': acc.enabled,
                        'healthy': acc.is_healthy,
                        'daily_pnl': round(acc.daily_pnl, 2),
                        'total_trades': acc.total_trades,
                        'connection_failures': acc.connection_failures
                    }
                    for acc in self.accounts.values()
                ]
            }


# Global instance
_manager_instance = None
_manager_lock = threading.Lock()


def get_account_manager() -> MultiAccountManager:
    """Get or create global account manager instance"""
    global _manager_instance
    
    if _manager_instance is None:
        with _manager_lock:
            if _manager_instance is None:
                _manager_instance = MultiAccountManager()
    
    return _manager_instance
