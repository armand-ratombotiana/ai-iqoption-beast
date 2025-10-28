"""
Strategy-Per-Thread Manager

This module implements a thread-per-strategy architecture where each strategy
runs in its own dedicated thread, analyzing markets independently and voting
on trade decisions through a consensus mechanism.

Features:
- Each strategy runs in isolated thread
- Independent market analysis per strategy
- Consensus-based trade execution
- Real-time strategy performance tracking
- Thread-safe vote aggregation
"""

import logging
import threading
import time
import queue
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import numpy as np

from strategies.advanced_strategies import AdvancedStrategyEngine, StrategySignal
from strategies.strategy_config import StrategyConfig


@dataclass
class StrategyVote:
    """Vote from a strategy thread"""
    strategy_name: str
    instrument: str
    direction: str  # 'CALL', 'PUT', 'NEUTRAL'
    confidence: float
    reasons: List[str]
    indicators: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)
    thread_id: int = 0


@dataclass
class StrategyPerformance:
    """Performance tracking for individual strategy"""
    strategy_name: str
    total_votes: int = 0
    call_votes: int = 0
    put_votes: int = 0
    neutral_votes: int = 0
    avg_confidence: float = 0.0
    trades_executed: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    total_profit: float = 0.0
    last_vote_time: Optional[datetime] = None
    is_healthy: bool = True
    error_count: int = 0


class StrategyThread(threading.Thread):
    """Individual strategy thread"""
    
    def __init__(self, strategy_name: str, strategy_engine: AdvancedStrategyEngine,
                 vote_queue: queue.Queue, candle_queue: queue.Queue,
                 config: StrategyConfig, logger: logging.Logger):
        super().__init__(name=f"Strategy-{strategy_name}", daemon=True)
        self.strategy_name = strategy_name
        self.strategy_engine = strategy_engine
        self.vote_queue = vote_queue
        self.candle_queue = candle_queue
        self.config = config
        self.logger = logging.getLogger(f"StrategyThread-{strategy_name}")
        self.running = False
        self.performance = StrategyPerformance(strategy_name=strategy_name)
        
    def run(self):
        """Main strategy thread loop"""
        self.running = True
        self.logger.info(f"🚀 Strategy thread started: {self.strategy_name}")
        
        while self.running:
            try:
                # Wait for candle data (with timeout)
                try:
                    candle_data = self.candle_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                instrument = candle_data['instrument']
                candles = candle_data['candles']
                
                # Analyze with this strategy
                signal = self._analyze_with_strategy(candles)
                
                # Create vote
                vote = StrategyVote(
                    strategy_name=self.strategy_name,
                    instrument=instrument,
                    direction=signal.direction,
                    confidence=signal.confidence,
                    reasons=signal.reasons,
                    indicators=signal.indicators,
                    thread_id=threading.get_ident()
                )
                
                # Submit vote
                self.vote_queue.put(vote)
                
                # Update performance
                self.performance.total_votes += 1
                if signal.direction == 'CALL':
                    self.performance.call_votes += 1
                elif signal.direction == 'PUT':
                    self.performance.put_votes += 1
                else:
                    self.performance.neutral_votes += 1
                
                self.performance.last_vote_time = datetime.now()
                
                # Calculate average confidence
                total_conf = (self.performance.avg_confidence * 
                             (self.performance.total_votes - 1) + signal.confidence)
                self.performance.avg_confidence = total_conf / self.performance.total_votes
                
                self.logger.debug(
                    f"📊 {self.strategy_name} voted {signal.direction} "
                    f"@ {signal.confidence:.0%} for {instrument}"
                )
                
            except Exception as e:
                self.logger.error(f"❌ Error in {self.strategy_name}: {e}")
                self.performance.error_count += 1
                if self.performance.error_count > 10:
                    self.performance.is_healthy = False
                    self.logger.error(f"⚠️ {self.strategy_name} marked unhealthy")
                time.sleep(5)
    
    def _analyze_with_strategy(self, candles: List[Dict]) -> StrategySignal:
        """Analyze candles with specific strategy"""
        # Map strategy name to specific analysis method
        strategy_methods = {
            'enhanced_candle_count': self.strategy_engine.enhanced_candle_count,
            'rsi_divergence': self.strategy_engine.rsi_divergence_strategy,
            'macd_momentum': self.strategy_engine.macd_momentum_strategy,
            'bollinger_rsi_combo': self.strategy_engine.bollinger_rsi_combo,
            'stochastic': self.strategy_engine.stochastic_strategy,
            'trend_alignment': self.strategy_engine.trend_alignment_strategy,
            'support_resistance': self.strategy_engine.support_resistance_strategy
        }
        
        method = strategy_methods.get(self.strategy_name)
        if not method:
            return StrategySignal('NEUTRAL', 0.0, self.strategy_name, 
                                ['Unknown strategy'], {})
        
        # Prepare data
        closes = np.array([c['close'] for c in candles], dtype=float)
        opens = np.array([c['open'] for c in candles], dtype=float)
        highs = np.array([c.get('max', c['close']) for c in candles], dtype=float)
        lows = np.array([c.get('min', c['close']) for c in candles], dtype=float)
        
        # Call appropriate method
        try:
            if self.strategy_name == 'enhanced_candle_count':
                result = method(candles, closes, opens)
            elif self.strategy_name in ['rsi_divergence']:
                result = method(closes, highs, lows)
            elif self.strategy_name in ['macd_momentum', 'bollinger_rsi_combo', 
                                        'trend_alignment']:
                result = method(closes)
            elif self.strategy_name == 'stochastic':
                result = method(highs, lows, closes)
            elif self.strategy_name == 'support_resistance':
                result = method(closes, highs, lows)
            else:
                result = None
            
            return result if result else StrategySignal(
                'NEUTRAL', 0.0, self.strategy_name, ['No signal'], {}
            )
            
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            return StrategySignal('NEUTRAL', 0.0, self.strategy_name, 
                                [f'Error: {str(e)}'], {})
    
    def stop(self):
        """Stop strategy thread"""
        self.running = False
        self.logger.info(f"🛑 Stopping {self.strategy_name}")
    
    def update_trade_result(self, won: bool, profit: float):
        """Update performance after trade execution"""
        self.performance.trades_executed += 1
        if won:
            self.performance.wins += 1
        else:
            self.performance.losses += 1
        
        self.performance.total_profit += profit
        
        if self.performance.trades_executed > 0:
            self.performance.win_rate = (
                self.performance.wins / self.performance.trades_executed
            )


class StrategyThreadManager:
    """Manages multiple strategy threads and aggregates votes"""
    
    def __init__(self, config: StrategyConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.strategy_threads: Dict[str, StrategyThread] = {}
        self.vote_queue = queue.Queue()
        self.candle_queues: Dict[str, queue.Queue] = {}
        self.running = False
        self.lock = threading.Lock()
        
        # Performance tracking
        self.strategy_performances: Dict[str, StrategyPerformance] = {}
        
    def initialize_strategies(self):
        """Initialize all strategy threads"""
        self.logger.info("="*80)
        self.logger.info("🧵 INITIALIZING STRATEGY THREADS")
        self.logger.info("="*80)
        
        enabled_strategies = self.config.enabled_strategies or [
            'enhanced_candle_count',
            'rsi_divergence',
            'macd_momentum',
            'bollinger_rsi_combo',
            'stochastic',
            'trend_alignment',
            'support_resistance'
        ]
        
        for strategy_name in enabled_strategies:
            # Create dedicated candle queue for this strategy
            candle_queue = queue.Queue(maxsize=10)
            self.candle_queues[strategy_name] = candle_queue
            
            # Create strategy engine instance
            strategy_engine = AdvancedStrategyEngine()
            
            # Create and start thread
            thread = StrategyThread(
                strategy_name=strategy_name,
                strategy_engine=strategy_engine,
                vote_queue=self.vote_queue,
                candle_queue=candle_queue,
                config=self.config,
                logger=self.logger
            )
            
            self.strategy_threads[strategy_name] = thread
            self.strategy_performances[strategy_name] = thread.performance
            
            thread.start()
            self.logger.info(f"✅ {strategy_name} thread started")
        
        self.running = True
        self.logger.info(f"✅ {len(self.strategy_threads)} strategy threads running")
        self.logger.info("="*80)
    
    def broadcast_candles(self, instrument: str, candles: List[Dict]):
        """Broadcast candle data to all strategy threads"""
        candle_data = {
            'instrument': instrument,
            'candles': candles,
            'timestamp': datetime.now()
        }
        
        for strategy_name, candle_queue in self.candle_queues.items():
            try:
                # Non-blocking put with timeout
                candle_queue.put(candle_data, block=False)
            except queue.Full:
                self.logger.warning(
                    f"⚠️ Candle queue full for {strategy_name}, skipping"
                )
    
    def collect_votes(self, timeout: float = 2.0) -> List[StrategyVote]:
        """Collect votes from all strategy threads"""
        votes = []
        start_time = time.time()
        expected_votes = len(self.strategy_threads)
        
        while len(votes) < expected_votes:
            remaining_time = timeout - (time.time() - start_time)
            if remaining_time <= 0:
                break
            
            try:
                vote = self.vote_queue.get(timeout=min(remaining_time, 0.1))
                votes.append(vote)
            except queue.Empty:
                continue
        
        if len(votes) < expected_votes:
            self.logger.warning(
                f"⚠️ Only received {len(votes)}/{expected_votes} votes"
            )
        
        return votes
    
    def aggregate_votes(self, votes: List[StrategyVote]) -> Tuple[str, float, List[str]]:
        """
        Aggregate votes from multiple strategies
        
        Returns:
            (direction, confidence, reasons)
        """
        if not votes:
            return 'NEUTRAL', 0.0, ['No votes received']
        
        # Count votes by direction
        call_votes = [v for v in votes if v.direction == 'CALL']
        put_votes = [v for v in votes if v.direction == 'PUT']
        neutral_votes = [v for v in votes if v.direction == 'NEUTRAL']
        
        # Calculate weighted scores
        call_score = sum(v.confidence for v in call_votes)
        put_score = sum(v.confidence for v in put_votes)
        
        # Collect reasons
        all_reasons = []
        
        # Check confluence requirements
        min_confluence = self.config.min_confluence
        min_confidence = self.config.min_confidence
        
        if len(call_votes) >= min_confluence and call_score > put_score:
            avg_confidence = call_score / len(call_votes)
            
            if avg_confidence >= min_confidence:
                # Boost confidence with confluence
                confluence_boost = min(0.05 * (len(call_votes) - 1), 0.15)
                final_confidence = min(0.95, avg_confidence + confluence_boost)
                
                all_reasons = [
                    f"[{v.strategy_name}] {r}" 
                    for v in call_votes 
                    for r in v.reasons
                ]
                
                return 'CALL', final_confidence, all_reasons
        
        elif len(put_votes) >= min_confluence and put_score > call_score:
            avg_confidence = put_score / len(put_votes)
            
            if avg_confidence >= min_confidence:
                # Boost confidence with confluence
                confluence_boost = min(0.05 * (len(put_votes) - 1), 0.15)
                final_confidence = min(0.95, avg_confidence + confluence_boost)
                
                all_reasons = [
                    f"[{v.strategy_name}] {r}" 
                    for v in put_votes 
                    for r in v.reasons
                ]
                
                return 'PUT', final_confidence, all_reasons
        
        # No consensus
        return 'NEUTRAL', 0.0, [
            f"No consensus: {len(call_votes)} CALL, {len(put_votes)} PUT, "
            f"{len(neutral_votes)} NEUTRAL"
        ]
    
    def analyze_instrument(self, instrument: str, candles: List[Dict]) -> Tuple[str, float, List[str]]:
        """
        Analyze instrument with all strategy threads
        
        Returns:
            (direction, confidence, reasons)
        """
        # Broadcast candles to all strategies
        self.broadcast_candles(instrument, candles)
        
        # Collect votes
        votes = self.collect_votes(timeout=2.0)
        
        # Aggregate votes
        direction, confidence, reasons = self.aggregate_votes(votes)
        
        self.logger.info(
            f"📊 {instrument}: {len(votes)} votes → {direction} @ {confidence:.0%}"
        )
        
        return direction, confidence, reasons
    
    def update_trade_results(self, strategy_names: List[str], won: bool, profit: float):
        """Update performance for strategies that voted for executed trade"""
        with self.lock:
            for strategy_name in strategy_names:
                if strategy_name in self.strategy_threads:
                    self.strategy_threads[strategy_name].update_trade_result(won, profit)
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary for all strategies"""
        with self.lock:
            summary = {
                'total_strategies': len(self.strategy_threads),
                'healthy_strategies': sum(
                    1 for p in self.strategy_performances.values() if p.is_healthy
                ),
                'strategies': []
            }
            
            for name, perf in self.strategy_performances.items():
                summary['strategies'].append({
                    'name': name,
                    'total_votes': perf.total_votes,
                    'call_votes': perf.call_votes,
                    'put_votes': perf.put_votes,
                    'neutral_votes': perf.neutral_votes,
                    'avg_confidence': perf.avg_confidence,
                    'trades_executed': perf.trades_executed,
                    'wins': perf.wins,
                    'losses': perf.losses,
                    'win_rate': perf.win_rate,
                    'total_profit': perf.total_profit,
                    'is_healthy': perf.is_healthy,
                    'error_count': perf.error_count
                })
            
            return summary
    
    def print_status(self):
        """Print current status of all strategy threads"""
        summary = self.get_performance_summary()
        
        self.logger.info("="*80)
        self.logger.info("🧵 STRATEGY THREADS STATUS")
        self.logger.info(f"Total: {summary['total_strategies']} | "
                        f"Healthy: {summary['healthy_strategies']}")
        self.logger.info("-"*80)
        
        for strat in summary['strategies']:
            status = "✅" if strat['is_healthy'] else "❌"
            self.logger.info(
                f"{status} {strat['name']:25s} | "
                f"Votes: {strat['total_votes']:4d} | "
                f"Trades: {strat['trades_executed']:3d} | "
                f"Win Rate: {strat['win_rate']*100:5.1f}% | "
                f"P&L: ${strat['total_profit']:+7.2f}"
            )
        
        self.logger.info("="*80)
    
    def stop_all(self):
        """Stop all strategy threads"""
        self.running = False
        self.logger.info("🛑 Stopping all strategy threads...")
        
        for thread in self.strategy_threads.values():
            thread.stop()
        
        # Wait for threads to finish
        for thread in self.strategy_threads.values():
            thread.join(timeout=5.0)
        
        self.logger.info("✅ All strategy threads stopped")
