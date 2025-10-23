# 📑 IQOption AI Trading System - File Index

Complete file structure and quick reference guide.

---

## 📁 Directory Structure

```
n8n-workflows/
├── workflows/              # n8n workflow JSON files
│   ├── Main_Trading_Workflow.json
│   ├── AI_Consensus_Engine.json
│   ├── Data_Logger.json
│   ├── Email_Reporter.json
│   └── Error_Alert_Workflow.json
├── schemas/               # Database schema and maintenance
│   ├── postgres_schema.sql
│   └── maintenance.sql
├── docs/                  # (placeholder for future docs)
├── .env.example          # Environment variables template
├── docker-compose.yml    # Docker deployment configuration
├── README.md             # Complete documentation
├── QUICK_START.md        # 15-minute setup guide
├── PROJECT_SUMMARY.md    # Project overview and architecture
└── INDEX.md              # This file

Related Files (in parent directories):
├── ../n8n-nodes-trading/         # Custom IQOption n8n node
│   ├── credentials/IQOptionApi.credentials.js
│   ├── nodes/Trading/Trading.node.js
│   └── package.json
└── ../advanced_trading_system/   # IQOption API server
    ├── main.py
    ├── requirements.txt
    └── ...
```

---

## 📄 File Descriptions

### 🔹 Workflows (Import into n8n)

| File | Purpose | Import Order | Activate? |
|------|---------|--------------|-----------|
| `Error_Alert_Workflow.json` | Handles errors, sends alerts | 1st | ✅ Yes |
| `AI_Consensus_Engine.json` | Queries AI models, calculates consensus | 2nd | ❌ No (called by main) |
| `Data_Logger.json` | Logs to PostgreSQL + Google Sheets | 3rd | ❌ No (called by main) |
| `Email_Reporter.json` | Sends email notifications | 4th | ❌ No (called by main) |
| `Main_Trading_Workflow.json` | Main orchestrator, runs every N minutes | 5th | ✅ Yes (after testing) |

### 🔹 Database Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `postgres_schema.sql` | Creates all tables, views, functions | Initial setup (run once) |
| `maintenance.sql` | Monitoring and maintenance queries | Ongoing (as needed) |

### 🔹 Configuration Files

| File | Purpose | Required? |
|------|---------|-----------|
| `.env.example` | Environment variables template | Copy to `.env` and configure |
| `docker-compose.yml` | Docker stack deployment | Optional (for Docker deployment) |

### 🔹 Documentation Files

| File | Purpose | Read When |
|------|---------|-----------|
| `README.md` | Complete setup guide | Detailed setup and troubleshooting |
| `QUICK_START.md` | 15-minute quick start | First-time setup |
| `PROJECT_SUMMARY.md` | Project overview | Understanding architecture |
| `INDEX.md` | This file | Finding specific files |

---

## 🚀 Quick Links

### For New Users
1. **Start here**: [QUICK_START.md](QUICK_START.md)
2. **Then read**: [README.md](README.md) (Sections as needed)
3. **Understand system**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

### For Setup
1. **Database**: [postgres_schema.sql](schemas/postgres_schema.sql)
2. **Configuration**: [.env.example](.env.example)
3. **Docker**: [docker-compose.yml](docker-compose.yml)

### For Maintenance
1. **Monitoring queries**: [maintenance.sql](schemas/maintenance.sql)
2. **Troubleshooting**: [README.md#troubleshooting](README.md#troubleshooting)
3. **Error handling**: [README.md#error-handling](README.md#error-handling)

---

## 📊 Workflow Details

### Main_Trading_Workflow.json
**Purpose**: Main orchestrator that runs every N minutes

**Key Features**:
- Cron trigger (configurable interval)
- Prevents concurrent executions
- Calls all sub-workflows
- Handles errors via Error_Alert_Workflow

**Nodes**: 18 nodes
- Cron Trigger
- Initialize Execution
- Check Running Executions
- Filter Concurrent Executions
- Register Execution
- Call AI Consensus Engine
- Check Tradeable Signal
- Prepare Trade Payload
- Execute Trade (IQOption custom node)
- Check Trade Success
- Prepare Log Data
- Handle Trade Error
- Call Data Logger
- Check Email Mode
- Set Email Type
- Call Email Reporter
- Mark Execution Complete
- Mark Execution Skipped

**Environment Variables Used**:
- `N8N_TRADE_INTERVAL_MINUTES`
- `N8N_TRADE_ASSET`
- `N8N_TRADE_AMOUNT`
- `IQOPTION_EMAIL`
- `IQOPTION_PASSWORD`
- `IQOPTION_ACCOUNT_TYPE`
- `IQOPTION_API_URL`
- `N8N_EMAIL_MODE`

---

### AI_Consensus_Engine.json
**Purpose**: Query 3 AI models and calculate hybrid consensus

**Key Features**:
- Parallel execution of OpenAI, Claude, DeepSeek
- Hybrid consensus logic (2+ agreement + >70% confidence)
- Detailed vote tracking
- Returns CALL/PUT/SKIP decision

**Nodes**: 8 nodes
- Start
- Prepare Market Context
- OpenAI Analysis (GPT-4o-mini)
- Claude Analysis (Sonnet 3.5)
- DeepSeek Analysis (DeepSeek Chat)
- Merge AI Responses
- Consensus Calculator (JavaScript)
- Filter Tradeable Signals

**Environment Variables Used**:
- `OPENAI_API_KEY`
- `CLAUDE_API_KEY`
- `DEEPSEEK_API_KEY`
- `N8N_TRADE_ASSET`

---

### Data_Logger.json
**Purpose**: Log trades to PostgreSQL and Google Sheets

**Key Features**:
- Dual logging (database + spreadsheet)
- Automatic daily statistics update
- Upsert logic (handles duplicates)
- Error handling

**Nodes**: 8 nodes
- Start
- Prepare Log Data
- Log to PostgreSQL
- Log to Google Sheets
- Merge Logs
- Prepare Stats Update
- Update Daily Stats
- Log Success Response

**Environment Variables Used**:
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `N8N_GOOGLE_SHEETS_ID`

---

### Email_Reporter.json
**Purpose**: Send email notifications (per-trade or daily summary)

**Key Features**:
- Configurable email modes
- Beautiful HTML email templates
- Per-trade alerts with trade details
- Daily summary with statistics
- AI model vote details

**Nodes**: 7 nodes
- Start
- Check Email Mode
- Format Per-Trade Email
- Fetch Daily Stats
- Format Daily Summary
- Send Email (SMTP)
- Email Success Response

**Environment Variables Used**:
- `N8N_SMTP_USER`
- `N8N_SMTP_PASS`
- `N8N_SMTP_HOST`
- `N8N_SMTP_PORT`
- `N8N_EMAIL_TO`
- `N8N_EMAIL_MODE`

---

### Error_Alert_Workflow.json
**Purpose**: Handle errors and send high-priority alerts

**Key Features**:
- Automatic error detection
- High-priority email alerts
- Detailed error logging
- Troubleshooting guidance in emails
- Logs to database and sheets

**Nodes**: 6 nodes
- Error Trigger
- Extract Error Info
- Format Error Email
- Send Error Email (high priority)
- Log Error to Database
- Log Error to Sheets

**Environment Variables Used**:
- `N8N_SMTP_USER`
- `N8N_SMTP_PASS`
- `N8N_EMAIL_TO`
- `POSTGRES_*` (database credentials)
- `N8N_GOOGLE_SHEETS_ID`

---

## 🗄️ Database Schema

### Tables (6)
1. **trades** - All trade records
   - Columns: id, trade_id, timestamp, asset, direction, ai_confidence, trade_result, payout, amount, duration, model_votes, error_message
   - Indexes: timestamp, asset, result, date

2. **daily_stats** - Aggregated daily statistics
   - Columns: id, date, total_trades, wins, losses, pending, errors, total_profit, win_rate (calculated), avg_confidence
   - Indexes: date

3. **workflow_executions** - Execution tracking
   - Columns: id, execution_id, status, started_at, completed_at, notes
   - Indexes: status, started_at

4. **error_logs** - Error tracking
   - Columns: id, timestamp, workflow_name, workflow_id, execution_id, error_node, error_message, error_description, stack_trace, input_data, resolved, resolved_at
   - Indexes: timestamp, workflow_name, resolved

5. **ai_model_performance** - AI model accuracy
   - Columns: id, date, model_name, total_predictions, correct_predictions, accuracy (calculated), avg_confidence
   - Indexes: date + model_name

6. **system_config** - Dynamic configuration
   - Columns: id, config_key, config_value, description, updated_at
   - Default configs: trading_enabled, max_daily_trades, max_daily_loss, min_consensus_confidence, maintenance_mode

### Views (3)
1. **v_recent_trades** - Last 100 trades with formatting
2. **v_daily_performance** - Daily win rate and profit summary
3. **v_ai_model_comparison** - Compare AI model accuracy

### Functions (3)
1. **update_updated_at_column()** - Auto-update timestamps
2. **cleanup_old_executions()** - Keep database size manageable
3. **archive_old_trades()** - Move old trades to archive

---

## 🔧 Environment Variables Reference

### Required Variables (22)

| Variable | Example | Purpose |
|----------|---------|---------|
| `OPENAI_API_KEY` | `sk-proj-xxx` | OpenAI API access |
| `CLAUDE_API_KEY` | `sk-ant-xxx` | Claude API access |
| `DEEPSEEK_API_KEY` | `sk-xxx` | DeepSeek API access |
| `IQOPTION_EMAIL` | `user@example.com` | IQOption login |
| `IQOPTION_PASSWORD` | `password` | IQOption password |
| `IQOPTION_ACCOUNT_TYPE` | `demo` | Account type (demo/real) |
| `IQOPTION_API_URL` | `http://localhost:5000` | API server URL |
| `N8N_SMTP_USER` | `user@gmail.com` | SMTP username |
| `N8N_SMTP_PASS` | `app_password` | SMTP password |
| `N8N_SMTP_HOST` | `smtp.gmail.com` | SMTP server |
| `N8N_SMTP_PORT` | `587` | SMTP port |
| `N8N_EMAIL_TO` | `alerts@example.com` | Email recipient |
| `N8N_EMAIL_MODE` | `per_trade` | Email mode |
| `N8N_GOOGLE_SHEETS_ID` | `abc123...` | Google Sheets ID |
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `POSTGRES_DB` | `iqoption_trading` | Database name |
| `POSTGRES_USER` | `trading_user` | Database user |
| `POSTGRES_PASSWORD` | `password` | Database password |
| `N8N_TRADE_INTERVAL_MINUTES` | `1` | Trade check interval |
| `N8N_TRADE_AMOUNT` | `1` | Trade amount ($) |
| `N8N_TRADE_ASSET` | `EURUSD` | Trading asset |

### Optional Variables (11)
- `N8N_HOST`, `N8N_PORT`, `N8N_PROTOCOL`
- `N8N_MIN_CONFIDENCE`, `N8N_MAX_DAILY_TRADES`, `N8N_MAX_DAILY_LOSS`
- `ENABLE_MARTINGALE`, `MARTINGALE_MULTIPLIER`, `MARTINGALE_MAX_LEVEL`
- `TRADING_HOURS`, `TRADING_DAYS`

---

## 📈 Statistics

### Project Metrics
- **Total Files**: 12
- **Workflows**: 5 (Main + 4 sub-workflows)
- **Total Workflow Nodes**: ~50 nodes
- **Database Tables**: 6 tables + 1 archive
- **Database Views**: 3 analytical views
- **Database Functions**: 3 automation functions
- **Lines of SQL**: ~800 lines
- **Lines of Documentation**: ~2,500 lines

### Code Breakdown
- **Workflow JSON**: ~3,000 lines
- **SQL Schema**: ~800 lines
- **Documentation**: ~2,500 lines
- **Configuration**: ~200 lines
- **Total**: ~6,500 lines

---

## ✅ Checklist for Deployment

Use this checklist before going live:

### Prerequisites
- [ ] n8n installed and running
- [ ] PostgreSQL installed and accessible
- [ ] Python 3.8+ with pip
- [ ] Node.js 18+ for custom node
- [ ] All API keys obtained (OpenAI, Claude, DeepSeek)
- [ ] IQOption demo account created
- [ ] Gmail App Password generated
- [ ] Google Sheets created with required tabs

### Installation
- [ ] Database created (`createdb iqoption_trading`)
- [ ] Schema loaded (`postgres_schema.sql`)
- [ ] Tables verified (`\dt`)
- [ ] Custom n8n node installed
- [ ] n8n restarted
- [ ] IQOption API server running
- [ ] API server accessible (`curl localhost:5000/status`)

### Configuration
- [ ] `.env` file created from template
- [ ] All required variables configured
- [ ] Environment variables loaded in n8n
- [ ] Database connection tested
- [ ] Google Sheets OAuth2 configured
- [ ] SMTP credentials verified

### Workflow Setup
- [ ] Error_Alert_Workflow imported and activated
- [ ] AI_Consensus_Engine imported
- [ ] Data_Logger imported
- [ ] Email_Reporter imported
- [ ] Main_Trading_Workflow imported
- [ ] All credentials configured
- [ ] Error workflow linked
- [ ] Workflows tested individually
- [ ] Main workflow tested (manual execution)

### Verification
- [ ] Test trade executed successfully
- [ ] Database logs confirmed
- [ ] Google Sheets logging confirmed
- [ ] Email notifications received
- [ ] Error workflow tested
- [ ] Daily stats calculating correctly
- [ ] No errors in n8n logs
- [ ] 24-48 hour demo test completed

### Security
- [ ] `.env` not in version control
- [ ] Strong passwords used
- [ ] Demo account configured (not real)
- [ ] Trade limits set
- [ ] Firewall rules configured
- [ ] Database access restricted
- [ ] API keys rotated

### Go-Live
- [ ] All tests passed
- [ ] Performance reviewed
- [ ] Backup strategy in place
- [ ] Monitoring plan established
- [ ] Documentation reviewed
- [ ] Main workflow activated
- [ ] System monitored for first 24 hours

---

## 🆘 Quick Help

### Common Issues
- **Workflow not running**: Check Active toggle, verify cron schedule
- **AI consensus returns SKIP**: Verify API keys, check confidence threshold
- **Trade fails**: Check IQOption API server, verify credentials
- **Database errors**: Check PostgreSQL service, verify connection
- **Email not sending**: Check SMTP credentials, regenerate App Password

### Getting Help
1. Check [README.md](README.md) Troubleshooting section
2. Review [maintenance.sql](schemas/maintenance.sql) for diagnostic queries
3. Check n8n execution logs
4. Review error_logs table in database
5. Check email alerts for error details

### Useful Commands
```bash
# Check services
sudo systemctl status postgresql
sudo systemctl status n8n
curl http://localhost:5000/status

# View logs
journalctl -u n8n -f
tail -f advanced_trading_system/logs/api.log

# Database queries
psql -U trading_user -d iqoption_trading
SELECT * FROM v_recent_trades LIMIT 10;

# Restart services
sudo systemctl restart postgresql
sudo systemctl restart n8n
```

---

## 📞 Support

- **Documentation**: See [README.md](README.md)
- **Quick Start**: See [QUICK_START.md](QUICK_START.md)
- **Architecture**: See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **n8n Help**: [n8n Community Forum](https://community.n8n.io/)

---

**Last Updated**: January 15, 2025
**Version**: 1.0.0
**Status**: Production Ready ✅
