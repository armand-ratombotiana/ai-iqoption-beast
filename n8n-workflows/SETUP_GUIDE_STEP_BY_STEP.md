# 🎯 Step-by-Step Setup Guide for n8n Workflows

## Complete walkthrough from zero to fully operational trading system

---

## 📋 Table of Contents

1. [Prerequisites Check](#step-1-prerequisites-check)
2. [Database Setup](#step-2-database-setup)
3. [Environment Configuration](#step-3-environment-configuration)
4. [Install Custom n8n Node](#step-4-install-custom-n8n-node)
5. [Start IQOption API Server](#step-5-start-iqoption-api-server)
6. [Setup Google Sheets](#step-6-setup-google-sheets)
7. [Import Workflows into n8n](#step-7-import-workflows-into-n8n)
8. [Configure Credentials in n8n](#step-8-configure-credentials-in-n8n)
9. [Test Individual Workflows](#step-9-test-individual-workflows)
10. [Activate Main Workflow](#step-10-activate-main-workflow)
11. [Monitor and Verify](#step-11-monitor-and-verify)

---

## ⏰ Time Required

- **Initial Setup**: 45-60 minutes
- **Testing**: 30 minutes
- **Total**: ~90 minutes

---

# STEP 1: Prerequisites Check

## ✅ What You Need

### Software
- [ ] **n8n** installed and running (version 1.0+)
- [ ] **PostgreSQL** installed (version 12+)
- [ ] **Python** 3.8+ with pip
- [ ] **Node.js** 18+ with npm
- [ ] **curl** (for testing)
- [ ] **psql** (PostgreSQL client)

### Accounts & API Keys
- [ ] **OpenAI API Key** - [Get here](https://platform.openai.com/api-keys)
- [ ] **Claude API Key** - [Get here](https://console.anthropic.com/)
- [ ] **DeepSeek API Key** - [Get here](https://platform.deepseek.com/)
- [ ] **IQOption Account** - [Sign up](https://iqoption.com/) (DEMO account)
- [ ] **Gmail Account** - For email notifications
- [ ] **Google Account** - For Google Sheets integration

### Verification

```bash
# Check software versions
n8n --version           # Should show v1.0+
psql --version          # Should show PostgreSQL 12+
python3 --version       # Should show Python 3.8+
node --version          # Should show v18+
npm --version           # Should show 9+

# If any missing, install them first!
```

**Checkpoint**: All software installed? ✅ → Proceed to Step 2

---

# STEP 2: Database Setup

## 🗄️ Create PostgreSQL Database

### Option A: Using psql (Recommended)

```bash
# Navigate to n8n-workflows directory
cd /app/app/KAEL/KAEL/n8n-workflows

# Create database
sudo -u postgres psql -c "CREATE DATABASE iqoption_trading;"

# Create user with password
sudo -u postgres psql <<EOF
CREATE USER trading_user WITH PASSWORD 'YourSecurePassword123!';
GRANT ALL PRIVILEGES ON DATABASE iqoption_trading TO trading_user;
ALTER DATABASE iqoption_trading OWNER TO trading_user;
EOF

# Load schema
psql -U trading_user -d iqoption_trading -f schemas/postgres_schema.sql

# Enter password when prompted: YourSecurePassword123!
```

### Option B: Using Docker (Alternative)

```bash
# Start PostgreSQL in Docker
docker run -d \
  --name iqoption_postgres \
  -e POSTGRES_DB=iqoption_trading \
  -e POSTGRES_USER=trading_user \
  -e POSTGRES_PASSWORD=YourSecurePassword123! \
  -p 5432:5432 \
  -v $(pwd)/schemas/postgres_schema.sql:/docker-entrypoint-initdb.d/init.sql \
  postgres:15-alpine
```

### Verify Database Setup

```bash
# Test connection
psql -U trading_user -d iqoption_trading -c "SELECT 1;"
# Should output: "?column? \n 1"

# Verify tables were created
psql -U trading_user -d iqoption_trading -c "\dt"
# Should show: trades, daily_stats, workflow_executions, error_logs, etc.

# Check table counts
psql -U trading_user -d iqoption_trading -c "
SELECT
  'trades' as table_name, COUNT(*) FROM trades
UNION ALL SELECT 'daily_stats', COUNT(*) FROM daily_stats
UNION ALL SELECT 'error_logs', COUNT(*) FROM error_logs;"
# All should show 0 (empty tables)
```

**Checkpoint**: Database created and tables exist? ✅ → Proceed to Step 3

---

# STEP 3: Environment Configuration

## ⚙️ Setup Environment Variables

### Create .env File

```bash
cd /app/app/KAEL/KAEL/n8n-workflows

# Copy template
cp .env.example .env

# Edit with your favorite editor
nano .env
# OR
vim .env
# OR
code .env  # VS Code
```

### Fill in Required Variables

**CRITICAL: Replace ALL placeholder values!**

```env
# =====================================================
# AI MODEL API KEYS
# =====================================================
OPENAI_API_KEY=sk-proj-YOUR_REAL_KEY_HERE
CLAUDE_API_KEY=sk-ant-YOUR_REAL_KEY_HERE
DEEPSEEK_API_KEY=sk-YOUR_REAL_KEY_HERE

# =====================================================
# IQOPTION CREDENTIALS
# =====================================================
IQOPTION_EMAIL=your_real_email@example.com
IQOPTION_PASSWORD=your_real_password
IQOPTION_ACCOUNT_TYPE=demo              # ALWAYS demo for testing!
IQOPTION_API_URL=http://localhost:5000

# =====================================================
# EMAIL / SMTP CONFIGURATION (Gmail Example)
# =====================================================
N8N_SMTP_USER=your_gmail@gmail.com
N8N_SMTP_PASS=your_16_char_app_password  # NOT your Gmail password!
N8N_SMTP_HOST=smtp.gmail.com
N8N_SMTP_PORT=587
N8N_EMAIL_TO=your_notifications@gmail.com
N8N_EMAIL_MODE=per_trade

# =====================================================
# POSTGRESQL DATABASE
# =====================================================
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=iqoption_trading
POSTGRES_USER=trading_user
POSTGRES_PASSWORD=YourSecurePassword123!  # Same as Step 2

# =====================================================
# GOOGLE SHEETS
# =====================================================
N8N_GOOGLE_SHEETS_ID=YOUR_SHEET_ID_WILL_BE_ADDED_IN_STEP_6

# =====================================================
# TRADING CONFIGURATION
# =====================================================
N8N_TRADE_INTERVAL_MINUTES=1
N8N_TRADE_AMOUNT=1
N8N_TRADE_ASSET=EURUSD
```

### Gmail App Password Setup

If using Gmail for email notifications:

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to your Google Account
3. Enable 2-Factor Authentication (if not already enabled)
4. Click **"App passwords"**
5. Select app: **"Mail"**, device: **"Other (Custom name)"**
6. Enter name: **"n8n Trading System"**
7. Click **"Generate"**
8. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
9. Paste into `.env` as `N8N_SMTP_PASS=abcdefghijklmnop` (no spaces)

### Verify .env File

```bash
# Check that all required variables are set
grep "^[A-Z]" .env | grep -v "^#" | head -20

# Should NOT see any lines with "your_" or "xxxxx" or "change_me"
# If you do, those need to be replaced with real values!
```

**Checkpoint**: All variables configured with real values? ✅ → Proceed to Step 4

---

# STEP 4: Install Custom n8n Node

## 📦 Install IQOption Custom Node

### Step 4.1: Navigate to Custom Node Directory

```bash
cd /app/app/KAEL/KAEL/n8n-nodes-trading

# Verify files exist
ls -la
# Should see: credentials/, nodes/, package.json
```

### Step 4.2: Install Dependencies

```bash
# Install npm dependencies
npm install

# Should complete without errors
```

### Step 4.3: Link to n8n

```bash
# Create global link
npm link

# Navigate to n8n directory
cd ~/.n8n/custom

# If directory doesn't exist, create it
mkdir -p ~/.n8n/custom
cd ~/.n8n/custom

# Link the custom node
npm link n8n-nodes-iqoption-trading

# Alternative: Copy directly
# cp -r /app/app/KAEL/KAEL/n8n-nodes-trading ~/.n8n/custom/
```

### Step 4.4: Restart n8n

```bash
# If running as systemd service
sudo systemctl restart n8n

# If running manually
pkill n8n
n8n start &

# If running with pm2
pm2 restart n8n

# Wait 10 seconds for n8n to fully restart
sleep 10
```

### Step 4.5: Verify Node Installation

```bash
# Open n8n in browser
# http://localhost:5678

# In n8n UI:
# 1. Click "Add node" (+)
# 2. Search for "IQOption"
# 3. You should see "IQOption AI Trading Bot" node
```

**Checkpoint**: Custom node appears in n8n? ✅ → Proceed to Step 5

---

# STEP 5: Start IQOption API Server

## 🚀 Launch Trading API Server

### Step 5.1: Navigate to Trading System

```bash
cd /app/app/KAEL/KAEL/advanced_trading_system
```

### Step 5.2: Install Python Dependencies (First Time Only)

```bash
# Install requirements
pip install -r requirements.txt

# Should install: flask, requests, iqoptionapi, etc.
```

### Step 5.3: Start API Server

**Option A: Foreground (for testing)**

```bash
python main.py --mode api --port 5000

# You should see:
# * Running on http://0.0.0.0:5000
# * Debug mode: off
```

**Option B: Background (for production)**

```bash
# Start in background
nohup python main.py --mode api --port 5000 > logs/api.log 2>&1 &

# Save process ID
echo $! > api.pid

# Check it's running
ps aux | grep "python main.py"
```

**Option C: Using systemd (recommended for production)**

Create service file:

```bash
sudo nano /etc/systemd/system/iqoption-api.service
```

Paste this:

```ini
[Unit]
Description=IQOption Trading API Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/app/app/KAEL/KAEL/advanced_trading_system
ExecStart=/usr/bin/python3 main.py --mode api --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl start iqoption-api
sudo systemctl enable iqoption-api
sudo systemctl status iqoption-api
```

### Step 5.4: Verify API Server

```bash
# Test API status
curl http://localhost:5000/status

# Expected response:
# {
#   "status": "ok",
#   "timestamp": "2025-01-15T12:34:56",
#   "version": "1.0.0"
# }

# If you get connection error:
# - Check if server is running: ps aux | grep python
# - Check logs: tail -f logs/api.log
# - Check firewall: sudo ufw status
```

**Checkpoint**: API server responds to /status? ✅ → Proceed to Step 6

---

# STEP 6: Setup Google Sheets

## 📊 Create and Configure Google Sheets

### Step 6.1: Create New Google Sheet

1. Go to: https://sheets.google.com
2. Click **"Blank"** to create new spreadsheet
3. Rename to: **"IQOption Trading Log"**

### Step 6.2: Create Required Tabs

Click **"+"** at bottom to add new sheets:

1. **Trades** (rename Sheet1)
2. **Errors** (add new)
3. **Daily_Summary** (add new)

### Step 6.3: Add Headers (Optional but Recommended)

**Trades Tab** - Row 1:
```
trade_id | timestamp | asset | direction | ai_confidence | trade_result | payout | amount | duration | model_votes | error_message
```

**Errors Tab** - Row 1:
```
timestamp | workflow_name | error_node | error_message | resolved
```

**Daily_Summary Tab** - Row 1:
```
date | total_trades | wins | losses | win_rate | total_profit
```

### Step 6.4: Get Sheet ID

From the URL:
```
https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p/edit
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                         This is your SHEET ID
```

Copy the ID and add to `.env`:

```bash
nano /app/app/KAEL/KAEL/n8n-workflows/.env

# Add this line:
N8N_GOOGLE_SHEETS_ID=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
```

### Step 6.5: Share Sheet (Important!)

1. Click **"Share"** button (top-right)
2. Click **"Anyone with the link"** → **"Editor"**
3. Click **"Copy link"**
4. Click **"Done"**

**Note**: We'll configure OAuth2 in Step 8

**Checkpoint**: Sheet created with 3 tabs and ID added to .env? ✅ → Proceed to Step 7

---

# STEP 7: Import Workflows into n8n

## 📥 Import All 5 Workflows

### Step 7.1: Access n8n

```bash
# Open n8n in browser
http://localhost:5678

# Or if using different port:
http://localhost:YOUR_PORT
```

### Step 7.2: Import Error Workflow FIRST

**This is critical - error workflow must exist before others!**

1. Click **"Workflows"** in left sidebar
2. Click **"Add Workflow"** (top-right)
3. Click **three dots (⋮)** → **"Import from File"**
4. Navigate to: `/app/app/KAEL/KAEL/n8n-workflows/workflows/`
5. Select: **Error_Alert_Workflow.json**
6. Click **"Open"**
7. Workflow imports successfully ✅
8. Click **"Save"** (Ctrl+S)
9. **ACTIVATE IT**: Toggle **"Active"** switch to ON (top-right)
10. Note the workflow name: **"Error_Alert_Workflow"**

### Step 7.3: Import Supporting Workflows

Import these in order (DO NOT activate yet):

**A. AI Consensus Engine**
1. Click **"Workflows"** → **"Add Workflow"**
2. Import: **AI_Consensus_Engine.json**
3. **Save** (Ctrl+S)
4. Leave **INACTIVE** (will be called by main workflow)

**B. Data Logger**
1. Click **"Workflows"** → **"Add Workflow"**
2. Import: **Data_Logger.json**
3. **Save** (Ctrl+S)
4. Leave **INACTIVE**

**C. Email Reporter**
1. Click **"Workflows"** → **"Add Workflow"**
2. Import: **Email_Reporter.json**
3. **Save** (Ctrl+S)
4. Leave **INACTIVE**

### Step 7.4: Import Main Workflow (Last!)

1. Click **"Workflows"** → **"Add Workflow"**
2. Import: **Main_Trading_Workflow.json**
3. **Save** (Ctrl+S)
4. **DO NOT ACTIVATE YET** (we need to configure credentials first)

### Step 7.5: Verify All Workflows Imported

Click **"Workflows"** in sidebar - you should see:

- ✅ Error_Alert_Workflow (Active: ON)
- ⚪ AI_Consensus_Engine (Active: OFF)
- ⚪ Data_Logger (Active: OFF)
- ⚪ Email_Reporter (Active: OFF)
- ⚪ Main_Trading_Workflow (Active: OFF)

**Checkpoint**: All 5 workflows imported? ✅ → Proceed to Step 8

---

# STEP 8: Configure Credentials in n8n

## 🔐 Setup All Required Credentials

### Step 8.1: PostgreSQL Credentials

1. Click **"Settings"** (gear icon, bottom-left)
2. Click **"Credentials"**
3. Click **"Add Credential"**
4. Search for: **"PostgreSQL"**
5. Fill in:
   ```
   Name: PostgreSQL Trading DB
   Host: localhost
   Database: iqoption_trading
   User: trading_user
   Password: YourSecurePassword123!
   Port: 5432
   ```
6. Click **"Test Connection"** - should show ✅ Success
7. Click **"Save"**

### Step 8.2: Google Sheets OAuth2 Credentials

1. Click **"Credentials"** → **"Add Credential"**
2. Search for: **"Google Sheets OAuth2 API"**
3. Fill in:
   ```
   Name: Google Sheets OAuth2
   ```
4. Click **"Connect my account"**
5. **Sign in with Google** (popup opens)
6. Select your Google account
7. Click **"Allow"** (grant permissions)
8. Popup closes - credential saved ✅
9. Click **"Save"**

### Step 8.3: OpenAI API Credentials

1. **"Credentials"** → **"Add Credential"**
2. Search for: **"OpenAI"** or **"OpenAI API"**
3. Fill in:
   ```
   Name: OpenAI API
   API Key: sk-proj-YOUR_REAL_KEY
   ```
4. Click **"Save"**

### Step 8.4: Anthropic (Claude) Credentials

1. **"Credentials"** → **"Add Credential"**
2. Search for: **"Anthropic"** or **"Claude"**
3. Fill in:
   ```
   Name: Anthropic Claude API
   API Key: sk-ant-YOUR_REAL_KEY
   ```
4. Click **"Save"**

### Step 8.5: SMTP (Email) Credentials

1. **"Credentials"** → **"Add Credential"**
2. Search for: **"SMTP"**
3. Fill in:
   ```
   Name: SMTP Account
   User: your_gmail@gmail.com
   Password: your_16_char_app_password
   Host: smtp.gmail.com
   Port: 587
   Security: TLS
   ```
4. Click **"Test Connection"** (if available)
5. Click **"Save"**

### Step 8.6: Assign Credentials to Workflows

Now we need to go through each workflow and assign the credentials we just created.

**For each workflow:**

1. Open the workflow
2. Click on each node that shows ⚠️ warning (missing credentials)
3. Select the appropriate credential from dropdown
4. Save the workflow

**Detailed steps per workflow:**

#### A. Error_Alert_Workflow

1. Open **Error_Alert_Workflow**
2. Click **"Send Error Email"** node
   - Credential: Select **"SMTP Account"**
3. Click **"Log Error to Database"** node
   - Credential: Select **"PostgreSQL Trading DB"**
4. Click **"Log Error to Sheets"** node
   - Credential: Select **"Google Sheets OAuth2"**
   - Document ID: Type `{{ $env.N8N_GOOGLE_SHEETS_ID }}`
   - Sheet: **"Errors"**
5. **Save** (Ctrl+S)

#### B. AI_Consensus_Engine

1. Open **AI_Consensus_Engine**
2. Click **"OpenAI Analysis"** node
   - Credential: Select **"OpenAI API"**
3. Click **"Claude Analysis"** node
   - Credential: Select **"Anthropic Claude API"**
4. **DeepSeek** node uses HTTP Request (no credential needed, API key from env)
5. **Save** (Ctrl+S)

#### C. Data_Logger

1. Open **Data_Logger**
2. Click **"Log to PostgreSQL"** node
   - Credential: Select **"PostgreSQL Trading DB"**
3. Click **"Log to Google Sheets"** node
   - Credential: Select **"Google Sheets OAuth2"**
   - Document ID: `{{ $env.N8N_GOOGLE_SHEETS_ID }}`
   - Sheet: **"Trades"**
4. Click **"Update Daily Stats"** node
   - Credential: Select **"PostgreSQL Trading DB"**
5. **Save** (Ctrl+S)

#### D. Email_Reporter

1. Open **Email_Reporter**
2. Click **"Fetch Daily Stats"** node
   - Credential: Select **"PostgreSQL Trading DB"**
3. Click **"Send Email"** node
   - Credential: Select **"SMTP Account"**
4. **Save** (Ctrl+S)

#### E. Main_Trading_Workflow

1. Open **Main_Trading_Workflow**
2. Click **"Check Running Executions"** node
   - Credential: Select **"PostgreSQL Trading DB"**
3. Click **"Register Execution"** node
   - Credential: Select **"PostgreSQL Trading DB"**
4. Click **"Mark Execution Complete"** node
   - Credential: Select **"PostgreSQL Trading DB"**
5. Click **"Mark Execution Skipped"** node
   - Credential: Select **"PostgreSQL Trading DB"**
6. **IQOption Trading Node** - No credential needed (uses .env vars)
7. **Save** (Ctrl+S)

### Step 8.7: Link Error Workflow

**CRITICAL STEP:**

1. Open **Main_Trading_Workflow**
2. Click **"Workflow Settings"** (gear icon top-right)
3. Scroll to **"Error Workflow"**
4. Select: **"Error_Alert_Workflow"**
5. Click **"Save"**

### Step 8.8: Load Environment Variables in n8n

**Option A: If n8n is running as systemd service**

```bash
sudo nano /etc/systemd/system/n8n.service

# Add this line under [Service]:
EnvironmentFile=/app/app/KAEL/KAEL/n8n-workflows/.env

# Save and exit
sudo systemctl daemon-reload
sudo systemctl restart n8n
```

**Option B: If running n8n manually**

```bash
# Stop n8n
pkill n8n

# Load env vars and start
cd /app/app/KAEL/KAEL/n8n-workflows
export $(grep -v '^#' .env | xargs)
n8n start &
```

**Option C: Set in n8n UI (tedious but works)**

1. **Settings** → **Environment Variables**
2. Add each variable manually from your `.env` file

**Checkpoint**: All credentials configured and assigned? ✅ → Proceed to Step 9

---

# STEP 9: Test Individual Workflows

## 🧪 Test Before Activating

### Step 9.1: Test Error Workflow

1. Open **Error_Alert_Workflow**
2. Click **"Execute Workflow"** button (play icon)
3. Should complete successfully ✅
4. **Check your email** - you should receive an error test email
5. If error: Check SMTP credentials and email settings

### Step 9.2: Test AI Consensus Engine

1. Open **AI_Consensus_Engine**
2. Click **"Execute Workflow"** button
3. Wait 5-10 seconds (queries 3 AI models)
4. Check output - should show:
   ```json
   {
     "final_signal": "CALL/PUT/SKIP",
     "confidence": 75.5,
     "consensus_reached": true/false,
     "model_votes": [...]
   }
   ```
5. If error: Check API keys are correct

### Step 9.3: Test Data Logger

1. Open **Data_Logger**
2. Click **"Execute Workflow"** button
3. Should complete successfully ✅
4. **Verify database**:
   ```bash
   psql -U trading_user -d iqoption_trading -c "SELECT * FROM trades LIMIT 1;"
   ```
5. **Verify Google Sheets** - open your sheet, should see new row in "Trades" tab

### Step 9.4: Test Email Reporter

1. Open **Email_Reporter**
2. Click **"Execute Workflow"** button
3. Should complete successfully ✅
4. **Check your email** - should receive a formatted email
5. If error: Check SMTP credentials

### Step 9.5: Test Main Workflow (Manual Execution)

**WARNING: This will execute a real trade on your demo account!**

1. Open **Main_Trading_Workflow**
2. Click **"Execute Workflow"** button
3. Wait 1-3 minutes for completion
4. Check execution log - should show:
   - ✅ Execution registered
   - ✅ AI consensus calculated
   - ✅ Trade executed (or skipped)
   - ✅ Data logged
   - ✅ Email sent (if configured)
5. **Verify in database**:
   ```bash
   psql -U trading_user -d iqoption_trading -c "SELECT * FROM v_recent_trades LIMIT 1;"
   ```
6. **Check Google Sheets** - should see trade logged
7. **Check email** - should receive notification

### Step 9.6: Common Test Issues

| Issue | Solution |
|-------|----------|
| "Cannot connect to database" | Check PostgreSQL is running: `sudo systemctl status postgresql` |
| "API key invalid" | Verify API keys in credentials (no extra spaces) |
| "Email failed to send" | Check Gmail App Password, ensure 2FA is enabled |
| "Google Sheets permission denied" | Re-authorize OAuth2 credential |
| "IQOption API not found" | Check API server is running: `curl localhost:5000/status` |

**Checkpoint**: All workflows tested successfully? ✅ → Proceed to Step 10

---

# STEP 10: Activate Main Workflow

## 🚀 Go Live!

### Step 10.1: Final Pre-Activation Checklist

Before activating, verify:

- [ ] Database has tables and is accessible
- [ ] All credentials are configured correctly
- [ ] Google Sheets has 3 tabs (Trades, Errors, Daily_Summary)
- [ ] IQOption API server is running
- [ ] Email notifications are working
- [ ] Using **DEMO** account (not real money!)
- [ ] Error workflow is active and linked
- [ ] All individual workflows tested successfully

### Step 10.2: Activate Main Trading Workflow

1. Open **Main_Trading_Workflow**
2. **Double-check** it's using demo account:
   - Look at **"Execute Trade"** node
   - Should show: `accountType: demo`
3. Click **"Active"** toggle (top-right) to **ON** 🟢
4. You should see: **"Workflow active"** notification

### Step 10.3: What Happens Now?

The workflow will now:

1. **Run every N minutes** (default: 1 minute)
2. **Check for running executions** (prevent overlaps)
3. **Query 3 AI models** in parallel
4. **Calculate consensus** (hybrid logic)
5. **Execute trade** if signal is valid
6. **Log to database** and Google Sheets
7. **Send email** notification (if configured)
8. **Repeat** every N minutes

### Step 10.4: Monitor First Execution

```bash
# Watch n8n logs
journalctl -u n8n -f

# OR if running manually:
tail -f ~/.n8n/logs/n8n.log

# Watch database
watch -n 5 "psql -U trading_user -d iqoption_trading -c 'SELECT * FROM v_recent_trades LIMIT 5;'"
```

**Checkpoint**: Workflow activated and first execution completed? ✅ → Proceed to Step 11

---

# STEP 11: Monitor and Verify

## 📊 Ensure System is Working

### Step 11.1: Check n8n Execution Logs

1. In n8n UI, click **"Executions"** (left sidebar)
2. You should see:
   - New executions every N minutes
   - Most will show **"Success"** ✅
   - Some may be **"Skipped"** (no tradeable signal - this is normal!)
3. Click on any execution to see detailed flow

### Step 11.2: Check Database

```bash
# Recent trades
psql -U trading_user -d iqoption_trading -c "SELECT * FROM v_recent_trades LIMIT 10;"

# Today's performance
psql -U trading_user -d iqoption_trading -c "SELECT * FROM v_daily_performance WHERE date = CURRENT_DATE;"

# Active executions (should be 0 or 1)
psql -U trading_user -d iqoption_trading -c "SELECT COUNT(*) FROM workflow_executions WHERE status = 'running';"

# Any errors?
psql -U trading_user -d iqoption_trading -c "SELECT * FROM error_logs WHERE resolved = false LIMIT 5;"
```

### Step 11.3: Check Google Sheets

1. Open your Google Sheet
2. **Trades tab** - should see new rows appearing
3. **Errors tab** - should be empty (or minimal errors)
4. **Daily_Summary tab** - will populate at end of day

### Step 11.4: Check Email Notifications

Based on your `N8N_EMAIL_MODE`:

- **per_trade**: Email after each trade
- **daily**: One email per day (at midnight)
- **errors_only**: Only when errors occur
- **errors_and_daily**: Errors immediately + daily summary

### Step 11.5: Performance Monitoring (First 24 Hours)

**Hour 1**: Check every 10 minutes
- Are executions running?
- Are trades being logged?
- Any errors in logs?

**Hours 2-6**: Check every hour
- How many trades executed?
- What's the win rate so far?
- Any patterns in AI decisions?

**Hours 7-24**: Check every 4 hours
- Daily statistics updating?
- Email summaries working?
- System stable?

### Step 11.6: Common Monitoring Commands

```bash
# System health check
psql -U trading_user -d iqoption_trading <<EOF
SELECT
    'Total Trades Today' as metric,
    COUNT(*) as value
FROM trades
WHERE DATE(timestamp) = CURRENT_DATE
UNION ALL
SELECT 'Win Rate',
    ROUND(AVG(CASE WHEN trade_result = 'WIN' THEN 100 ELSE 0 END), 1)
FROM trades
WHERE DATE(timestamp) = CURRENT_DATE AND trade_result IN ('WIN', 'LOSS');
EOF

# Check for stuck executions
psql -U trading_user -d iqoption_trading -c "
SELECT execution_id, started_at,
  EXTRACT(EPOCH FROM (NOW() - started_at)) / 60 as minutes_running
FROM workflow_executions
WHERE status = 'running';"

# API server health
curl -s http://localhost:5000/status | jq
```

### Step 11.7: Adjust Parameters (Optional)

After 24-48 hours of monitoring, you may want to adjust:

**Trade Interval**
```bash
# Edit .env
nano /app/app/KAEL/KAEL/n8n-workflows/.env

# Change:
N8N_TRADE_INTERVAL_MINUTES=5  # From 1 to 5 minutes

# Restart n8n to apply
sudo systemctl restart n8n
```

**Trade Amount**
```bash
# Edit .env
N8N_TRADE_AMOUNT=2  # From 1 to 2 dollars

# Restart n8n
sudo systemctl restart n8n
```

**Email Mode**
```bash
# Edit .env
N8N_EMAIL_MODE=daily  # From per_trade to daily

# Restart n8n
sudo systemctl restart n8n
```

**Confidence Threshold**
Edit **AI_Consensus_Engine.json**:
1. Open workflow in n8n
2. Click **"Consensus Calculator"** node
3. Find line: `if (avgConfidence >= 70 ...`
4. Change `70` to `75` (stricter) or `65` (more trades)
5. Save workflow

---

## ✅ Setup Complete!

**Congratulations! Your AI trading system is now fully operational! 🎉**

### What's Running

- ✅ Main workflow executing every N minutes
- ✅ AI models analyzing markets
- ✅ Trades being executed on demo account
- ✅ Data logged to PostgreSQL + Google Sheets
- ✅ Email notifications being sent
- ✅ Errors handled gracefully

### Next Steps

1. **Monitor for 2 weeks** on demo account
2. **Review performance daily**
3. **Adjust parameters** as needed
4. **Only switch to real account** if consistently profitable

### Daily Maintenance

```bash
# Morning check
psql -U trading_user -d iqoption_trading -c "SELECT * FROM v_daily_performance WHERE date >= CURRENT_DATE - 7;"

# Evening check
psql -U trading_user -d iqoption_trading -c "SELECT COUNT(*), SUM(payout) FROM trades WHERE DATE(timestamp) = CURRENT_DATE;"
```

### Weekly Maintenance

```bash
# Run maintenance queries
psql -U trading_user -d iqoption_trading -f /app/app/KAEL/KAEL/n8n-workflows/schemas/maintenance.sql

# Backup database
pg_dump -U trading_user iqoption_trading > backup_$(date +%Y%m%d).sql
```

---

## 🆘 Troubleshooting

### Workflow Not Executing

1. Check if active: **Main_Trading_Workflow** toggle should be ON
2. Check n8n logs: `journalctl -u n8n -f`
3. Check cron trigger: Open workflow, click trigger node, verify interval

### No Trades Being Executed

This is actually **normal**! The hybrid consensus is conservative:
- Requires 2+ AI models to agree
- Requires >70% confidence
- Most signals are filtered out as SKIP

**Expected**: 5-20 trades per day (out of 1440 checks at 1-min interval)

### Database Errors

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U trading_user -d iqoption_trading -c "SELECT 1;"

# Check for locks
psql -U trading_user -d iqoption_trading -c "SELECT * FROM pg_locks WHERE NOT granted;"
```

### Email Not Sending

1. Verify Gmail App Password (16 characters, no spaces)
2. Check 2FA is enabled on Gmail
3. Test SMTP manually:
   ```bash
   echo "Test" | mail -s "Test" -S smtp=smtp.gmail.com:587 your_email@gmail.com
   ```

### Google Sheets Not Updating

1. Re-authorize OAuth2 credential in n8n
2. Verify sheet ID is correct
3. Check sheet has tabs: Trades, Errors, Daily_Summary
4. Ensure sheet is shared (anyone with link can edit)

### High API Costs

If AI API costs are too high:

1. Increase trade interval (1 min → 5 min)
2. Use cheaper models (GPT-4o-mini instead of GPT-4)
3. Reduce AI query frequency
4. Set daily trade limits

---

## 📚 Additional Resources

- **Full Documentation**: [README.md](README.md)
- **Quick Reference**: [QUICK_START.md](QUICK_START.md)
- **Architecture**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **File Index**: [INDEX.md](INDEX.md)
- **Database Queries**: [schemas/maintenance.sql](schemas/maintenance.sql)

---

## ⚠️ Final Reminders

1. **ALWAYS use demo account for testing** (minimum 2 weeks)
2. **Never share your API keys** or credentials
3. **Set trade limits** to protect capital
4. **Monitor daily** (especially first week)
5. **Comply with local regulations**
6. **Only trade money you can afford to lose**

---

**🎉 You're all set! Happy automated trading! 🚀**

**Questions? Check the documentation or troubleshooting sections above.**
