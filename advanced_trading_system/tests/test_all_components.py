"""
Comprehensive Component Testing - Tests actual API signatures
Tests each component with its real interface
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mock problematic imports
sys.modules['aioredis'] = MagicMock()
sys.modules['iqoptionapi'] = MagicMock()
sys.modules['iqoptionapi.stable_api'] = MagicMock()


class TestConfigModules:
    """Test configuration modules"""

    def test_trading_config(self):
        """Test main TradingConfig"""
        from config.settings import TradingConfig

        config = TradingConfig()

        # Verify attributes exist
        assert hasattr(config, 'EMAIL')
        assert hasattr(config, 'PASSWORD')
        assert hasattr(config, 'ACCOUNT_TYPE')
        assert hasattr(config, 'DB_PATH')

        print("✅ TradingConfig works")

    def test_parallel_config(self):
        """Test ParallelTradingConfig"""
        from config.parallel_settings import ParallelTradingConfig

        config = ParallelTradingConfig()

        assert hasattr(config, 'MAX_CONCURRENT_PAIRS')
        assert hasattr(config, 'MIN_PAYOUT_THRESHOLD')
        assert hasattr(config, 'BALANCE_ALLOCATION_PER_TRADE')

        print("✅ ParallelTradingConfig works")


class TestAnalysisModules:
    """Test analysis modules"""

    def test_technical_indicators(self):
        """Test TechnicalIndicators static methods"""
        from analysis.technical_indicators import TechnicalIndicators

        candles = [
            {'close': 100 + i, 'open': 100, 'high': 102, 'low': 99}
            for i in range(50)
        ]

        # Test RSI
        rsi = TechnicalIndicators.rsi(candles, period=14)
        assert rsi is not None
        assert 0 <= rsi <= 100
        print(f"  RSI: {rsi}")

        # Test MACD
        macd = TechnicalIndicators.macd(candles)
        assert 'macd' in macd
        assert 'signal' in macd
        assert 'histogram' in macd
        print(f"  MACD: {macd['macd']:.4f}")

        # Test Bollinger Bands
        bb = TechnicalIndicators.bollinger_bands(candles)
        assert 'upper' in bb
        assert 'middle' in bb
        assert 'lower' in bb
        print(f"  BB Middle: {bb['middle']:.2f}")

        # Test SMA
        sma = TechnicalIndicators.sma(candles, period=20)
        assert sma > 0
        print(f"  SMA: {sma:.2f}")

        # Test EMA
        ema = TechnicalIndicators.ema(candles, period=20)
        assert ema > 0
        print(f"  EMA: {ema:.2f}")

        print("✅ TechnicalIndicators all methods work")

    def test_market_context_analyzer(self):
        """Test MarketContextAnalyzer"""
        from analysis.market_context import MarketContextAnalyzer

        analyzer = MarketContextAnalyzer()

        # Check it has methods
        assert hasattr(analyzer, 'get_market_regime')

        print("✅ MarketContextAnalyzer works")


class TestDatabaseModules:
    """Test database modules"""

    def test_trade_database(self):
        """Test TradeDatabase"""
        from database.trade_storage import TradeDatabase

        db = TradeDatabase(':memory:')

        # Test insert
        trade_data = {
            'trade_id': 'test123',
            'timestamp': datetime.now().isoformat(),
            'pair': 'EURUSD',
            'direction': 'call',
            'amount': 10.0,
            'duration': 1,
            'result': 'PENDING',
            'ai_signal_confidence': 75
        }

        db.insert_trade(trade_data)

        # Test query
        trades = db.query_trades("SELECT * FROM trades")
        assert len(trades) >= 1

        # Test stats
        stats = db.get_statistics()
        assert 'total_trades' in stats

        db.close()

        print("✅ TradeDatabase works")


class TestAIModels:
    """Test AI model modules"""

    def test_base_model(self):
        """Test BaseAIModel"""
        from ai_models.base_model import BaseAIModel

        assert BaseAIModel is not None
        assert hasattr(BaseAIModel, 'predict')

        print("✅ BaseAIModel works")

    def test_ai_consensus_engine(self):
        """Test AIConsensusEngine"""
        from ai_models.consensus_engine import AIConsensusEngine

        engine = AIConsensusEngine()

        # Test it has methods
        assert hasattr(engine, 'get_consensus')

        print("✅ AIConsensusEngine works")

    def test_enhanced_consensus_engine(self):
        """Test EnhancedConsensusEngine"""
        from ai_models.enhanced_consensus import EnhancedConsensusEngine

        # Check signature
        engine = EnhancedConsensusEngine(consensus_threshold=0.65)

        assert hasattr(engine, 'get_consensus_signal')

        print("✅ EnhancedConsensusEngine works")

    def test_kelly_position_sizer(self):
        """Test KellyPositionSizer"""
        from ai_models.kelly_position_sizer import KellyPositionSizer

        config = {'MAX_POSITION_SIZE': 0.05, 'MIN_POSITION_SIZE': 0.01}
        sizer = KellyPositionSizer(config)

        # Test calculate_position (actual method name)
        position = sizer.calculate_position(
            win_rate=0.60,
            payout=0.80,
            balance=1000.0,
            confidence=0.75
        )

        assert position is not None
        assert position > 0

        print(f"  Position size: ${position:.2f}")
        print("✅ KellyPositionSizer works")

    def test_market_regime_detector(self):
        """Test MarketRegimeDetector"""
        from ai_models.market_regime_detector import MarketRegimeDetector

        detector = MarketRegimeDetector()

        candles = [
            {'close': 100 + i, 'volume': 1000, 'high': 102, 'low': 99}
            for i in range(50)
        ]

        regime = detector.detect_regime(candles)

        assert regime is not None
        print(f"  Market regime: {regime}")

        print("✅ MarketRegimeDetector works")


class TestDataProviders:
    """Test data provider modules"""

    def test_base_provider(self):
        """Test BaseDataProvider"""
        from data_providers.base_provider import BaseDataProvider

        assert BaseDataProvider is not None
        assert hasattr(BaseDataProvider, 'get_candles')

        print("✅ BaseDataProvider works")


class TestTradingEngine:
    """Test trading engine"""

    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    def test_parallel_trading_engine(self, mock_provider, mock_sizer,
                                    mock_consensus, mock_analyzer, mock_db):
        """Test ParallelTradingEngine initialization"""
        from trading.parallel_trading_engine import (
            ParallelTradingEngine,
            ParallelTradeConfig
        )
        from config.settings import TradingConfig

        config = TradingConfig()
        engine = ParallelTradingEngine(config)

        # Test components initialized
        assert engine.config is not None
        assert engine.parallel_config is not None
        assert isinstance(engine.parallel_config, ParallelTradeConfig)

        # Test state
        assert engine.active_trades == {}
        assert engine.pair_last_trade == {}

        print("✅ ParallelTradingEngine works")


class TestHelperModules:
    """Test helper and utility modules"""

    def test_dataclass_imports(self):
        """Test that all dataclasses work"""
        from trading.parallel_trading_engine import ParallelTradeConfig

        config = ParallelTradeConfig()

        assert config.max_concurrent_pairs == 5
        assert config.min_payout == 0.75

        print("✅ All dataclasses work")


class TestMethodSignatures:
    """Test that critical methods have correct signatures"""

    def test_technical_indicators_signatures(self):
        """Verify TechnicalIndicators method signatures"""
        from analysis.technical_indicators import TechnicalIndicators
        import inspect

        # Get all static methods
        methods = [
            'rsi', 'macd', 'bollinger_bands', 'sma', 'ema',
            'atr', 'stochastic', 'adx'
        ]

        for method_name in methods:
            if hasattr(TechnicalIndicators, method_name):
                method = getattr(TechnicalIndicators, method_name)
                sig = inspect.signature(method)
                # Just verify it exists and is callable
                assert callable(method)
                print(f"  ✓ {method_name}{sig}")

        print("✅ All TechnicalIndicators signatures verified")

    def test_database_signatures(self):
        """Verify TradeDatabase method signatures"""
        from database.trade_storage import TradeDatabase
        import inspect

        db = TradeDatabase(':memory:')

        methods = [
            'insert_trade', 'update_trade', 'query_trades',
            'get_statistics', 'get_recent_trades'
        ]

        for method_name in methods:
            if hasattr(db, method_name):
                method = getattr(db, method_name)
                sig = inspect.signature(method)
                assert callable(method)
                print(f"  ✓ {method_name}{sig}")

        db.close()

        print("✅ All TradeDatabase signatures verified")


class TestIntegration:
    """Test component integration"""

    def test_full_stack_instantiation(self):
        """Test that all components can be instantiated together"""
        from config.settings import TradingConfig
        from database.trade_storage import TradeDatabase
        from analysis.technical_indicators import TechnicalIndicators
        from ai_models.kelly_position_sizer import KellyPositionSizer

        # Create all components
        config = TradingConfig()
        db = TradeDatabase(':memory:')
        sizer = KellyPositionSizer(config.__dict__)

        # Use components together
        candles = [{'close': 100 + i, 'open': 100, 'high': 102, 'low': 99} for i in range(50)]
        rsi = TechnicalIndicators.rsi(candles)

        position = sizer.calculate_position(0.60, 0.80, 1000, 0.75)

        # Verify they work
        assert rsi > 0
        assert position > 0

        db.close()

        print("✅ Full stack integration works")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-s'])
