import time
import types
import pytest
from autonomous_parallel_trading_bot import ParallelTradingBot, ParallelTradingConfig


class DummyAPI:
    def __init__(self, candles=None, all_profit=None, rem=None):
        self._candles = candles
        self._all_profit = all_profit or {}
        self._rem = rem

    def get_candles(self, instrument, interval, count, endtime):
        return self._candles

    def get_all_profit(self):
        return self._all_profit

    def get_remaning(self, duration):
        return self._rem


@pytest.fixture
def bot(tmp_path):
    logger = __import__('logging').getLogger('test')
    b = ParallelTradingBot(logger)
    return b


def make_candle(open_p, close_p, low=None, high=None, volume=0):
    return {'open': open_p, 'close': close_p, 'min': low or min(open_p, close_p), 'max': high or max(open_p, close_p), 'from': int(time.time()), 'volume': volume}


def test_fallback_random_when_no_candles(bot):
    bot.api = DummyAPI(candles=None)
    sig = bot.get_ai_signal('EURUSD')
    assert sig is not None
    assert 'signal' in sig
    assert 'strategy_breakdown' in sig


def test_respects_min_payout(bot):
    # candles that give a CALL bias
    candles = [make_candle(1.0, 1.1) for _ in range(20)]
    # low payout
    all_profit = {'EURUSD': {'binary': 0.5}}
    bot.api = DummyAPI(candles=candles, all_profit=all_profit, rem=(30,))
    sig = bot.get_ai_signal('EURUSD')
    # Should produce signal but tradeable should be False because payout < MIN_PAYOUT_RATIO
    assert 'tradeable' in sig
    assert sig['payout_ratio'] == 0.5
    assert sig['tradeable'] is False


def test_timing_risk_sets_tradeable_false(bot):
    candles = [make_candle(1.0, 0.9) for _ in range(20)]
    all_profit = {'EURUSD': {'binary': 0.8}}
    # simulate bad remaining seconds (very large)
    bot.api = DummyAPI(candles=candles, all_profit=all_profit, rem=(10000,))
    sig = bot.get_ai_signal('EURUSD')
    assert sig['timing_risk'] is True
    assert sig['tradeable'] is False


def test_normal_signal_and_estimated_win_prob(bot):
    # mix of candles
    candles = []
    for i in range(30):
        candles.append(make_candle(1.0 + i*0.0001, 1.0 + (i+1)*0.0001))
    all_profit = {'EURUSD': {'binary': 0.8}}
    bot.api = DummyAPI(candles=candles, all_profit=all_profit, rem=(30,))
    sig = bot.get_ai_signal('EURUSD')
    assert 'estimated_win_prob' in sig
    assert 0.0 <= sig['estimated_win_prob'] <= 1.0
    assert 'confidence' in sig
    assert 50 <= sig['confidence'] <= 99
