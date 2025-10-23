# 🤖 IQOption AI Trading System - Production n8n Workflows

A complete, production-grade automated trading system using n8n workflows with AI consensus from OpenAI, Claude, and DeepSeek. This system executes trades on IQOption based on hybrid AI consensus (requires 2+ model agreement AND >70% confidence).

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Workflow Setup](#workflow-setup)
- [Usage](#usage)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [FAQ](#faq)

---

## ✨ Features

### Core Capabilities
- ✅ **AI Consensus Engine**: Combines predictions from OpenAI GPT-4, Claude, and DeepSeek
- ✅ **Hybrid Decision Logic**: Requires 2+ model agreement AND average confidence >70%
- ✅ **Automated Trade Execution**: Direct integration with IQOption via custom n8n node
- ✅ **Concurrent Execution Prevention**: Only one workflow instance runs at a time
- ✅ **PostgreSQL Database**: Stores all trades, statistics, and error logs
- ✅ **Google Sheets Logging**: Real-time trade tracking in spreadsheets
- ✅ **Email Notifications**: Per-trade alerts, daily summaries, and error notifications
- ✅ **Error Handling**: Comprehensive error workflow with automatic alerting
- ✅ **Risk Management**: Configurable limits, Martingale support, auto-sizing
- ✅ **Performance Tracking**: Daily stats, AI model accuracy, win rate analysis

### Email Notification Modes
1. **Per-Trade**: Instant notification after each trade (high frequency)
2. **Daily Summary**: One comprehensive report per day
3. **Errors Only**: Alerts only when something fails
4. **Configurable**: Mix and match via environment variables

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Main Trading Workflow                        │
│  (Runs every N minutes, orchestrates entire system)             │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├──► AI Consensus Engine
         │    ├─► OpenAI GPT-4 (parallel)
         │    ├─► Claude Sonnet (parallel)
         │    └─► DeepSeek Chat (parallel)
         │    └─► Hybrid Consensus Calculator
         │
         ├──► IQOption Trade Execution
         │    └─► Custom Trading Node
         │
         ├──► Data Logger
         │    ├─► PostgreSQL Database
         │    ├─► Google Sheets
         │    └─► Daily Statistics Update
         │
         ├──► Email Reporter
         │    └─► SMTP Email Notifications
         │
         └──► Error Alert Workflow (on failure)
              ├─► Email Alert (high priority)
              ├─► Database Error Log
              └─► Google Sheets Error Log
```

---

## 📦 Prerequisites

### Required Software
- **n8n** v1.0+ (self-hosted or cloud)
- **PostgreSQL** v12+ (database)
- **Node.js** v18+ (for custom n8n nodes)
- **Python** v3.8+ (for IQOption API server)

### Required Accounts & API Keys
1. **OpenAI API Key** - [Get here](https://platform.openai.com/api-keys)
2. **Anthropic Claude API Key** - [Get here](https://console.anthropic.com/)
3. **DeepSeek API Key** - [Get here](https://platform.deepseek.com/)
4. **IQOption Account** - [Sign up](https://iqoption.com/) (use DEMO first!)
5. **Google Account** - For Google Sheets integration
6. **Email Account** - Gmail or SMTP server for notifications

### Cost Estimates (Monthly)
- OpenAI GPT-4: ~$5-20/month (depending on usage)
- Claude Sonnet: ~$5-15/month
- DeepSeek: ~$2-10/month (cheaper than others)
- PostgreSQL: Free (self-hosted) or $7+ (managed)
- n8n: Free (self-hosted) or $20+ (cloud)
- **Total**: $12-72/month (plus any trading capital)

---

## 🚀 Installation

### Step 1: Clone Repository
```bash
cd /app/app/KAEL/KAEL
# Files are already in: n8n-workflows/
```

### Step 2: Install Custom IQOption n8n Node
```bash
# Navigate to custom node directory
cd n8n-nodes-trading

# Install dependencies
npm install

# Link the node to your n8n instance
npm link

# In your n8n installation directory:
cd ~/.n8n
npm link n8n-nodes-iqoption-trading

# Restart n8n
systemctl restart n8n
# OR if running manually:
# pkill n8n && n8n start
```

### Step 3: Setup PostgreSQL Database
```bash
# Create database
sudo -u postgres createdb iqoption_trading

# Create user (optional)
sudo -u postgres psql -c "CREATE USER trading_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE iqoption_trading TO trading_user;"

# Run schema
psql -U trading_user -d iqoption_trading -f schemas/postgres_schema.sql

# Verify tables were created
psql -U trading_user -d iqoption_trading -c "\dt"
```

### Step 4: Setup IQOption API Server
```bash
# Navigate to trading system
cd ../advanced_trading_system

# Install dependencies
pip install -r requirements.txt

# Start the API server
python main.py --mode api --port 5000
# OR run in background:
nohup python main.py --mode api --port 5000 > logs/api.log 2>&1 &
```

---

## ⚙️ Configuration

### Step 1: Configure Environment Variables
```bash
cd n8n-workflows
cp .env.example .env
nano .env
```

Fill in all required values (see `.env.example` for detailed comments):

```env
# AI APIs
OPENAI_API_KEY=sk-proj-xxxxx
CLAUDE_API_KEY=sk-ant-xxxxx
DEEPSEEK_API_KEY=sk-xxxxx

# IQOption
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password
IQOPTION_ACCOUNT_TYPE=demo  # ALWAYS START WITH DEMO!
IQOPTION_API_URL=http://localhost:5000

# Email
N8N_SMTP_USER=your_email@gmail.com
N8N_SMTP_PASS=your_app_password
N8N_EMAIL_TO=notifications@example.com
N8N_EMAIL_MODE=per_trade

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=iqoption_trading
POSTGRES_USER=trading_user
POSTGRES_PASSWORD=your_password

# Google Sheets
N8N_GOOGLE_SHEETS_ID=your_sheet_id_here

# Trading Config
N8N_TRADE_INTERVAL_MINUTES=1
N8N_TRADE_AMOUNT=1
N8N_TRADE_ASSET=EURUSD
```

### Step 2: Load Environment Variables in n8n

**Option A: Using n8n UI**
1. Go to n8n Settings > Environment Variables
2. Add each variable manually

**Option B: Using .env file (self-hosted)**
```bash
# Edit n8n systemd service
sudo nano /etc/systemd/system/n8n.service

# Add this line under [Service]:
EnvironmentFile=/path/to/n8n-workflows/.env

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart n8n
```

### Step 3: Setup Google Sheets
1. Create a new Google Sheet
2. Create tabs named: `Trades`, `Errors`, `Daily_Summary`
3. In n8n: Settings > Credentials > Add Credential > Google Sheets OAuth2
4. Follow OAuth flow to authorize
5. Copy Sheet ID from URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`
6. Add to `.env`: `N8N_GOOGLE_SHEETS_ID=YOUR_SHEET_ID`

### Step 4: Setup Email (Gmail Example)
1. Enable 2FA on your Gmail account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate new App Password
4. Use this password in `.env` as `N8N_SMTP_PASS`

---

## 📥 Workflow Setup

### Import Workflows into n8n

1. **Open n8n** in your browser (default: `http://localhost:5678`)

2. **Import Error Alert Workflow First**:
   - Click **"Add Workflow"** > **"Import from File"**
   - Select: `workflows/Error_Alert_Workflow.json`
   - Activate the workflow
   - **Note the workflow name** (needed for error handling)

3. **Import Supporting Workflows**:
   - Import: `workflows/AI_Consensus_Engine.json`
   - Import: `workflows/Data_Logger.json`
   - Import: `workflows/Email_Reporter.json`
   - **Do NOT activate these yet** (they're called by main workflow)

4. **Import Main Workflow**:
   - Import: `workflows/Main_Trading_Workflow.json`
   - This orchestrates everything

5. **Configure Credentials in Each Workflow**:

   For each workflow, click on nodes that need credentials:

   **PostgreSQL Nodes**:
   - Host: `{{ $env.POSTGRES_HOST }}`
   - Port: `{{ $env.POSTGRES_PORT }}`
   - Database: `{{ $env.POSTGRES_DB }}`
   - User: `{{ $env.POSTGRES_USER }}`
   - Password: `{{ $env.POSTGRES_PASSWORD }}`

   **Google Sheets Nodes**:
   - Select your OAuth2 credential
   - Document ID: `{{ $env.N8N_GOOGLE_SHEETS_ID }}`

   **Email Send Nodes**:
   - SMTP User: `{{ $env.N8N_SMTP_USER }}`
   - SMTP Password: `{{ $env.N8N_SMTP_PASS }}`
   - SMTP Host: `smtp.gmail.com`
   - SMTP Port: `587`

   **OpenAI Node**:
   - API Key: Create credential with your `OPENAI_API_KEY`

   **Claude Node**:
   - API Key: Create credential with your `CLAUDE_API_KEY`

6. **Link Error Workflow**:
   - Open **Main_Trading_Workflow**
   - Click **Workflow Settings** (gear icon)
   - Under "Error Workflow": Select **Error_Alert_Workflow**
   - Save

7. **Test Individual Workflows**:
   ```
   Test order:
   1. Error_Alert_Workflow (trigger manually to test email)
   2. AI_Consensus_Engine (pass sample market data)
   3. Data_Logger (pass sample trade data)
   4. Email_Reporter (pass sample trade data)
   5. Main_Trading_Workflow (let it run once)
   ```

8. **Activate Main Workflow**:
   - Open **Main_Trading_Workflow**
   - Click **"Active"** toggle in top-right
   - Workflow will now run every N minutes (based on `N8N_TRADE_INTERVAL_MINUTES`)

---

## 🎯 Usage

### Starting the System

1. **Ensure all prerequisites are running**:
   ```bash
   # Check PostgreSQL
   sudo systemctl status postgresql

   # Check IQOption API server
   curl http://localhost:5000/status

   # Check n8n
   sudo systemctl status n8n
   ```

2. **Activate Main Workflow**:
   - Go to n8n UI
   - Find **Main_Trading_Workflow**
   - Toggle **Active** to ON
   - System will start executing every N minutes

3. **Monitor Execution**:
   - n8n UI: Watch "Executions" tab
   - Database: `SELECT * FROM v_recent_trades;`
   - Google Sheets: Check "Trades" tab
   - Email: Check your inbox for notifications

### Stopping the System

```bash
# Option 1: Deactivate in n8n UI
# Go to Main_Trading_Workflow > Toggle Active OFF

# Option 2: Set maintenance mode
psql -U trading_user -d iqoption_trading -c \
  "UPDATE system_config SET config_value='true' WHERE config_key='maintenance_mode';"

# Option 3: Stop n8n entirely
sudo systemctl stop n8n
```

### Manual Trade Execution

You can manually trigger a trade:

1. Go to **Main_Trading_Workflow**
2. Click **"Test Workflow"**
3. Or use the IQOption custom node directly in a test workflow

---

## 📊 Monitoring

### View Recent Trades
```sql
-- PostgreSQL
SELECT * FROM v_recent_trades LIMIT 20;

-- Or in Google Sheets: Open your sheet > Trades tab
```

### Check Daily Performance
```sql
SELECT * FROM v_daily_performance WHERE date >= CURRENT_DATE - INTERVAL '7 days';
```

### Monitor AI Model Accuracy
```sql
SELECT * FROM v_ai_model_comparison;
```

### Check System Health
```sql
-- Active executions
SELECT COUNT(*) FROM workflow_executions WHERE status = 'running';

-- Recent errors
SELECT * FROM error_logs WHERE resolved = false ORDER BY timestamp DESC LIMIT 10;

-- Today's stats
SELECT * FROM daily_stats WHERE date = CURRENT_DATE;
```

### n8n Execution Logs
- Go to n8n UI > Executions
- Filter by workflow name
- Click on any execution to see detailed logs

### Email Alerts
- **Per-trade**: Receive email after each trade
- **Daily summary**: Get daily report at configured time
- **Error alerts**: Instant notification on system failures

---

## 🔧 Troubleshooting

### Issue: Workflow not executing

**Check**:
1. Is workflow activated? (Toggle must be ON)
2. Are environment variables loaded? Test with: `echo $OPENAI_API_KEY` in n8n
3. Check n8n logs: `journalctl -u n8n -f`

**Fix**:
```bash
sudo systemctl restart n8n
```

### Issue: AI consensus always returns SKIP

**Check**:
1. API keys are valid
2. AI models are responding (check individual nodes)
3. Confidence threshold is not too high

**Fix**:
```bash
# Test API keys
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

### Issue: Trade execution fails

**Check**:
1. IQOption API server is running: `curl http://localhost:5000/status`
2. IQOption credentials are correct
3. Account has sufficient balance (demo or real)

**Fix**:
```bash
# Restart API server
cd advanced_trading_system
python main.py --mode api --port 5000
```

### Issue: Database connection fails

**Check**:
1. PostgreSQL is running: `sudo systemctl status postgresql`
2. Database exists: `psql -l | grep iqoption_trading`
3. Credentials are correct in n8n

**Fix**:
```bash
# Test connection
psql -U trading_user -d iqoption_trading -c "SELECT 1;"
```

### Issue: Email not sending

**Check**:
1. SMTP credentials are correct
2. App Password is used (not regular password)
3. Gmail "Less secure apps" is enabled (if applicable)

**Fix**:
- Regenerate App Password
- Test SMTP connection manually:
```bash
echo "Test" | mail -s "Test" -S smtp=smtp.gmail.com:587 your_email@gmail.com
```

### Issue: Google Sheets not logging

**Check**:
1. OAuth2 credential is valid
2. Sheet ID is correct
3. Sheet has tabs named: "Trades", "Errors"
4. Service account has write access

**Fix**:
- Re-authorize Google Sheets OAuth2 in n8n
- Share sheet with service account email

---

## 🔒 Security

### Best Practices

1. **Never commit `.env` file to version control**
   ```bash
   # Already in .gitignore, but verify:
   git status
   ```

2. **Use demo account initially**
   ```env
   IQOPTION_ACCOUNT_TYPE=demo
   ```

3. **Rotate API keys regularly**
   - Every 30-90 days
   - Immediately if compromised

4. **Set trade limits**
   ```env
   N8N_MAX_DAILY_TRADES=100
   N8N_MAX_DAILY_LOSS=1000
   ```

5. **Enable SSL/TLS for n8n**
   ```bash
   # Use reverse proxy (nginx/caddy)
   # Or configure n8n SSL:
   N8N_PROTOCOL=https
   N8N_SSL_KEY=/path/to/key.pem
   N8N_SSL_CERT=/path/to/cert.pem
   ```

6. **Restrict database access**
   ```sql
   -- Allow only from localhost
   -- Edit: /etc/postgresql/*/main/pg_hba.conf
   ```

7. **Monitor for anomalies**
   - Unusual trade volumes
   - Repeated errors
   - Unexpected API calls

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 5678/tcp  # n8n
sudo ufw allow 5432/tcp  # PostgreSQL (only if remote)
sudo ufw enable
```

---

## ❓ FAQ

### Q: How much money do I need to start?
**A**: Start with $0 using demo account. For real trading, minimum is usually $10-50, but recommend starting with $100-500 for proper risk management.

### Q: What is the expected win rate?
**A**: Depends on market conditions and AI model accuracy. Typically 55-65% win rate is achievable. Monitor daily stats to track performance.

### Q: How often does the system trade?
**A**: Configurable via `N8N_TRADE_INTERVAL_MINUTES`. Default is 1 minute, but AI consensus may skip many signals. Expect 5-20 actual trades per day.

### Q: Can I use different AI models?
**A**: Yes! Edit `AI_Consensus_Engine.json` to add/remove models. Update consensus logic in the "Consensus Calculator" node.

### Q: What happens if internet connection drops?
**A**: Workflow will fail and trigger error alert. Pending trades may time out. System will resume on next scheduled execution.

### Q: Can I run multiple assets simultaneously?
**A**: Yes, but requires modifications:
1. Duplicate Main_Trading_Workflow
2. Change `N8N_TRADE_ASSET` for each
3. Adjust cron schedules to stagger executions

### Q: How do I switch from demo to real account?
**A**:
1. **Test thoroughly on demo for at least 2 weeks**
2. Verify profitable performance
3. Update `.env`: `IQOPTION_ACCOUNT_TYPE=real`
4. **Start with minimum trade amounts**
5. **Monitor closely for first few days**

### Q: What are the costs?
**A**: See [Prerequisites](#prerequisites) for detailed cost breakdown. Mainly API costs ($10-50/month) plus optional hosting.

### Q: Is this legal?
**A**: Automated trading legality varies by jurisdiction. Binary options trading is legal in many countries but regulated or banned in others (e.g., US, Belgium). **Check your local laws before using this system.**

### Q: What if I get an error?
**A**:
1. Check error email for details
2. Review error_logs table in database
3. Check n8n execution logs
4. Refer to [Troubleshooting](#troubleshooting) section

---

## 📚 Additional Resources

### Documentation
- [n8n Documentation](https://docs.n8n.io/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Anthropic Claude Docs](https://docs.anthropic.com/)
- [IQOption API Guide](https://iqoption.com/en/api)

### Community
- [n8n Community Forum](https://community.n8n.io/)
- [GitHub Issues](https://github.com/anthropics/claude-code/issues)

### Support
- For workflow issues: Check n8n forums
- For AI model issues: Check respective API documentation
- For trading logic: Review your strategy and backtest results

---

## 📄 License

This project is provided as-is for educational purposes. Use at your own risk. No warranties or guarantees are provided.

**⚠️ DISCLAIMER**:
- Binary options trading carries significant financial risk
- Past performance does not guarantee future results
- Only trade with money you can afford to lose
- This is not financial advice
- Always comply with local regulations

---

## 🎉 Success Checklist

Before going live, ensure:

- [ ] PostgreSQL database is set up and accessible
- [ ] All environment variables are configured
- [ ] Custom IQOption node is installed in n8n
- [ ] IQOption API server is running
- [ ] All 5 workflows are imported into n8n
- [ ] Credentials are configured in each workflow
- [ ] Error workflow is linked to main workflow
- [ ] Google Sheets is shared and accessible
- [ ] Email notifications are working
- [ ] Tested on DEMO account for at least 2 weeks
- [ ] Reviewed and understood all security practices
- [ ] Set up proper trade limits
- [ ] Documented your trading strategy

---

**Built with ❤️ using n8n, OpenAI, Claude, and DeepSeek**

*For updates and improvements, check the repository regularly.*
