# 🚀 Quick Start Guide - IQOption AI Trading System

Get up and running in **15 minutes**! This guide covers the absolute essentials.

## ⚡ Prerequisites Checklist

Before starting, have these ready:

- [ ] n8n installed and running
- [ ] PostgreSQL installed
- [ ] Python 3.8+ with pip
- [ ] OpenAI API key
- [ ] Claude API key
- [ ] DeepSeek API key
- [ ] IQOption demo account
- [ ] Gmail account (for notifications)
- [ ] Google Sheets access

---

## 📝 Step-by-Step Setup

### 1️⃣ Database Setup (5 minutes)

```bash
# Create database
sudo -u postgres createdb iqoption_trading

# Create user
sudo -u postgres psql <<EOF
CREATE USER trading_user WITH PASSWORD 'SecurePass123!';
GRANT ALL PRIVILEGES ON DATABASE iqoption_trading TO trading_user;
EOF

# Load schema
cd /app/app/KAEL/KAEL/n8n-workflows
psql -U trading_user -d iqoption_trading -f schemas/postgres_schema.sql

# Verify
psql -U trading_user -d iqoption_trading -c "\dt"
# Should show: trades, daily_stats, workflow_executions, error_logs, etc.
```

### 2️⃣ Environment Configuration (3 minutes)

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Minimum required variables**:
```env
# AI APIs
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
CLAUDE_API_KEY=sk-ant-YOUR_KEY_HERE
DEEPSEEK_API_KEY=sk-YOUR_KEY_HERE

# IQOption (use demo!)
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password
IQOPTION_ACCOUNT_TYPE=demo
IQOPTION_API_URL=http://localhost:5000

# Email
N8N_SMTP_USER=your_gmail@gmail.com
N8N_SMTP_PASS=your_app_password_16_chars
N8N_EMAIL_TO=your_notifications@gmail.com

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=iqoption_trading
POSTGRES_USER=trading_user
POSTGRES_PASSWORD=SecurePass123!

# Trading
N8N_TRADE_INTERVAL_MINUTES=1
N8N_TRADE_AMOUNT=1
N8N_TRADE_ASSET=EURUSD
```

### 3️⃣ Install Custom Node (2 minutes)

```bash
# Install dependencies
cd /app/app/KAEL/KAEL/n8n-nodes-trading
npm install

# Link to n8n
npm link
cd ~/.n8n/nodes
npm link n8n-nodes-iqoption-trading

# Restart n8n
sudo systemctl restart n8n
# OR: pkill n8n && n8n start &
```

### 4️⃣ Start API Server (1 minute)

```bash
cd /app/app/KAEL/KAEL/advanced_trading_system

# Install dependencies (first time only)
pip install -r requirements.txt

# Start server
python main.py --mode api --port 5000 &

# Verify it's running
curl http://localhost:5000/status
# Should return: {"status": "ok", ...}
```

### 5️⃣ Setup Google Sheets (2 minutes)

1. Create new Google Sheet: [sheets.google.com](https://sheets.google.com)
2. Create tabs: `Trades`, `Errors`, `Daily_Summary`
3. Copy Sheet ID from URL: `https://docs.google.com/spreadsheets/d/COPY_THIS_ID/edit`
4. Add to `.env`: `N8N_GOOGLE_SHEETS_ID=YOUR_SHEET_ID`

### 6️⃣ Import Workflows (2 minutes)

1. Open n8n: `http://localhost:5678`
2. Import in this order:
   - `workflows/Error_Alert_Workflow.json` → Activate
   - `workflows/AI_Consensus_Engine.json` → Leave inactive
   - `workflows/Data_Logger.json` → Leave inactive
   - `workflows/Email_Reporter.json` → Leave inactive
   - `workflows/Main_Trading_Workflow.json` → Leave inactive for now

3. **Configure credentials** in each workflow:
   - PostgreSQL: Use values from `.env`
   - Google Sheets: Create OAuth2 credential
   - Email/SMTP: Use Gmail credentials
   - OpenAI/Claude: Create API credentials

### 7️⃣ Test System (5 minutes)

```bash
# Test database connection
psql -U trading_user -d iqoption_trading -c "SELECT 1;"

# Test API server
curl http://localhost:5000/status

# Test email (optional)
# In n8n, manually execute Error_Alert_Workflow to test email

# Test AI Consensus Engine
# Manually execute AI_Consensus_Engine with sample data
```

### 8️⃣ Activate Main Workflow (1 minute)

1. Open **Main_Trading_Workflow** in n8n
2. Click **Workflow Settings** (gear icon)
3. Set **Error Workflow** to: `Error_Alert_Workflow`
4. Save
5. Toggle **Active** to ON 🟢
6. System is now live!

---

## ✅ Verification

Check that everything is working:

```bash
# 1. Check workflow executions in n8n UI
# Go to: Executions tab

# 2. Check database logs
psql -U trading_user -d iqoption_trading -c "SELECT * FROM v_recent_trades LIMIT 5;"

# 3. Check Google Sheets
# Open your sheet and look for new rows in "Trades" tab

# 4. Check email
# You should receive notifications based on N8N_EMAIL_MODE

# 5. Monitor API server logs
tail -f /app/app/KAEL/KAEL/advanced_trading_system/logs/api.log
```

---

## 🎯 What Happens Next?

Once activated, the system will:

1. **Every 1 minute** (or your configured interval):
   - Check for running executions (prevent overlaps)
   - Query 3 AI models in parallel
   - Calculate hybrid consensus
   - Execute trade if conditions met (2+ agreement + >70% confidence)
   - Log to database and Google Sheets
   - Send email notification
   - Update daily statistics

2. **On errors**:
   - Trigger Error_Alert_Workflow
   - Send high-priority email alert
   - Log error to database and sheets

3. **Trade execution flow**:
   - Prepare payload with AI consensus data
   - Call IQOption API via custom node
   - Wait for trade result
   - Log outcome (WIN/LOSS/ERROR)
   - Update performance metrics

---

## 🛑 How to Stop

```bash
# Option 1: Deactivate in n8n UI
# Open Main_Trading_Workflow > Toggle Active OFF

# Option 2: Stop API server
pkill -f "python main.py"

# Option 3: Stop n8n (nuclear option)
sudo systemctl stop n8n
```

---

## 📊 Monitoring Dashboard

Quick queries for monitoring:

```sql
-- Today's performance
SELECT * FROM v_daily_performance WHERE date = CURRENT_DATE;

-- Last 10 trades
SELECT * FROM v_recent_trades LIMIT 10;

-- Error summary
SELECT COUNT(*) as unresolved_errors FROM error_logs WHERE resolved = false;

-- Win rate
SELECT
  COUNT(*) as total,
  SUM(CASE WHEN trade_result = 'WIN' THEN 1 ELSE 0 END) as wins,
  ROUND(
    SUM(CASE WHEN trade_result = 'WIN' THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100,
    1
  ) as win_rate_pct
FROM trades
WHERE DATE(timestamp) >= CURRENT_DATE - INTERVAL '7 days';
```

---

## 🚨 Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Workflow not executing | Check if Active toggle is ON |
| AI consensus returns SKIP | Verify API keys are valid |
| Trade execution fails | Check IQOption API server: `curl localhost:5000/status` |
| Database errors | Restart PostgreSQL: `sudo systemctl restart postgresql` |
| Email not sending | Regenerate Gmail App Password |
| Google Sheets not logging | Re-authorize OAuth2 credential |

---

## 🎓 Next Steps

1. **Monitor for 24-48 hours** on demo account
2. **Review daily statistics** to assess performance
3. **Adjust parameters** if needed:
   - Trade interval
   - Confidence threshold
   - Trade amount
   - Email notification mode
4. **Backtest strategy** before going live
5. **Only switch to real account** after proven success on demo

---

## 📚 Full Documentation

For detailed information, see:
- **Full Setup Guide**: [README.md](README.md)
- **Database Schema**: [schemas/postgres_schema.sql](schemas/postgres_schema.sql)
- **Environment Variables**: [.env.example](.env.example)

---

## ⚠️ Important Reminders

- ✅ **Always start with demo account**
- ✅ **Never share API keys or credentials**
- ✅ **Set trade limits** to protect capital
- ✅ **Monitor system regularly** (at least daily)
- ✅ **Comply with local trading regulations**
- ❌ **Do not trade more than you can afford to lose**

---

**🎉 You're all set! The system is now running and will trade automatically based on AI consensus.**

**Need help? Check [README.md](README.md) for detailed troubleshooting and FAQs.**
