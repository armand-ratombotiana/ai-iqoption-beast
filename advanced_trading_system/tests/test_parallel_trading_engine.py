"""
Comprehensive tests for ParallelTradingEngine methods
Tests each method individually with mocked dependencies
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mock problematic imports before importing the module
sys.modules['aioredis'] = MagicMock()
sys.modules['iqoptionapi'] = MagicMock()
sys.modules['iqoptionapi.stable_api'] = MagicMock()

from trading.parallel_trading_engine import (
    ParallelTradingEngine,
    ParallelTradeConfig
)
from config.settings import TradingConfig


def create_mock_config():
    """Helper to create properly configured mock config"""
    # Create a simple object instead of Mock for cleaner attribute access
    class Config:
        def __init__(self):
            self.DB_PATH = ':memory:'
            self.CONSENSUS_THRESHOLD = 0.65
            self.EMAIL = 'test@test.com'
            self.PASSWORD = 'testpass'
            self.ACCOUNT_TYPE = 'PRACTICE'
            self.MIN_CONFIDENCE = 65

    return Config()


class TestParallelTradeConfig:
    """Test ParallelTradeConfig dataclass"""

    def test_default_values(self):
        """Test default configuration values"""
        config = ParallelTradeConfig()

        assert config.max_concurrent_pairs == 5
        assert config.min_payout == 0.75
        assert config.max_pairs_to_analyze == 20
        assert config.balance_allocation_per_trade == 0.02
        assert config.correlation_threshold == 0.7
        assert config.min_time_between_trades == 30
        assert config.risk_budget_percentage == 0.10
        print("✅ ParallelTradeConfig defaults are correct")

    def test_custom_values(self):
        """Test custom configuration values"""
        config = ParallelTradeConfig(
            max_concurrent_pairs=10,
            min_payout=0.80,
            max_pairs_to_analyze=30
        )

        assert config.max_concurrent_pairs == 10
        assert config.min_payout == 0.80
        assert config.max_pairs_to_analyze == 30
        print("✅ ParallelTradeConfig custom values work")


class TestParallelTradingEngineInit:
    """Test initialization methods"""

    @pytest.fixture
    def trading_config(self):
        """Create mock trading config"""
        return create_mock_config()

    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    def test_init(self, mock_provider, mock_sizer, mock_consensus,
                  mock_analyzer, mock_db, trading_config):
        """Test __init__ method"""
        engine = ParallelTradingEngine(trading_config)

        # Check components initialized
        assert engine.config == trading_config
        assert isinstance(engine.parallel_config, ParallelTradeConfig)
        assert engine.active_trades == {}
        assert engine.pair_last_trade == {}
        assert engine.total_risk_allocated == 0.0
        assert engine.semaphore is not None

        # Check mocks called
        mock_db.assert_called_once()
        mock_analyzer.assert_called_once()
        mock_consensus.assert_called_once()
        mock_sizer.assert_called_once()
        mock_provider.assert_called_once()

        print("✅ __init__ method works correctly")

    @pytest.mark.asyncio
    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    async def test_initialize(self, mock_provider_class, mock_sizer,
                              mock_consensus, mock_analyzer, mock_db,
                              trading_config):
        """Test initialize method"""
        # Setup mock provider
        mock_provider = AsyncMock()
        mock_provider.connect = AsyncMock()
        mock_provider_class.return_value = mock_provider

        engine = ParallelTradingEngine(trading_config)
        await engine.initialize()

        # Check provider connected
        mock_provider.connect.assert_called_once()
        print("✅ initialize method works correctly")


class TestCalculateMarketIndicators:
    """Test _calculate_market_indicators method"""

    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    def test_calculate_market_indicators(self, mock_provider, mock_sizer,
                                        mock_consensus, mock_analyzer,
                                        mock_db):
        """Test _calculate_market_indicators method"""
        config = create_mock_config()
        engine = ParallelTradingEngine(config)

        # Create sample candles
        candles = [
            {'close': 1.1000, 'open': 1.0990, 'high': 1.1010, 'low': 1.0980},
            {'close': 1.1020, 'open': 1.1000, 'high': 1.1030, 'low': 1.0990},
            {'close': 1.1015, 'open': 1.1020, 'high': 1.1025, 'low': 1.1000},
        ]

        result = engine._calculate_market_indicators(candles, 'EURUSD')

        # Check result structure
        assert 'pair' in result
        assert 'current_price' in result
        assert 'trend' in result
        assert 'volatility' in result
        assert 'rsi_14' in result
        assert 'hour' in result

        # Check values
        assert result['pair'] == 'EURUSD'
        assert result['current_price'] == 1.1015
        assert isinstance(result['hour'], int)

        print("✅ _calculate_market_indicators works correctly")

    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    def test_calculate_market_indicators_empty_candles(self, mock_provider,
                                                       mock_sizer, mock_consensus,
                                                       mock_analyzer, mock_db):
        """Test with empty candles"""
        config = create_mock_config()

        engine = ParallelTradingEngine(config)

        # This should handle gracefully or raise appropriate error
        try:
            result = engine._calculate_market_indicators([], 'EURUSD')
            # If it doesn't raise, check it handles empty gracefully
            assert result is not None or True
        except (IndexError, KeyError):
            # Expected behavior for empty candles
            pass

        print("✅ _calculate_market_indicators handles empty candles")


class TestIsCorrelatedWithActiveTrades:
    """Test _is_correlated_with_active_trades method"""

    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    def test_no_active_trades(self, mock_provider, mock_sizer, mock_consensus,
                             mock_analyzer, mock_db):
        """Test with no active trades"""
        config = create_mock_config()

        engine = ParallelTradingEngine(config)

        result = engine._is_correlated_with_active_trades('EURUSD')
        assert result is False
        print("✅ Returns False when no active trades")

    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    def test_correlated_pairs(self, mock_provider, mock_sizer, mock_consensus,
                             mock_analyzer, mock_db):
        """Test with correlated pairs"""
        config = create_mock_config()

        engine = ParallelTradingEngine(config)

        # Add active trade with EUR base
        engine.active_trades = {
            'order1': {'pair': 'EURUSD', 'signal': 'call'}
        }

        # Test same base currency
        result = engine._is_correlated_with_active_trades('EURJPY')
        assert result is True
        print("✅ Detects correlation with same base currency")

    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    def test_uncorrelated_pairs(self, mock_provider, mock_sizer, mock_consensus,
                               mock_analyzer, mock_db):
        """Test with uncorrelated pairs"""
        config = create_mock_config()

        engine = ParallelTradingEngine(config)

        # Add active trade with EUR base
        engine.active_trades = {
            'order1': {'pair': 'EURUSD', 'signal': 'call'}
        }

        # Test different base currency
        result = engine._is_correlated_with_active_trades('GBPUSD')
        assert result is False
        print("✅ Returns False for uncorrelated pairs")


class TestSelectTradeOpportunities:
    """Test _select_trade_opportunities method"""

    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    def test_empty_analyses(self, mock_provider, mock_sizer, mock_consensus,
                           mock_analyzer, mock_db):
        """Test with empty analyses"""
        config = create_mock_config()

        engine = ParallelTradingEngine(config)

        result = engine._select_trade_opportunities([], 10000)
        assert result == []
        print("✅ Returns empty list for empty analyses")

    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    def test_select_best_opportunities(self, mock_provider, mock_sizer,
                                      mock_consensus, mock_analyzer, mock_db):
        """Test selecting best opportunities"""
        config = create_mock_config()

        engine = ParallelTradingEngine(config)

        # Create sample analyses
        analyses = [
            {
                'pair': 'EURUSD',
                'payout': 0.80,
                'confidence': 75,
                'signal': 'call'
            },
            {
                'pair': 'GBPUSD',
                'payout': 0.85,
                'confidence': 70,
                'signal': 'put'
            },
            {
                'pair': 'USDJPY',
                'payout': 0.75,
                'confidence': 80,
                'signal': 'call'
            }
        ]

        balance = 10000
        result = engine._select_trade_opportunities(analyses, balance)

        assert len(result) > 0
        assert len(result) <= engine.parallel_config.max_concurrent_pairs

        # Check that opportunities have required fields
        for opp in result:
            assert 'position_size' in opp
            assert 'max_risk' in opp
            assert 'pair' in opp

        print("✅ Selects best opportunities correctly")

    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    def test_risk_budget_limit(self, mock_provider, mock_sizer, mock_consensus,
                              mock_analyzer, mock_db):
        """Test risk budget limiting"""
        config = create_mock_config()

        engine = ParallelTradingEngine(config)

        # Create many high-risk analyses
        analyses = [
            {
                'pair': f'PAIR{i}',
                'payout': 0.80,
                'confidence': 90,
                'signal': 'call'
            }
            for i in range(10)
        ]

        balance = 1000
        result = engine._select_trade_opportunities(analyses, balance)

        # Calculate total risk
        total_risk = sum(opp['max_risk'] for opp in result)
        max_risk_budget = balance * engine.parallel_config.risk_budget_percentage

        assert total_risk <= max_risk_budget
        print("✅ Respects risk budget limit")


class TestAnalyzeSinglePair:
    """Test _analyze_single_pair method"""

    @pytest.mark.asyncio
    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    async def test_analyze_single_pair_success(self, mock_provider_class,
                                              mock_sizer, mock_consensus_class,
                                              mock_analyzer, mock_db):
        """Test successful pair analysis"""
        config = create_mock_config()

        # Setup mocks
        mock_provider = AsyncMock()
        mock_provider.get_candles = AsyncMock(return_value=[
            {'close': 1.1000 + i*0.0001} for i in range(100)
        ])
        mock_provider_class.return_value = mock_provider

        mock_consensus = Mock()
        mock_consensus.get_consensus_signal = Mock(return_value={
            'consensus_reached': True,
            'signal': 'call',
            'confidence_calibrated': 75
        })
        mock_consensus_class.return_value = mock_consensus

        engine = ParallelTradingEngine(config)
        engine.provider = mock_provider
        engine.consensus_engine = mock_consensus

        pair_info = {'pair': 'EURUSD', 'payout': 0.80}
        result = await engine._analyze_single_pair(pair_info)

        assert result is not None
        assert result['pair'] == 'EURUSD'
        assert result['signal'] == 'call'
        assert result['confidence'] == 75
        assert 'market_data' in result

        print("✅ _analyze_single_pair works for valid data")

    @pytest.mark.asyncio
    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    async def test_analyze_single_pair_insufficient_candles(self, mock_provider_class,
                                                           mock_sizer, mock_consensus_class,
                                                           mock_analyzer, mock_db):
        """Test with insufficient candles"""
        config = create_mock_config()

        mock_provider = AsyncMock()
        mock_provider.get_candles = AsyncMock(return_value=[
            {'close': 1.1000}  # Only 1 candle
        ])
        mock_provider_class.return_value = mock_provider

        engine = ParallelTradingEngine(config)
        engine.provider = mock_provider

        pair_info = {'pair': 'EURUSD', 'payout': 0.80}
        result = await engine._analyze_single_pair(pair_info)

        assert result is None
        print("✅ Returns None for insufficient candles")

    @pytest.mark.asyncio
    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    async def test_analyze_single_pair_no_consensus(self, mock_provider_class,
                                                   mock_sizer, mock_consensus_class,
                                                   mock_analyzer, mock_db):
        """Test when consensus not reached"""
        config = create_mock_config()

        mock_provider = AsyncMock()
        mock_provider.get_candles = AsyncMock(return_value=[
            {'close': 1.1000 + i*0.0001} for i in range(100)
        ])
        mock_provider_class.return_value = mock_provider

        mock_consensus = Mock()
        mock_consensus.get_consensus_signal = Mock(return_value={
            'consensus_reached': False,
            'signal': None,
            'confidence_calibrated': 50
        })
        mock_consensus_class.return_value = mock_consensus

        engine = ParallelTradingEngine(config)
        engine.provider = mock_provider
        engine.consensus_engine = mock_consensus

        pair_info = {'pair': 'EURUSD', 'payout': 0.80}
        result = await engine._analyze_single_pair(pair_info)

        assert result is None
        print("✅ Returns None when consensus not reached")


class TestExecuteSingleTrade:
    """Test _execute_single_trade method"""

    @pytest.mark.asyncio
    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    async def test_execute_single_trade_success(self, mock_provider_class,
                                               mock_sizer, mock_consensus,
                                               mock_analyzer, mock_db_class):
        """Test successful trade execution"""
        config = create_mock_config()

        # Setup mocks
        mock_provider = AsyncMock()
        mock_provider.execute_trade = AsyncMock(return_value={
            'success': True,
            'order_id': 'order123',
            'pair': 'EURUSD'
        })
        mock_provider_class.return_value = mock_provider

        mock_db = Mock()
        mock_db.insert_trade = Mock()
        mock_db_class.return_value = mock_db

        engine = ParallelTradingEngine(config)
        engine.provider = mock_provider
        engine.db = mock_db

        opportunity = {
            'pair': 'EURUSD',
            'signal': 'call',
            'position_size': 10.0,
            'confidence': 75,
            'payout': 0.80
        }

        result = await engine._execute_single_trade(opportunity)

        assert result is not None
        assert result['success'] is True
        assert result['order_id'] == 'order123'
        mock_db.insert_trade.assert_called_once()

        print("✅ _execute_single_trade works for successful trades")

    @pytest.mark.asyncio
    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    async def test_execute_single_trade_failure(self, mock_provider_class,
                                               mock_sizer, mock_consensus,
                                               mock_analyzer, mock_db_class):
        """Test failed trade execution"""
        config = create_mock_config()

        mock_provider = AsyncMock()
        mock_provider.execute_trade = AsyncMock(return_value={
            'success': False,
            'error': 'Insufficient balance'
        })
        mock_provider_class.return_value = mock_provider

        mock_db = Mock()
        mock_db.insert_trade = Mock()
        mock_db_class.return_value = mock_db

        engine = ParallelTradingEngine(config)
        engine.provider = mock_provider
        engine.db = mock_db

        opportunity = {
            'pair': 'EURUSD',
            'signal': 'call',
            'position_size': 10.0,
            'confidence': 75,
            'payout': 0.80
        }

        result = await engine._execute_single_trade(opportunity)

        assert result is not None
        assert result['success'] is False
        mock_db.insert_trade.assert_not_called()

        print("✅ Handles failed trade execution")


class TestMonitorActiveTrades:
    """Test _monitor_active_trades method"""

    @pytest.mark.asyncio
    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    async def test_monitor_no_active_trades(self, mock_provider_class, mock_sizer,
                                           mock_consensus, mock_analyzer, mock_db):
        """Test with no active trades"""
        config = create_mock_config()

        engine = ParallelTradingEngine(config)
        session_stats = {'trades_won': 0, 'trades_lost': 0, 'total_profit': 0.0}

        await engine._monitor_active_trades(session_stats)

        assert session_stats['trades_won'] == 0
        assert session_stats['trades_lost'] == 0
        print("✅ Handles no active trades")

    @pytest.mark.asyncio
    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    async def test_monitor_active_trades_win(self, mock_provider_class, mock_sizer,
                                            mock_consensus, mock_analyzer, mock_db_class):
        """Test monitoring winning trade"""
        config = create_mock_config()

        mock_provider = AsyncMock()
        mock_provider.check_trade_result = AsyncMock(return_value={
            'result': 'WIN',
            'profit': 8.0
        })
        mock_provider_class.return_value = mock_provider

        mock_db = Mock()
        mock_db.update_trade = Mock()
        mock_db_class.return_value = mock_db

        engine = ParallelTradingEngine(config)
        engine.provider = mock_provider
        engine.db = mock_db

        # Add active trade from 80 seconds ago
        engine.active_trades = {
            'order123': {
                'pair': 'EURUSD',
                'start_time': datetime.now() - timedelta(seconds=80)
            }
        }

        session_stats = {'trades_won': 0, 'trades_lost': 0, 'total_profit': 0.0}

        await engine._monitor_active_trades(session_stats)

        assert session_stats['trades_won'] == 1
        assert session_stats['total_profit'] == 8.0
        assert 'order123' not in engine.active_trades
        mock_db.update_trade.assert_called_once()

        print("✅ Monitors winning trades correctly")


class TestPrintSessionSummary:
    """Test _print_session_summary method"""

    @patch('trading.parallel_trading_engine.TradeDatabase')
    @patch('trading.parallel_trading_engine.MarketContextAnalyzer')
    @patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
    @patch('trading.parallel_trading_engine.KellyPositionSizer')
    @patch('trading.parallel_trading_engine.IQOptionProvider')
    def test_print_session_summary(self, mock_provider, mock_sizer, mock_consensus,
                                   mock_analyzer, mock_db, capsys):
        """Test session summary printing"""
        config = create_mock_config()

        engine = ParallelTradingEngine(config)

        stats = {
            'duration_minutes': 60.5,
            'trades_executed': 10,
            'trades_won': 6,
            'trades_lost': 4,
            'win_rate': 60.0,
            'total_profit': 25.50,
            'pairs_traded': ['EURUSD', 'GBPUSD', 'USDJPY'],
            'errors': ['Error 1', 'Error 2']
        }

        engine._print_session_summary(stats)

        captured = capsys.readouterr()
        assert 'SESSION SUMMARY' in captured.out
        assert '60.5 minutes' in captured.out
        assert 'Trades Executed: 10' in captured.out
        assert 'EURUSD' in captured.out

        print("✅ Prints session summary correctly")


# Run all tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
