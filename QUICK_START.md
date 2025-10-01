# 🚀 Quick Start Guide - N8N Trading Node

Get started with the n8n Trading Bot node in 5 minutes!

---

## ⚡ Quick Installation

### One-Line Install

```bash
cd /app/app/KAEL/KAEL && bash install.sh
```

### Manual Install (3 steps)

```bash
# 1. Install dependencies
cd /app/app/KAEL/KAEL/n8n-nodes-trading
npm install

# 2. Link to npm globally
npm link

# 3. Start API
cd .. && python3 trading_api.py
```

---

## 🎯 First Trade in n8n

### Step 1: Open n8n
```
http://localhost:5678
```

### Step 2: Create New Workflow
- Click "+ New Workflow"

### Step 3: Add Trading Bot Node
- Click "Add Node"
- Search "Trading Bot"
- Click to add

### Step 4: Configure
```javascript
{
  "apiUrl": "http://localhost:5000",
  "action": "call",               // ← Choose Call or Put
  "pair": "AUDCHF-OTC",           // ← OTC pairs are open 24/7
  "amount": 1,                    // ← Start with $1
  "duration": 1,                  // ← 1 minute
  "email": "your@email.com",      // ← Your IQ Option email
  "password": "yourpassword",     // ← Your IQ Option password
  "accountType": "demo"           // ← Use demo first!
}
```

### Step 5: Execute
- Click "Execute Node"
- Wait ~70 seconds
- See results!

---

## 📊 Expected Output

```json
{
  "success": true,
  "orderId": "13137286824",
  "action": "call",
  "pair": "AUDCHF-OTC",
  "result": "win",              // ← or "loss"
  "profit": 0.85,               // ← profit/loss amount
  "oldBalance": 10000.00,
  "newBalance": 10000.85,
  "balanceChange": 0.85,
  "timestamp": "2025-10-01 12:34:56"
}
```

---

## 🎨 Simple Workflows

### 1. Manual Trading
```
Manual Trigger → Trading Bot → Display Result
```

### 2. Scheduled Trading
```
Schedule (Every hour) → Trading Bot → Email Notification
```

### 3. Conditional Trading
```
Webhook → IF Condition → Trading Bot → Log to Database
```

---

## 🔧 Quick Commands

### Check if API is running
```bash
curl http://localhost:5000/health
```

Expected: `{"status": "ok"}`

### Check available markets
```bash
python3 check_markets.py
```

### Test a simple trade
```bash
python3 simple_trade.py
```

### Run full test suite
```bash
python3 test_n8n_node.py
```

---

## ✅ Verification Checklist

After installation, verify:

- [ ] API health check responds: `curl http://localhost:5000/health`
- [ ] Node appears in n8n: Search "Trading Bot"
- [ ] Test trade executes: Run simple_trade.py
- [ ] All tests pass: Run test_n8n_node.py

---

## 🐛 Quick Troubleshooting

### Node not showing in n8n?
```bash
# Restart n8n
sudo systemctl restart n8n
# or
n8n start
```

### API not responding?
```bash
# Check if running
ps aux | grep trading_api

# Restart
pkill -f trading_api.py
python3 trading_api.py &
```

### Trade failed?
```bash
# Check which markets are open
python3 check_markets.py

# Use OTC pairs (available 24/7)
pair: "AUDCHF-OTC"
```

---

## 📚 Next Steps

### Learn More
- Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed setup
- See [IMPROVEMENTS.md](IMPROVEMENTS.md) for feature list
- Check [TEST_REPORT.md](TEST_REPORT.md) for test results

### Production Setup
- Use gunicorn for API: `gunicorn -w 4 trading_api:app`
- Enable HTTPS
- Add authentication
- Set up monitoring

---

## 🎉 You're Ready!

Your n8n Trading Bot node is deployed and ready to use!

**Remember:**
- ✅ Always test on demo account first
- ✅ Start with small amounts
- ✅ Monitor logs carefully
- ✅ Use OTC pairs for 24/7 trading

**Happy Trading! 📈**

---

## 📞 Quick Links

| Resource | Command |
|----------|---------|
| Health Check | `curl http://localhost:5000/health` |
| Check Markets | `python3 check_markets.py` |
| Test Trade | `python3 simple_trade.py` |
| Full Tests | `python3 test_n8n_node.py` |
| API Logs | `tail -f api.log` |

---

**Installation Time**: ~2 minutes
**First Trade**: ~5 minutes
**Status**: ✅ Production Ready
