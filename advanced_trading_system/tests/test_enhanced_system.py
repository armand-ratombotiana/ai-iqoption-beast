"""
Comprehensive Test Suite for Enhanced Trading System
Property-based testing, performance benchmarks, and integration tests
"""
import pytest
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import hypothesis
from hypothesis import strategies as st
import time
from typing import Dict, List

# Import system components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.enhanced_settings import EnhancedTradingConfig
from data_providers.multi_provider import MultiDataProvider
from ai_models.ensemble_model import EnsembleModel
from backtesting.backtesting_engine import BacktestingEngine, BacktestConfig
from risk_management.portfolio_risk_manager import PortfolioRiskManager, Position
from api.main import app
from fastapi.testclient import TestClient


class TestEnhancedTradingSystem:
    """Comprehensive test suite for the enhanced trading system"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return EnhancedTradingConfig(
            environment="test",
            debug=True,
            email="test@example.com",
            password="test_password"
        )
    
    @pytest.fixture
    def sample_market_data(self):
        """Sample market data for testing"""
        return {
            'pair': 'EURUSD-OTC',
            'current_price': 1.0850,
            'rsi_14': 65.5,
            'rsi_7': 70.2,
            'macd': {'macd': 0.0012, 'signal': 0.0008, 'histogram': 0.0004},
            'bb_position': 0.75,
            'stochastic': {'k': 68.5, 'd': 65.2},
            'adx': 45.2,
            'atr': 0.0015,
            'cci': 120.5,
            'williams_r': -25.8,
            'trend': 'uptrend',
            'volatility': 'medium',
            'volatility_value': 1.2,
            'support': 1.0820,
            'resistance': 1.0880,
            'hour': 14,
            'day_of_week': 2
        }
    
    @pytest.fixture
    def sample_candles(self):
        """Sample candle data for testing"""
        candles = []
        base_price = 1.0850
        
        for i in range(100):
            # Random walk
            change = np.random.normal(0, 0.0005)
            base_price += change
            
            candle = {
                'timestamp': (datetime.now() - timedelta(minutes=100-i)).isoformat(),
                'open': base_price,
                'high': base_price + abs(np.random.normal(0, 0.0003)),
                'low': base_price - abs(np.random.normal(0, 0.0003)),
                'close': base_price + np.random.normal(0, 0.0002),
                'volume': np.random.uniform(1000, 5000)
            }
            candles.append(candle)
        
        return candles


class TestConfiguration:
    """Test configuration management"""
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid configuration
        config = EnhancedTradingConfig(
            email="test@example.com",
            password="test_password"
        )
        config.setup_ai_models()
        
        errors = config.validate()
        assert len(errors) >= 3  # Should have errors for missing API keys
    
    def test_config_from_env(self):
        """Test loading configuration from environment"""
        with patch.dict('os.environ', {
            'IQOPTION_EMAIL': 'test@example.com',
            'IQOPTION_PASSWORD': 'test_password',
            'OPENAI_API_KEY': 'test_key'
        }):
            config = EnhancedTradingConfig.load_from_env()
            assert config.email == 'test@example.com'
            assert config.password == 'test_password'
    
    def test_config_display(self, capsys):
        """Test configuration display"""
        config = EnhancedTradingConfig(
            email="test@example.com",
            password="test_password"
        )
        config.display()
        
        captured = capsys.readouterr()
        assert "ENHANCED TRADING SYSTEM CONFIGURATION" in captured.out
        assert "test@example.com" in captured.out


class TestDataProviders:
    """Test data provider functionality"""
    
    @pytest.mark.asyncio
    async def test_multi_provider_initialization(self):
        """Test multi-provider initialization"""
        provider = MultiDataProvider("redis://localhost:6379")
        
        # Mock Redis connection
        with patch('aioredis.from_url') as mock_redis:
            mock_redis.return_value.ping = AsyncMock()
            await provider.initialize()
            
            assert provider.redis is not None
    
    @pytest.mark.asyncio
    async def test_consensus_price_calculation(self):
        """Test consensus price calculation"""
        provider = MultiDataProvider("redis://localhost:6379")
        
        # Mock provider prices
        mock_prices = {
            'provider1': 1.0850,
            'provider2': 1.0852,
            'provider3': 1.0851
        }
        
        consensus = provider._calculate_price_consensus(mock_prices)
        
        assert consensus is not None
        assert 1.0850 <= consensus['price'] <= 1.0852
        assert consensus['sources'] == 3
        assert consensus['confidence'] > 0
    
    @pytest.mark.asyncio
    async def test_provider_health_monitoring(self):
        """Test provider health monitoring"""
        provider = MultiDataProvider("redis://localhost:6379")
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.provider_name = "test_provider"
        mock_provider.health_check = AsyncMock(return_value={
            'status': 'healthy',
            'provider': 'test_provider'
        })
        
        await provider.add_provider(mock_provider, weight=1.0)
        health_results = await provider.health_check_all()
        
        assert 'test_provider' in health_results
        assert health_results['test_provider']['status'] == 'healthy'


class TestAIModels:
    """Test AI model functionality"""
    
    def test_ensemble_model_initialization(self):
        """Test ensemble model initialization"""
        model = EnsembleModel()
        
        assert len(model.base_models) > 0
        assert model.meta_learner is not None
        assert len(model.feature_names) > 0
    
    def test_feature_engineering(self, sample_market_data):
        """Test feature engineering"""
        model = EnsembleModel()
        features = model.engineer_features(sample_market_data)
        
        assert len(features) == len(model.feature_names)
        assert all(isinstance(f, (int, float, np.number)) for f in features)
        assert not any(np.isnan(features))
    
    @pytest.mark.asyncio
    async def test_ensemble_prediction(self, sample_market_data):
        """Test ensemble prediction without training"""
        model = EnsembleModel()
        
        # Mock trained state
        model.is_trained = True
        model.feature_scaler.fit([[0] * len(model.feature_names)])
        
        # Mock base model predictions
        for name, base_model in model.base_models.items():
            base_model.predict = Mock(return_value=[1])  # CALL
            base_model.predict_proba = Mock(return_value=[[0.2, 0.7, 0.1]])
        
        prediction = await model.predict_async(sample_market_data)
        
        assert prediction['signal'] in ['CALL', 'PUT', 'NEUTRAL']
        assert 0 <= prediction['confidence'] <= 100
        assert 'reasoning' in prediction
    
    @hypothesis.given(
        rsi=st.floats(min_value=0, max_value=100),
        price=st.floats(min_value=0.5, max_value=2.0),
        confidence=st.integers(min_value=0, max_value=100)
    )
    def test_feature_engineering_properties(self, rsi, price, confidence):
        """Property-based testing for feature engineering"""
        model = EnsembleModel()
        
        market_data = {
            'rsi_14': rsi,
            'current_price': price,
            'confidence': confidence,
            'trend': 'uptrend',
            'volatility': 'medium'
        }
        
        features = model.engineer_features(market_data)
        
        # Properties that should always hold
        assert len(features) == len(model.feature_names)
        assert all(np.isfinite(f) for f in features)
        assert features[0] == rsi / 100  # RSI should be normalized


class TestBacktesting:
    """Test backtesting functionality"""
    
    def test_backtest_config_validation(self):
        """Test backtest configuration validation"""
        config = BacktestConfig(
            initial_balance=10000,
            base_amount=2.0,
            min_amount=1.0,
            max_amount=20.0
        )
        
        assert config.initial_balance == 10000
        assert config.max_amount > config.min_amount
    
    def test_backtest_engine_initialization(self):
        """Test backtest engine initialization"""
        config = BacktestConfig()
        engine = BacktestingEngine(config)
        
        assert engine.config == config
        assert engine.balance == config.initial_balance
        assert len(engine.trades) == 0
    
    def test_market_data_calculation(self, sample_candles):
        """Test market data calculation in backtesting"""
        config = BacktestConfig()
        engine = BacktestingEngine(config)
        
        # Convert to pandas Series format
        current_candle = pd.Series({
            'timestamp': datetime.now().isoformat(),
            'close': 1.0850,
            'high': 1.0860,
            'low': 1.0840,
            'volume': 2000
        })
        
        market_data = engine._calculate_market_data(sample_candles, current_candle)
        
        assert 'rsi_14' in market_data
        assert 'macd' in market_data
        assert 'trend' in market_data
        assert market_data['current_price'] == 1.0850
    
    def test_risk_management_checks(self):
        """Test risk management in backtesting"""
        config = BacktestConfig(max_daily_loss=100.0)
        engine = BacktestingEngine(config)
        
        # Simulate daily loss
        from datetime import date
        today = date.today()
        engine.daily_pnl[today] = -150.0  # Exceeds limit
        
        # Should reject new trades
        allowed = engine._check_risk_management(datetime.now().isoformat())
        assert not allowed


class TestRiskManagement:
    """Test risk management functionality"""
    
    def test_portfolio_risk_manager_initialization(self):
        """Test portfolio risk manager initialization"""
        config = {'max_portfolio_risk': 0.05}
        manager = PortfolioRiskManager(config)
        
        assert manager.config == config
        assert len(manager.positions) == 0
        assert manager.max_portfolio_risk == 0.05
    
    def test_position_validation(self):
        """Test position validation"""
        config = {
            'max_single_position': 0.02,
            'max_pair_exposure': 0.10
        }
        manager = PortfolioRiskManager(config)
        
        # Add a position that should be valid
        position = Position(
            position_id="test_1",
            pair="EURUSD-OTC",
            direction="CALL",
            amount=100.0,
            entry_price=1.0850,
            entry_time=datetime.now(),
            duration=1
        )
        
        # Should be valid for empty portfolio
        assert manager._validate_new_position(position)
    
    def test_concentration_risk_calculation(self):
        """Test concentration risk calculation"""
        config = {}
        manager = PortfolioRiskManager(config)
        
        # Add positions with different concentrations
        positions = [
            Position("1", "EURUSD-OTC", "CALL", 500, 1.0850, datetime.now(), 1),
            Position("2", "EURUSD-OTC", "PUT", 300, 1.0860, datetime.now(), 1),
            Position("3", "GBPUSD-OTC", "CALL", 200, 1.2500, datetime.now(), 1)
        ]
        
        for pos in positions:
            manager.positions[pos.position_id] = pos
        
        concentration_risk = manager._calculate_concentration_risk()
        
        # Should be between 0 and 1
        assert 0 <= concentration_risk <= 1
        # Should be higher than perfectly diversified portfolio
        assert concentration_risk > 0.33  # 1/3 for 3 equal positions
    
    @pytest.mark.asyncio
    async def test_risk_monitoring_loop(self):
        """Test risk monitoring loop"""
        config = {}
        manager = PortfolioRiskManager(config)
        
        # Mock the risk calculation
        manager.calculate_portfolio_risk = AsyncMock(return_value=Mock(
            overall_risk_level=Mock(),
            var_95=0,
            concentration_risk=0.3,
            correlation_risk=0.2
        ))
        manager.check_risk_violations = Mock(return_value=[])
        
        # Start monitoring briefly
        await manager.start_monitoring()
        await asyncio.sleep(0.1)  # Let it run briefly
        await manager.stop_monitoring()
        
        # Should have called risk calculation
        manager.calculate_portfolio_risk.assert_called()


class TestAPI:
    """Test API functionality"""
    
    @pytest.fixture
    def client(self):
        """Test client for API"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data
    
    def test_system_status(self, client):
        """Test system status endpoint"""
        response = client.get("/api/v1/system/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "total_trades" in data
        assert "win_rate" in data
    
    def test_market_data_endpoint(self, client):
        """Test market data endpoint"""
        # This will fail without proper setup, but tests the endpoint structure
        response = client.get("/api/v1/market/data/EURUSD-OTC")
        
        # Should return 503 (service unavailable) due to no data provider
        assert response.status_code == 503
    
    def test_trade_execution_validation(self, client):
        """Test trade execution validation"""
        # Test invalid trade request
        invalid_trade = {
            "pair": "INVALID-PAIR",
            "direction": "CALL",
            "amount": -10  # Invalid negative amount
        }
        
        response = client.post(
            "/api/v1/trades/execute",
            json=invalid_trade,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should return validation error
        assert response.status_code in [400, 422]  # Bad request or validation error
    
    def test_configuration_endpoint(self, client):
        """Test configuration endpoint"""
        response = client.get("/api/v1/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "environment" in data
        assert "account_type" in data
        assert "base_amount" in data


class TestPerformance:
    """Performance and benchmark tests"""
    
    def test_feature_engineering_performance(self, sample_market_data):
        """Test feature engineering performance"""
        model = EnsembleModel()
        
        # Benchmark feature engineering
        start_time = time.time()
        
        for _ in range(1000):
            features = model.engineer_features(sample_market_data)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 1000
        
        # Should be fast (less than 1ms per call)
        assert avg_time < 0.001
        print(f"Feature engineering: {avg_time*1000:.2f}ms per call")
    
    @pytest.mark.asyncio
    async def test_async_model_performance(self, sample_market_data):
        """Test async model performance"""
        model = EnsembleModel()
        model.is_trained = True
        model.feature_scaler.fit([[0] * len(model.feature_names)])
        
        # Mock predictions
        for base_model in model.base_models.values():
            base_model.predict = Mock(return_value=[1])
            base_model.predict_proba = Mock(return_value=[[0.2, 0.7, 0.1]])
        
        # Benchmark async predictions
        start_time = time.time()
        
        tasks = []
        for _ in range(100):
            tasks.append(model.predict_async(sample_market_data))
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        # Should be reasonably fast
        assert avg_time < 0.1  # Less than 100ms per prediction
        assert len(results) == 100
        print(f"Async prediction: {avg_time*1000:.2f}ms per call")
    
    def test_risk_calculation_performance(self):
        """Test risk calculation performance"""
        config = {}
        manager = PortfolioRiskManager(config)
        
        # Add many positions
        for i in range(100):
            position = Position(
                position_id=f"test_{i}",
                pair=f"PAIR{i%10}-OTC",
                direction="CALL" if i % 2 == 0 else "PUT",
                amount=100.0,
                entry_price=1.0 + (i * 0.0001),
                entry_time=datetime.now(),
                duration=1
            )
            manager.positions[position.position_id] = position
        
        # Add some historical P&L
        manager.historical_pnl = list(np.random.normal(0, 10, 100))
        
        # Benchmark risk calculation
        start_time = time.time()
        
        for _ in range(10):
            # This is async, so we'll test the sync parts
            concentration_risk = manager._calculate_concentration_risk()
            max_drawdown = manager._calculate_max_drawdown()
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        
        # Should be reasonably fast even with many positions
        assert avg_time < 0.1  # Less than 100ms
        print(f"Risk calculation: {avg_time*1000:.2f}ms per call")


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_trading_workflow(self, sample_market_data):
        """Test complete trading workflow integration"""
        # This is a simplified integration test
        
        # 1. Initialize components
        config = EnhancedTradingConfig(
            environment="test",
            email="test@example.com",
            password="test_password"
        )
        
        # 2. Create AI model
        model = EnsembleModel()
        model.is_trained = True
        model.feature_scaler.fit([[0] * len(model.feature_names)])
        
        # Mock predictions
        for base_model in model.base_models.values():
            base_model.predict = Mock(return_value=[1])  # CALL
            base_model.predict_proba = Mock(return_value=[[0.2, 0.7, 0.1]])
        
        # 3. Get prediction
        prediction = await model.predict_async(sample_market_data)
        
        # 4. Validate prediction
        assert prediction['signal'] in ['CALL', 'PUT', 'NEUTRAL']
        assert 0 <= prediction['confidence'] <= 100
        
        # 5. Risk management check
        risk_manager = PortfolioRiskManager({})
        
        position = Position(
            position_id="integration_test",
            pair=sample_market_data['pair'],
            direction=prediction['signal'],
            amount=100.0,
            entry_price=sample_market_data['current_price'],
            entry_time=datetime.now(),
            duration=1
        )
        
        # Should be able to add position
        can_add = risk_manager.add_position(position)
        assert can_add
        
        # 6. Portfolio summary
        summary = risk_manager.get_portfolio_summary()
        assert summary['total_positions'] == 1
        assert summary['total_exposure'] == 100.0
    
    def test_error_handling_integration(self):
        """Test error handling across components"""
        # Test configuration errors
        config = EnhancedTradingConfig()
        errors = config.validate()
        assert len(errors) > 0  # Should have validation errors
        
        # Test model errors
        model = EnsembleModel()
        
        # Should handle invalid market data gracefully
        invalid_data = {"invalid": "data"}
        
        # Should not crash, should return neutral prediction
        try:
            features = model.engineer_features(invalid_data)
            assert len(features) == len(model.feature_names)
        except Exception as e:
            # Should handle gracefully
            assert isinstance(e, (KeyError, TypeError, ValueError))


# Property-based testing examples
class TestPropertyBased:
    """Property-based testing with Hypothesis"""
    
    @hypothesis.given(
        balance=st.floats(min_value=100, max_value=100000),
        amount=st.floats(min_value=1, max_value=1000),
        confidence=st.integers(min_value=0, max_value=100)
    )
    def test_position_sizing_properties(self, balance, amount, confidence):
        """Test position sizing properties"""
        # Position size should never exceed balance
        effective_amount = min(amount, balance)
        assert effective_amount <= balance
        
        # Confidence-based sizing should be proportional
        confidence_factor = confidence / 100
        adjusted_amount = effective_amount * confidence_factor
        assert 0 <= adjusted_amount <= effective_amount
    
    @hypothesis.given(
        prices=st.lists(
            st.floats(min_value=0.5, max_value=2.0), 
            min_size=2, 
            max_size=10
        )
    )
    def test_consensus_price_properties(self, prices):
        """Test consensus price calculation properties"""
        provider = MultiDataProvider("redis://localhost:6379")
        
        # Create mock price dictionary
        price_dict = {f"provider_{i}": price for i, price in enumerate(prices)}
        
        consensus = provider._calculate_price_consensus(price_dict)
        
        if consensus:
            # Consensus price should be within the range of input prices
            assert min(prices) <= consensus['price'] <= max(prices)
            
            # Sources should match input count
            assert consensus['sources'] == len(prices)
            
            # Confidence should be between 0 and 1
            assert 0 <= consensus['confidence'] <= 1


# Fixtures for test data
@pytest.fixture(scope="session")
def sample_historical_data():
    """Generate sample historical data for testing"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='1min')
    
    data = []
    price = 1.0850
    
    for date in dates[:1000]:  # Limit to 1000 samples for testing
        # Random walk
        change = np.random.normal(0, 0.0005)
        price += change
        
        data.append({
            'timestamp': date.isoformat(),
            'open': price,
            'high': price + abs(np.random.normal(0, 0.0003)),
            'low': price - abs(np.random.normal(0, 0.0003)),
            'close': price + np.random.normal(0, 0.0002),
            'volume': np.random.uniform(1000, 5000)
        })
    
    return data


# Test configuration
pytest_plugins = ["pytest_asyncio"]


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--hypothesis-show-statistics"
    ])