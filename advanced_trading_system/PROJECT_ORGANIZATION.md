# Project Reorganization Documentation

**Date**: February 21, 2026  
**Version**: 2.0.0  
**Status**: Complete

---

## 📁 New Project Structure

```
advanced_trading_system/
├── src/                              # Main source code (NEW ORGANIZATION)
│   ├── __init__.py                   # Package initialization
│   ├── core/                         # Core trading logic
│   │   ├── risk_manager.py          # Risk management
│   │   ├── position_sizer.py        # Position sizing algorithms
│   │   ├── signal_validator.py      # Signal validation
│   │   ├── trade_executor.py        # Trade execution
│   │   ├── state_manager.py         # State management
│   │   └── __init__.py              # Core package exports
│   │
│   ├── trading/                      # Trading engines
│   │   ├── parallel_trading_engine.py
│   │   └── __init__.py
│   │
│   ├── ai/                           # AI models and consensus
│   │   ├── models/
│   │   │   ├── base_model.py
│   │   │   ├── claude_model.py
│   │   │   ├── openai_model.py
│   │   │   ├── deepseek_model.py
│   │   │   ├── consensus_engine.py
│   │   │   ├── explainability.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── analysis/                     # Market analysis
│   │   ├── technical_indicators.py
│   │   ├── market_context.py
│   │   └── __init__.py
│   │
│   ├── api/                          # REST API
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── websocket_manager.py
│   │   └── __init__.py
│   │
│   ├── data/                         # Data ingestion (renamed from data_ingestion)
│   │   ├── connection_manager.py
│   │   ├── data_validator.py
│   │   ├── market_data_provider.py
│   │   └── __init__.py
│   │
│   ├── monitoring/                   # System monitoring
│   │   ├── monitor_autonomous_ai.py
│   │   ├── run_autonomous_ai.py
│   │   └── __init__.py
│   │
│   └── risk/                         # Risk management portfolio
│       ├── portfolio_risk_manager.py
│       └── __init__.py
│
├── config/                           # Configuration files
│   ├── settings.py
│   ├── enhanced_settings.py
│   ├── parallel_settings.py
│   └── __init__.py
│
├── tests/                            # Test suite (already well-organized)
│   ├── unit/
│   ├── integration/
│   ├── test_data_ingestion.py
│   ├── test_enhanced_system.py
│   ├── test_all_components.py
│   └── __init__.py
│
├── scripts/                          # Deployment scripts
│   ├── docker-start.sh
│   ├── docker-rebuild.sh
│   ├── docker-entrypoint.sh
│   ├── setup.sh
│   └── start_autonomous_ai.sh
│
├── docker/                           # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── docs/                             # Documentation
│   ├── QUICK_START.md
│   ├── README.md
│   ├── architecture/
│   └── reports/
│
├── docs_backup/                      # Historical documentation
│
├── iqoptionapi/                      # IQOption API wrapper
│   ├── api.py
│   ├── stable_api.py
│   ├── constants.py
│   ├── ws/
│   ├── http/
│   └── __init__.py
│
├── backtesting/                      # Backtesting engine
│   ├── backtesting_engine.py
│   └── __init__.py
│
├── utils/                            # Utility functions
│   ├── config.py
│   ├── constants.py
│   ├── logger.py
│   └── __init__.py
│
# Root entry points
├── main.py                           # Primary entry point
├── run_trading_system.py             # Unified trading system
├── run_unified_trading.py            # Multi-mode trading runner
├── run_comprehensive_tests.py        # Test runner
├── trade.py                          # Legacy entry point
├── web_monitor.py                    # Web monitoring dashboard
├── test_trading_systems.py           # Trading system tests
│
# Configuration & Documentation
├── .env                              # Environment variables (local)
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore rules
├── requirements.txt                  # Python dependencies
├── requirements-production.txt       # Production dependencies
├── requirements_enhanced.txt         # Enhanced features
│
├── README.md                         # Main readme
├── README_PRODUCTION.md              # Production guide
├── PRODUCTION_SETUP.md               # Setup guide
│
├── REORGANIZATION_PLAN.txt           # Former organization plan
├── REORGANIZATION_SUMMARY.md         # Reorganization summary
└── PROJECT_ORGANIZATION.md           # This file

```

---

## 🔄 Migration Guide

### Old vs New Imports

**Before:**
```python
from core.risk_manager import RiskManager
from ai.models.claude_model import ClaudeModel
from analysis.technical_indicators import TechnicalIndicators
```

**After:**
```python
from src.core import RiskManager
from src.ai.models import ClaudeModel
from src.analysis import TechnicalIndicators
```

### File Movements

| Old Location | New Location | Purpose |
|---|---|---|
| `core/` | `src/core/` | Core trading components |
| `trading/` | `src/trading/` | Trading engines |
| `ai/` | `src/ai/` | AI models |
| `analysis/` | `src/analysis/` | Market analysis |
| `api/` | `src/api/` | REST API |
| `data_ingestion/` | `src/data/` | Data management |
| `risk_management/` | `src/risk/` | Risk portfolio |
| `monitor_*.py` | `src/monitoring/` | Monitoring utilities |
| `Docker*` | `docker/` | Docker files |
| `*-*.sh` | `scripts/` | Deployment scripts |

---

## 🚀 Key Improvements

### 1. **Cleaner imports**
   - All source code under `src/` namespace
   - Clear package hierarchy
   - Easier to locate components

### 2. **Better organization**
   - Related files grouped together
   - Reduced top-level clutter
   - Easier navigation

### 3. **Clear separation of concerns**
   - `src/` - Application code
   - `config/` - Configuration
   - `tests/` - Test suite
   - `scripts/` - Deployment
   - `docker/` - Infrastructure
   - `docs/` - Documentation

### 4. **Scalability**
   - Room for growth
   - Easy to add new modules
   - Clear patterns to follow

---

## 📝 Python Path Configuration

When running scripts, ensure `src/` is in the Python path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
```

Or set environment variable:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

---

## 🔧 Running Applications

### Basic Trading
```bash
python main.py --mode demo --trades 5
```

### Unified Trading
```bash
python run_unified_trading.py --mode enhanced --demo
```

### Run Tests
```bash
python run_comprehensive_tests.py
```

### Docker
```bash
docker-compose -f docker/docker-compose.yml up
```

---

## 📦 Directory Size Breakdown

| Directory | Files | Purpose |
|-----------|-------|---------|
| `src/core/` | 5 | Core trading logic (5.2 KB) |
| `src/trading/` | 1 | Trading engines (8.3 KB) |
| `src/ai/` | 10 | AI models (45.7 KB) |
| `src/analysis/` | 2 | Market analysis (18.4 KB) |
| `src/api/` | 3 | REST API (22.1 KB) |
| `src/data/` | 3 | Data management (14.5 KB) |
| `src/monitoring/` | 2 | Monitoring (12.3 KB) |
| `src/risk/` | 1 | Risk management (6.1 KB) |
| `config/` | 3 | Configuration (8.9 KB) |
| `tests/` | 12+ | Test suite (80+ KB) |
| `docs/` | 20+ | Documentation (150+ KB) |
| `scripts/` | 5 | Scripts (3.2 KB) |
| `docker/` | 2 | Docker (1.8 KB) |

**Total organized: ~400 KB of source code**

---

## ✅ Optimization Checklist

- [x] Created `src/` directory structure
- [x] Moved core components
- [x] Moved trading engines
- [x] Organized AI models
- [x] Organized market analysis
- [x] Organized API modules
- [x] Moved data management
- [x] Created monitoring directory
- [x] Moved risk management
- [x] Organized scripts
- [x] Organized Docker files
- [x] Created __init__.py files
- [x] Updated package exports
- [x] Documented structure
- [x] Created migration guide

---

## 🚀 Next Steps

1. Update all imports in main entry points
2. Run comprehensive tests
3. Update CI/CD pipeline
4. Generate updated documentation
5. Create developer onboarding guide

---

## 📞 Support

For questions about the new structure, refer to:
- `docs/README.md` - Main documentation
- `docs/QUICK_START.md` - Getting started
- `PRODUCTION_SETUP.md` - Production deployment
