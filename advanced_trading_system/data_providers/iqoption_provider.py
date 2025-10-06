"""
IQOption Data Provider with Parallel Pair Management
Handles fetching available pairs, payouts, and market data concurrently
"""
import asyncio
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import concurrent.futures
from iqoptionapi.stable_api import IQ_Option

from .base_provider import BaseDataProvider


class IQOptionProvider(BaseDataProvider):
    """
    IQOption provider with parallel capabilities
    """
    
    def __init__(self, email: str, password: str, account_type: str = 'PRACTICE'):
        super().__init__("iqoption")
        self.email = email
        self.password = password
        self.account_type = account_type
        self.api = None
        self.available_pairs = {}
        self.pair_payouts = {}
        self.last_pairs_update = None
        self.pairs_cache_duration = 300  # 5 minutes
        
    async def connect(self) -> bool:
        """Connect to IQOption API"""
        try:
            self.api = IQ_Option(self.email, self.password)
            check, reason = self.api.connect()
            
            if not check:
                raise Exception(f"Connection failed: {reason}")
            
            # Set account type
            self.api.change_balance(self.account_type)
            self.is_connected = True
            
            # Fetch available pairs on connection
            await self.update_available_pairs()
            
            print(f"✅ Connected to IQOption ({self.account_type})")
            return True
            
        except Exception as e:
            print(f"❌ IQOption connection failed: {e}")
            self.is_connected = False
            return False
    
    async def update_available_pairs(self) -> Dict[str, Dict]:
        """
        Fetch all available pairs with their payouts and status
        
        Returns:
        {
            'EURUSD-OTC': {
                'payout': 0.85,
                'is_open': True,
                'expiration_times': [1, 2, 3, 5],
                'category': 'forex'
            }
        }
        """
        if not self.is_connected:
            return {}
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Get all available pairs
                all_pairs = await loop.run_in_executor(
                    executor, self._get_all_pairs_sync
                )
                
                # Get payouts for all pairs
                payouts = await loop.run_in_executor(
                    executor, self._get_all_payouts_sync, all_pairs
                )
            
            # Combine data
            self.available_pairs = {}
            self.pair_payouts = payouts
            
            for pair_info in all_pairs:
                pair_name = pair_info['name']
                payout = payouts.get(pair_name, 0)
                
                self.available_pairs[pair_name] = {
                    'payout': payout,
                    'is_open': pair_info.get('is_open', False),
                    'expiration_times': pair_info.get('expiration_times', [1, 2, 3, 5]),
                    'category': pair_info.get('category', 'unknown'),
                    'min_amount': pair_info.get('min_amount', 1.0),
                    'max_amount': pair_info.get('max_amount', 1000.0)
                }
            
            self.last_pairs_update = datetime.now()
            
            print(f"✅ Updated {len(self.available_pairs)} available pairs")
            return self.available_pairs
            
        except Exception as e:
            print(f"❌ Error updating available pairs: {e}")
            return {}
    
    async def get_filtered_pairs(self, 
                                min_payout: float = 0.75,
                                max_pairs: int = 10,
                                categories: List[str] = None,
                                exclude_pairs: List[str] = None) -> List[Dict]:
        """
        Get filtered pairs based on criteria
        
        Args:
            min_payout: Minimum payout percentage (0.75 = 75%)
            max_pairs: Maximum number of pairs to return
            categories: List of categories to include ['forex', 'crypto', 'stocks']
            exclude_pairs: List of pairs to exclude
        
        Returns:
            List of filtered pair dictionaries
        """
        # Update pairs if cache is stale
        if (not self.last_pairs_update or 
            (datetime.now() - self.last_pairs_update).seconds > self.pairs_cache_duration):
            await self.update_available_pairs()
        
        if not self.available_pairs:
            return []
        
        # Apply filters
        filtered_pairs = []
        categories = categories or ['forex', 'crypto', 'stocks']
        exclude_pairs = exclude_pairs or []
        
        for pair_name, pair_info in self.available_pairs.items():
            # Skip if excluded
            if pair_name in exclude_pairs:
                continue
            
            # Check if open
            if not pair_info.get('is_open', False):
                continue
            
            # Check payout
            if pair_info.get('payout', 0) < min_payout:
                continue
            
            # Check category
            if pair_info.get('category', 'unknown') not in categories:
                continue
            
            filtered_pairs.append({
                'pair': pair_name,
                'payout': pair_info['payout'],
                'category': pair_info['category'],
                'expiration_times': pair_info['expiration_times'],
                'min_amount': pair_info.get('min_amount', 1.0),
                'max_amount': pair_info.get('max_amount', 1000.0)
            })
        
        # Sort by payout (highest first)
        filtered_pairs.sort(key=lambda x: x['payout'], reverse=True)
        
        # Limit results
        return filtered_pairs[:max_pairs]