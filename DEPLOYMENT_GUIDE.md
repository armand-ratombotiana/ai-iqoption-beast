# N8N Trading Node - Deployment Guide

Complete guide to deploy and use the n8n Trading Bot node in your n8n instance.

---

## 📋 Prerequisites

### System Requirements
- Node.js 18+ installed
- Python 3.8+ installed
- n8n installed (version 0.200+)
- IQ Option account (demo or real)

### Check Installations
```bash
# Check Node.js
node --version  # Should be v18 or higher

# Check Python
python3 --version  # Should be 3.8 or higher

# Check n8n
n8n --version  # Should be 0.200 or higher
```

---

## 🚀 Deployment Steps

### Step 1: Prepare the Node Package

```bash
# Navigate to the node directory
cd /app/app/KAEL/KAEL/n8n-nodes-trading

# Install dependencies
npm install

# Verify installation
ls -la node_modules/  # Should show axios and dependencies
```

**Expected output:**
```
added 23 packages
found 0 vulnerabilities
```

---

### Step 2: Link the Node to n8n

#### Option A: Global npm link (Recommended for Development)

```bash
# In the node directory
cd /app/app/KAEL/KAEL/n8n-nodes-trading
npm link

# Link in n8n
cd ~/.n8n
npm link n8n-nodes-trading
```

#### Option B: Install in n8n Custom Nodes Directory

```bash
# Copy to n8n custom nodes
cp -r /app/app/KAEL/KAEL/n8n-nodes-trading ~/.n8n/custom/

# Install dependencies
cd ~/.n8n/custom/n8n-nodes-trading
npm install
```

#### Option C: Environment Variable (For n8n Docker)

Add to your n8n environment:
```bash
export N8N_CUSTOM_EXTENSIONS="/app/app/KAEL/KAEL/n8n-nodes-trading"
```

---

### Step 3: Start the Flask API Server

The n8n node requires the Flask API to be running.

#### Development Mode

```bash
cd /app/app/KAEL/KAEL

# Start the API
python3 trading_api.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
```

#### Production Mode (Recommended)

```bash
# Install gunicorn
pip3 install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 trading_api:app
```

#### Background Mode (with nohup)

```bash
nohup python3 trading_api.py > api.log 2>&1 &

# Check if running
ps aux | grep trading_api
```

#### Systemd Service (Linux)

Create `/etc/systemd/system/trading-api.service`:

```ini
[Unit]
Description=Trading API for n8n
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/app/app/KAEL/KAEL
ExecStart=/usr/bin/python3 trading_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable trading-api
sudo systemctl start trading-api
sudo systemctl status trading-api
```

---

### Step 4: Restart n8n

```bash
# If running as service
sudo systemctl restart n8n

# If running manually
# Press Ctrl+C to stop, then:
n8n start

# If using docker
docker restart n8n
```

---

### Step 5: Verify Node Installation

#### Method 1: Check n8n UI
1. Open n8n in browser (usually http://localhost:5678)
2. Create new workflow
3. Click "Add Node"
4. Search for "Trading Bot"
5. The node should appear in the list

#### Method 2: Check n8n logs
```bash
# Look for the node loading message
grep -i "trading" ~/.n8n/logs/*.log
```

---

## 🎨 Using the Node in n8n

### Basic Workflow Setup

1. **Create a New Workflow**
   - Open n8n
   - Click "New Workflow"

2. **Add Trading Bot Node**
   - Click "Add Node"
   - Search "Trading Bot"
   - Click to add

3. **Configure the Node**

   | Field | Value | Notes |
   |-------|-------|-------|
   | API URL | http://localhost:5000 | Change if API is on different host |
   | Action | Call or Put | Choose trading direction |
   | Trading Pair | AUDCHF-OTC | Use OTC pairs for 24/7 availability |
   | Amount | 1 | Start small for testing |
   | Duration | 1 | Minutes (1-5 typical) |
   | Email | your@email.com | IQ Option account |
   | Password | ******** | IQ Option password |
   | Account Type | Demo | Use Demo first! |

4. **Test the Node**
   - Click "Execute Node"
   - Wait ~70 seconds
   - Check the output

---

## 📊 Example Workflows

### Example 1: Manual Trading

```
┌─────────────────┐
│ Manual Trigger  │
│  (Click button) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Trading Bot    │
│  Action: Call   │
│  Pair: EUR/USD  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Show Result    │
│  (Notification) │
└─────────────────┘
```

### Example 2: Scheduled Trading

```
┌─────────────────┐
│   Schedule      │
│  Every 1 hour   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Trading Bot    │
│  Action: Call   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  IF Node        │
│ result = "win"? │
└─────┬───────┬───┘
  Yes │       │ No
      ▼       ▼
   Email   Discord
   Alert   Notify
```

### Example 3: Webhook-Based Trading

```
┌─────────────────┐
│    Webhook      │
│  Receive Signal │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Code Node     │
│  Parse Signal   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Trading Bot    │
│  Dynamic Config │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│  Log Results    │
└─────────────────┘
```

---

## 🔧 Configuration

### API URL Configuration

If your Flask API is running on a different host:

```javascript
// In n8n node configuration
{
  "apiUrl": "http://192.168.1.100:5000"  // Change to your API host
}
```

### Environment Variables

Create `.env` file in the API directory:

```bash
# /app/app/KAEL/KAEL/.env
IQ_OPTION_EMAIL=your@email.com
IQ_OPTION_PASSWORD=yourpassword
FLASK_ENV=production
FLASK_PORT=5000
```

Update `trading_api.py` to use env vars:
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variables
email = os.getenv('IQ_OPTION_EMAIL')
password = os.getenv('IQ_OPTION_PASSWORD')
```

---

## 🔒 Security Best Practices

### 1. API Security

**Add authentication to Flask API:**

```python
from flask import request
import os

API_KEY = os.getenv('API_KEY', 'your-secret-key')

@app.before_request
def check_api_key():
    if request.endpoint != 'health':
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
```

**Update n8n node to send API key:**

```javascript
// In Trading.node.js
const response = await axios.post(`${apiUrl}/trade`, payload, {
    headers: {
        'X-API-Key': this.getNodeParameter('apiKey', i)
    }
});
```

### 2. Use HTTPS

For production, use HTTPS:

```bash
# Generate SSL certificate
sudo certbot certonly --standalone -d yourdomain.com

# Run with HTTPS
gunicorn --certfile=/etc/letsencrypt/live/yourdomain.com/fullchain.pem \
         --keyfile=/etc/letsencrypt/live/yourdomain.com/privkey.pem \
         -b 0.0.0.0:443 trading_api:app
```

### 3. Credentials Management

**Use n8n credentials:**

Instead of storing passwords in workflow, create a credential type.

### 4. Rate Limiting

Add rate limiting to API:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per minute"]
)

@app.route('/trade', methods=['POST'])
@limiter.limit("5 per minute")
def execute_trade():
    # ...
```

---

## 🐛 Troubleshooting

### Node Not Appearing in n8n

**Check 1: Verify node is linked**
```bash
ls -la ~/.n8n/node_modules/ | grep n8n-nodes-trading
```

**Check 2: Check n8n logs**
```bash
tail -f ~/.n8n/logs/*.log
```

**Check 3: Verify package.json**
```bash
cat n8n-nodes-trading/package.json | grep -A 3 "n8n"
```

**Fix:**
```bash
cd /app/app/KAEL/KAEL/n8n-nodes-trading
npm unlink
npm link
cd ~/.n8n
npm unlink n8n-nodes-trading
npm link n8n-nodes-trading
# Restart n8n
```

---

### API Connection Failed

**Check 1: Is API running?**
```bash
curl http://localhost:5000/health
```

**Check 2: Check API logs**
```bash
tail -f api.log
```

**Check 3: Test API endpoint**
```bash
curl -X POST http://localhost:5000/trade \
  -H "Content-Type: application/json" \
  -d '{"email":"test","password":"test"}'
```

**Fix:**
```bash
# Restart API
pkill -f trading_api.py
python3 trading_api.py &
```

---

### Trade Execution Failed

**Check 1: Market is open**
```bash
python3 check_markets.py
```

**Check 2: Credentials are correct**
- Verify email/password
- Check account type (demo/real)

**Check 3: API logs**
```bash
grep -i "error" api.log
```

---

### Node Execution Timeout

**Issue**: Trade takes too long (>2 minutes)

**Fix**: Increase timeout in Trading.node.js:
```javascript
axios.post(`${apiUrl}/trade`, payload, {
    timeout: 300000  // 5 minutes
});
```

---

## 📈 Monitoring & Logging

### API Logs

```bash
# View real-time logs
tail -f api.log

# Search for errors
grep -i "error" api.log

# View specific trade
grep "Order ID: 12345" api.log
```

### n8n Execution Logs

In n8n UI:
1. Go to "Executions"
2. Click on execution
3. View detailed logs

### System Monitoring

```bash
# Check API process
ps aux | grep trading_api

# Check API port
netstat -tuln | grep 5000

# Check API health
watch -n 5 'curl -s http://localhost:5000/health'
```

---

## 🚀 Production Deployment

### 1. Use Process Manager (PM2)

```bash
# Install PM2
npm install -g pm2

# Start API with PM2
pm2 start trading_api.py --name trading-api --interpreter python3

# Start n8n with PM2
pm2 start n8n --name n8n-server

# Save configuration
pm2 save

# Set to start on boot
pm2 startup
```

### 2. Use Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  trading-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: always

  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_CUSTOM_EXTENSIONS=/custom
    volumes:
      - ./n8n-nodes-trading:/custom/n8n-nodes-trading
    depends_on:
      - trading-api
    restart: always
```

Start:
```bash
docker-compose up -d
```

### 3. Use Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/trading-api

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/trading-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📊 Performance Optimization

### 1. API Connection Pooling

Update `trading_api.py`:
```python
# Keep connections alive
api_connections = {}

def get_api(email):
    if email not in api_connections:
        api_connections[email] = IQ_Option(email, password)
        api_connections[email].connect()
    return api_connections[email]
```

### 2. Caching

Add caching for market data:
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=60)
def get_open_markets():
    # Cache for 60 seconds
    pass
```

### 3. Async Execution

For multiple trades:
```python
import asyncio

async def execute_multiple_trades(trades):
    tasks = [execute_trade_async(t) for t in trades]
    return await asyncio.gather(*tasks)
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed
- [ ] n8n installed
- [ ] Dependencies installed (`npm install`, `pip install`)

### Deployment
- [ ] Node linked to n8n
- [ ] Flask API running
- [ ] n8n restarted
- [ ] Node appears in n8n UI

### Testing
- [ ] Health check passes
- [ ] Test trade executes
- [ ] Results returned correctly
- [ ] Logs working

### Security
- [ ] API authentication enabled
- [ ] HTTPS configured (production)
- [ ] Environment variables used
- [ ] Credentials secured

### Monitoring
- [ ] Logging configured
- [ ] Process manager setup
- [ ] Auto-restart enabled
- [ ] Monitoring dashboard (optional)

---

## 🎉 Success Confirmation

After deployment, verify everything works:

```bash
# 1. Check API
curl http://localhost:5000/health
# Expected: {"status": "ok"}

# 2. Check n8n node
# Open n8n, search "Trading Bot", should appear

# 3. Execute test trade
# Run workflow with demo account

# 4. Check logs
tail -f api.log
# Should see: [TRADE REQUEST], [CONNECTED], [RESULT]
```

**✅ If all checks pass, deployment is successful!**

---

## 📞 Support & Resources

- **Documentation**: See `README_IMPLEMENTATION.md`
- **Improvements**: See `IMPROVEMENTS.md`
- **Tests**: Run `python3 test_n8n_node.py`
- **Troubleshooting**: See sections above

---

## 🔄 Updating the Node

To update after code changes:

```bash
# 1. Update code
cd /app/app/KAEL/KAEL/n8n-nodes-trading

# 2. Reinstall if needed
npm install

# 3. Restart n8n
sudo systemctl restart n8n
# or
pm2 restart n8n-server
```

---

**Last Updated**: 2025-10-01
**Version**: 1.0.0
**Status**: Production Ready
