# Project Cleanup and Reorganization Plan

## Current Issues
1. Test files scattered in root directory (9 files)
2. Multiple configuration files (settings, parallel_settings, enhanced_settings)
3. Documentation files mixed with code
4. No clear separation of production vs development files

## Proposed Structure

```
advanced_trading_system/
├── src/                          # Production source code
│   ├── core/                     # Core trading logic
│   │   ├── __init__.py
│   │   ├── iqoption_wrapper.py  # IQOption API wrapper
│   │   └── trading_engine.py    # Main trading engine
│   ├── ai_models/               # AI models (keep as is)
│   ├── analysis/                # Market analysis (keep as is)
│   ├── database/                # Database operations (keep as is)
│   ├── risk_management/         # Risk management (keep as is)
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── helpers.py
│
├── config/                       # Configuration files
│   ├── __init__.py
│   ├── settings.py              # Main settings (consolidated)
│   └── credentials.example.py   # Example credentials
│
├── api/                         # FastAPI application
│   ├── __init__.py
│   ├── main.py                  # API entry point
│   ├── models.py                # Pydantic models
│   └── routes/                  # API routes
│       ├── __init__.py
│       ├── trading.py
│       └── analysis.py
│
├── scripts/                     # Utility scripts
│   ├── run_trading.py          # Main trading script
│   ├── run_api.py              # API server
│   └── setup.py                # Setup utilities
│
├── tests/                       # All tests (moved from root)
│   ├── __init__.py
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test fixtures
│
├── docs/                        # Documentation
│   ├── API.md
│   ├── DEPLOYMENT.md
│   ├── TESTING.md
│   └── reports/                # Test reports
│
├── logs/                        # Log files (gitignored)
│
├── .env.example                 # Environment variables example
├── .gitignore                  # Git ignore file
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker composition
├── Dockerfile                  # Docker image
└── README.md                   # Main documentation
```

## Cleanup Actions

### 1. Move Test Files
- Move all `test_*.py` to `tests/integration/`
- Move all `*_output.txt` to `docs/reports/`
- Keep only production code in root

### 2. Consolidate Configuration
- Merge `settings.py`, `parallel_settings.py`, `enhanced_settings.py`
- Create single `config/settings.py` with all options
- Use environment variables for credentials

### 3. Organize Documentation
- Move all `.md` files to `docs/`
- Keep only `README.md` in root

### 4. Clean Up Root Directory
- Remove test files
- Remove temporary files
- Keep only essential production files

## Files to Archive
- `test_all_components_*.py` → `tests/integration/`
- `test_parallel_real.py` → `tests/integration/`
- `test_real_credentials.py` → `tests/integration/`
- All `*_output.txt` → `docs/reports/`
- All report `.md` files → `docs/reports/`

## Production Entry Points
1. `scripts/run_trading.py` - Main trading bot
2. `scripts/run_api.py` - API server
3. `docker-compose up` - Full stack deployment
