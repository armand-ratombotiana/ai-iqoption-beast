#!/usr/bin/env python3
"""
Automated Paper Trading Engine
Runs demo trades with TA-Lib indicators and comprehensive monitoring

Features:
- Automated signal generation using TA-Lib
- Real-time trade execution on demo account
- Comprehensive metrics tracking
- Trade validation and logging
- Performance analytics
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration
from paper_trading_config import get_config, TESTING_PAIRS

# Import analysis (TA-Lib)
from analysis import TechnicalIndicators, USING_TALIB

# Import IQOption API
from iqoptionapi.stable_api import IQ_Option

# Import secrets manager
from utils.secrets_manager import SecretsManager


@dataclass
class Trade:
    """Paper trading trade record"""
    timestamp: str
    pair: str
    signal: str  # CALL or PUT
    confidence: float
    amount: float
    duration: int
    entry_price: float
    payout: float

    # Indicator values at trade time
    rsi: float
    macd_histogram: float
    stoch_k: float
    adx: float
    bb_position: float

    # Trade result (filled after completion)
    order_id: Optional[int] = None
    exit_price: Optional[float] = None
    profit: Optional[float] = None
    result: Optional[str] = None  # WIN, LOSS, TIE


class PaperTradingEngine:
    """Automated paper trading engine with TA-Lib indicators"""

    def __init__(self, config: Dict):
        """Initialize paper trading engine"""
        self.config = config['trading']
        self.indicator_config = config['indicators']
        self.validation_config = config['validation']
        self.safety_config = config['safety']

        # Get credentials
        secrets = SecretsManager()
        self.email, self.password = secrets.get_iqoption_credentials()

        # Initialize API
        self.api = None
        self.connected = False

        # Trading state
        self.trades: List[Trade] = []
        self.daily_profit = 0.0
        self.daily_loss = 0.0
        self.consecutive_losses = 0
        self.is_running = False

        # Metrics
        self.metrics = {
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'ties': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'max_drawdown': 0.0,
        }

        # Validate TA-Lib is being used
        if not USING_TALIB:
            print("WARNING: TA-Lib not available, using custom indicators")
        else:
            print("Using professional TA-Lib indicators")

    def connect(self) -> bool:
        """Connect to IQOption demo account"""
        print("\n" + "="*70)
        print("CONNECTING TO IQOPTION DEMO ACCOUNT")
        print("="*70)

        try:
            self.api = IQ_Option(self.email, self.password)
            check, reason = self.api.connect()

            if not check:
                print(f"ERROR: Connection failed - {reason}")
                return False

            print("Connected successfully!")

            # Switch to demo account
            self.api.change_balance('PRACTICE')
            time.sleep(1)

            balance = self.api.get_balance()
            print(f"Demo Account Balance: ${balance:.2f}")

            self.connected = True
            return True

        except Exception as e:
            print(f"ERROR: Connection exception - {e}")
            return False

    def get_candles(self, pair: str, count: int = 100) -> Optional[List[Dict]]:
        """Get historical candles for analysis"""
        try:
            # Clean pair name
            clean_pair = pair.replace('-OTC', '')

            # Start candle stream
            self.api.start_candles_stream(clean_pair, 60, count)
            time.sleep(3)  # Wait for data

            # Get candles
            candles_dict = self.api.get_realtime_candles(clean_pair, 60)
            self.api.stop_candles_stream(clean_pair, 60)

            if not candles_dict:
                return None

            # Convert to list format
            candles = []
            for timestamp, data in sorted(candles_dict.items()):
                candles.append({
                    'timestamp': timestamp,
                    'open': data['open'],
                    'high': data['max'],
                    'low': data['min'],
                    'close': data['close'],
                    'volume': data.get('volume', 0)
                })

            return candles if len(candles) >= 50 else None

        except Exception as e:
            print(f"ERROR getting candles for {pair}: {e}")
            return None

    def analyze_market(self, pair: str, candles: List[Dict]) -> Optional[Dict]:
        """Analyze market using TA-Lib indicators"""
        try:
            # Calculate indicators using TA-Lib
            rsi = TechnicalIndicators.rsi(candles, period=self.indicator_config['RSI']['period'])
            macd = TechnicalIndicators.macd(candles)
            stoch = TechnicalIndicators.stochastic(candles)
            adx = TechnicalIndicators.adx(candles)
            bb = TechnicalIndicators.bollinger_bands(candles)

            # Current price
            current_price = candles[-1]['close']

            return {
                'pair': pair,
                'price': current_price,
                'rsi': rsi,
                'macd': macd,
                'stochastic': stoch,
                'adx': adx,
                'bollinger_bands': bb,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"ERROR analyzing {pair}: {e}")
            return None

    def generate_signal(self, analysis: Dict) -> Tuple[Optional[str], float]:
        """
        Generate trading signal from analysis

        Returns:
            (signal, confidence) where signal is 'CALL', 'PUT', or None
        """
        signals = {'CALL': 0, 'PUT': 0}
        confidence = 50.0

        rsi = analysis['rsi']
        macd = analysis['macd']
        stoch = analysis['stochastic']
        adx = analysis['adx']
        bb = analysis['bollinger_bands']

        # Check if trend is strong enough (ADX filter)
        if adx < self.indicator_config['ADX']['min_trend_strength']:
            return None, 0  # Don't trade in weak/ranging markets

        # RSI signals
        if rsi < self.indicator_config['RSI']['oversold']:
            signals['CALL'] += 1
            confidence += 10
        elif rsi > self.indicator_config['RSI']['overbought']:
            signals['PUT'] += 1
            confidence += 10

        # MACD signals
        if macd['histogram'] > 0:
            signals['CALL'] += 1
            confidence += 8
        elif macd['histogram'] < 0:
            signals['PUT'] += 1
            confidence += 8

        # Stochastic signals
        if stoch['k'] < self.indicator_config['STOCHASTIC']['oversold']:
            signals['CALL'] += 1
            confidence += 7
        elif stoch['k'] > self.indicator_config['STOCHASTIC']['overbought']:
            signals['PUT'] += 1
            confidence += 7

        # Bollinger Bands signals
        if bb['position'] < 0.2:  # Near lower band
            signals['CALL'] += 1
            confidence += 6
        elif bb['position'] > 0.8:  # Near upper band
            signals['PUT'] += 1
            confidence += 6

        # Require multiple indicators to agree
        if self.config['REQUIRE_MULTIPLE_INDICATORS']:
            min_agreement = self.config['MIN_INDICATOR_AGREEMENT']
            if signals['CALL'] < min_agreement and signals['PUT'] < min_agreement:
                return None, 0

        # Determine final signal
        if signals['CALL'] > signals['PUT']:
            return 'CALL', min(confidence, 100.0)
        elif signals['PUT'] > signals['CALL']:
            return 'PUT', min(confidence, 100.0)
        else:
            return None, 0

    def execute_trade(self, pair: str, signal: str, confidence: float, analysis: Dict) -> Optional[Trade]:
        """Execute a paper trade"""
        try:
            # Get payout
            clean_pair = pair.replace('-OTC', '')
            payout = self.api.get_binary_payout(clean_pair)
            if not payout:
                payout = 0.80  # Default 80%

            # Create trade record
            trade = Trade(
                timestamp=datetime.now().isoformat(),
                pair=pair,
                signal=signal,
                confidence=confidence,
                amount=self.config['TRADE_AMOUNT'],
                duration=self.config['TRADE_DURATION'],
                entry_price=analysis['price'],
                payout=payout,
                rsi=analysis['rsi'],
                macd_histogram=analysis['macd']['histogram'],
                stoch_k=analysis['stochastic']['k'],
                adx=analysis['adx'],
                bb_position=analysis['bollinger_bands']['position']
            )

            # Execute on IQOption
            print(f"\n[TRADE] {signal} {pair} @ ${analysis['price']:.5f}")
            print(f"        Confidence: {confidence:.1f}% | Amount: ${trade.amount} | Payout: {payout:.0%}")

            status, order_id = self.api.buy(
                trade.amount,
                clean_pair,
                signal.lower(),
                trade.duration
            )

            if not status or not order_id:
                print("        Trade execution FAILED")
                return None

            trade.order_id = order_id
            print(f"        Order ID: {order_id} - Waiting {trade.duration} min...")

            return trade

        except Exception as e:
            print(f"ERROR executing trade: {e}")
            return None

    def wait_for_result(self, trade: Trade) -> Trade:
        """Wait for trade result and update trade record"""
        # Wait for trade duration + 5 seconds
        wait_time = trade.duration * 60 + 5
        time.sleep(wait_time)

        # Get result
        for attempt in range(20):
            try:
                profit = self.api.check_win_v3(trade.order_id)
                if profit is not None:
                    trade.profit = profit

                    if profit > 0:
                        trade.result = 'WIN'
                        self.metrics['wins'] += 1
                        self.daily_profit += profit
                        self.consecutive_losses = 0
                    elif profit < 0:
                        trade.result = 'LOSS'
                        self.metrics['losses'] += 1
                        self.daily_loss += abs(profit)
                        self.consecutive_losses += 1
                    else:
                        trade.result = 'TIE'
                        self.metrics['ties'] += 1

                    self.metrics['total_trades'] += 1
                    self.metrics['total_profit'] += profit

                    # Calculate win rate
                    if self.metrics['total_trades'] > 0:
                        self.metrics['win_rate'] = (self.metrics['wins'] / self.metrics['total_trades']) * 100

                    print(f"\n[RESULT] {trade.result} - Profit: ${profit:+.2f}")
                    print(f"         Win Rate: {self.metrics['win_rate']:.1f}% ({self.metrics['wins']}/{self.metrics['total_trades']})")

                    return trade

            except Exception as e:
                print(f"[RETRY] Check error: {e}")

            time.sleep(0.5)

        print("[ERROR] Could not get trade result")
        trade.result = 'UNKNOWN'
        return trade

    def check_risk_limits(self) -> bool:
        """Check if risk limits allow trading"""
        # Daily loss limit
        if self.daily_loss >= self.config['MAX_DAILY_LOSS']:
            print(f"\n[STOP] Daily loss limit reached: ${self.daily_loss:.2f}")
            return False

        # Daily profit target
        if self.daily_profit >= self.config['MAX_DAILY_PROFIT']:
            print(f"\n[STOP] Daily profit target reached: ${self.daily_profit:.2f}")
            return False

        # Consecutive losses
        if self.consecutive_losses >= self.config['MAX_CONSECUTIVE_LOSSES']:
            print(f"\n[STOP] Max consecutive losses reached: {self.consecutive_losses}")
            return False

        # Trade count limit
        if len(self.trades) >= self.config['MAX_DAILY_TRADES']:
            print(f"\n[STOP] Daily trade limit reached: {len(self.trades)}")
            return False

        return True

    def print_summary(self):
        """Print trading session summary"""
        print("\n" + "="*70)
        print("PAPER TRADING SESSION SUMMARY")
        print("="*70)
        print(f"Total Trades: {self.metrics['total_trades']}")
        print(f"Wins: {self.metrics['wins']}")
        print(f"Losses: {self.metrics['losses']}")
        print(f"Ties: {self.metrics['ties']}")
        print(f"Win Rate: {self.metrics['win_rate']:.2f}%")
        print(f"Total Profit: ${self.metrics['total_profit']:+.2f}")
        print(f"Daily Profit: ${self.daily_profit:.2f}")
        print(f"Daily Loss: ${self.daily_loss:.2f}")
        print("="*70)

    def run(self):
        """Run automated paper trading"""
        print("\n" + "="*70)
        print("STARTING AUTOMATED PAPER TRADING")
        print("="*70)
        print(f"Using {'TA-Lib (Professional)' if USING_TALIB else 'Custom'} Indicators")
        print(f"Target: {self.config['TARGET_TRADE_COUNT']} trades")
        print(f"Pairs: {', '.join(TESTING_PAIRS)}")
        print("="*70)

        if not self.connect():
            return False

        self.is_running = True

        try:
            while self.is_running and len(self.trades) < self.config['TARGET_TRADE_COUNT']:
                # Check risk limits
                if not self.check_risk_limits():
                    break

                # Analyze each pair
                for pair in TESTING_PAIRS:
                    if not self.is_running:
                        break

                    print(f"\n[ANALYZING] {pair}...")

                    # Get market data
                    candles = self.get_candles(pair)
                    if not candles:
                        print(f"            No data available")
                        continue

                    # Analyze
                    analysis = self.analyze_market(pair, candles)
                    if not analysis:
                        continue

                    # Generate signal
                    signal, confidence = self.generate_signal(analysis)

                    if signal and confidence >= self.config['MIN_CONFIDENCE']:
                        # Execute trade
                        trade = self.execute_trade(pair, signal, confidence, analysis)
                        if trade:
                            # Wait for result
                            trade = self.wait_for_result(trade)
                            self.trades.append(trade)

                        # Pause between trades
                        time.sleep(5)
                    else:
                        print(f"            No signal (Conf: {confidence:.1f}%)")

                # Pause before next analysis cycle
                time.sleep(10)

        except KeyboardInterrupt:
            print("\n\n[STOPPED] Paper trading interrupted by user")
        except Exception as e:
            print(f"\n\n[ERROR] {e}")
        finally:
            self.is_running = False
            self.print_summary()
            return True


if __name__ == '__main__':
    # Get configuration
    config = get_config()

    # Create engine
    engine = PaperTradingEngine(config)

    # Run paper trading
    engine.run()
