"""
Pytest configuration and fixtures for KAEL Trading System tests
"""
import os
import sys
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Add advanced_trading_system to path
sys.path.insert(0, str(Path(__file__).parent.parent / "advanced_trading_system"))

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session")
def trading_config():
    """Load trading configuration from environment"""
    return {
        'iqoption_email': os.getenv('IQOPTION_EMAIL'),
        'iqoption_password': os.getenv('IQOPTION_PASSWORD'),
        'trading_mode': os.getenv('TRADING_MODE', 'demo'),
        'anthropic_key': os.getenv('ANTHROPIC_API_KEY'),
        'openai_key': os.getenv('OPENAI_API_KEY'),
        'deepseek_key': os.getenv('DEEPSEEK_API_KEY'),
    }


@pytest.fixture(scope="session")
def verify_demo_mode():
    """Ensure we're in demo mode for integration tests"""
    mode = os.getenv('TRADING_MODE', 'demo')
    if mode != 'demo':
        pytest.fail(
            "Integration tests must run in DEMO mode! "
            "Set TRADING_MODE=demo in .env file"
        )
    return True


@pytest.fixture(scope="session")
def check_credentials(trading_config):
    """Check that required credentials are set"""
    if not trading_config['iqoption_email']:
        pytest.skip("IQOPTION_EMAIL not set in .env")
    if not trading_config['iqoption_password']:
        pytest.skip("IQOPTION_PASSWORD not set in .env")
    return True


def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (requires real API credentials)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (trade execution, waiting for results)"
    )
    config.addinivalue_line(
        "markers", "ai: AI model tests (requires API keys)"
    )
    config.addinivalue_line(
        "markers", "data: Data ingestion tests"
    )
    config.addinivalue_line(
        "markers", "trading: Trading execution tests"
    )
    config.addinivalue_line(
        "markers", "demo_only: Tests that must run in DEMO mode only"
    )
