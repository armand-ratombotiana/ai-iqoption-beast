"""
Test Advanced Strategies

This script tests the advanced strategy engine with sample data
to verify all indicators and strategies work correctly.
"""

import sys
import logging
import numpy as np
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def generate_sample_candles(count: int = 100, trend: str = 'up') -> list:
    """
    Generate sample candle data for testing

    Args:
        count: Number of candles to generate
        trend: 'up', 'down', or 'sideways'
    """
    candles = []
    base_price = 1.10000
    timestamp = datetime.now()

    for i in range(count):
        # Generate price movement based on trend
        if trend == 'up':
            change = np.random.uniform(0, 0.0002) + 0.00005
        elif trend == 'down':
            change = -np.random.uniform(0, 0.0002) - 0.00005
        else:  # sideways
            change = np.random.uniform(-0.0001, 0.0001)

        open_price = base_price
        close_price = base_price + change

        # Add some randomness for high/low
        high_price = max(open_price, close_price) + np.random.uniform(0, 0.00005)
        low_price = min(open_price, close_price) - np.random.uniform(0, 0.00005)

        candles.append({
            'open': open_price,
            'close': close_price,
            'max': high_price,
            'min': low_price,
            'volume': np.random.randint(100, 1000),
            'timestamp': int(timestamp.timestamp())
        })

        base_price = close_price
        timestamp += timedelta(seconds=60)

    return candles


def test_strategies():
    """Test all strategies with different market conditions"""

    try:
        from strategies import AdvancedStrategyEngine
        from strategies.strategy_integrator import create_integrator

        logger.info("=" * 80)
        logger.info("🧪 TESTING ADVANCED STRATEGIES")
        logger.info("=" * 80)

        # Create integrator with moderate risk profile
        integrator = create_integrator('moderate')

        # Test 1: Uptrend
        logger.info("\n" + "=" * 80)
        logger.info("📈 TEST 1: UPTREND MARKET")
        logger.info("=" * 80)
        uptrend_candles = generate_sample_candles(100, 'up')
        signal = integrator.analyze_instrument(uptrend_candles)
        logger.info(integrator.format_signal_log('TEST-UPTREND', signal))

        # Test 2: Downtrend
        logger.info("\n" + "=" * 80)
        logger.info("📉 TEST 2: DOWNTREND MARKET")
        logger.info("=" * 80)
        downtrend_candles = generate_sample_candles(100, 'down')
        signal = integrator.analyze_instrument(downtrend_candles)
        logger.info(integrator.format_signal_log('TEST-DOWNTREND', signal))

        # Test 3: Sideways
        logger.info("\n" + "=" * 80)
        logger.info("↔️ TEST 3: SIDEWAYS MARKET")
        logger.info("=" * 80)
        sideways_candles = generate_sample_candles(100, 'sideways')
        signal = integrator.analyze_instrument(sideways_candles)
        logger.info(integrator.format_signal_log('TEST-SIDEWAYS', signal))

        # Test 4: Risk management
        logger.info("\n" + "=" * 80)
        logger.info("💰 TEST 4: RISK MANAGEMENT")
        logger.info("=" * 80)

        # Test trade sizing
        balance = 100.0
        logger.info(f"Balance: ${balance}")
        logger.info(f"Normal trade: ${integrator.get_trade_amount(balance)}")
        logger.info(f"After 2 wins: ${integrator.get_trade_amount(balance, win_streak=2)}")
        logger.info(f"After 3 wins: ${integrator.get_trade_amount(balance, win_streak=3)}")
        logger.info(f"After 2 losses: ${integrator.get_trade_amount(balance, loss_streak=2)}")
        logger.info(f"After 4 losses: ${integrator.get_trade_amount(balance, loss_streak=4)}")

        # Test stop conditions
        should_stop, reason = integrator.should_stop_trading(-5.0, 100)
        logger.info(f"\nDaily P&L: -$5.00 -> Stop: {should_stop} ({reason})")

        should_stop, reason = integrator.should_stop_trading(-11.0, 100)
        logger.info(f"Daily P&L: -$11.00 -> Stop: {should_stop} ({reason})")

        should_stop, reason = integrator.should_stop_trading(0, 45)
        logger.info(f"Balance: $45 -> Stop: {should_stop} ({reason})")

        # Test 5: Different risk profiles
        logger.info("\n" + "=" * 80)
        logger.info("⚙️ TEST 5: RISK PROFILES")
        logger.info("=" * 80)

        for profile in ['conservative', 'moderate', 'aggressive']:
            integrator = create_integrator(profile)
            logger.info(f"\n{profile.upper()} Profile:")
            logger.info(f"  Min Confidence: {integrator.config.min_confidence}")
            logger.info(f"  Min Confluence: {integrator.config.min_confluence}")
            logger.info(f"  Max Trade: ${integrator.config.max_trade_amount}")
            logger.info(f"  Max Daily Loss: ${integrator.config.max_daily_loss}")

        logger.info("\n" + "=" * 80)
        logger.info("✅ ALL TESTS COMPLETED")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    logger.info("Checking dependencies...")

    try:
        import numpy
        logger.info("✅ NumPy installed")
    except ImportError:
        logger.error("❌ NumPy not installed")
        return False

    try:
        import talib
        logger.info("✅ TA-Lib installed")
    except ImportError:
        logger.warning("⚠️  TA-Lib not installed (will use fallback implementations)")

    try:
        from strategies import AdvancedStrategyEngine
        logger.info("✅ Strategy module accessible")
    except ImportError as e:
        logger.error(f"❌ Strategy module not accessible: {e}")
        return False

    return True


if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("ADVANCED STRATEGY TEST SUITE")
    logger.info("=" * 80)

    # Check dependencies
    if not check_dependencies():
        logger.error("Dependency check failed")
        sys.exit(1)

    # Run tests
    success = test_strategies()

    if success:
        logger.info("\n✅ All tests passed!")
        sys.exit(0)
    else:
        logger.error("\n❌ Tests failed!")
        sys.exit(1)
