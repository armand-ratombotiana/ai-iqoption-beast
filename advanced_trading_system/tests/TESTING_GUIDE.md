# Testing Guide for Parallel Trading Engine

## Quick Start

```bash
cd /app/app/KAEL/KAEL/advanced_trading_system/tests
python -m pytest test_parallel_trading_engine.py -v
```

## Test File Structure

```
tests/
├── test_parallel_trading_engine.py  # Main test file (20 tests)
├── TEST_RESULTS_PARALLEL_ENGINE.md  # Detailed results
└── TESTING_GUIDE.md                 # This file
```

## Test Organization

### 1. Helper Functions
```python
def create_mock_config()
```
Creates a properly configured mock TradingConfig object for testing.

### 2. Test Classes

#### TestParallelTradeConfig (2 tests)
Tests the configuration dataclass:
- Default values
- Custom values

#### TestParallelTradingEngineInit (2 tests)
Tests initialization:
- `__init__()` method
- `initialize()` async method

#### TestCalculateMarketIndicators (2 tests)
Tests market indicator calculation:
- Normal candle data
- Empty candle data (edge case)

#### TestIsCorrelatedWithActiveTrades (3 tests)
Tests correlation detection:
- No active trades
- Correlated pairs (same base currency)
- Uncorrelated pairs

#### TestSelectTradeOpportunities (3 tests)
Tests opportunity selection:
- Empty analyses
- Multiple opportunities
- Risk budget limits

#### TestAnalyzeSinglePair (3 tests)
Tests async pair analysis:
- Successful analysis
- Insufficient candle data
- No consensus reached

#### TestExecuteSingleTrade (2 tests)
Tests async trade execution:
- Successful execution
- Failed execution

#### TestMonitorActiveTrades (2 tests)
Tests async trade monitoring:
- No active trades
- Winning trade completion

#### TestPrintSessionSummary (1 test)
Tests session summary output

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest test_parallel_trading_engine.py -v

# Run with output
pytest test_parallel_trading_engine.py -v -s

# Run specific test class
pytest test_parallel_trading_engine.py::TestCalculateMarketIndicators -v

# Run specific test
pytest test_parallel_trading_engine.py::TestCalculateMarketIndicators::test_calculate_market_indicators -v
```

### Advanced Commands

```bash
# Run with coverage
pytest test_parallel_trading_engine.py --cov=trading.parallel_trading_engine --cov-report=html

# Run with detailed output
pytest test_parallel_trading_engine.py -vv --tb=long

# Run and show durations
pytest test_parallel_trading_engine.py -v --durations=10

# Run in parallel (if pytest-xdist installed)
pytest test_parallel_trading_engine.py -n auto
```

## Test Patterns

### 1. Mocking Dependencies

All external dependencies are mocked using `@patch`:

```python
@patch('trading.parallel_trading_engine.TradeDatabase')
@patch('trading.parallel_trading_engine.MarketContextAnalyzer')
@patch('trading.parallel_trading_engine.EnhancedConsensusEngine')
@patch('trading.parallel_trading_engine.KellyPositionSizer')
@patch('trading.parallel_trading_engine.IQOptionProvider')
def test_method(self, mock_provider, mock_sizer, mock_consensus,
                mock_analyzer, mock_db):
    config = create_mock_config()
    engine = ParallelTradingEngine(config)
    # Test implementation
```

### 2. Async Testing

Async methods use `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_async_method(self):
    # Setup mocks
    mock_provider = AsyncMock()
    mock_provider.get_candles = AsyncMock(return_value=[...])

    # Test async method
    result = await engine._analyze_single_pair(pair_info)

    # Assertions
    assert result is not None
```

### 3. Configuration Mock

Using the helper function:

```python
def test_something(self):
    config = create_mock_config()
    # config.DB_PATH, config.EMAIL, etc. are all set
    engine = ParallelTradingEngine(config)
```

## What Each Method Tests

### _calculate_market_indicators(candles, pair)
- ✅ Processes candle data correctly
- ✅ Returns proper market indicator structure
- ✅ Handles empty/invalid input

### _is_correlated_with_active_trades(pair)
- ✅ Returns False when no active trades
- ✅ Detects correlation (same base currency)
- ✅ Identifies uncorrelated pairs

### _select_trade_opportunities(analyses, balance)
- ✅ Returns empty for empty input
- ✅ Sorts by expected value (confidence * payout)
- ✅ Respects risk budget limits
- ✅ Limits concurrent trades

### _analyze_single_pair(pair_info)
- ✅ Fetches candles
- ✅ Calculates indicators
- ✅ Gets AI consensus
- ✅ Validates confidence threshold
- ✅ Returns analysis or None

### _execute_single_trade(opportunity)
- ✅ Executes trade via provider
- ✅ Stores in database
- ✅ Handles execution failures

### _monitor_active_trades(session_stats)
- ✅ Checks trade completion
- ✅ Updates session statistics
- ✅ Removes completed trades

## Common Issues and Solutions

### Issue: ModuleNotFoundError
```bash
# Solution: Install dependencies
pip install pytest pytest-asyncio aioredis redis websockets
```

### Issue: Async tests not running
```bash
# Solution: Install pytest-asyncio
pip install pytest-asyncio
```

### Issue: Import errors
```bash
# Solution: Set PYTHONPATH
export PYTHONPATH="/app/app/KAEL/KAEL/src:$PYTHONPATH"
```

## Test Data Examples

### Sample Candle Data
```python
candles = [
    {'close': 1.1000, 'open': 1.0990, 'high': 1.1010, 'low': 1.0980},
    {'close': 1.1020, 'open': 1.1000, 'high': 1.1030, 'low': 1.0990},
]
```

### Sample Analysis
```python
analysis = {
    'pair': 'EURUSD',
    'payout': 0.80,
    'confidence': 75,
    'signal': 'call'
}
```

### Sample Trade Result
```python
result = {
    'success': True,
    'order_id': 'order123',
    'pair': 'EURUSD'
}
```

## Assertions Used

### Basic Assertions
```python
assert result is not None
assert result == expected
assert 'key' in result
assert len(items) > 0
```

### Type Assertions
```python
assert isinstance(result, dict)
assert isinstance(value, int)
```

### Mock Assertions
```python
mock_method.assert_called_once()
mock_method.assert_called_with(expected_arg)
mock_method.assert_not_called()
```

## Test Coverage Goals

- ✅ All public methods tested
- ✅ All private methods tested
- ✅ Happy path scenarios
- ✅ Error conditions
- ✅ Edge cases
- ✅ Async operations
- ⚠️ Integration tests (future)
- ⚠️ Performance tests (future)

## Adding New Tests

### Template for New Test

```python
@patch('trading.parallel_trading_engine.Dependency')
def test_new_feature(self, mock_dependency):
    """Test description"""
    # Arrange
    config = create_mock_config()
    engine = ParallelTradingEngine(config)

    # Act
    result = engine.method_to_test()

    # Assert
    assert result is not None
    assert expected_condition
    print("✅ Test description passed")
```

### Template for Async Test

```python
@pytest.mark.asyncio
@patch('trading.parallel_trading_engine.Provider')
async def test_async_feature(self, mock_provider_class):
    """Test async feature"""
    # Arrange
    mock_provider = AsyncMock()
    mock_provider.async_method = AsyncMock(return_value=expected)
    mock_provider_class.return_value = mock_provider

    config = create_mock_config()
    engine = ParallelTradingEngine(config)
    engine.provider = mock_provider

    # Act
    result = await engine.async_method()

    # Assert
    assert result == expected
    print("✅ Async test passed")
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Test names should describe what is being tested
3. **Mock Everything**: Mock all external dependencies
4. **Fast Tests**: Tests should run in < 2 seconds total
5. **Assertions**: Include clear assertion messages
6. **Edge Cases**: Test both success and failure paths
7. **Documentation**: Add docstrings to all tests

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests with coverage and generate reports
pytest tests/test_parallel_trading_engine.py \
    --cov=trading.parallel_trading_engine \
    --cov-report=xml \
    --cov-report=html \
    --junitxml=test-results.xml \
    -v
```

## Maintenance

### When to Update Tests

- ✅ After changing method signatures
- ✅ After adding new methods
- ✅ After changing business logic
- ✅ After fixing bugs (add regression test)
- ✅ After performance improvements

### Test Review Checklist

- [ ] All tests pass
- [ ] New features are tested
- [ ] Edge cases are covered
- [ ] Mocks are properly configured
- [ ] Async tests use proper decorators
- [ ] Test names are descriptive
- [ ] Assertions have clear messages
- [ ] No test interdependencies

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Test file](./test_parallel_trading_engine.py)
- [Test results](./TEST_RESULTS_PARALLEL_ENGINE.md)
