"""
Market Context Analyzer
Captures comprehensive market state before and after trades
"""
import time
from datetime import datetime
from typing import Dict, List, Optional
from .technical_indicators import TechnicalIndicators


class MarketContextAnalyzer:
    """
    Captures and analyzes market conditions before and after trades
    """

    def __init__(self):
        self.indicators = TechnicalIndicators()

    def capture_pre_trade_context(self, api, pair: str, timeframe: str = '1m',
                                  candle_count: int = 100) -> Dict:
        """
        Capture comprehensive market state BEFORE trade execution

        Returns dictionary with 20+ technical indicators and market conditions
        """
        try:
            # Get candles
            current_time = int(time.time())
            candles = api.get_candles(pair, timeframe, candle_count, current_time)

            if not candles or len(candles) < 20:
                print(f"⚠️  Insufficient candle data for {pair}")
                return self._get_default_context(pair)

            # Calculate all technical indicators
            rsi_14 = self.indicators.rsi(candles, 14)
            rsi_7 = self.indicators.rsi(candles, 7)
            macd = self.indicators.macd(candles)
            bb = self.indicators.bollinger_bands(candles)
            stoch = self.indicators.stochastic(candles)

            # Moving averages
            ema_12 = self.indicators.ema(candles, 12)
            ema_26 = self.indicators.ema(candles, 26)
            sma_20 = self.indicators.sma(candles, 20)
            sma_50 = self.indicators.sma(candles, 50)

            # Volatility and trend strength
            atr = self.indicators.atr(candles)
            adx = self.indicators.adx(candles)
            cci = self.indicators.cci(candles)
            williams = self.indicators.williams_r(candles)

            # Market analysis
            trend = self.indicators.identify_trend(candles)
            volatility, volatility_value = self.indicators.calculate_volatility(candles)
            support, resistance = self.indicators.find_support_resistance(candles)
            candlestick_pattern = self.indicators.detect_candlestick_pattern(candles)
            volume_ma, volume_trend = self.indicators.volume_analysis(candles)

            # Current candle
            current_candle = candles[-1]
            current_price = current_candle['close']

            # Time context
            now = datetime.now()
            hour = now.hour
            day_of_week = now.weekday()  # 0=Monday, 6=Sunday

            # Market session
            if 0 <= hour < 8:
                session = 'asian'
            elif 8 <= hour < 16:
                session = 'london'
            else:
                session = 'newyork'

            context = {
                'timestamp': now.isoformat(),
                'pair': pair,
                'timeframe': timeframe,

                # Price Data
                'current_price': current_price,
                'open': current_candle['open'],
                'high': current_candle['high'],
                'low': current_candle['low'],
                'volume': current_candle.get('volume', 0),

                # Technical Indicators
                'rsi_14': rsi_14,
                'rsi_7': rsi_7,
                'macd_value': macd['macd'],
                'macd_signal': macd['signal'],
                'macd_histogram': macd['histogram'],
                'bb_upper': bb['upper'],
                'bb_middle': bb['middle'],
                'bb_lower': bb['lower'],
                'bb_position': bb['position'],
                'ema_12': ema_12,
                'ema_26': ema_26,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'atr': atr,
                'stochastic_k': stoch['k'],
                'stochastic_d': stoch['d'],
                'adx': adx,
                'cci': cci,
                'williams_r': williams,

                # Market Conditions
                'trend': trend,
                'volatility': volatility,
                'volatility_value': volatility_value,
                'support_level': support,
                'resistance_level': resistance,
                'volume_ma': volume_ma,
                'volume_trend': volume_trend,

                # Time Context
                'hour_of_day': hour,
                'day_of_week': day_of_week,
                'market_session': session,

                # Patterns
                'candlestick_pattern': candlestick_pattern,
                'chart_pattern': self._detect_chart_pattern(candles),

                # Additional Analysis
                'price_to_sma20_pct': ((current_price - sma_20) / sma_20 * 100) if sma_20 > 0 else 0,
                'distance_to_support': current_price - support,
                'distance_to_resistance': resistance - current_price,
            }

            return context

        except Exception as e:
            print(f"❌ Error capturing pre-trade context: {e}")
            return self._get_default_context(pair)

    def capture_post_trade_context(self, api, pair: str, pre_context: Dict,
                                   expiration: int) -> Dict:
        """
        Capture market state AFTER trade expiration

        Args:
            api: IQ Option API instance
            pair: Trading pair
            pre_context: Pre-trade context dictionary
            expiration: Trade duration in minutes

        Returns:
            Dictionary with post-trade analysis
        """
        try:
            # Wait for expiration
            wait_time = expiration * 60
            print(f"\n⏳ Waiting {expiration} minutes for trade expiration...")
            time.sleep(wait_time)

            # Get candles during trade period
            current_time = int(time.time())
            candles = api.get_candles(pair, '1m', expiration + 5, current_time)

            if not candles or len(candles) < expiration:
                print(f"⚠️  Insufficient post-trade candle data")
                return self._get_default_post_context(pre_context)

            # Price analysis
            entry_price = pre_context['current_price']
            exit_price = candles[-1]['close']
            price_change = exit_price - entry_price
            price_change_percent = (price_change / entry_price * 100) if entry_price > 0 else 0

            # High/Low during trade
            trade_candles = candles[-expiration:]
            highest = max([c['high'] for c in trade_candles])
            lowest = min([c['low'] for c in trade_candles])
            price_range = highest - lowest

            # Direction analysis
            actual_direction = 'UP' if exit_price > entry_price else 'DOWN'

            # Post-trade indicators (current state)
            rsi_14_post = self.indicators.rsi(candles, 14)
            macd_post = self.indicators.macd(candles)
            trend_post = self.indicators.identify_trend(candles)
            volatility_post, volatility_value_post = self.indicators.calculate_volatility(candles)

            # Trend analysis
            trend_continued = (pre_context['trend'] == trend_post)
            trend_reversed = (
                (pre_context['trend'] == 'uptrend' and trend_post == 'downtrend') or
                (pre_context['trend'] == 'downtrend' and trend_post == 'uptrend')
            )

            # Volatility analysis
            avg_volatility = sum([c['high'] - c['low'] for c in trade_candles]) / len(trade_candles)
            max_candle_size = max([c['high'] - c['low'] for c in trade_candles])
            volatility_spike = max_candle_size > (avg_volatility * 2)

            post_context = {
                'timestamp': datetime.now().isoformat(),

                # Price Movement
                'entry_price': entry_price,
                'exit_price': exit_price,
                'price_change': price_change,
                'price_change_percent': price_change_percent,

                # High/Low During Trade
                'highest_price': highest,
                'lowest_price': lowest,
                'price_range': price_range,

                # Volatility Analysis
                'avg_volatility': avg_volatility,
                'max_candle_size': max_candle_size,
                'volatility_spike': volatility_spike,

                # Direction Analysis
                'actual_direction': actual_direction,
                'trend_continued': trend_continued,
                'trend_reversal': trend_reversed,

                # Post-Trade Indicators
                'rsi_14_post': rsi_14_post,
                'macd_value_post': macd_post['macd'],
                'macd_signal_post': macd_post['signal'],
                'trend_post': trend_post,
                'volatility_post': volatility_post,
                'volatility_value_post': volatility_value_post,

                # Events Detection
                'news_event': None,  # Would integrate news API here
                'major_order_detected': self._detect_large_orders(trade_candles),
            }

            return post_context

        except Exception as e:
            print(f"❌ Error capturing post-trade context: {e}")
            return self._get_default_post_context(pre_context)

    def _detect_chart_pattern(self, candles: List[Dict]) -> str:
        """Detect chart patterns (simplified)"""
        if len(candles) < 20:
            return 'none'

        recent = candles[-20:]
        highs = [c['high'] for c in recent]
        lows = [c['low'] for c in recent]

        # Simple pattern detection
        if len(set(highs[-5:])) == 1:  # Horizontal resistance
            return 'horizontal_resistance'
        if len(set(lows[-5:])) == 1:  # Horizontal support
            return 'horizontal_support'

        # Ascending/descending triangles (simplified)
        if highs[-1] > highs[-10] and lows[-1] > lows[-10]:
            return 'ascending_triangle'
        if highs[-1] < highs[-10] and lows[-1] < lows[-10]:
            return 'descending_triangle'

        return 'none'

    def _detect_large_orders(self, candles: List[Dict]) -> bool:
        """Detect if large orders occurred (volume spike)"""
        if len(candles) < 5:
            return False

        volumes = [c.get('volume', 0) for c in candles]
        avg_volume = sum(volumes) / len(volumes)
        max_volume = max(volumes)

        return max_volume > (avg_volume * 3)  # 3x average = large order

    def _get_default_context(self, pair: str) -> Dict:
        """Return default context when data unavailable"""
        return {
            'timestamp': datetime.now().isoformat(),
            'pair': pair,
            'timeframe': '1m',
            'current_price': 0,
            'error': 'Insufficient data'
        }

    def _get_default_post_context(self, pre_context: Dict) -> Dict:
        """Return default post context when data unavailable"""
        return {
            'timestamp': datetime.now().isoformat(),
            'entry_price': pre_context.get('current_price', 0),
            'exit_price': pre_context.get('current_price', 0),
            'price_change': 0,
            'actual_direction': 'UNKNOWN',
            'error': 'Insufficient data'
        }
