# 🧪 KAEL Trading System - Comprehensive Testing Guide

## 📋 Overview

This guide covers all testing procedures for the KAEL trading system, including setup, execution, and interpretation of results.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 2. Set Up Credentials

```bash
# Interactive credential setup
python3 setup_credentials.py
```

Or manually create `.env` file:

```bash
# Copy template
cp .env.production.example .env

# Edit with your credentials
nano .env
```

**Required credentials:**
- `IQOPTION_EMAIL` - Your IQ Option email
- `IQOPTION_PASSWORD` - Your IQ Option password
- `ANTHROPIC_API_KEY` - For Claude AI (optional)
- `OPENAI_API_KEY` - For OpenAI models (optional)
- `DEEPSEEK_API_KEY` - For DeepSeek models (optional)

**⚠️ CRITICAL**: Set `TRADING_MODE=demo` for all tests!

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test category
pytest tests/integration/test_01_connection.py -v

# Run with coverage
pytest tests/ --cov=advanced_trading_system --cov-report=html
```

---

## 📂 Test Structure

```
tests/
├── conftest.py                          # Pytest configuration
├── unit/                                # Unit tests (no API calls)
│   ├── test_config.py
│   ├── test_risk_manager.py
│   ├── test_position_sizer.py
│   └── test_technical_indicators.py
└── integration/                         # Integration tests (real API)
    ├── test_01_connection.py           # ✅ IQ Option connection
    ├── test_02_data_ingestion.py       # ✅ Market data fetching
    ├── test_03_technical_indicators.py # 📊 Technical analysis
    ├── test_04_ai_models.py            # 🤖 AI model testing
    ├── test_05_consensus_engine.py     # 🧠 AI consensus
    ├── test_06_risk_management.py      # 🛡️ Risk controls
    ├── test_07_trade_execution.py      # 💰 Trade execution
    └── test_08_end_to_end.py           # 🔄 Full cycle test
```

---

## 🧪 Test Categories

### Category 1: Connection Tests ✅

**File**: `tests/integration/test_01_connection.py`

**Purpose**: Verify IQ Option API connectivity

**Tests**:
- ✅ Basic connection to IQ Option
- ✅ Balance retrieval
- ✅ Reconnection capability

**Run**:
```bash
pytest tests/integration/test_01_connection.py -v -s
```

**Expected Output**:
```
TEST 1.1: IQ Option API Connection
📡 Connecting to IQ Option...
   Email: your@email.com
   Mode: DEMO
   ✅ Connection successful!

TEST 1.2: Retrieve Account Balance
💰 Switching to DEMO account...
   Balance: $10000.00
   ✅ Balance retrieved successfully: $10000.00

TEST 1.3: Reconnection Test
🔌 First connection...
   ✅ First connection successful
🔌 Disconnecting...
   ✅ Disconnected
🔌 Reconnecting...
   ✅ Reconnection successful
```

---

### Category 2: Data Ingestion Tests 📊

**File**: `tests/integration/test_02_data_ingestion.py`

**Purpose**: Test market data fetching and validation

**Tests**:
- ✅ Connection Manager
- ✅ Market Data Provider
- ✅ Real-time price data
- ✅ Data validation
- ✅ Payout rates

**Run**:
```bash
pytest tests/integration/test_02_data_ingestion.py -v -s
```

**Expected Output**:
```
TEST 2.1: Connection Manager
🔌 Testing ConnectionManager...
   Connecting...
   ✅ Connection successful
   ✅ Connection status verified
   Balance: $10000.00
   ✅ Balance retrieved
   ✅ Disconnected successfully

TEST 2.2: Market Data Provider
📊 Testing MarketDataProvider...
   Getting available assets...
   ✅ Found 42 available assets
   First 10: ['EURUSD', 'GBPUSD', 'USDJPY', ...]

   Fetching candles for EURUSD...
   ✅ Retrieved 100 candles for EURUSD
   ✅ Candle structure validated
```

---

### Category 3: Technical Indicators Tests 📈

**File**: `tests/integration/test_03_technical_indicators.py`

**Purpose**: Test technical analysis calculations

**Tests**:
- RSI calculation
- MACD calculation
- Bollinger Bands
- Moving averages
- Volume analysis

**Run**:
```bash
pytest tests/integration/test_03_technical_indicators.py -v -s
```

---

### Category 4: AI Model Tests 🤖

**File**: `tests/integration/test_04_ai_models.py`

**Purpose**: Test individual AI models with real data

**Tests**:
- Claude model prediction
- OpenAI model prediction
- DeepSeek model prediction
- LSTM model training & prediction
- Signal validation

**Requirements**:
- `ANTHROPIC_API_KEY` for Claude
- `OPENAI_API_KEY` for OpenAI
- `DEEPSEEK_API_KEY` for DeepSeek

**Run**:
```bash
pytest tests/integration/test_04_ai_models.py -v -s -m ai
```

---

### Category 5: Consensus Engine Tests 🧠

**File**: `tests/integration/test_05_consensus_engine.py`

**Purpose**: Test multi-model AI consensus

**Tests**:
- Consensus calculation
- Agreement threshold
- Confidence weighting
- Signal generation

**Run**:
```bash
pytest tests/integration/test_05_consensus_engine.py -v -s
```

---

### Category 6: Risk Management Tests 🛡️

**File**: `tests/integration/test_06_risk_management.py`

**Purpose**: Test risk control mechanisms

**Tests**:
- Daily loss limit
- Daily profit limit
- Consecutive loss protection
- Position sizing
- Balance validation
- Rate limiting

**Run**:
```bash
pytest tests/integration/test_06_risk_management.py -v -s
```

---

### Category 7: Trade Execution Tests 💰

**File**: `tests/integration/test_07_trade_execution.py`

**Purpose**: Test actual trade execution (DEMO mode)

**Tests**:
- Single trade execution
- Trade result checking
- Win/loss tracking
- Profit/loss calculation

**⚠️ WARNING**: This executes real trades on DEMO account!

**Run**:
```bash
pytest tests/integration/test_07_trade_execution.py -v -s -m "trading and demo_only"
```

**Expected Duration**: ~2-3 minutes per trade (60s execution + buffer)

---

### Category 8: End-to-End Tests 🔄

**File**: `tests/integration/test_08_end_to_end.py`

**Purpose**: Test complete trading cycle

**Tests**:
1. Connect to broker
2. Fetch market data
3. Calculate indicators
4. Get AI signal
5. Validate signal
6. Check risk limits
7. Execute trade (DEMO)
8. Wait for result
9. Update statistics

**Run**:
```bash
pytest tests/integration/test_08_end_to_end.py -v -s -m "slow and demo_only"
```

---

## 🎯 Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Integration Tests Only
```bash
pytest tests/integration/ -v -s
```

### Run Specific Test File
```bash
pytest tests/integration/test_01_connection.py -v -s
```

### Run by Marker
```bash
# Run only fast unit tests
pytest -m unit -v

# Run integration tests
pytest -m integration -v

# Run data ingestion tests
pytest -m data -v

# Run AI model tests
pytest -m ai -v

# Run trading tests (DEMO only)
pytest -m "trading and demo_only" -v
```

### Run with Coverage
```bash
pytest tests/ --cov=advanced_trading_system --cov-report=html
# View coverage: open htmlcov/index.html
```

### Run Verbose Output
```bash
pytest tests/ -v -s
# -v: verbose
# -s: show print statements
```

---

## 📊 Interpreting Results

### Success Example
```
tests/integration/test_01_connection.py::test_iqoption_connection PASSED  [33%]
tests/integration/test_01_connection.py::test_get_balance PASSED       [66%]
tests/integration/test_01_connection.py::test_reconnection PASSED      [100%]

========================== 3 passed in 15.23s ===========================
```

### Failure Example
```
tests/integration/test_01_connection.py::test_iqoption_connection FAILED [33%]
FAILED: Connection failed: Invalid credentials

Fix: Check IQOPTION_EMAIL and IQOPTION_PASSWORD in .env
```

### Skip Example
```
tests/integration/test_04_ai_models.py::test_claude_model SKIPPED
SKIPPED: ANTHROPIC_API_KEY not set in .env
```

---

## ⚙️ Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests advanced_trading_system/tests
markers =
    unit: Unit tests
    integration: Integration tests (requires credentials)
    slow: Slow tests (trade execution)
    ai: AI model tests
    data: Data ingestion tests
    trading: Trading execution tests
    demo_only: Must run in DEMO mode
```

### conftest.py

Provides fixtures:
- `trading_config` - Configuration from .env
- `verify_demo_mode` - Ensures DEMO mode for integration tests
- `check_credentials` - Validates credentials are set

---

## 🐛 Troubleshooting

### Issue: Connection Failed

**Error**: `Connection failed: Invalid credentials`

**Solution**:
1. Check `.env` file exists
2. Verify `IQOPTION_EMAIL` and `IQOPTION_PASSWORD`
3. Try logging in manually to IQ Option website
4. Check for typos in credentials

### Issue: No Assets Available

**Error**: `No assets available`

**Solution**:
1. Check market hours (forex markets closed on weekends)
2. Try different times of day
3. Verify account is in DEMO mode
4. Check internet connection

### Issue: AI Model Tests Skipped

**Error**: `ANTHROPIC_API_KEY not set`

**Solution**:
1. Add API key to `.env` file
2. Get key from https://console.anthropic.com/
3. Verify key is valid

### Issue: Trade Execution Failed

**Error**: `Insufficient balance`

**Solution**:
1. Check demo account balance
2. Reduce `BASE_TRADE_AMOUNT` in .env
3. Verify trading mode is DEMO

---

## 📈 Coverage Report

Generate coverage report:

```bash
pytest tests/ --cov=advanced_trading_system --cov-report=html
```

View report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Target Coverage**: >80% for critical components

---

## ✅ Pre-Deployment Checklist

Before deploying to production:

- [ ] All connection tests pass
- [ ] All data ingestion tests pass
- [ ] Technical indicators calculated correctly
- [ ] AI models generating signals
- [ ] Consensus engine working
- [ ] Risk management enforced
- [ ] Trade execution tested on DEMO
- [ ] End-to-end cycle successful
- [ ] Coverage >80%
- [ ] No critical warnings
- [ ] All logs clean
- [ ] Documentation updated

---

## 🚨 Safety Reminders

1. **ALWAYS** use DEMO mode for testing
2. **NEVER** commit .env file to git
3. **VERIFY** trading mode before each test run
4. **MONITOR** test execution closely
5. **REVIEW** all test results before production
6. **START** with small trade amounts
7. **TEST** thoroughly before live trading

---

## 📞 Support

If tests fail or you encounter issues:

1. Check this guide's troubleshooting section
2. Review test output carefully
3. Check `.env` configuration
4. Verify API credentials
5. Check market hours
6. Review logs in `logs/` directory

---

**Last Updated**: 2025-10-23
**Test Suite Version**: 1.0.0
**Status**: Ready for Testing
