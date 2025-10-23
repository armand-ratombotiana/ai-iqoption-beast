# IQOption AI Trading Bot

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-beta-yellow.svg)

**AI-Powered Binary Options Trading Bot with Advanced Risk Management**

[Features](#features) • [Installation](#installation) • [Documentation](#documentation) • [Usage](#usage) • [Contributing](#contributing)

</div>

---

## ⚠️ Disclaimer

**This software is for educational and defensive security analysis purposes only.** Binary options trading involves significant risk. Always:

- Start with demo accounts
- Never risk more than you can afford to lose
- Understand regulations in your jurisdiction
- This is not financial advice
- Past performance does not guarantee future results

---

## 🚀 Features

### Core Capabilities

- **🤖 AI Signal Integration** - Confidence-based trade execution
- **🛡️ Advanced Risk Management** - Multi-layer protection system
- **📊 Dynamic Position Sizing** - Adaptive Martingale strategy
- **📈 Real-time Monitoring** - Comprehensive statistics tracking
- **🔄 n8n Integration** - Workflow automation support
- **🐳 Docker Support** - Containerized deployment
- **📝 Extensive Logging** - Detailed trade tracking

### Risk Management

- ✅ Daily loss/profit limits
- ✅ Consecutive loss protection
- ✅ Balance monitoring
- ✅ Martingale level caps
- ✅ Confidence thresholds
- ✅ Auto-reset mechanisms

---

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Architecture](#architecture)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## 🔧 Installation

### Prerequisites

- Python 3.8+
- pip
- (Optional) Docker & Docker Compose
- (Optional) n8n for workflow automation

### Local Installation

```bash
# Clone repository
git clone <repository-url>
cd iqoption-ai-trading-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp config/.env.example .env

# Edit configuration
nano .env
```

### Docker Installation

```bash
# Build image
make docker-build

# Run container
make docker-run
```

---

## ⚡ Quick Start

### 1. Configure Environment

Edit `.env` file with your settings:

```env
MAX_DAILY_LOSS=50
MAX_DAILY_PROFIT=100
MAX_CONSECUTIVE_LOSSES=3
MIN_CONFIDENCE_THRESHOLD=60
BASE_TRADE_AMOUNT=1
```

### 2. Start API Server

```bash
# Development
make run

# Production (with Gunicorn)
gunicorn --bind 0.0.0.0:5000 app:app
```

### 3. Test Connection

```bash
curl http://localhost:5000/health
```

### 4. Execute First Trade

```bash
curl -X POST http://localhost:5000/trade \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "demopassword",
    "action": "call",
    "pair": "EURUSD",
    "confidence": 75,
    "accountType": "demo"
  }'
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_DAILY_LOSS` | 50 | Maximum daily loss ($) |
| `MAX_DAILY_PROFIT` | 100 | Daily profit target ($) |
| `MAX_CONSECUTIVE_LOSSES` | 3 | Max consecutive losses |
| `MIN_BALANCE` | 50 | Minimum balance required ($) |
| `MARTINGALE_MULTIPLIER` | 1.5 | Martingale multiplier |
| `MAX_MARTINGALE_LEVEL` | 4 | Maximum Martingale level |
| `MIN_CONFIDENCE_THRESHOLD` | 60 | Minimum AI confidence (%) |
| `BASE_TRADE_AMOUNT` | 1 | Base trade amount ($) |
| `MAX_TRADE_MULTIPLIER` | 5 | Maximum trade size multiplier |

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for detailed configuration guide.

---

## 📡 API Reference

### Endpoints

#### `POST /trade`
Execute a trade with risk management

**Request:**
```json
{
  "email": "your@email.com",
  "password": "yourpassword",
  "action": "call",
  "pair": "EURUSD",
  "confidence": 75,
  "amount": 1,
  "duration": 2,
  "accountType": "demo"
}
```

**Response:**
```json
{
  "success": true,
  "trade": { ... },
  "tradingState": { ... }
}
```

#### `GET /status`
Get trading statistics

#### `POST /reset`
Reset trading state

#### `GET /health`
Health check

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for complete API documentation.

---

## 🏗️ Architecture

### Project Structure

```
iqoption-ai-trading-bot/
├── src/
│   ├── api/              # Flask API layer
│   ├── core/             # Business logic
│   ├── models/           # Data models
│   ├── utils/            # Utilities
│   └── iqoptionapi/      # IQOption API wrapper
├── tests/                # Test suite
├── scripts/              # Utility scripts
├── docs/                 # Documentation
├── docker/               # Docker configuration
├── config/               # Configuration files
└── n8n/                  # n8n integration
```

### Key Components

- **SignalValidator** - Validates AI trading signals
- **RiskManager** - Enforces risk limits
- **PositionSizer** - Calculates trade amounts
- **TradeExecutor** - Executes trades on IQOption
- **StateManager** - Tracks statistics

See [docs/architecture/overview.md](docs/architecture/overview.md) for detailed architecture.

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test
pytest tests/test_risk_manager.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Set all environment variables
- [ ] Use `accountType: "demo"` for testing
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Enable HTTPS
- [ ] Restrict API access
- [ ] Regular backups

### Deployment Options

1. **Docker** - Recommended for production
2. **Heroku** - Quick cloud deployment
3. **AWS/GCP** - Scalable cloud deployment
4. **VPS** - Traditional server deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment guide.

---

## 🤝 Contributing

Contributions welcome! Please read [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) first.

### Development Setup

```bash
# Install dev dependencies
make dev

# Format code
make format

# Run linting
make lint

# Run tests
make test
```

---

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [API Reference](docs/API_REFERENCE.md)
- [Risk Management](docs/RISK_MANAGEMENT.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture Overview](docs/architecture/overview.md)

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- IQOption API community
- n8n automation platform
- Flask framework

---

## 📞 Support

For issues and questions:

1. Check [documentation](docs/)
2. Search [existing issues](https://github.com/your-repo/issues)
3. Create new issue with details

---

<div align="center">

**⚠️ Remember: Always start with demo accounts and trade responsibly ⚠️**

Made with ❤️ for educational purposes

</div>
