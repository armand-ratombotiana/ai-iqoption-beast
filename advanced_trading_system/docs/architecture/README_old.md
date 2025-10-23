# 🚀 Advanced Binary Options Trading System

A production-ready binary options trading system with **multi-AI consensus**, **comprehensive market analysis**, and **complete data persistence**.

## ✨ Features

- ✅ **Multi-AI Consensus** - OpenAI GPT-4o-mini + Claude Haiku + DeepSeek
- ✅ **20+ Technical Indicators** - RSI, MACD, Bollinger Bands, and more
- ✅ **Pre/Post-Trade Analysis** - Capture market conditions before and after
- ✅ **Complete Database** - SQLite with 40+ fields per trade
- ✅ **Performance Tracking** - AI model accuracy and statistics
- ✅ **Self-Learning** - Identifies patterns and optimizes strategies

## 📁 Project Structure

```
advanced_trading_system/
├── database/
│   ├── __init__.py
│   └── trade_storage.py         # SQLite database management
│
├── analysis/
│   ├── __init__.py
│   ├── technical_indicators.py  # 20+ technical indicators
│   └── market_context.py        # Pre/post-trade analysis
│
├── ai_models/
│   ├── __init__.py
│   ├── base_model.py            # Abstract AI model interface
│   ├── openai_model.py          # OpenAI integration
│   ├── claude_model.py          # Claude integration
│   ├── deepseek_model.py        # DeepSeek integration
│   └── consensus_engine.py      # Multi-model voting
│
├── config/
│   ├── __init__.py
│   └── settings.py              # Configuration management
│
├── scripts/
│   └── run_trading.py           # Main trading script
│
├── tests/
│   └── test_system.py           # Component tests
│
├── data/                        # Database storage
├── logs/                        # Trading logs
├── requirements.txt
└── README.md
```

## 🔧 Setup

### 1. Install Dependencies

```bash
pip install numpy requests
```

### 2. Set API Keys

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export DEEPSEEK_API_KEY="sk-..."

# Optional: IQ Option credentials
export IQOPTION_EMAIL="your@email.com"
export IQOPTION_PASSWORD="yourpassword"
```

### 3. Run Tests

```bash
cd advanced_trading_system
python tests/test_system.py
```

### 4. Run Trading System

```bash
cd advanced_trading_system
python scripts/run_trading.py
```

## 📊 How It Works

### Trade Execution Flow

```
1. Connect to IQ Option (Demo/Real account)
   ↓
2. Capture Pre-Trade Market Context
   • Get 100 candles
   • Calculate 20+ technical indicators
   • Identify trend, volatility, patterns
   ↓
3. Get AI Consensus
   • OpenAI analyzes → CALL (82%)
   • Claude analyzes → CALL (75%)
   • DeepSeek analyzes → PUT (60%)
   • Consensus: CALL (78% confidence, 69% agreement)
   ↓
4. Validate Signal
   • Consensus reached? (≥66%)
   • Confidence high enough? (≥65%)
   ↓
5. Execute Trade
   • Calculate position size (confidence-based)
   • Place trade via IQ Option API
   • Store everything in database
   ↓
6. Wait for Expiration
   ↓
7. Capture Post-Trade Context
   • Actual price movement
   • Volatility during trade
   • Market events
   ↓
8. Get Result (WIN/LOSS)
   ↓
9. Update Database & AI Performance
   • Store complete trade record
   • Update model accuracy
   • Adjust model weights
```

## 🎯 AI Consensus

Each AI model independently analyzes the market:

| Model | Weight | Example Output |
|-------|--------|----------------|
| OpenAI GPT-4o-mini | 1.2 | CALL 82% "RSI oversold, MACD bullish" |
| Claude Haiku | 1.0 | CALL 75% "Uptrend confirmed, support nearby" |
| DeepSeek | 1.0 | PUT 60% "Approaching resistance" |

**Consensus Calculation:**
- CALL votes: 1.2 + 1.0 = 2.2
- PUT votes: 1.0
- Agreement: 2.2 / 3.2 = 68.75% ✅
- Final: CALL with 78% average confidence

## 📈 Technical Indicators

### Momentum
- RSI (14, 7 periods)
- Stochastic Oscillator
- Williams %R
- CCI

### Trend
- MACD (value, signal, histogram)
- ADX (trend strength)
- EMA (12, 26)
- SMA (20, 50)

### Volatility
- ATR (Average True Range)
- Bollinger Bands (upper, middle, lower, position)

### Support/Resistance
- Dynamic support/resistance levels

### Patterns
- Candlestick patterns (doji, engulfing, hammer, etc.)
- Chart patterns (triangles, etc.)

## 💾 Database

```sql
trades (40+ fields):
├── Trade Details (ID, timestamp, pair, direction, amount, result, profit)
├── AI Consensus (confidence, agreement, model count)
├── Pre-Trade Indicators (20+ fields)
│   ├── RSI, MACD, Bollinger Bands
│   ├── Trend, volatility, support/resistance
│   └── Patterns, time context
├── Post-Trade Analysis
│   ├── Actual movement, high/low range
│   └── Prediction accuracy
└── Full Context (JSON)
    ├── Complete pre-trade data
    ├── Complete post-trade data
    └── All AI model votes
```

## ⚙️ Configuration

Edit `config/settings.py` or use environment variables:

```python
# AI Models
USE_OPENAI = True
USE_CLAUDE = True
USE_DEEPSEEK = True

# Consensus
CONSENSUS_THRESHOLD = 0.66  # 66% agreement required
MIN_CONFIDENCE = 65         # Minimum confidence to trade

# Trading
BASE_AMOUNT = 2.0           # Base trade amount
MIN_AMOUNT = 1.0            # Minimum allowed
MAX_AMOUNT = 20.0           # Maximum allowed

# Risk Management
MAX_DAILY_LOSS = 50.0
MAX_DAILY_PROFIT = 200.0
MAX_CONSECUTIVE_LOSSES = 3
```

## 📊 Example Output

```
======================================================================
🚀 ADVANCED TRADING SYSTEM - AUDCHF-OTC
======================================================================

🔌 Connecting to IQ Option...
✅ Connected
💰 Balance: $10000.00

📊 STEP 1: Capturing Market Context...
✅ Captured 35 market indicators
   Trend: uptrend
   RSI(14): 65.2
   Volatility: medium
   Pattern: bullish_engulfing

🤖 STEP 2: Getting AI Consensus...

======================================================================
🤖 AI CONSENSUS ANALYSIS
======================================================================

📊 Consensus Signal: CALL
   Confidence: 78.3%
   Agreement: 68.8%
   Consensus Reached: ✅ YES

🗳️  Individual Model Votes:
   • openai-gpt-4o-mini (weight: 1.2)
     Signal: CALL | Confidence: 82%
     Reasoning: RSI oversold, MACD bullish crossover

   • claude-claude-3-5-haiku-20241022 (weight: 1.0)
     Signal: CALL | Confidence: 75%
     Reasoning: Uptrend confirmed, stochastic oversold

   • deepseek-deepseek-chat (weight: 1.0)
     Signal: PUT | Confidence: 60%
     Reasoning: Approaching resistance

======================================================================

✅ Trading Signal: CALL
   Confidence: 78.3%
   Agreement: 68.8%

💵 STEP 3: Position Sizing...
   Final amount: $1.57

🚀 STEP 4: Executing Trade...
✅ Trade executed!
   Order ID: 123456789

💾 Trade data saved to database

⏳ STEP 5: Waiting for trade result...

📈 Post-Trade Analysis:
   Entry: $0.568500
   Exit: $0.568650
   Change: +0.03%
   Direction: UP

📊 STEP 6: Checking Result...
✅ Result retrieved

======================================================================
📈 TRADE RESULT
======================================================================
✅ WIN!
   Profit: +$1.26

   Prediction: CALL
   Actual: UP
   Correct: YES

💰 Balance: $10000.00 → $10001.26 (+1.26)

======================================================================
```

## 📚 Usage Examples

### Run Single Trade

```python
from config.settings import TradingConfig
from scripts.run_trading import AdvancedTradingSystem

config = TradingConfig()
system = AdvancedTradingSystem(config)

result = system.execute_trade(pair='AUDCHF-OTC', duration=1)
```

### View Statistics

```python
system.show_statistics()
```

### Export Data

```python
from database.trade_storage import TradeDatabase

db = TradeDatabase('data/trades_advanced.db')
db.export_to_csv('my_trades.csv')
```

## 🧪 Testing

```bash
# Run all tests
python tests/test_system.py

# Expected output:
✅ Database Storage         - PASSED
✅ Technical Indicators      - PASSED
✅ AI Consensus Engine       - PASSED
```

## 📊 Performance Metrics

The system tracks:
- Overall win rate
- Win rate by trend (uptrend/downtrend/sideways)
- Win rate by hour of day
- AI model accuracy (which models perform best)
- Confidence calibration (is 80% really 80%?)
- Profit/Loss per trade

## ⚠️ Important Notes

1. **Demo First** - Always test on demo account before real trading
2. **API Keys Required** - Set OpenAI, Claude, and DeepSeek keys
3. **Risk Management** - Never trade more than you can afford to lose
4. **Binary Options Risk** - High-risk trading instrument
5. **Data Privacy** - All data stored locally in SQLite

## 🔄 Continuous Improvement

The system learns by:
1. Storing every trade with complete market context
2. Tracking which AI models are most accurate
3. Identifying patterns that lead to wins/losses
4. Adjusting AI model weights based on performance
5. Providing insights for strategy optimization

## 📞 Support

- **Tests**: Run `python tests/test_system.py`
- **Database**: Located in `data/trades_advanced.db`
- **Logs**: Check console output
- **Config**: Edit `config/settings.py`

## 🚀 Next Steps

1. Set your API keys
2. Run tests to verify setup
3. Execute demo trades
4. Analyze results in database
5. Optimize based on findings

---

**Version**: 1.0.0
**Status**: ✅ Production Ready (Demo Testing)
**License**: Private Use

🎉 **Happy Trading!** (Responsibly)
