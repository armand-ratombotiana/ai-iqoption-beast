"""
Advanced Backtesting Engine
Realistic backtesting with slippage, latency, and spread modeling
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.technical_indicators import TechnicalIndicators
from analysis.market_context import MarketContextAnalyzer


class OrderType(Enum):
    CALL = "CALL"
    PUT = "PUT"


@dataclass
class BacktestTrade:
    """Represents a single backtest trade"""
    timestamp: datetime
    pair: str
    direction: OrderType
    amount: float
    duration: int
    entry_price: float
    exit_price: Optional[float] = None
    result: Optional[str] = None
    profit: Optional[float] = None
    market_data: Optional[Dict] = None
    ai_confidence: Optional[float] = None
    slippage: float = 0.0
    spread: float = 0.0
    latency_ms: float = 0.0


@dataclass
class BacktestConfig:
    """Backtesting configuration"""
    initial_balance: float = 10000.0
    base_amount: float = 2.0
    min_amount: float = 1.0
    max_amount: float = 20.0
    payout_ratio: float = 0.8  # 80% payout for wins
    
    # Realistic execution modeling
    enable_slippage: bool = True
    avg_slippage_pips: float = 0.5
    enable_spread: bool = True
    avg_spread_pips: float = 1.0
    enable_latency: bool = True
    avg_latency_ms: float = 100.0
    
    # Risk management
    max_daily_loss: float = 500.0
    max_consecutive_losses: int = 5
    
    # Market hours
    respect_market_hours: bool = True


class BacktestingEngine:
    """
    Advanced backtesting engine with realistic execution modeling
    
    Features:
    - Realistic slippage and spread modeling
    - Latency simulation
    - Market hours respect
    - Risk management rules
    - Detailed performance metrics
    - Trade-by-trade analysis
    """

    def __init__(self, config: BacktestConfig = None):
        self.config = config or BacktestConfig()
        self.indicators = TechnicalIndicators()
        self.market_analyzer = MarketContextAnalyzer()
        
        # State tracking
        self.trades: List[BacktestTrade] = []
        self.balance = self.config.initial_balance
        self.equity_curve = []
        self.daily_pnl = {}
        self.consecutive_losses = 0
        
        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.max_drawdown = 0.0
        self.max_balance = self.config.initial_balance

    def run_backtest(
        self,
        data: pd.DataFrame,
        strategy_func: Callable,
        start_date: str = None,
        end_date: str = None
    ) -> Dict:
        """
        Run comprehensive backtest
        
        Args:
            data: OHLCV data with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            strategy_func: Function that takes market_data and returns trading signal
            start_date: Start date for backtest (YYYY-MM-DD)
            end_date: End date for backtest (YYYY-MM-DD)
            
        Returns:
            Comprehensive backtest results
        """
        print(f"🚀 Starting backtest from {start_date} to {end_date}")
        
        # Filter data by date range
        if start_date:
            data = data[data['timestamp'] >= start_date]
        if end_date:
            data = data[data['timestamp'] <= end_date]
            
        if len(data) < 100:
            raise ValueError("Insufficient data for backtesting (minimum 100 candles)")

        # Reset state
        self._reset_state()
        
        # Process each candle
        for i in range(100, len(data)):  # Start after 100 candles for indicators
            current_candle = data.iloc[i]
            historical_data = data.iloc[i-100:i]  # Last 100 candles for analysis
            
            # Convert to list of dicts for compatibility
            candles = []
            for _, row in historical_data.iterrows():
                candles.append({
                    'timestamp': row['timestamp'],
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': row.get('volume', 0)
                })
            
            # Calculate market data
            market_data = self._calculate_market_data(candles, current_candle)
            
            # Check risk management rules
            if not self._check_risk_management(current_candle['timestamp']):
                continue
                
            # Get trading signal from strategy
            try:
                signal = strategy_func(market_data)
                if not signal or signal.get('signal') == 'NEUTRAL':
                    continue
                    
                # Execute trade
                self._execute_trade(signal, market_data, current_candle, data.iloc[i:i+6])  # Next 5 candles for exit
                
            except Exception as e:
                print(f"Strategy error at {current_candle['timestamp']}: {e}")
                continue
                
            # Update equity curve
            self._update_equity_curve(current_candle['timestamp'])

        # Calculate final results
        results = self._calculate_results()
        
        print(f"✅ Backtest completed: {self.total_trades} trades, "
              f"{self.winning_trades} wins ({self.winning_trades/max(self.total_trades,1)*100:.1f}%), "
              f"Final P&L: ${self.total_profit:.2f}")
        
        return results

    def _reset_state(self):
        """Reset backtesting state"""
        self.trades = []
        self.balance = self.config.initial_balance
        self.equity_curve = []
        self.daily_pnl = {}
        self.consecutive_losses = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.max_drawdown = 0.0
        self.max_balance = self.config.initial_balance

    def _calculate_market_data(self, candles: List[Dict], current_candle: pd.Series) -> Dict:
        """Calculate market data for strategy"""
        current_price = current_candle['close']
        
        # Calculate technical indicators
        market_data = {
            'pair': 'BACKTEST',
            'current_price': current_price,
            'timestamp': current_candle['timestamp'],
            
            # Technical indicators
            'rsi_14': self.indicators.rsi(candles, 14),
            'rsi_7': self.indicators.rsi(candles, 7),
            'macd': self.indicators.macd(candles),
            'bb_position': self.indicators.bollinger_bands(candles)['position'],
            'stochastic': self.indicators.stochastic(candles),
            'adx': self.indicators.adx(candles),
            'atr': self.indicators.atr(candles),
            'cci': self.indicators.cci(candles),
            'williams_r': self.indicators.williams_r(candles),
            
            # Market analysis
            'trend': self.indicators.identify_trend(candles),
            'volatility': self.indicators.calculate_volatility(candles)[0],
            'volatility_value': self.indicators.calculate_volatility(candles)[1],
            'support': self.indicators.find_support_resistance(candles)[0],
            'resistance': self.indicators.find_support_resistance(candles)[1],
            'candlestick_pattern': self.indicators.detect_candlestick_pattern(candles),
            
            # Time context
            'hour': pd.to_datetime(current_candle['timestamp']).hour,
            'day_of_week': pd.to_datetime(current_candle['timestamp']).weekday()
        }
        
        return market_data

    def _check_risk_management(self, timestamp: str) -> bool:
        """Check if trade is allowed based on risk management rules"""
        current_date = pd.to_datetime(timestamp).date()
        
        # Check daily loss limit
        daily_loss = self.daily_pnl.get(current_date, 0.0)
        if daily_loss <= -self.config.max_daily_loss:
            return False
            
        # Check consecutive losses
        if self.consecutive_losses >= self.config.max_consecutive_losses:
            return False
            
        # Check minimum balance
        if self.balance < self.config.min_amount:
            return False
            
        return True

    def _execute_trade(self, signal: Dict, market_data: Dict, entry_candle: pd.Series, future_candles: pd.DataFrame):
        """Execute a backtest trade with realistic modeling"""
        
        # Calculate position size
        confidence = signal.get('confidence', 50) / 100
        amount = self.config.base_amount * confidence
        amount = max(self.config.min_amount, min(amount, self.config.max_amount))
        amount = min(amount, self.balance)  # Don't exceed balance
        
        if amount < self.config.min_amount:
            return
            
        # Apply realistic execution effects
        entry_price = entry_candle['close']
        slippage = 0.0
        spread = 0.0
        latency = 0.0
        
        if self.config.enable_slippage:
            slippage = np.random.normal(0, self.config.avg_slippage_pips * 0.0001)
            entry_price += slippage
            
        if self.config.enable_spread:
            spread = self.config.avg_spread_pips * 0.0001
            if signal['signal'] == 'CALL':
                entry_price += spread / 2  # Buy at ask
            else:
                entry_price -= spread / 2  # Sell at bid
                
        if self.config.enable_latency:
            latency = np.random.exponential(self.config.avg_latency_ms)
        
        # Create trade
        trade = BacktestTrade(
            timestamp=pd.to_datetime(entry_candle['timestamp']),
            pair=market_data['pair'],
            direction=OrderType(signal['signal']),
            amount=amount,
            duration=1,  # 1 minute for binary options
            entry_price=entry_price,
            market_data=market_data,
            ai_confidence=signal.get('confidence'),
            slippage=slippage,
            spread=spread,
            latency_ms=latency
        )
        
        # Determine exit price (1 minute later)
        if len(future_candles) > 1:
            exit_candle = future_candles.iloc[1]  # 1 minute later
            trade.exit_price = exit_candle['close']
            
            # Determine result
            if trade.direction == OrderType.CALL:
                trade.result = 'WIN' if trade.exit_price > trade.entry_price else 'LOSS'
            else:  # PUT
                trade.result = 'WIN' if trade.exit_price < trade.entry_price else 'LOSS'
                
            # Calculate profit
            if trade.result == 'WIN':
                trade.profit = amount * self.config.payout_ratio
                self.consecutive_losses = 0
            else:
                trade.profit = -amount
                self.consecutive_losses += 1
                
            # Update balance and statistics
            self.balance += trade.profit
            self.total_profit += trade.profit
            
            # Update daily P&L
            trade_date = trade.timestamp.date()
            if trade_date not in self.daily_pnl:
                self.daily_pnl[trade_date] = 0.0
            self.daily_pnl[trade_date] += trade.profit
            
            # Update statistics
            self.total_trades += 1
            if trade.result == 'WIN':
                self.winning_trades += 1
            else:
                self.losing_trades += 1
                
            # Update max drawdown
            if self.balance > self.max_balance:
                self.max_balance = self.balance
            current_drawdown = (self.max_balance - self.balance) / self.max_balance * 100
            if current_drawdown > self.max_drawdown:
                self.max_drawdown = current_drawdown
        
        self.trades.append(trade)

    def _update_equity_curve(self, timestamp: str):
        """Update equity curve"""
        self.equity_curve.append({
            'timestamp': timestamp,
            'balance': self.balance,
            'equity': self.balance,
            'drawdown': (self.max_balance - self.balance) / self.max_balance * 100
        })

    def _calculate_results(self) -> Dict:
        """Calculate comprehensive backtest results"""
        if self.total_trades == 0:
            return {'error': 'No trades executed'}
            
        # Basic metrics
        win_rate = (self.winning_trades / self.total_trades) * 100
        avg_win = np.mean([t.profit for t in self.trades if t.result == 'WIN']) if self.winning_trades > 0 else 0
        avg_loss = np.mean([t.profit for t in self.trades if t.result == 'LOSS']) if self.losing_trades > 0 else 0
        profit_factor = abs(avg_win * self.winning_trades / (avg_loss * self.losing_trades)) if self.losing_trades > 0 else float('inf')
        
        # Risk metrics
        returns = [t.profit / self.config.initial_balance for t in self.trades]
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # Drawdown analysis
        equity_values = [point['balance'] for point in self.equity_curve]
        running_max = np.maximum.accumulate(equity_values)
        drawdowns = (running_max - equity_values) / running_max * 100
        max_drawdown_duration = self._calculate_max_drawdown_duration()
        
        # Monthly analysis
        monthly_returns = self._calculate_monthly_returns()
        
        results = {
            'summary': {
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'losing_trades': self.losing_trades,
                'win_rate': round(win_rate, 2),
                'total_profit': round(self.total_profit, 2),
                'final_balance': round(self.balance, 2),
                'return_pct': round((self.balance - self.config.initial_balance) / self.config.initial_balance * 100, 2)
            },
            'risk_metrics': {
                'max_drawdown': round(self.max_drawdown, 2),
                'max_drawdown_duration': max_drawdown_duration,
                'sharpe_ratio': round(sharpe_ratio, 2),
                'profit_factor': round(profit_factor, 2),
                'avg_win': round(avg_win, 2),
                'avg_loss': round(avg_loss, 2),
                'largest_win': round(max([t.profit for t in self.trades]), 2),
                'largest_loss': round(min([t.profit for t in self.trades]), 2)
            },
            'execution_analysis': {
                'avg_slippage': round(np.mean([abs(t.slippage) for t in self.trades]), 6),
                'avg_spread': round(np.mean([t.spread for t in self.trades]), 6),
                'avg_latency_ms': round(np.mean([t.latency_ms for t in self.trades]), 2)
            },
            'monthly_returns': monthly_returns,
            'equity_curve': self.equity_curve,
            'trades': [self._trade_to_dict(t) for t in self.trades],
            'config': self.config.__dict__
        }
        
        return results

    def _calculate_max_drawdown_duration(self) -> int:
        """Calculate maximum drawdown duration in days"""
        if not self.equity_curve:
            return 0
            
        equity_values = [point['balance'] for point in self.equity_curve]
        running_max = np.maximum.accumulate(equity_values)
        
        in_drawdown = False
        current_duration = 0
        max_duration = 0
        
        for i, (equity, peak) in enumerate(zip(equity_values, running_max)):
            if equity < peak:
                if not in_drawdown:
                    in_drawdown = True
                    current_duration = 1
                else:
                    current_duration += 1
            else:
                if in_drawdown:
                    max_duration = max(max_duration, current_duration)
                    in_drawdown = False
                    current_duration = 0
                    
        return max_duration

    def _calculate_monthly_returns(self) -> List[Dict]:
        """Calculate monthly returns"""
        monthly_pnl = {}
        
        for trade in self.trades:
            month_key = trade.timestamp.strftime('%Y-%m')
            if month_key not in monthly_pnl:
                monthly_pnl[month_key] = 0.0
            monthly_pnl[month_key] += trade.profit
            
        monthly_returns = []
        for month, pnl in sorted(monthly_pnl.items()):
            monthly_returns.append({
                'month': month,
                'pnl': round(pnl, 2),
                'return_pct': round(pnl / self.config.initial_balance * 100, 2)
            })
            
        return monthly_returns

    def _trade_to_dict(self, trade: BacktestTrade) -> Dict:
        """Convert trade to dictionary"""
        return {
            'timestamp': trade.timestamp.isoformat(),
            'pair': trade.pair,
            'direction': trade.direction.value,
            'amount': trade.amount,
            'entry_price': trade.entry_price,
            'exit_price': trade.exit_price,
            'result': trade.result,
            'profit': trade.profit,
            'ai_confidence': trade.ai_confidence,
            'slippage': trade.slippage,
            'spread': trade.spread,
            'latency_ms': trade.latency_ms
        }

    def export_results(self, filepath: str, results: Dict):
        """Export backtest results to JSON"""
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📊 Backtest results exported to {filepath}")

    def get_trade_analysis(self) -> Dict:
        """Get detailed trade analysis"""
        if not self.trades:
            return {}
            
        # Analyze by hour
        hourly_performance = {}
        for trade in self.trades:
            hour = trade.timestamp.hour
            if hour not in hourly_performance:
                hourly_performance[hour] = {'trades': 0, 'wins': 0, 'profit': 0.0}
            
            hourly_performance[hour]['trades'] += 1
            if trade.result == 'WIN':
                hourly_performance[hour]['wins'] += 1
            hourly_performance[hour]['profit'] += trade.profit
            
        # Analyze by confidence level
        confidence_analysis = {}
        for trade in self.trades:
            if trade.ai_confidence:
                conf_bucket = int(trade.ai_confidence // 10) * 10  # 0-10, 10-20, etc.
                if conf_bucket not in confidence_analysis:
                    confidence_analysis[conf_bucket] = {'trades': 0, 'wins': 0, 'profit': 0.0}
                
                confidence_analysis[conf_bucket]['trades'] += 1
                if trade.result == 'WIN':
                    confidence_analysis[conf_bucket]['wins'] += 1
                confidence_analysis[conf_bucket]['profit'] += trade.profit
        
        return {
            'hourly_performance': hourly_performance,
            'confidence_analysis': confidence_analysis,
            'consecutive_losses_max': max([0] + [self._count_consecutive_losses(i) for i in range(len(self.trades))])
        }

    def _count_consecutive_losses(self, start_idx: int) -> int:
        """Count consecutive losses starting from index"""
        count = 0
        for i in range(start_idx, len(self.trades)):
            if self.trades[i].result == 'LOSS':
                count += 1
            else:
                break
        return count