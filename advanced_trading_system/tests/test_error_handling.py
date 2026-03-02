"""
Unit tests for error handling in critical path files
Tests specific exception handling, logging, and error recovery
"""
import unittest
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.trade_executor import TradeExecutor
from core.risk_manager import RiskManager
from data_ingestion.market_data_provider import MarketDataProvider
from data_ingestion.connection_manager import ConnectionManager
from models.trade import Trade, TradeResult
from models.state import TradingState


class TestTradeExecutorErrorHandling(unittest.TestCase):
    """Test error handling in TradeExecutor"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_api = Mock()
        self.executor = TradeExecutor(self.mock_api)

        # Capture logs
        self.log_handler = logging.StreamHandler()
        self.log_handler.setLevel(logging.DEBUG)
        logging.basicConfig(handlers=[self.log_handler], level=logging.DEBUG)

    def test_check_market_open_handles_exception(self):
        """Test check_market_open handles API exceptions gracefully"""
        # Simulate API exception
        self.mock_api.get_all_open_time.side_effect = ConnectionError("API unavailable")

        result = self.executor.check_market_open("EURUSD")

        # Should return False instead of crashing
        self.assertFalse(result)

    def test_get_payout_returns_none_on_error(self):
        """Test get_payout returns None on exception"""
        self.mock_api.get_binary_payout.side_effect = TimeoutError("Timeout")

        result = self.executor.get_payout("EURUSD")

        self.assertIsNone(result)

    def test_execute_handles_market_closed(self):
        """Test execute properly handles closed market"""
        # Setup: market is closed
        self.mock_api.get_all_open_time.return_value = {
            'binary': {'EURUSD': {'open': False}}
        }

        trade = Trade(pair='EURUSD', action='call', amount=1.0, duration=1, confidence=80.0)
        result = self.executor.execute(trade)

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, 'MARKET_CLOSED')
        self.assertIn('not open', result.error)

    def test_execute_handles_api_buy_failure(self):
        """Test execute handles buy API failure"""
        # Setup: market open but buy fails
        self.mock_api.get_all_open_time.return_value = {
            'binary': {'EURUSD': {'open': True}}
        }
        self.mock_api.get_balance.return_value = 100.0
        self.mock_api.get_binary_payout.return_value = 0.85
        self.mock_api.buy.return_value = (False, None)  # Buy failed

        trade = Trade(pair='EURUSD', action='call', amount=1.0, duration=1, confidence=80.0)
        result = self.executor.execute(trade)

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, 'EXECUTION_FAILED')

    def test_execute_handles_unexpected_exception(self):
        """Test execute handles unexpected exceptions"""
        # Simulate unexpected error
        self.mock_api.get_all_open_time.side_effect = RuntimeError("Unexpected error")

        trade = Trade(pair='EURUSD', action='call', amount=1.0, duration=1, confidence=80.0)
        result = self.executor.execute(trade)

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, 'EXCEPTION')
        self.assertIn('Unexpected error', result.error)

    def test_wait_for_result_handles_missing_order_id(self):
        """Test wait_for_result handles missing order ID"""
        trade = Trade(pair='EURUSD', action='call', amount=1.0, duration=1, confidence=80.0)
        # No order_id set

        result = self.executor.wait_for_result(trade, max_attempts=1)

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, 'NO_ORDER_ID')

    def test_wait_for_result_handles_check_failures(self):
        """Test wait_for_result handles check_win_v3 failures"""
        trade = Trade(pair='EURUSD', action='call', amount=1.0, duration=1, confidence=80.0)
        trade.order_id = 12345

        # API check always returns None
        self.mock_api.check_win_v3.return_value = None

        with patch('time.sleep'):  # Skip actual sleep
            result = self.executor.wait_for_result(trade, max_attempts=3)

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, 'RESULT_UNAVAILABLE')


class TestRiskManagerErrorHandling(unittest.TestCase):
    """Test error handling in RiskManager"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'MIN_BALANCE': 10.0,
            'MAX_DAILY_LOSS': 50.0,
            'MAX_DAILY_PROFIT': 100.0,
            'MAX_CONSECUTIVE_LOSSES': 3,
            'MAX_MARTINGALE_LEVEL': 3
        }
        self.risk_manager = RiskManager(self.config)

    def test_check_risk_guards_handles_low_balance(self):
        """Test risk guards properly handle low balance"""
        state = TradingState()
        balance = 5.0  # Below MIN_BALANCE

        allowed, reason = self.risk_manager.check_risk_guards(state, balance)

        self.assertFalse(allowed)
        self.assertIn('below minimum', reason)

    def test_check_risk_guards_handles_daily_loss_limit(self):
        """Test risk guards handle daily loss limit"""
        state = TradingState()
        state.daily_loss = 60.0  # Above MAX_DAILY_LOSS
        balance = 100.0

        allowed, reason = self.risk_manager.check_risk_guards(state, balance)

        self.assertFalse(allowed)
        self.assertIn('Daily loss limit', reason)

    def test_check_risk_guards_handles_consecutive_losses(self):
        """Test risk guards handle consecutive losses"""
        state = TradingState()
        state.consecutive_losses = 5  # Above MAX_CONSECUTIVE_LOSSES
        balance = 100.0

        allowed, reason = self.risk_manager.check_risk_guards(state, balance)

        self.assertFalse(allowed)
        self.assertIn('Consecutive losses', reason)

    def test_should_stop_trading_multiple_conditions(self):
        """Test should_stop_trading with various conditions"""
        state = TradingState()

        # Test daily loss
        state.daily_loss = 60.0
        should_stop, reason = self.risk_manager.should_stop_trading(state)
        self.assertTrue(should_stop)
        self.assertIn('Daily loss', reason)

        # Reset and test daily profit
        state = TradingState()
        state.daily_profit = 150.0
        should_stop, reason = self.risk_manager.should_stop_trading(state)
        self.assertTrue(should_stop)
        self.assertIn('Daily profit', reason)


class TestMarketDataProviderErrorHandling(unittest.TestCase):
    """Test error handling in MarketDataProvider"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_connection_manager = Mock(spec=ConnectionManager)
        self.provider = MarketDataProvider(
            self.mock_connection_manager,
            enable_caching=False
        )

    def test_get_candles_handles_no_api(self):
        """Test get_candles handles missing API"""
        self.mock_connection_manager.get_api.return_value = None

        result = self.provider.get_candles('EURUSD')

        self.assertIsNone(result)
        self.assertEqual(self.provider.stats['failed_requests'], 1)

    def test_get_candles_handles_fetch_failure(self):
        """Test get_candles handles fetch failures"""
        mock_api = Mock()
        self.mock_connection_manager.get_api.return_value = mock_api

        # Simulate fetch failure
        mock_api.start_candles_stream.side_effect = ConnectionError("Connection lost")

        result = self.provider.get_candles('EURUSD')

        self.assertIsNone(result)
        self.assertEqual(self.provider.stats['failed_requests'], 1)

    def test_get_candles_handles_insufficient_data(self):
        """Test get_candles handles insufficient data"""
        mock_api = Mock()
        self.mock_connection_manager.get_api.return_value = mock_api

        # Return insufficient candles
        mock_api.get_realtime_candles.return_value = {
            1234567890: {'open': 1.0, 'close': 1.0, 'max': 1.0, 'min': 1.0}
        }

        with patch('time.sleep'):  # Skip sleep
            result = self.provider.get_candles('EURUSD', count=100)

        # Should retry and eventually fail
        self.assertIsNone(result)

    def test_get_market_status_handles_exception(self):
        """Test get_market_status handles exceptions gracefully"""
        mock_api = Mock()
        self.mock_connection_manager.get_api.return_value = mock_api
        mock_api.get_all_open_time.side_effect = RuntimeError("API error")

        result = self.provider.get_market_status('EURUSD')

        # Should return closed status instead of crashing
        self.assertEqual(result, {'binary': False, 'digital': False})

    def test_get_available_assets_handles_exception(self):
        """Test get_available_assets handles exceptions"""
        mock_api = Mock()
        self.mock_connection_manager.get_api.return_value = mock_api
        mock_api.get_all_open_time.side_effect = TimeoutError("Timeout")

        result = self.provider.get_available_assets()

        # Should return empty lists instead of crashing
        self.assertEqual(result, {'binary': [], 'digital': []})


class TestConnectionManagerErrorHandling(unittest.TestCase):
    """Test error handling in ConnectionManager"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = ConnectionManager(
            email="test@example.com",
            password="test_password",
            max_retries=3,
            retry_delay=1
        )

    @patch('data_ingestion.connection_manager.IQ_Option')
    def test_connect_handles_import_error(self, mock_iq_option):
        """Test connect handles import errors"""
        # Simulate import failure by raising ImportError
        with patch.dict('sys.modules', {'iqoptionapi.stable_api': None}):
            success, message = self.manager.connect()

            # Should handle gracefully
            self.assertFalse(success)
            self.assertIn("not installed", message)

    @patch('data_ingestion.connection_manager.IQ_Option')
    def test_connect_handles_connection_failure(self, mock_iq_option):
        """Test connect handles connection failures"""
        mock_api_instance = Mock()
        mock_api_instance.connect.return_value = (False, "Invalid credentials")
        mock_iq_option.return_value = mock_api_instance

        with patch('time.sleep'):  # Skip sleep
            success, message = self.manager.connect()

        self.assertFalse(success)
        self.assertIn("Max retries", message)

    @patch('data_ingestion.connection_manager.IQ_Option')
    def test_connect_handles_balance_retrieval_failure(self, mock_iq_option):
        """Test connect handles balance retrieval failure"""
        mock_api_instance = Mock()
        mock_api_instance.connect.return_value = (True, "Connected")
        mock_api_instance.get_balance.return_value = None  # Balance retrieval fails
        mock_iq_option.return_value = mock_api_instance

        with patch('time.sleep'):  # Skip sleep
            success, message = self.manager.connect()

        self.assertFalse(success)

    def test_verify_connection_handles_missing_api(self):
        """Test _verify_connection handles missing API"""
        self.manager.api = None

        result = self.manager._verify_connection()

        self.assertFalse(result)

    def test_ensure_connected_reconnects_on_failure(self):
        """Test ensure_connected attempts reconnection"""
        self.manager.connected = False

        with patch.object(self.manager, 'connect') as mock_connect:
            mock_connect.return_value = (True, "Connected")

            result = self.manager.ensure_connected()

            mock_connect.assert_called_once()

    def test_get_balance_handles_exception(self):
        """Test get_balance handles exceptions"""
        mock_api = Mock()
        mock_api.get_balance.side_effect = RuntimeError("API error")
        self.manager.api = mock_api
        self.manager.connected = True

        result = self.manager.get_balance()

        # Should return None instead of crashing
        self.assertIsNone(result)


class TestMainPyErrorHandling(unittest.TestCase):
    """Test error handling in main.py RobustTradingSystem"""

    def setUp(self):
        """Set up test fixtures"""
        # We'll test the specific methods we fixed
        pass

    @patch('main.TradingConfig')
    @patch('main.TradeDatabase')
    @patch('main.TechnicalIndicators')
    @patch('main.MarketContextAnalyzer')
    def test_check_connection_health_handles_connection_error(self, mock_analyzer, mock_indicators, mock_db, mock_config):
        """Test check_connection_health handles ConnectionError"""
        from main import RobustTradingSystem

        mock_config.DB_PATH = 'test.db'
        mock_config.USE_OPENAI = False
        mock_config.USE_CLAUDE = False
        mock_config.USE_DEEPSEEK = False
        mock_config.USE_FREE_AI = False

        system = RobustTradingSystem(mock_config)

        # Mock API that raises ConnectionError
        mock_api = Mock()
        mock_api.get_balance.side_effect = ConnectionError("Connection lost")
        system.api = mock_api

        result = system.check_connection_health()

        # Should return False and log warning
        self.assertFalse(result)

    @patch('main.TradingConfig')
    @patch('main.TradeDatabase')
    @patch('main.TechnicalIndicators')
    @patch('main.MarketContextAnalyzer')
    def test_check_connection_health_handles_timeout(self, mock_analyzer, mock_indicators, mock_db, mock_config):
        """Test check_connection_health handles TimeoutError"""
        from main import RobustTradingSystem

        mock_config.DB_PATH = 'test.db'
        mock_config.USE_OPENAI = False
        mock_config.USE_CLAUDE = False
        mock_config.USE_DEEPSEEK = False
        mock_config.USE_FREE_AI = False

        system = RobustTradingSystem(mock_config)

        # Mock API that raises TimeoutError
        mock_api = Mock()
        mock_api.get_balance.side_effect = TimeoutError("Request timeout")
        system.api = mock_api

        result = system.check_connection_health()

        # Should return False and log warning
        self.assertFalse(result)


def run_tests():
    """Run all error handling tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTradeExecutorErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskManagerErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestMarketDataProviderErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionManagerErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestMainPyErrorHandling))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_tests()

    # Print summary
    print("\n" + "="*70)
    print("ERROR HANDLING TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
