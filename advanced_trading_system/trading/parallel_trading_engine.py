"""
Parallel Trading Engine
Handles multiple pairs simultaneously with proper risk management
"""
import asyncio
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import concurrent.futures
from dataclasses import dataclass

from config.settings import TradingConfig
from database.trade_storage import TradeDatabase
from analysis.market_context import MarketContextAnalyzer
from ai_models.enhanced_consensus import EnhancedConsensusEngine
from ai_models.kelly_position_sizer import KellyPositionSizer
from data_providers.iqoption_provider import IQOptionProvider


@dataclass
class ParallelTradeConfig:
    """Configuration for parallel trading"""
    max_concurrent_pairs: int = 5
    min_payout: float = 0.75
    max_pairs_to_analyze: int = 20
    balance_allocation_per_trade: float = 0.02  # 2% of balance per trade
    correlation_threshold: float = 0.7  # Avoid highly correlated pairs
    min_time_between_trades: int = 30  # seconds
    risk_budget_percentage: float = 0.10  # 10% of balance total risk


class ParallelTradingEngine:
    """
    Advanced parallel trading engine with:
    - Concurrent pair analysis
    - Risk-aware position sizing
    - Correlation filtering
    - Dynamic pair selection
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.parallel_config = ParallelTradeConfig()
        
        # Initialize components
        self.db = TradeDatabase(config.DB_PATH)
        self.market_analyzer = MarketContextAnalyzer()
        self.consensus_engine = EnhancedConsensusEngine(config.CONSENSUS_THRESHOLD)
        self.position_sizer = KellyPositionSizer(config.__dict__)
        self.provider = IQOptionProvider(config.EMAIL, config.PASSWORD, config.ACCOUNT_TYPE)
        
        # Parallel trading state
        self.active_trades = {}
        self.pair_last_trade = {}
        self.total_risk_allocated = 0.0
        self.semaphore = asyncio.Semaphore(self.parallel_config.max_concurrent_pairs)
        
        print("✅ Parallel Trading Engine initialized")
    
    async def initialize(self):
        """Initialize all components"""
        # Connect to provider
        await self.provider.connect()
        
        # Initialize AI models
        await self._initialize_ai_models()
        
        print("✅ All components initialized")
    
    async def _initialize_ai_models(self):
        """Initialize AI models for consensus"""
        # Add your AI models here
        # This would be similar to the existing implementation
        pass
    
    async def run_parallel_trading_session(self, duration_minutes: int = 60) -> Dict:
        """
        Run a parallel trading session
        
        Args:
            duration_minutes: How long to run the session
            
        Returns:
            Session summary with results
        """
        print(f"\n🚀 Starting Parallel Trading Session ({duration_minutes} minutes)")
        print("=" * 80)
        
        session_start = datetime.now()
        session_end = session_start.timestamp() + (duration_minutes * 60)
        
        session_stats = {
            'trades_executed': 0,
            'trades_won': 0,
            'trades_lost': 0,
            'total_profit': 0.0,
            'pairs_traded': set(),
            'start_time': session_start.isoformat(),
            'errors': []
        }
        
        try:
            while time.time() < session_end:
                # Get current balance
                balance = self.provider.get_balance()
                if not balance:
                    print("❌ Cannot get balance, stopping session")
                    break
                
                print(f"\n💰 Current Balance: ${balance:.2f}")
                
                # Step 1: Get filtered pairs
                filtered_pairs = await self.provider.get_filtered_pairs(
                    min_payout=self.parallel_config.min_payout,
                    max_pairs=self.parallel_config.max_pairs_to_analyze
                )
                
                if not filtered_pairs:
                    print("⚠️ No suitable pairs found, waiting...")
                    await asyncio.sleep(30)
                    continue
                
                print(f"📊 Found {len(filtered_pairs)} suitable pairs")
                
                # Step 2: Analyze pairs in parallel
                analysis_results = await self._analyze_pairs_parallel(filtered_pairs)
                
                # Step 3: Select best opportunities
                trade_opportunities = self._select_trade_opportunities(
                    analysis_results, balance
                )
                
                if not trade_opportunities:
                    print("⚠️ No trading opportunities found, waiting...")
                    await asyncio.sleep(60)
                    continue
                
                print(f"🎯 Selected {len(trade_opportunities)} trading opportunities")
                
                # Step 4: Execute trades in parallel
                trade_results = await self._execute_trades_parallel(trade_opportunities)
                
                # Step 5: Update session stats
                for result in trade_results:
                    if result.get('success'):
                        session_stats['trades_executed'] += 1
                        session_stats['pairs_traded'].add(result['pair'])
                
                # Step 6: Monitor active trades
                await self._monitor_active_trades(session_stats)
                
                # Wait before next cycle
                await asyncio.sleep(30)
                
        except Exception as e:
            session_stats['errors'].append(str(e))
            print(f"❌ Session error: {e}")
        
        # Final session summary
        session_stats['pairs_traded'] = list(session_stats['pairs_traded'])
        session_stats['duration_minutes'] = (datetime.now() - session_start).seconds / 60
        session_stats['win_rate'] = (
            session_stats['trades_won'] / session_stats['trades_executed'] * 100
            if session_stats['trades_executed'] > 0 else 0
        )
        
        self._print_session_summary(session_stats)
        return session_stats
    
    async def _analyze_pairs_parallel(self, pairs: List[Dict]) -> List[Dict]:
        """Analyze multiple pairs concurrently"""
        print(f"\n🔍 Analyzing {len(pairs)} pairs in parallel...")
        
        # Create analysis tasks
        analysis_tasks = []
        for pair_info in pairs:
            task = self._analyze_single_pair(pair_info)
            analysis_tasks.append(task)
        
        # Execute all analyses concurrently
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Filter successful results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Analysis failed for {pairs[i]['pair']}: {result}")
            elif result:
                valid_results.append(result)
        
        print(f"✅ Successfully analyzed {len(valid_results)} pairs")
        return valid_results
    
    async def _analyze_single_pair(self, pair_info: Dict) -> Optional[Dict]:
        """Analyze a single pair"""
        pair_name = pair_info['pair']
        
        try:
            # Get market data
            candles = await self.provider.get_candles(pair_name, '1m', 100)
            if not candles or len(candles) < 20:
                return None
            
            # Calculate technical indicators
            market_data = self._calculate_market_indicators(candles, pair_name)
            
            # Get AI consensus
            consensus = self.consensus_engine.get_consensus_signal(market_data, candles)
            
            # Check if signal is valid
            if not consensus.get('consensus_reached', False):
                return None
            
            if consensus.get('confidence_calibrated', 0) < self.config.MIN_CONFIDENCE:
                return None
            
            return {
                'pair': pair_name,
                'payout': pair_info['payout'],
                'signal': consensus['signal'],
                'confidence': consensus['confidence_calibrated'],
                'consensus': consensus,
                'market_data': market_data,
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {pair_name}: {e}")
            return None
    
    def _select_trade_opportunities(self, analyses: List[Dict], balance: float) -> List[Dict]:
        """Select best trading opportunities with risk management"""
        if not analyses:
            return []
        
        # Sort by confidence * payout (expected value)
        analyses.sort(
            key=lambda x: x['confidence'] * x['payout'], 
            reverse=True
        )
        
        selected_opportunities = []
        total_risk_budget = balance * self.parallel_config.risk_budget_percentage
        allocated_risk = 0.0
        
        for analysis in analyses:
            pair = analysis['pair']
            
            # Check time since last trade on this pair
            if pair in self.pair_last_trade:
                time_since_last = (datetime.now() - self.pair_last_trade[pair]).seconds
                if time_since_last < self.parallel_config.min_time_between_trades:
                    continue
            
            # Calculate position size
            max_trade_amount = balance * self.parallel_config.balance_allocation_per_trade
            
            # Risk-based position sizing
            confidence = analysis['confidence']
            risk_amount = max_trade_amount * (confidence / 100)
            
            # Check if we have enough risk budget
            if allocated_risk + risk_amount > total_risk_budget:
                continue
            
            # Check correlation with existing positions
            if self._is_correlated_with_active_trades(pair):
                continue
            
            selected_opportunities.append({
                **analysis,
                'position_size': risk_amount,
                'max_risk': risk_amount
            })
            
            allocated_risk += risk_amount
            
            # Limit concurrent trades
            if len(selected_opportunities) >= self.parallel_config.max_concurrent_pairs:
                break
        
        return selected_opportunities
    
    async def _execute_trades_parallel(self, opportunities: List[Dict]) -> List[Dict]:
        """Execute multiple trades concurrently"""
        if not opportunities:
            return []
        
        print(f"\n🚀 Executing {len(opportunities)} trades in parallel...")
        
        # Create trade execution tasks
        trade_tasks = []
        for opportunity in opportunities:
            async with self.semaphore:  # Limit concurrent executions
                task = self._execute_single_trade(opportunity)
                trade_tasks.append(task)
        
        # Execute all trades concurrently
        results = await asyncio.gather(*trade_tasks, return_exceptions=True)
        
        # Process results
        successful_trades = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Trade execution failed: {result}")
            elif result and result.get('success'):
                successful_trades.append(result)
                # Track active trade
                self.active_trades[result['order_id']] = {
                    **result,
                    'start_time': datetime.now(),
                    'opportunity': opportunities[i]
                }
                # Update last trade time for pair
                self.pair_last_trade[result['pair']] = datetime.now()
        
        print(f"✅ Successfully executed {len(successful_trades)} trades")
        return results
    
    async def _execute_single_trade(self, opportunity: Dict) -> Optional[Dict]:
        """Execute a single trade"""
        try:
            pair = opportunity['pair']
            signal = opportunity['signal']
            amount = opportunity['position_size']
            
            print(f"📈 Executing {signal} on {pair} - ${amount:.2f}")
            
            # Execute trade
            result = await self.provider.execute_trade(
                pair=pair,
                direction=signal,
                amount=amount,
                duration=1  # 1 minute
            )
            
            if result and result.get('success'):
                # Store in database
                trade_data = {
                    'trade_id': result['order_id'],
                    'timestamp': datetime.now().isoformat(),
                    'pair': pair,
                    'direction': signal,
                    'amount': amount,
                    'duration': 1,
                    'result': 'PENDING',
                    'ai_signal_confidence': int(opportunity['confidence']),
                    'payout_rate': opportunity['payout'],
                    'strategy_version': 'parallel_v1.0'
                }
                
                self.db.insert_trade(trade_data)
                
                print(f"✅ Trade executed: {pair} {signal} ${amount:.2f}")
                return result
            else:
                print(f"❌ Trade failed: {pair}")
                return result
                
        except Exception as e:
            print(f"❌ Error executing trade for {opportunity['pair']}: {e}")
            return {'success': False, 'error': str(e), 'pair': opportunity['pair']}
    
    async def _monitor_active_trades(self, session_stats: Dict):
        """Monitor active trades and update results"""
        if not self.active_trades:
            return
        
        completed_trades = []
        
        for order_id, trade_info in self.active_trades.items():
            # Check if trade duration has passed
            elapsed_time = (datetime.now() - trade_info['start_time']).seconds
            
            if elapsed_time >= 70:  # 1 minute + 10 seconds buffer
                # Check trade result
                result = await self.provider.check_trade_result(order_id)
                
                if result:
                    # Update database
                    self.db.update_trade(order_id, {
                        'result': result['result'],
                        'profit': result['profit']
                    })
                    
                    # Update session stats
                    if result['result'] == 'WIN':
                        session_stats['trades_won'] += 1
                        session_stats['total_profit'] += result['profit']
                        print(f"✅ WIN: {trade_info['pair']} +${result['profit']:.2f}")
                    else:
                        session_stats['trades_lost'] += 1
                        session_stats['total_profit'] += result['profit']  # Will be negative
                        print(f"❌ LOSS: {trade_info['pair']} ${result['profit']:.2f}")
                    
                    completed_trades.append(order_id)
        
        # Remove completed trades
        for order_id in completed_trades:
            del self.active_trades[order_id]
    
    def _is_correlated_with_active_trades(self, pair: str) -> bool:
        """Check if pair is correlated with active trades"""
        # Simple correlation check based on currency pairs
        # In a more advanced system, you'd use actual correlation data
        
        if not self.active_trades:
            return False
        
        active_pairs = [trade['pair'] for trade in self.active_trades.values()]
        
        # Extract base currencies
        pair_base = pair.split('-')[0][:3] if '-' in pair else pair[:3]
        
        for active_pair in active_pairs:
            active_base = active_pair.split('-')[0][:3] if '-' in active_pair else active_pair[:3]
            
            # Simple correlation: same base currency
            if pair_base == active_base:
                return True
        
        return False
    
    def _calculate_market_indicators(self, candles: List[Dict], pair: str) -> Dict:
        """Calculate market indicators for a pair"""
        # This would use your existing TechnicalIndicators class
        # Simplified version here
        current_price = candles[-1]['close']
        
        return {
            'pair': pair,
            'current_price': current_price,
            'trend': 'uptrend',  # Simplified
            'volatility': 'medium',
            'rsi_14': 50,  # Would calculate actual RSI
            'hour': datetime.now().hour
        }
    
    def _print_session_summary(self, stats: Dict):
        """Print session summary"""
        print("\n" + "=" * 80)
        print("📊 PARALLEL TRADING SESSION SUMMARY")
        print("=" * 80)
        
        print(f"\n⏱️  Duration: {stats['duration_minutes']:.1f} minutes")
        print(f"📈 Trades Executed: {stats['trades_executed']}")
        print(f"✅ Wins: {stats['trades_won']}")
        print(f"❌ Losses: {stats['trades_lost']}")
        print(f"🎯 Win Rate: {stats['win_rate']:.1f}%")
        print(f"💰 Total P/L: ${stats['total_profit']:+.2f}")
        
        print(f"\n🔄 Pairs Traded: {len(stats['pairs_traded'])}")
        for pair in stats['pairs_traded']:
            print(f"   • {pair}")
        
        if stats['errors']:
            print(f"\n⚠️  Errors: {len(stats['errors'])}")
            for error in stats['errors'][:5]:  # Show first 5 errors
                print(f"   • {error}")
        
        print("\n" + "=" * 80)
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.provider.disconnect()
        print("✅ Parallel Trading Engine cleaned up")
