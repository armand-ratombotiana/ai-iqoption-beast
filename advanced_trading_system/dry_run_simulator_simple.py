#!/usr/bin/env python
"""
SIMPLIFIED DRY-RUN SIMULATOR - Comprehensive Testing Without External Dependencies
Simulates realistic market data and tests signal generation, risk management, and safety mechanisms

This version uses pure Python (no NumPy) for compatibility
"""

import sys
import os
import time
import random
import math
from datetime import datetime, timedelta
from collections import namedtuple

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration
from paper_trading_config import get_config, TESTING_PAIRS


class SignalType(object):
    """Trading signal types"""
    CALL = "CALL"
    PUT = "PUT"
    NEUTRAL = "NEUTRAL"


# Named tuples for data structures
SimulatedCandle = namedtuple('SimulatedCandle', [
    'timestamp', 'open', 'high', 'low', 'close', 'volume'
])

SimulatedTrade = namedtuple('SimulatedTrade', [
    'trade_id', 'timestamp', 'pair', 'signal', 'entry_price', 'exit_price',
    'amount', 'duration_minutes', 'confidence', 'rsi', 'macd_histogram',
    'stoch_k', 'adx', 'bb_position', 'profit_loss', 'result'
])


class SimpleIndicators(object):
    """Simple technical indicator calculations (pure Python, no dependencies)"""

    @staticmethod
    def rsi(closes, period=14):
        """Calculate RSI"""
        if len(closes) < period + 1:
            return 50.0

        gains = []
        losses = []

        for i in range(1, len(closes)):
            delta = closes[i] - closes[i-1]
            if delta > 0:
                gains.append(delta)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(delta))

        avg_gain = sum(gains[:period]) / float(period)
        avg_loss = sum(losses[:period]) / float(period)

        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    @staticmethod
    def macd(closes, fast=12, slow=26, signal_period=9):
        """Calculate MACD"""
        if len(closes) < slow:
            return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}

        # Simple EMA calculation
        def ema(data, period):
            multiplier = 2.0 / (period + 1)
            ema_val = data[0]
            for price in data[1:]:
                ema_val = (price * multiplier) + (ema_val * (1 - multiplier))
            return ema_val

        ema_fast = ema(closes, fast)
        ema_slow = ema(closes, slow)
        macd_line = ema_fast - ema_slow

        # Signal line
        signal_line = ema([macd_line], signal_period)

        histogram = macd_line - signal_line

        return {
            'macd': round(macd_line, 6),
            'signal': round(signal_line, 6),
            'histogram': round(histogram, 6)
        }

    @staticmethod
    def adx(high, low, close, period=14):
        """Simplified ADX calculation"""
        if len(close) < period + 1:
            return 20.0

        # Calculate true range
        tr_values = []
        for i in range(1, len(close)):
            h = high[i]
            l = low[i]
            c = close[i - 1]

            tr1 = h - l
            tr2 = abs(h - c)
            tr3 = abs(l - c)
            tr = max(tr1, tr2, tr3)
            tr_values.append(tr)

        atr = sum(tr_values[-period:]) / period

        # Directional movement
        plus_dm = []
        minus_dm = []

        for i in range(1, len(high)):
            up_move = high[i] - high[i-1]
            down_move = low[i-1] - low[i]

            if up_move > down_move and up_move > 0:
                plus_dm.append(up_move)
                minus_dm.append(0)
            elif down_move > up_move and down_move > 0:
                plus_dm.append(0)
                minus_dm.append(down_move)
            else:
                plus_dm.append(0)
                minus_dm.append(0)

        plus_di = (sum(plus_dm[-period:]) / atr) * 100 if atr > 0 else 0
        minus_di = (sum(minus_dm[-period:]) / atr) * 100 if atr > 0 else 0

        dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
        adx = min(100, max(0, dx))

        return round(adx, 1)

    @staticmethod
    def bollinger_bands(closes, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if len(closes) < period:
            current = closes[-1] if closes else 1.10000
            return {
                'upper': current,
                'middle': current,
                'lower': current,
                'position': 0.5
            }

        recent = closes[-period:]
        middle = sum(recent) / float(period)

        # Calculate std dev
        variance = sum((x - middle) ** 2 for x in recent) / period
        std = math.sqrt(variance)

        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)

        current_price = closes[-1]
        if upper != lower:
            position = (current_price - lower) / (upper - lower)
        else:
            position = 0.5

        return {
            'upper': round(upper, 6),
            'middle': round(middle, 6),
            'lower': round(lower, 6),
            'position': round(position, 2)
        }


class SimulationMetrics(object):
    """Simulation performance metrics"""

    def __init__(self):
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.breakeven_trades = 0
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.win_rate = 0.0
        self.avg_profit_per_trade = 0.0
        self.max_consecutive_wins = 0
        self.max_consecutive_losses = 0
        self.max_drawdown = 0.0
        self.signal_generation_time_ms = 0.0
        self.indicator_calc_time_ms = 0.0
        self.trades_by_signal_type = {}
        self.trades_by_pair = {}

    def calculate(self, trades):
        """Calculate all metrics from trades"""
        if not trades:
            return

        self.total_trades = len(trades)
        self.winning_trades = sum(1 for t in trades if t.profit_loss > 0)
        self.losing_trades = sum(1 for t in trades if t.profit_loss < 0)
        self.breakeven_trades = sum(1 for t in trades if t.profit_loss == 0)

        self.total_profit = sum(t.profit_loss for t in trades if t.profit_loss > 0)
        self.total_loss = sum(abs(t.profit_loss) for t in trades if t.profit_loss < 0)

        if self.total_trades > 0:
            self.win_rate = (float(self.winning_trades) / self.total_trades) * 100

        if self.winning_trades > 0:
            self.avg_profit_per_trade = self.total_profit / float(self.winning_trades)

        # Calculate consecutive wins/losses
        current_wins = 0
        current_losses = 0
        for trade in trades:
            if trade.profit_loss > 0:
                current_wins += 1
                current_losses = 0
                self.max_consecutive_wins = max(self.max_consecutive_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                self.max_consecutive_losses = max(self.max_consecutive_losses, current_losses)

        # Calculate drawdown
        cumulative = 0
        peak = 0
        for trade in trades:
            cumulative += trade.profit_loss
            peak = max(peak, cumulative)
            drawdown = peak - cumulative
            self.max_drawdown = max(self.max_drawdown, drawdown)

        # Count by signal type and pair
        for trade in trades:
            signal_key = trade.signal
            self.trades_by_signal_type[signal_key] = self.trades_by_signal_type.get(signal_key, 0) + 1
            self.trades_by_pair[trade.pair] = self.trades_by_pair.get(trade.pair, 0) + 1

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'breakeven_trades': self.breakeven_trades,
            'total_profit': self.total_profit,
            'total_loss': self.total_loss,
            'win_rate': self.win_rate,
            'avg_profit_per_trade': self.avg_profit_per_trade,
            'max_consecutive_wins': self.max_consecutive_wins,
            'max_consecutive_losses': self.max_consecutive_losses,
            'max_drawdown': self.max_drawdown,
            'signal_generation_time_ms': self.signal_generation_time_ms,
            'indicator_calc_time_ms': self.indicator_calc_time_ms,
            'trades_by_signal_type': self.trades_by_signal_type,
            'trades_by_pair': self.trades_by_pair,
        }


class MarketSimulator(object):
    """Generates realistic market data for simulation"""

    def __init__(self, seed=42):
        """Initialize market simulator"""
        random.seed(seed)

    def generate_realistic_prices(self, initial_price, num_candles, volatility=0.01, trend=0.0):
        """Generate realistic price movements"""
        candles = []
        current_price = initial_price

        for i in range(num_candles):
            # Simplified price movement
            drift = trend / 252.0
            random_return = random.gauss(drift, volatility)

            open_price = current_price
            close_price = current_price * (1 + random_return)

            movement_range = abs(close_price - open_price) * 1.5
            high_price = max(open_price, close_price) + abs(random.gauss(0, movement_range * 0.3))
            low_price = min(open_price, close_price) - abs(random.gauss(0, movement_range * 0.3))

            candle = SimulatedCandle(
                timestamp=datetime.now() - timedelta(minutes=num_candles - i),
                open=round(open_price, 5),
                high=round(high_price, 5),
                low=round(low_price, 5),
                close=round(close_price, 5),
                volume=random.randint(1000, 10000)
            )
            candles.append(candle)
            current_price = close_price

        return candles

    def generate_high_volatility_prices(self, initial_price, num_candles):
        """Generate high volatility market conditions"""
        return self.generate_realistic_prices(initial_price, num_candles, volatility=0.05, trend=0.1)

    def generate_flat_market_prices(self, initial_price, num_candles):
        """Generate flat/ranging market"""
        return self.generate_realistic_prices(initial_price, num_candles, volatility=0.001, trend=0.0)


class SignalGenerator(object):
    """Generates trading signals based on technical indicators"""

    def __init__(self, config):
        """Initialize signal generator"""
        self.config = config
        self.indicator_config = config['indicators']
        self.indicators = SimpleIndicators()

    def calculate_indicators(self, candles):
        """Calculate all technical indicators"""
        if len(candles) < 26:
            return None

        start_time = time.time()

        try:
            closes = [c.close for c in candles]
            highs = [c.high for c in candles]
            lows = [c.low for c in candles]

            indicators = {
                'rsi': self.indicators.rsi(closes),
                'adx': self.indicators.adx(highs, lows, closes),
            }

            macd_result = self.indicators.macd(closes)
            indicators['macd_histogram'] = macd_result.get('histogram', 0)

            bb_result = self.indicators.bollinger_bands(closes)
            indicators['bb_position'] = bb_result.get('position', 0.5)

            # Stochastic (simplified)
            indicators['stoch_k'] = 50.0

            indicators['calculation_time_ms'] = (time.time() - start_time) * 1000
            return indicators

        except Exception as e:
            print("Error calculating indicators: %s" % str(e))
            return None

    def generate_signal(self, indicators):
        """Generate trading signal"""
        if not indicators:
            # Generate random signal for simulation
            signal = random.choice([SignalType.CALL, SignalType.PUT])
            confidence = random.uniform(55, 85)
            return signal, confidence

        rsi = indicators.get('rsi', 50)
        macd_hist = indicators.get('macd_histogram', 0)
        adx = indicators.get('adx', 20)
        bb_pos = indicators.get('bb_position', 0.5)

        signal_votes = {'CALL': 0, 'PUT': 0}
        confidence = 50.0

        # RSI signals
        if rsi < 35:
            signal_votes['CALL'] += 1
            confidence += 10
        elif rsi > 65:
            signal_votes['PUT'] += 1
            confidence += 10

        # MACD signals
        if macd_hist > 0:
            signal_votes['CALL'] += 1
            confidence += 12
        elif macd_hist < 0:
            signal_votes['PUT'] += 1
            confidence += 12

        # Bollinger Bands signals
        if bb_pos < 0.3:
            signal_votes['CALL'] += 1
            confidence += 8
        elif bb_pos > 0.7:
            signal_votes['PUT'] += 1
            confidence += 8

        # ADX trend strength
        if adx < 20:
            confidence -= 10
        elif adx > 40:
            confidence += 5

        # If no votes, generate random signal
        if signal_votes['CALL'] == 0 and signal_votes['PUT'] == 0:
            signal = random.choice([SignalType.CALL, SignalType.PUT])
            confidence = random.uniform(55, 75)
        # Determine signal
        elif signal_votes['CALL'] > signal_votes['PUT']:
            signal = SignalType.CALL
        elif signal_votes['PUT'] > signal_votes['CALL']:
            signal = SignalType.PUT
        else:
            signal = SignalType.NEUTRAL

        confidence = max(0, min(100, confidence))

        return signal, confidence


class RiskManager(object):
    """Manages trading risks and safety mechanisms"""

    def __init__(self, config):
        """Initialize risk manager"""
        self.config = config
        self.daily_profit = 0.0
        self.daily_loss = 0.0
        self.consecutive_losses = 0
        self.consecutive_wins = 0

    def should_trade(self):
        """Check if trading should continue"""
        safety = self.config['safety']
        trading = self.config['trading']

        if self.daily_loss >= safety['EMERGENCY_STOP_LOSS']:
            return False, "Emergency stop activated: Lost $%.2f" % self.daily_loss

        if self.daily_loss >= trading['MAX_DAILY_LOSS']:
            return False, "Daily loss limit reached: $%.2f" % self.daily_loss

        if self.daily_profit >= trading['MAX_DAILY_PROFIT']:
            return False, "Daily profit target reached: $%.2f" % self.daily_profit

        if self.consecutive_losses >= trading['MAX_CONSECUTIVE_LOSSES']:
            return False, "Consecutive loss limit: %d losses" % self.consecutive_losses

        return True, None

    def validate_trade(self, signal, confidence):
        """Validate if trade meets requirements"""
        if signal == SignalType.NEUTRAL:
            return False, "Neutral signal, no trade"

        min_conf = self.config['trading']['MIN_CONFIDENCE']
        if confidence < min_conf:
            return False, "Confidence %.0f%% below minimum %.0f%%" % (confidence, min_conf)

        return True, None

    def record_trade_result(self, profit_loss):
        """Record trade result"""
        if profit_loss > 0:
            self.daily_profit += profit_loss
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        elif profit_loss < 0:
            self.daily_loss += abs(profit_loss)
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        else:
            self.consecutive_wins = 0
            self.consecutive_losses = 0


class DryRunSimulator(object):
    """Main simulator engine"""

    def __init__(self, config=None):
        """Initialize simulator"""
        self.config = config or get_config()
        self.market_sim = MarketSimulator()
        self.signal_gen = SignalGenerator(self.config)
        self.risk_mgr = RiskManager(self.config)

        self.trades = []
        self.metrics = SimulationMetrics()
        self.trade_id_counter = 0
        self.total_signal_gen_time = 0.0
        self.total_indicator_time = 0.0

    def simulate_trade_outcome(self, signal, entry_price, candles_after, payout_ratio=0.80):
        """Simulate trade outcome"""
        if not candles_after:
            return 0.0, "BREAKEVEN"

        if signal == SignalType.CALL:
            exit_price = max(c.high for c in candles_after)
        else:
            exit_price = min(c.low for c in candles_after)

        if signal == SignalType.CALL:
            won = exit_price > entry_price
        else:
            won = exit_price < entry_price

        amount = self.config['trading']['TRADE_AMOUNT']

        if won:
            profit = amount * payout_ratio
            return profit, "WIN"
        else:
            loss = -amount
            return loss, "LOSS"

    def run_simulation(self, num_trades=50, market_condition="normal"):
        """Run simulation"""
        print("\n" + "="*80)
        print("DRY-RUN SIMULATION - %s MARKET" % market_condition.upper())
        print("="*80)
        print("Target Trades: %d" % num_trades)
        print("Trade Amount: $%.2f" % self.config['trading']['TRADE_AMOUNT'])
        print("")

        # Generate market data
        if market_condition == "high_volatility":
            candles = self.market_sim.generate_high_volatility_prices(1.10000, num_trades * 5 + 100)
        elif market_condition == "flat":
            candles = self.market_sim.generate_flat_market_prices(1.10000, num_trades * 5 + 100)
        else:
            candles = self.market_sim.generate_realistic_prices(1.10000, num_trades * 5 + 100)

        trades_executed = 0
        candle_index = 30

        while trades_executed < num_trades and candle_index < len(candles) - 2:
            # Check risk management
            can_trade, reason = self.risk_mgr.should_trade()
            if not can_trade:
                print("WARNING: Trading stopped: %s" % reason)
                break

            # Get recent candles
            recent_candles = candles[max(0, candle_index-100):candle_index]

            # Calculate indicators
            indicators = self.signal_gen.calculate_indicators(recent_candles)
            if indicators:
                self.total_indicator_time += indicators.get('calculation_time_ms', 0)

            # Generate signal
            signal_start = time.time()
            signal, confidence = self.signal_gen.generate_signal(indicators)
            signal_time = (time.time() - signal_start) * 1000
            self.total_signal_gen_time += signal_time

            # Validate trade
            can_trade, reason = self.risk_mgr.validate_trade(signal, confidence)

            if can_trade:
                # Execute trade
                entry_price = candles[candle_index].close

                duration = self.config['trading']['TRADE_DURATION']
                candles_during = candles[candle_index:min(candle_index + duration + 1, len(candles))]

                profit_loss, result = self.simulate_trade_outcome(signal, entry_price, candles_during)

                self.trade_id_counter += 1
                pair = TESTING_PAIRS[trades_executed % len(TESTING_PAIRS)]
                trade = SimulatedTrade(
                    trade_id=self.trade_id_counter,
                    timestamp=candles[candle_index].timestamp,
                    pair=pair,
                    signal=signal,
                    entry_price=entry_price,
                    exit_price=candles_during[-1].close if candles_during else entry_price,
                    amount=self.config['trading']['TRADE_AMOUNT'],
                    duration_minutes=duration,
                    confidence=confidence,
                    rsi=indicators.get('rsi', 0) if indicators else 50,
                    macd_histogram=indicators.get('macd_histogram', 0) if indicators else 0,
                    stoch_k=indicators.get('stoch_k', 0) if indicators else 50,
                    adx=indicators.get('adx', 0) if indicators else 20,
                    bb_position=indicators.get('bb_position', 0) if indicators else 0.5,
                    profit_loss=profit_loss,
                    result=result
                )

                self.trades.append(trade)
                self.risk_mgr.record_trade_result(profit_loss)

                status = "OK" if profit_loss > 0 else "XX"
                print("[%s] Trade #%d: %s %s | Conf: %.0f%% | P&L: %+.2f | ADX: %.1f | RSI: %.0f" % (
                    status, trade.trade_id, trade.pair, signal, confidence, profit_loss,
                    indicators.get('adx', 0) if indicators else 0,
                    indicators.get('rsi', 0) if indicators else 50
                ))

                trades_executed += 1

            candle_index += 1

        # Calculate metrics
        self.metrics.calculate(self.trades)
        if len(self.trades) > 0:
            self.metrics.signal_generation_time_ms = self.total_signal_gen_time / len(self.trades)
            self.metrics.indicator_calc_time_ms = self.total_indicator_time / len(self.trades)

        return self.metrics

    def print_results(self):
        """Print results"""
        print("\n" + "="*80)
        print("SIMULATION RESULTS")
        print("="*80)

        m = self.metrics
        print("Total Trades Executed:    %d" % m.total_trades)
        print("Winning Trades:           %d (%.1f%%)" % (m.winning_trades, m.win_rate))
        print("Losing Trades:            %d" % m.losing_trades)
        print("Breakeven Trades:         %d" % m.breakeven_trades)
        print("")
        print("Total Profit:             $%.2f" % m.total_profit)
        print("Total Loss:               $%.2f" % m.total_loss)
        print("Net P&L:                  $%+.2f" % (m.total_profit - m.total_loss))
        print("Avg Profit Per Win:       $%.2f" % m.avg_profit_per_trade)
        print("")
        print("Max Consecutive Wins:     %d" % m.max_consecutive_wins)
        print("Max Consecutive Losses:   %d" % m.max_consecutive_losses)
        print("Max Drawdown:             $%.2f" % m.max_drawdown)
        print("")
        print("Avg Signal Gen Time:      %.2fms" % m.signal_generation_time_ms)
        print("Avg Indicator Calc Time:  %.2fms" % m.indicator_calc_time_ms)
        print("")

        if m.trades_by_signal_type:
            print("Trades by Signal Type:")
            for signal_type, count in m.trades_by_signal_type.items():
                print("  %s: %d" % (signal_type, count))

        if m.trades_by_pair:
            print("\nTrades by Pair:")
            for pair, count in m.trades_by_pair.items():
                pair_trades = [t for t in self.trades if t.pair == pair]
                pair_wins = sum(1 for t in pair_trades if t.profit_loss > 0)
                pair_wr = (pair_wins / float(len(pair_trades)) * 100) if pair_trades else 0
                print("  %s: %d trades, %.1f%% win rate" % (pair, count, pair_wr))

        print("="*80)


def run_edge_case_tests():
    """Run edge case tests"""
    print("\n" + "="*80)
    print("EDGE CASE TESTING")
    print("="*80)

    results = {}
    config = get_config()

    print("\n[Test 1] High Volatility Market")
    sim1 = DryRunSimulator(config)
    metrics1 = sim1.run_simulation(15, "high_volatility")
    sim1.print_results()
    results['high_volatility'] = metrics1.to_dict()

    print("\n[Test 2] Flat/Ranging Market (Low ADX)")
    sim2 = DryRunSimulator(config)
    metrics2 = sim2.run_simulation(15, "flat")
    sim2.print_results()
    results['flat_market'] = metrics2.to_dict()

    print("\n[Test 3] Normal Market Conditions")
    sim3 = DryRunSimulator(config)
    metrics3 = sim3.run_simulation(15, "normal")
    sim3.print_results()
    results['normal_market'] = metrics3.to_dict()

    return results


def test_safety_mechanisms():
    """Test safety mechanisms"""
    print("\n" + "="*80)
    print("SAFETY MECHANISM TESTING")
    print("="*80)

    results = {}
    config = get_config()
    risk_mgr = RiskManager(config)

    print("\n[Safety Test 1] Daily Loss Limit Enforcement")
    risk_mgr.daily_loss = config['trading']['MAX_DAILY_LOSS'] + 1
    can_trade, reason = risk_mgr.should_trade()
    results['daily_loss_limit'] = not can_trade and "Daily loss limit" in reason
    print("  Status: %s" % ("PASS" if results['daily_loss_limit'] else "FAIL"))
    print("  Reason: %s" % reason)

    print("\n[Safety Test 2] Emergency Stop Activation")
    risk_mgr.daily_loss = config['safety']['EMERGENCY_STOP_LOSS'] + 1
    can_trade, reason = risk_mgr.should_trade()
    results['emergency_stop'] = not can_trade and "Emergency stop" in reason
    print("  Status: %s" % ("PASS" if results['emergency_stop'] else "FAIL"))
    print("  Reason: %s" % reason)

    print("\n[Safety Test 3] Consecutive Loss Pause")
    risk_mgr = RiskManager(config)
    risk_mgr.consecutive_losses = config['trading']['MAX_CONSECUTIVE_LOSSES']
    can_trade, reason = risk_mgr.should_trade()
    results['consecutive_loss_pause'] = not can_trade and "Consecutive loss" in reason
    print("  Status: %s" % ("PASS" if results['consecutive_loss_pause'] else "FAIL"))
    print("  Reason: %s" % reason)

    print("\n[Safety Test 4] Trade Validation (Low Confidence)")
    risk_mgr = RiskManager(config)
    signal = SignalType.CALL
    confidence = config['trading']['MIN_CONFIDENCE'] - 10
    can_trade, reason = risk_mgr.validate_trade(signal, confidence)
    results['trade_validation'] = not can_trade
    print("  Status: %s" % ("PASS" if results['trade_validation'] else "FAIL"))
    print("  Reason: %s" % reason)

    print("\n[Safety Test 5] Daily Profit Target (Take Profits)")
    risk_mgr = RiskManager(config)
    risk_mgr.daily_profit = config['trading']['MAX_DAILY_PROFIT'] + 1
    can_trade, reason = risk_mgr.should_trade()
    results['profit_target'] = not can_trade and "profit target" in reason
    print("  Status: %s" % ("PASS" if results['profit_target'] else "FAIL"))
    print("  Reason: %s" % reason)

    print("\n" + "-"*80)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print("Safety Tests Passed: %d/%d" % (passed, total))

    return results


def test_performance():
    """Test performance"""
    print("\n" + "="*80)
    print("PERFORMANCE BASELINE TESTING")
    print("="*80)

    config = get_config()
    signal_gen = SignalGenerator(config)
    market_sim = MarketSimulator()

    results = {}

    print("\n[Performance Test 1] Signal Generation Speed (100 iterations)")
    candles = market_sim.generate_realistic_prices(1.10000, 100)

    start = time.time()
    for _ in range(100):
        indicators = signal_gen.calculate_indicators(candles)
        signal, confidence = signal_gen.generate_signal(indicators)
    elapsed = (time.time() - start) * 1000

    avg_time = elapsed / 100.0
    results['avg_signal_gen_ms'] = avg_time
    print("  Total Time: %.2fms" % elapsed)
    print("  Average Time per Signal: %.3fms" % avg_time)
    print("  Signals per Second: %.0f" % (1000.0/avg_time))
    print("  Status: %s" % ("PASS" if avg_time < 100 else "SLOW"))

    print("\n[Performance Test 2] Indicator Calculation Speed (100 iterations)")
    start = time.time()
    for _ in range(100):
        indicators = signal_gen.calculate_indicators(candles)
    elapsed = (time.time() - start) * 1000

    avg_time = elapsed / 100.0
    results['avg_indicator_calc_ms'] = avg_time
    print("  Total Time: %.2fms" % elapsed)
    print("  Average Time per Calculation: %.3fms" % avg_time)
    print("  Calculations per Second: %.0f" % (1000.0/avg_time))
    print("  Status: %s" % ("PASS" if avg_time < 50 else "SLOW"))

    print("\n" + "-"*80)
    for key, value in results.items():
        print("%s: %.2fms" % (key, value))

    return results


if __name__ == '__main__':
    print("\n" + "*"*80)
    print("* COMPREHENSIVE DRY-RUN SIMULATION AND TEST SUITE")
    print("*"*80)

    # Configuration validation
    config = get_config()
    from paper_trading_config import validate_config

    if not validate_config():
        print("ERROR: Configuration validation failed!")
        sys.exit(1)

    print("\nConfiguration validated successfully")

    # Run simulations
    edge_case_results = run_edge_case_tests()
    safety_results = test_safety_mechanisms()
    performance_results = test_performance()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    safety_passed = sum(1 for v in safety_results.values() if isinstance(v, bool) and v)

    print("Safety Mechanism Tests: %d/5 PASSED" % safety_passed)
    print("Performance Tests:      2/2 BASELINE MEASURED")
    print("Edge Case Tests:        3/3 COMPLETED")

    print("\n" + "="*80)
    print("DRY-RUN SIMULATION COMPLETE")
    print("="*80)
