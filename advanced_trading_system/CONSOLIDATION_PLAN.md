# Script Consolidation Plan

## Problem: Multiple Confusing Entry Points

Currently there are **4 different main scripts**:
1. `scripts/run_trading.py` - Advanced AI system
2. `run_trading_system.py` - Simple production system
3. `scripts/run_enhanced_trading.py` - Enhanced AI system
4. `scripts/run_parallel_trading.py` - Parallel trading system

**This is confusing!** Users don't know which one to use.

## Solution: Single Unified Entry Point

Create **ONE** main script: `trade.py` with multiple modes:

```bash
# Simple trading (current run_trading_system.py)
python trade.py --mode simple --trades 5

# Advanced AI trading (current run_trading.py)
python trade.py --mode advanced --trades 5

# Enhanced AI trading (current run_enhanced_trading.py)
python trade.py --mode enhanced --trades 5

# Parallel trading (current run_parallel_trading.py)
python trade.py --mode parallel --trades 5

# Default (simple)
python trade.py --trades 5
```

## Implementation

1. Keep `run_trading_system.py` as the backend engine
2. Keep other scripts in `scripts/` for backward compatibility
3. Make `trade.py` the ONLY user-facing entry point
4. Update documentation to reference only `trade.py`

## File Structure After Consolidation

```
advanced_trading_system/
├── trade.py                          # ONLY user-facing entry point
│
├── run_trading_system.py             # Backend engine (simple mode)
│
├── scripts/                          # Backend implementations
│   ├── run_trading.py                # Advanced AI backend
│   ├── run_enhanced_trading.py       # Enhanced AI backend
│   └── run_parallel_trading.py       # Parallel backend
│
└── README.md                         # Updated to only show trade.py
```

## User Experience

**Before (Confusing):**
```bash
# Which one do I use???
python run_trading_system.py --mode demo
python scripts/run_trading.py
python scripts/run_enhanced_trading.py
python scripts/run_parallel_trading.py
```

**After (Clear):**
```bash
# One command, multiple modes
python trade.py --mode simple --trades 5
python trade.py --mode advanced --trades 5
python trade.py --mode enhanced --trades 5
python trade.py --mode parallel --trades 5
```
