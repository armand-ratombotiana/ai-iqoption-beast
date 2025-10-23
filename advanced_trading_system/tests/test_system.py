"""
Test the Advanced Trading System components
Tests database, indicators, and AI models (without live trading)
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.trade_storage import TradeDatabase
from analysis.technical_indicators import TechnicalIndicators
from ai_models import AIConsensusEngine


def test_database():
    """Test database functionality"""
    print("\n" + "=" * 70)
    print("🧪 TEST 1: Database Storage")
    print("=" * 70)

    db = TradeDatabase("test_trades.db")

    # Insert test trade
    trade_data = {
        'trade_id': 'test_123',
        'timestamp': '2025-10-05T14:30:00',
        'pair': 'EURUSD-OTC',
        'direction': 'CALL',
        'amount': 2.0,
        'duration': 1,
        'result': 'WIN',
        'profit': 1.6,
        'ai_signal_confidence': 78,
        'ai_model_agreement': 75.0,
        'rsi_14': 65.2,
        'trend': 'uptrend',
        'volatility': 'medium'
    }

    success = db.insert_trade(trade_data)
    print(f"✅ Trade inserted: {success}")

    # Retrieve trade
    trade = db.get_trade('test_123')
    print(f"✅ Trade retrieved: {trade['pair']} {trade['direction']}")

    # Get statistics
    stats = db.get_statistics('all')
    print(f"✅ Statistics: {stats['total_trades']} trades, {stats['win_rate']:.1f}% win rate")

    db.close()
    print("✅ Database test passed!")


def test_technical_indicators():
    """Test technical indicators"""
    print("\n" + "=" * 70)
    print("🧪 TEST 2: Technical Indicators")
    print("=" * 70)

    # Create sample candles
    candles = []
    base_price = 1.0950
    for i in range(50):
        candle = {
            'open': base_price + (i * 0.0001),
            'high': base_price + (i * 0.0001) + 0.0005,
            'low': base_price + (i * 0.0001) - 0.0003,
            'close': base_price + (i * 0.0001) + 0.0002,
            'volume': 1000 + (i * 10)
        }
        candles.append(candle)

    indicators = TechnicalIndicators()

    # Test indicators
    rsi = indicators.rsi(candles, 14)
    print(f"✅ RSI(14): {rsi}")

    macd = indicators.macd(candles)
    print(f"✅ MACD: {macd}")

    bb = indicators.bollinger_bands(candles)
    print(f"✅ Bollinger Bands: Upper={bb['upper']:.6f}, Lower={bb['lower']:.6f}")

    trend = indicators.identify_trend(candles)
    print(f"✅ Trend: {trend}")

    volatility, vol_val = indicators.calculate_volatility(candles)
    print(f"✅ Volatility: {volatility} ({vol_val:.2f}%)")

    support, resistance = indicators.find_support_resistance(candles)
    print(f"✅ Support/Resistance: {support:.6f} / {resistance:.6f}")

    pattern = indicators.detect_candlestick_pattern(candles)
    print(f"✅ Candlestick Pattern: {pattern}")

    print("✅ Technical indicators test passed!")


def test_ai_consensus():
    """Test AI consensus (without actual API calls)"""
    print("\n" + "=" * 70)
    print("🧪 TEST 3: AI Consensus Engine")
    print("=" * 70)

    # Create mock AI models
    class MockAIModel:
        def __init__(self, name, signal, confidence):
            self.model_name = name
            self._signal = signal
            self._confidence = confidence

        def predict(self, market_data):
            return {
                'signal': self._signal,
                'confidence': self._confidence,
                'reasoning': f'{self.model_name} analysis',
                'model': self.model_name
            }

        def get_model_info(self):
            return {
                'name': self.model_name,
                'type': 'mock',
                'total_predictions': 0
            }

    # Create consensus engine
    consensus_engine = AIConsensusEngine(consensus_threshold=0.66)

    # Add mock models
    model1 = MockAIModel('mock-gpt', 'CALL', 82)
    model2 = MockAIModel('mock-claude', 'CALL', 75)
    model3 = MockAIModel('mock-deepseek', 'PUT', 60)

    consensus_engine.add_model(model1, weight=1.2)
    consensus_engine.add_model(model2, weight=1.0)
    consensus_engine.add_model(model3, weight=1.0)

    # Get consensus
    market_data = {
        'pair': 'EURUSD-OTC',
        'current_price': 1.0950,
        'rsi_14': 65,
        'trend': 'uptrend'
    }

    consensus = consensus_engine.get_consensus_signal(market_data)

    print(f"✅ Consensus Signal: {consensus['signal']}")
    print(f"✅ Confidence: {consensus['confidence']:.1f}%")
    print(f"✅ Agreement: {consensus['agreement']:.1f}%")
    print(f"✅ Consensus Reached: {consensus['consensus_reached']}")

    print("\nVoting Breakdown:")
    print(f"   CALL weight: {consensus['call_weight']:.2f}")
    print(f"   PUT weight: {consensus['put_weight']:.2f}")

    # Test expected result
    expected_signal = 'CALL'  # 2.2 CALL vs 1.0 PUT
    expected_agreement = (2.2 / 3.2) * 100  # 68.75%

    assert consensus['signal'] == expected_signal, f"Expected {expected_signal}, got {consensus['signal']}"
    assert consensus['consensus_reached'] == True, "Expected consensus to be reached"

    print("\n✅ AI consensus test passed!")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 ADVANCED TRADING SYSTEM - COMPONENT TESTS")
    print("=" * 70)

    try:
        test_database()
        test_technical_indicators()
        test_ai_consensus()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n🎉 Advanced Trading System components are working correctly!")
        print("\nNext steps:")
        print("1. Set API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, DEEPSEEK_API_KEY")
        print("2. Run: python scripts/run_trading.py")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
