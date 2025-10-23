# 🤖 AUTONOMOUS 24/7 BINARY OPTIONS TRADING BOT

## 🎯 Overview

This is a **production-ready autonomous trading bot** designed to trade binary options 24/7 with minimal human intervention. The bot features:

- ✅ **24/7 Continuous Operation** - Runs autonomously around the clock
- ✅ **1-Minute Binary Options** - Fast-paced 60-second expiry trades
- ✅ **AI-Driven Decisions** - Consensus-based signals from multiple AI models
- ✅ **Advanced Risk Management** - Multiple safety layers to protect capital
- ✅ **Auto-Recovery** - Automatically recovers from errors and connection issues
- ✅ **Comprehensive Logging** - Detailed trade history and performance tracking
- ✅ **Health Monitoring** - REST API for real-time status checks
- ✅ **Emergency Stop** - Instant halt mechanism for critical situations

---

## ⚠️ CRITICAL WARNINGS

### 🚨 READ BEFORE USING

1. **BINARY OPTIONS ARE HIGH RISK**
   - You can lose your entire investment
   - Past performance does NOT guarantee future results
   - This is NOT financial advice

2. **ALWAYS START WITH DEMO MODE**
   - Test thoroughly on demo account first
   - Verify all settings before live trading
   - Monitor for at least 24-48 hours on demo

3. **LIVE TRADING USES REAL MONEY**
   - Losses are real and permanent
   - Only trade with money you can afford to lose
   - Never leave the bot unmonitored for extended periods

4. **NOT A GET-RICH-QUICK SCHEME**
   - Trading is risky and requires capital
   - The bot can and will have losing periods
   - Proper risk management is essential

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- IQ Option account (demo or live)
- Linux/macOS environment (Windows via WSL2)
- Stable internet connection

### Installation

```bash
# 1. Clone/navigate to project directory
cd /path/to/KAEL

# 2. Copy environment file
cp .env.production.example .env

# 3. Edit configuration
nano .env

# 4. Configure your credentials:
#    - Set IQOPTION_EMAIL
#    - Set IQOPTION_PASSWORD
#    - Set TRADING_MODE=demo (for testing)

# 5. Start the bot
./start_24_7_bot.sh
```

---

## ⚙️ Configuration

### Critical Settings (`.env` file)

#### Trading Mode
```env
TRADING_MODE=demo    # 'demo' for practice, 'live' for real money
```

#### Account Credentials
```env
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password
```

#### Risk Management (MOST IMPORTANT!)
```env
MAX_DAILY_LOSS=50              # Stop trading after $50 loss per day
MAX_DAILY_PROFIT=100           # Stop trading after $100 profit per day
MAX_CONSECUTIVE_LOSSES=5       # Pause after 5 losses in a row
MIN_BALANCE=50                 # Minimum account balance to continue
BASE_TRADE_AMOUNT=1.0          # Base amount per trade
MAX_TRADE_AMOUNT=10.0          # Maximum trade size
```

#### Martingale Strategy
```env
ENABLE_MARTINGALE=true         # Enable/disable martingale
MARTINGALE_MULTIPLIER=1.5      # Multiply trade size after loss
MAX_MARTINGALE_LEVEL=3         # Maximum martingale steps
```

⚠️ **WARNING**: Martingale is risky! It can lead to large losses.

#### AI Configuration
```env
MIN_AI_CONFIDENCE=65           # Minimum AI confidence (0-100)
MIN_CONSENSUS_AGREEMENT=0.7    # 70% of AI models must agree
```

#### Rate Limiting
```env
MAX_TRADES_PER_HOUR=30         # Maximum 30 trades/hour
MAX_TRADES_PER_DAY=200         # Maximum 200 trades/day
MIN_SECONDS_BETWEEN_TRADES=70  # Wait time between trades
```

---

## 📊 How It Works

### Trading Flow

```
┌─────────────────────────────────────┐
│  1. Check Risk Limits               │
│     - Daily loss/profit             │
│     - Consecutive losses            │
│     - Account balance               │
│     - Rate limits                   │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  2. Find Best Market                │
│     - Check open markets            │
│     - Verify liquidity              │
│     - Check payout rates            │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  3. Get AI Signal                   │
│     - Query multiple AI models      │
│     - Calculate consensus           │
│     - Verify confidence thresholds  │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  4. Calculate Position Size         │
│     - Apply base amount             │
│     - Apply martingale (if enabled) │
│     - Check balance limits          │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  5. Execute Trade                   │
│     - Place binary option order     │
│     - Wait 80 seconds               │
│     - Check result                  │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  6. Update Statistics               │
│     - Record profit/loss            │
│     - Update consecutive counters   │
│     - Adjust martingale level       │
└──────────┬──────────────────────────┘
           ▼
           ◄──────── Loop ────────────┐
```

### 1-Minute Binary Options

- **Duration**: 60 seconds (1 minute)
- **Execution Time**: ~5 seconds
- **Wait Time**: 80 seconds (60s trade + 20s buffer)
- **Result Check**: Up to 30 seconds
- **Total Cycle**: ~2 minutes per trade

This allows approximately **30 trades per hour** maximum.

---

## 🛡️ Safety Features

### Multi-Layer Risk Management

1. **Daily Limits**
   - Stops trading when max daily loss reached
   - Stops trading when profit target achieved
   - Resets automatically at midnight

2. **Consecutive Loss Protection**
   - Pauses trading after X consecutive losses
   - Prevents catastrophic loss spirals
   - Requires manual review before resuming

3. **Balance Monitoring**
   - Checks balance before each trade
   - Stops if balance falls below minimum
   - Prevents trading with insufficient funds

4. **Rate Limiting**
   - Maximum trades per hour
   - Maximum trades per day
   - Minimum time between trades

5. **Connection Monitoring**
   - Periodic connection health checks
   - Automatic reconnection on failure
   - Graceful handling of network issues

### Emergency Stop Mechanism

Create a file named `EMERGENCY_STOP` to immediately halt trading:

```bash
# Stop the bot immediately
touch EMERGENCY_STOP

# Resume trading (remove the file)
rm EMERGENCY_STOP
```

The bot checks for this file before EVERY trade.

---

## 📈 Monitoring

### Real-Time Statistics

The bot logs comprehensive statistics:

- Current balance
- Daily profit/loss
- Win rate
- Consecutive wins/losses
- Total trades executed
- Best/worst streaks
- Uptime

### Log Files

Logs are stored in the `logs/` directory:

```
logs/
├── autonomous_bot_20251023.log    # Main log (daily rotation)
└── trades_20251023.log            # Trade-only log
```

### Health Monitoring API

Access real-time status via REST API:

```bash
# Check health
curl http://localhost:5001/health

# Get statistics
curl http://localhost:5001/statistics

# Stop bot remotely
curl -X POST http://localhost:5001/stop
```

Response example:
```json
{
  "status": "running",
  "mode": "demo",
  "balance": 10250.50,
  "daily_profit": 125.00,
  "daily_loss": 75.00,
  "daily_net": 50.00,
  "trades_today": 45,
  "wins_today": 27,
  "losses_today": 18,
  "win_rate": 60.0,
  "consecutive_wins": 3,
  "consecutive_losses": 0,
  "uptime_hours": 8.5
}
```

---

## 🧠 AI Integration

### Current Implementation

The bot includes a placeholder for AI signal generation. **You must implement your own AI logic.**

### Integration Points

Edit the `get_ai_signal()` method in `autonomous_trading_bot_24_7.py`:

```python
def get_ai_signal(self, asset: str) -> Optional[Dict]:
    """
    Get AI consensus signal for trading
    TODO: Integrate actual AI models here
    """
    # Implement your AI logic here
    # Return format:
    return {
        'signal': 'CALL' or 'PUT' or 'NEUTRAL',
        'confidence': 0-100,
        'agreement': 0.0-1.0,
        'reasoning': 'Analysis explanation',
        'asset': asset
    }
```

### Available AI Models (from codebase)

The project includes these AI models (integrate as needed):

- **Claude Model** (`ai/models/claude_model.py`)
- **OpenAI Model** (`ai/models/openai_model.py`)
- **DeepSeek Model** (`ai/models/deepseek_model.py`)
- **LSTM Model** (`ai/models/lstm_model.py`)
- **Consensus Engine** (`ai/models/consensus_engine.py`)
- **Market Regime Detector** (`ai/models/market_regime_detector.py`)

### Maximum Data Ingestion

To maximize AI data usage:

1. **Technical Indicators**
   - RSI, MACD, Bollinger Bands
   - Moving averages (multiple timeframes)
   - Volume analysis
   - Support/resistance levels

2. **Market Data**
   - Real-time price feeds
   - Historical candle data
   - Order book depth
   - Market sentiment

3. **Multiple Timeframes**
   - 1-minute (primary)
   - 5-minute (context)
   - 15-minute (trend)
   - 1-hour (major trend)

4. **Model Ensemble**
   - Use AIConsensusEngine
   - Weight models by performance
   - Require minimum agreement threshold

---

## 🐳 Docker Deployment

### Build Docker Image

```bash
cd docker/
docker-compose build
```

### Run in Container

```bash
# Start bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop bot
docker-compose down
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  trading-bot:
    build: .
    container_name: iqoption-24-7-bot
    environment:
      - TRADING_MODE=demo
      - MAX_DAILY_LOSS=50
      - MAX_DAILY_PROFIT=100
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

---

## 🔧 Troubleshooting

### Bot Won't Start

**Problem**: Connection fails
```
❌ Connection failed: Invalid credentials
```

**Solution**: Check credentials in `.env`:
```bash
# Verify settings
cat .env | grep IQOPTION_

# Test login manually
python3 -c "from iqoptionapi.stable_api import IQ_Option; ..."
```

### No Trades Executing

**Problem**: Bot running but not trading

**Possible Causes**:
1. No markets open (check trading hours)
2. AI confidence too low (lower MIN_AI_CONFIDENCE)
3. Daily limits reached (check logs)
4. All assets closed (try different times)

**Solution**: Check logs:
```bash
tail -f logs/autonomous_bot_*.log | grep "Trading paused"
```

### High Loss Rate

**Problem**: Losing too many trades

**Solutions**:
1. **Increase AI threshold**: Raise MIN_AI_CONFIDENCE to 75%+
2. **Disable martingale**: Set ENABLE_MARTINGALE=false
3. **Reduce trade frequency**: Increase MIN_SECONDS_BETWEEN_TRADES
4. **Better AI models**: Implement stronger signal generation
5. **Review market selection**: Trade only during liquid hours

### Connection Drops

**Problem**: Bot loses connection frequently

**Solutions**:
1. Check internet stability
2. Increase CONNECTION_CHECK_INTERVAL
3. Review firewall settings
4. Use VPS with stable connection

---

## 📋 Best Practices

### 1. Start Small
- Begin with minimum trade amounts
- Use demo mode for at least 1 week
- Gradually increase stakes as you gain confidence

### 2. Monitor Actively
- Check logs daily for first week
- Review statistics regularly
- Adjust settings based on performance

### 3. Set Conservative Limits
- Low daily loss limits (1-5% of balance)
- Realistic profit targets
- Maximum 3-5 consecutive losses

### 4. Backup Configuration
```bash
# Save working configuration
cp .env .env.backup.$(date +%Y%m%d)

# Save trade logs
cp -r logs logs.backup.$(date +%Y%m%d)
```

### 5. Version Control
```bash
# Never commit .env with real credentials!
git add .env.production.example
git commit -m "Update production config template"
```

---

## 🚨 When to Stop the Bot

### Immediate Stop Required:

1. **Unusual behavior**
   - Trades executing at wrong prices
   - Unexpected trade sizes
   - API errors

2. **External factors**
   - Major news events
   - Market volatility spikes
   - IQ Option maintenance

3. **Performance issues**
   - Win rate drops below 45%
   - Losing streak exceeds 10
   - Daily loss approaching limit

### How to Stop:

```bash
# Method 1: Emergency stop file
touch EMERGENCY_STOP

# Method 2: Graceful shutdown (Ctrl+C)
# Press Ctrl+C in terminal

# Method 3: Via API
curl -X POST http://localhost:5001/stop

# Method 4: Kill process
pkill -f autonomous_trading_bot_24_7.py
```

---

## 📊 Performance Expectations

### Realistic Goals

- **Win Rate**: 55-60% is good for binary options
- **Daily Profit**: 2-5% of balance is realistic
- **Losses**: Expect losing days/weeks
- **Recovery**: May take time after drawdowns

### Red Flags

- Win rate below 45% consistently
- Daily losses exceeding limits regularly
- Martingale reaching max level frequently
- Connection issues multiple times per hour

---

## 🔐 Security

### Credential Protection

```bash
# .env file should be:
chmod 600 .env

# Never commit:
echo ".env" >> .gitignore

# Use environment variables in production:
export IQOPTION_EMAIL="your@email.com"
export IQOPTION_PASSWORD="yourpassword"
```

### API Security

```bash
# Restrict health API access
# Use firewall or reverse proxy
iptables -A INPUT -p tcp --dport 5001 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 5001 -j DROP
```

---

## 🆘 Support

### Getting Help

1. **Check logs first**: `logs/autonomous_bot_*.log`
2. **Review configuration**: Verify all `.env` settings
3. **Test connection**: Try manual login to IQ Option
4. **Check market hours**: Verify assets are tradeable
5. **Reduce complexity**: Disable martingale, lower limits

### Common Issues

See troubleshooting section above.

---

## 📝 License & Disclaimer

This software is provided "as is" without warranty of any kind. Trading binary options involves substantial risk of loss. Use at your own risk.

**Not financial advice. For educational purposes only.**

---

## 🎯 Next Steps

1. ✅ Copy `.env.production.example` to `.env`
2. ✅ Configure credentials and settings
3. ✅ Test on **DEMO MODE** for at least 48 hours
4. ✅ Monitor performance and adjust settings
5. ✅ Only switch to live mode after thorough testing
6. ✅ Start with minimum trade amounts
7. ✅ Keep monitoring and optimizing

**Good luck and trade responsibly! 🚀**
