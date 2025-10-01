# IQOption AI Binary Trading Bot - Implementation Guide

## Overview

This is a production-ready AI-powered binary options trading bot for IQOption, featuring:

- **AI Signal Validation** with configurable confidence thresholds
- **Advanced Risk Management** (daily loss/profit limits, consecutive loss protection, balance monitoring)
- **Dynamic Trade Sizing** with adaptive Martingale strategy
- **Market Status Checking** and payout calculation
- **Comprehensive State Tracking** and statistics
- **n8n Integration** for workflow automation

## Architecture

### Components

1. **trading_api.py** - Flask API server with trading logic and risk management
2. **n8n-nodes-trading** - Custom n8n node for workflow integration
3. **BOT_KAEL.py** - Standalone testing script (optional)

## Installation & Setup

### 1. Install Python Dependencies

```bash
pip3 install flask iqoptionapi
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your preferred settings:

```env
# Risk Management
MAX_DAILY_LOSS=50              # Stop trading after losing $50 in a day
MAX_DAILY_PROFIT=100           # Stop trading after profiting $100 in a day
MAX_CONSECUTIVE_LOSSES=3       # Stop after 3 consecutive losses
MIN_BALANCE=50                 # Minimum account balance required

# Martingale Strategy
MARTINGALE_MULTIPLIER=1.5      # Multiply trade amount by 1.5 after each loss
MAX_MARTINGALE_LEVEL=4         # Maximum Martingale level (prevents exponential risk)

# Trading Parameters
MIN_CONFIDENCE_THRESHOLD=60    # Minimum AI confidence % to execute trade
BASE_TRADE_AMOUNT=1            # Base trade amount in dollars
MAX_TRADE_MULTIPLIER=5         # Maximum trade size (base_amount * 5)
```

### 3. Start the Trading API

```bash
python3 trading_api.py
```

The API will start on `http://localhost:5000`

### 4. Install n8n Node (Optional)

If using n8n for workflow automation:

```bash
cd n8n-nodes-trading
npm install
npm link
```

Then restart n8n to load the custom node.

## API Endpoints

### POST /trade

Execute a trade with AI signal validation and risk management.

**Request:**
```json
{
  "email": "your@email.com",
  "password": "yourpassword",
  "action": "call",              // or "put"
  "pair": "EURUSD",
  "confidence": 75,               // AI confidence 0-100
  "amount": 1,                    // Optional - auto-calculated if omitted
  "duration": 1,                  // Optional - auto-calculated if omitted
  "accountType": "demo"           // or "real"
}
```

**Response:**
```json
{
  "success": true,
  "orderId": 123456789,
  "action": "call",
  "pair": "EURUSD",
  "amount": 1.5,
  "duration": 2,
  "confidence": 75,
  "profit": 1.35,
  "result": "win",
  "payout": 0.90,
  "potentialProfit": 1.35,
  "oldBalance": 1000.00,
  "newBalance": 1001.35,
  "balanceChange": 1.35,
  "tradingState": {
    "dailyProfit": 5.50,
    "dailyLoss": 2.00,
    "consecutiveLosses": 0,
    "consecutiveWins": 2,
    "martingaleLevel": 0,
    "tradesToday": 8,
    "totalTrades": 42
  },
  "timestamp": "2025-10-01 12:34:56"
}
```

### GET /status

Get current trading statistics and state.

**Response:**
```json
{
  "status": "active",
  "tradingState": {
    "daily_loss": 10.5,
    "daily_profit": 25.3,
    "consecutive_losses": 0,
    "consecutive_wins": 3,
    "martingale_level": 0,
    "last_reset": "2025-10-01",
    "trades_today": 15,
    "total_trades": 127
  },
  "config": {
    "MAX_DAILY_LOSS": 50,
    "MAX_DAILY_PROFIT": 100,
    ...
  },
  "timestamp": "2025-10-01T12:34:56.789Z"
}
```

### POST /reset

Reset trading state (use with caution).

**Request:**
```json
{
  "type": "daily"  // or "martingale" or "full"
}
```

### GET /health

Health check endpoint.

## Risk Management System

The bot implements multiple layers of risk protection:

### 1. Balance Check
- Trades blocked if balance falls below `MIN_BALANCE`

### 2. Daily Loss Limit
- Automatically stops trading when daily loss exceeds `MAX_DAILY_LOSS`
- Resets at midnight

### 3. Daily Profit Target
- Stops trading when profit target reached (`MAX_DAILY_PROFIT`)
- Prevents giving back profits

### 4. Consecutive Loss Protection
- Stops trading after `MAX_CONSECUTIVE_LOSSES` consecutive losses
- Resets after a win

### 5. Martingale Level Limit
- Caps Martingale progression at `MAX_MARTINGALE_LEVEL`
- Prevents exponential risk exposure

### 6. Confidence Threshold
- Only executes trades with AI confidence >= `MIN_CONFIDENCE_THRESHOLD`

## Dynamic Trade Sizing

Trade amounts are calculated using:

```javascript
amount = BASE_TRADE_AMOUNT
         × MARTINGALE_MULTIPLIER^martingale_level
         × (confidence / 100)
         × capped at MAX_TRADE_MULTIPLIER
         × capped at 5% of balance
```

**Example:**
- Base: $1
- Confidence: 80%
- Martingale Level: 2
- Multiplier: 1.5

```
amount = 1 × 1.5² × 0.8 = $1.80
```

## Duration Calculation

Trade duration is automatically calculated based on confidence:

- **90-100% confidence**: 1 minute
- **80-89% confidence**: 2 minutes
- **70-79% confidence**: 3 minutes
- **60-69% confidence**: 5 minutes

Higher confidence = shorter duration (more certain prediction)

## Using with n8n

### Example Workflow

1. **Asset Selector Node** → Defines trading pairs
2. **AI Signal Generator** → Generates CALL/PUT signals with confidence
3. **IQOption AI Trading Bot Node** → Executes trade
4. **Conditional Node** → Handle success/failure
5. **Logging/Alert Nodes** → Track results

### Node Configuration

The custom n8n node supports three operations:

#### Execute Trade
- Action: CALL or PUT
- Trading Pair: EURUSD, GBPUSD, etc.
- Confidence: 0-100
- Amount: Auto-calculated or manual
- Duration: Auto-calculated or manual
- Account Type: Demo or Real

#### Get Status
- Fetches current trading statistics
- No parameters required

#### Reset State
- Reset Type: daily, martingale, or full
- Use carefully in production

## Best Practices

### 1. Always Start with Demo Account
Never use real money until thoroughly tested:
```json
{
  "accountType": "demo"
}
```

### 2. Conservative Risk Settings
Start with conservative limits:
- `MAX_DAILY_LOSS`: 2-5% of balance
- `MAX_CONSECUTIVE_LOSSES`: 3
- `BASE_TRADE_AMOUNT`: 1% of balance

### 3. Monitor Performance
- Use `/status` endpoint regularly
- Track win rate and profit factor
- Adjust parameters based on results

### 4. Confidence Threshold
- Start with higher threshold (70-80%)
- Lower only after consistent wins
- Never go below 60%

### 5. Martingale Caution
- Keep `MAX_MARTINGALE_LEVEL` low (3-4)
- Martingale increases risk exponentially
- Consider disabling by setting to 0

### 6. Market Selection
- Trade only major pairs initially (EURUSD, GBPUSD)
- Avoid volatile/exotic pairs
- Check market hours

## Monitoring & Logging

The API provides detailed console logging:

```
============================================================
[TRADE REQUEST] CALL EURUSD | Confidence: 75%
============================================================
[VALIDATION] Signal validated
[CONNECTED] Successfully connected to IQ Option
[BALANCE] Current balance: $1000.00
[RISK GUARD] Risk checks passed
[MARKET] EURUSD is open
[TRADE SIZING] Amount: $1.5 (Martingale Level: 0)
[EXPIRATION] Duration: 2 minute(s)
[PAYOUT] 90.00% | Potential profit: $1.35
[EXECUTING] CALL trade...
[PLACED] Trade placed successfully, Order ID: 123456789
[WAITING] Waiting 125s for trade to complete...
[CHECKING] Checking result...
[RESULT] WIN - Profit: $1.35, Balance: $1000.00 -> $1001.35
[STATS] Daily P/L: +$5.50 / -$2.00
============================================================
```

## Troubleshooting

### Connection Issues
- Verify IQOption credentials
- Check internet connection
- Ensure IQOption account is verified

### Risk Guard Blocking Trades
- Check `/status` endpoint
- Verify daily limits not exceeded
- Reset if needed with `/reset`

### Confidence Too Low
- Adjust `MIN_CONFIDENCE_THRESHOLD`
- Improve AI signal quality
- Check signal generation logic

### Market Closed
- Verify trading hours for pair
- Different pairs have different schedules
- Forex closes on weekends

## Security Considerations

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Start with demo accounts** always
4. **Limit API access** to localhost in production
5. **Monitor for unusual activity** regularly
6. **Keep software updated** (dependencies)

## Performance Optimization

### For High-Frequency Trading
- Reduce wait times if testing in demo
- Use connection pooling
- Consider async processing for multiple pairs
- Cache market status

### For Production
- Use process manager (pm2, systemd)
- Set up monitoring/alerts
- Log to file, not just console
- Database for trade history (not just memory)

## Future Enhancements

Potential improvements based on documentation:

1. **Multi-AI Ensemble** - Combine multiple AI signals
2. **Sentiment Analysis** - Integrate news/social sentiment
3. **Advanced Position Sizing** - Kelly Criterion, Fixed Fractional
4. **Adaptive Martingale** - Dynamic multiplier based on volatility
5. **Telegram Integration** - Real-time alerts and control
6. **Database Logging** - Persistent trade history
7. **Backtesting** - Historical performance analysis
8. **Dashboard** - Web UI for monitoring

## Support

For issues and questions:
1. Check logs for detailed error messages
2. Verify configuration in `.env`
3. Test with demo account first
4. Review API response codes and messages

## Disclaimer

**Trading binary options involves significant risk. This bot is provided for educational purposes only. Always:**
- Start with demo accounts
- Never risk more than you can afford to lose
- Understand binary options regulations in your jurisdiction
- This is not financial advice
- Past performance does not guarantee future results

## License

See LICENSE file for details.
