# n8n Trading Node - Simple Put/Call Execution

A production-ready n8n custom node for executing Put or Call trades via IQ Option.

## ✨ New Features (Based on BOT_KAEL.py Analysis)

- ✅ **Market Validation** - Checks if market is open before trading
- ✅ **Payout Information** - Shows expected profit before trade
- ✅ **Improved Result Checking** - Retries up to 20 times for reliable results
- ✅ **Balance Tracking** - Tracks old/new balance and changes
- ✅ **Better Error Handling** - Detailed error messages
- ✅ **Connection Validation** - Ensures stable connection before trading
- ✅ **Enhanced Logging** - Complete trade lifecycle logging

## Installation

### Option 1: Install in n8n (Community Node)

1. In n8n, go to **Settings** > **Community Nodes**
2. Click **Install**
3. Enter the package name or local path

### Option 2: Local Development

```bash
cd n8n-nodes-trading
npm install
npm link
```

Then in your n8n installation:
```bash
cd ~/.n8n
npm link n8n-nodes-trading
```

## Setup API Server

The node communicates with your Python trading bot via a Flask API.

1. Install dependencies:
```bash
pip install flask iqoptionapi
```

2. Run the API server:
```bash
python trading_api.py
```

The API will be available at `http://localhost:5000`

## Usage in n8n

1. Add the **Trading Bot** node to your workflow
2. Configure the parameters:
   - **Action**: Choose "Call" or "Put"
   - **Trading Pair**: e.g., "EURUSD", "GBPUSD"
   - **Amount**: Trade amount in dollars
   - **Duration**: Trade duration in minutes
   - **Email**: Your IQ Option email
   - **Password**: Your IQ Option password
   - **Account Type**: "Demo" or "Real"

## Example Workflow

```
Trigger (Schedule/Webhook) → Trading Bot → Send Email/Notification
```

## API Endpoints

### POST /trade
Execute a trade

**Request Body:**
```json
{
  "email": "your@email.com",
  "password": "password",
  "action": "call",
  "pair": "EURUSD",
  "amount": 1,
  "duration": 1,
  "accountType": "demo"
}
```

**Response:**
```json
{
  "success": true,
  "orderId": "123456",
  "action": "call",
  "pair": "EURUSD",
  "amount": 1,
  "duration": 1,
  "profit": 0.85,
  "result": "win",
  "payout": 0.85,
  "oldBalance": 10000.00,
  "newBalance": 10000.85,
  "balanceChange": 0.85,
  "timestamp": "2025-10-01 12:34:56"
}
```

### GET /health
Health check endpoint

## Quick Test

### 1. Check Available Markets
```bash
python3 check_markets.py
```

### 2. Test Simple Trade
```bash
python3 simple_trade.py
```

### 3. Start API Server
```bash
python3 trading_api.py
```

### 4. Test API
```bash
python3 test_api.py
```

## Improvements Documentation

See [IMPROVEMENTS.md](../IMPROVEMENTS.md) for detailed documentation of all improvements based on BOT_KAEL.py analysis.

## Troubleshooting

### Trade Execution Failed
- Check if market is open using `check_markets.py`
- Use OTC pairs (e.g., `AUDCHF-OTC`) which are often open
- Verify your account has sufficient balance

### Connection Issues
- The improved code includes automatic reconnection
- Retries up to 3 times on connection failure
- Check your internet connection

### Result Not Available
- The code retries up to 20 times (10 seconds)
- Usually resolves automatically
- If persists, check IQ Option API status

## Security Notes

- Always use environment variables for credentials in production
- Start with demo account for testing
- The API should be secured with authentication in production
- Consider using HTTPS for API communication

## Files Structure

```
├── n8n-nodes-trading/          # n8n node package
│   ├── package.json            # Node configuration
│   ├── nodes/Trading/
│   │   ├── Trading.node.js     # Node implementation
│   │   └── trading.svg         # Node icon
│   └── README.md               # This file
├── trading_api.py              # Flask API server (improved)
├── simple_trade.py             # Standalone test script (improved)
├── check_markets.py            # Market availability checker
├── test_api.py                 # API testing script
└── IMPROVEMENTS.md             # Detailed improvements documentation
```

## License

MIT
