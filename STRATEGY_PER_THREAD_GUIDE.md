# 🧵 Strategy-Per-Thread Architecture Guide

## 🎯 Overview

The **Strategy-Per-Thread** architecture runs each trading strategy in its own dedicated thread, allowing 7 strategies to trade independently and simultaneously.

---

## 🏗️ Architecture

### Thread Model

```
┌─────────────────────────────────────────────────────────────┐
│                  Strategy Orchestrator                       │
│  (Main Coordinator + API Connection + Database Logger)      │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─────────────────────────────────────────────────┐
             │                                                 │
    ┌────────▼────────┐                              ┌────────▼────────┐
    │  Thread 1       │                              │  Thread 7       │
    │  enhanced_      │                              │  support_       │
    │  candle_count   │                              │  resistance     │
    │                 │                              │                 │
    │  • Scan         │         ...                  │  • Scan         │
    │  • Analyze      │                              │  • Analyze      │
    │  • Trade        │                              │  • Trade        │
    │  • Track P&L    │                              │  • Track P&L    │
    └─────────────────┘                              └─────────────────┘
```

### 7 Independent Strategy Threads

Each strategy runs in isolation:

1. **enhanced_candle_count** - Multi-window candle pattern analysis
2. **rsi_divergence** - RSI with divergence detection
3. **macd_momentum** - MACD crossover with momentum
4. **bollinger_rsi_combo** - Bollinger Bands + RSI combo
5. **stochastic** - Stochastic oscillator reversals
6. **trend_alignment** - Multi-timeframe EMA alignment
7. **support_resistance** - S/R breakout detection

---

## 🔧 Key Components

### 1. StrategyThread Class

Each strategy thread is an independent trader:

```python
class StrategyThread:
    - strategy_name: str
    - api_client: ApiClient (shared, thread-safe)
    - db_logger: MultiAccountTradeLogger (shared)
    - strategy_engine: AdvancedStrategyEngine
    
    Methods:
    - can_trade() -> bool
    - get_available_instruments() -> List[str]
    - analyze_instrument(instrument) -> Optional[Tuple]
    - execute_trade(...) -> Optional[Dict]
    - trade_cycle()
    - run() (main loop)
    - start() / stop()
    - get_stats() -> Dict
```

### 2. StrategyOrchestrator Class

Coordinates all strategy threads:

```python
class StrategyOrchestrator:
    - api: IQ_Option (single connection)
    - api_client: ApiClient (thread-safe wrapper)
    - db_logger: MultiAccountTradeLogger
    - strategies: Dict[str, StrategyThread]
    
    Methods:
    - connect() -> bool
    - initialize_strategies()
    - start() / stop()
    - get_statistics() -> Dict
```

---

## 📊 How It Works

### Startup Sequence

1. **Orchestrator Initialization**
   ```
   ✅ Connect to IQ Option
   ✅ Initialize API client (thread-safe)
   ✅ Initialize database logger
   ✅ Create 7 strategy threads
   ```

2. **Strategy Thread Initialization**
   ```
   For each strategy:
   ✅ Create StrategyThread instance
   ✅ Initialize AdvancedStrategyEngine
   ✅ Set up performance tracking
   ✅ Start dedicated thread
   ```

3. **Parallel Execution**
   ```
   All 7 threads run simultaneously:
   Thread 1: Scan → Analyze → Trade → Wait → Repeat
   Thread 2: Scan → Analyze → Trade → Wait → Repeat
   ...
   Thread 7: Scan → Analyze → Trade → Wait → Repeat
   ```

### Trading Cycle (Per Strategy)

```python
while running:
    1. Check if can trade (loss limits, consecutive losses)
    2. Get available instruments
    3. For each instrument:
        a. Get candles
        b. Analyze with strategy engine
        c. Filter by this strategy's signals
        d. If signal found:
            - Execute trade
            - Wait for result
            - Update stats
            - Log to database
            - Update Prometheus metrics
            - Break (wait before next trade)
    4. Sleep for STRATEGY_SCAN_INTERVAL (5 seconds)
```

---

## 🎛️ Configuration

### Environment Variables

```bash
# Strategy Settings
STRATEGY_SCAN_INTERVAL=5          # Seconds between scans per strategy
MIN_SECONDS_BETWEEN_TRADES=70     # Minimum time between trades per strategy

# Risk Management (Per Strategy)
MAX_DAILY_LOSS=50                 # Max loss per strategy
MAX_CONSECUTIVE_LOSSES=5          # Max consecutive losses per strategy

# Trading
BASE_TRADE_AMOUNT=1.0             # Default trade amount
MIN_AI_CONFIDENCE=70              # Minimum confidence threshold
```

### Strategy Configuration

Strategies are defined in `StrategyThreadConfig.STRATEGIES_TO_RUN`:

```python
STRATEGIES_TO_RUN = [
    'enhanced_candle_count',
    'rsi_divergence',
    'macd_momentum',
    'bollinger_rsi_combo',
    'stochastic',
    'trend_alignment',
    'support_resistance'
]
```

---

## 📈 Performance Tracking

### Per-Strategy Metrics

Each strategy tracks independently:

- **Trades**: Total trades executed
- **Wins/Losses**: Win/loss count
- **Win Rate**: Percentage of winning trades
- **Daily P&L**: Profit/loss for the day
- **Average Confidence**: Average signal confidence
- **Consecutive Losses**: Current losing streak

### Prometheus Metrics

```
# Per-strategy metrics
kael_strategy_total_trades{strategy="rsi_divergence"}
kael_strategy_wins{strategy="rsi_divergence"}
kael_strategy_losses{strategy="rsi_divergence"}
kael_strategy_win_rate{strategy="rsi_divergence"}
kael_strategy_daily_pnl{strategy="rsi_divergence"}
kael_strategy_avg_confidence{strategy="rsi_divergence"}

# Portfolio metrics
kael_portfolio_balance
kael_portfolio_daily_pnl
kael_active_strategies
```

---

## 🔒 Thread Safety

### Shared Resources

1. **API Client** - Thread-safe with locking
   ```python
   class ApiClient:
       self.lock = threading.Lock()
       
       def _rate_limit(self):
           with self.lock:
               # Rate limiting logic
   ```

2. **Database Logger** - Thread-safe connections
   ```python
   # Each thread gets its own database session
   # Transactions are isolated
   ```

3. **Prometheus Metrics** - Thread-safe by design
   ```python
   # Prometheus client library handles thread safety
   prometheus_strategy_trades.labels(strategy=name).inc()
   ```

---

## 🚀 Running the System

### Start the Bot

```bash
# Using Python directly
python autonomous_parallel_trading_bot.py

# Using Docker
docker-compose -f docker-compose.parallel.yml up -d
```

### Monitor Strategies

```bash
# View logs
docker logs kael-parallel-trading-bot -f

# Check strategy status
curl http://localhost:5001/strategies

# Get specific strategy
curl http://localhost:5001/strategy/rsi_divergence

# View recent trades
curl http://localhost:5001/recent_trades?strategy=macd_momentum
```

---

## 📊 API Endpoints

### Strategy Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/statistics` | GET | Overall statistics |
| `/strategies` | GET | All strategies status |
| `/strategy/<name>` | GET | Specific strategy details |
| `/strategy_stats` | GET | Strategy performance from DB |
| `/recent_trades` | GET | Recent trades (filterable by strategy) |
| `/stop` | POST | Graceful shutdown |
| `/metrics` | GET | Prometheus metrics |

### Example Responses

**GET /strategies**
```json
{
  "strategies": [
    {
      "strategy": "rsi_divergence",
      "trades": 15,
      "wins": 10,
      "losses": 5,
      "win_rate": 66.67,
      "daily_pnl": 5.50,
      "avg_confidence": 0.78,
      "consecutive_losses": 0,
      "is_running": true
    },
    ...
  ],
  "total": 7,
  "active": 7
}
```

**GET /strategy/rsi_divergence**
```json
{
  "strategy": "rsi_divergence",
  "trades": 15,
  "wins": 10,
  "losses": 5,
  "win_rate": 66.67,
  "daily_pnl": 5.50,
  "avg_confidence": 0.78,
  "consecutive_losses": 0,
  "is_running": true
}
```

---

## 🎯 Advantages

### 1. True Parallelism
- All 7 strategies trade simultaneously
- No waiting for other strategies
- Maximum market coverage

### 2. Strategy Isolation
- Each strategy has independent:
  - P&L tracking
  - Risk limits
  - Performance metrics
  - Trade history

### 3. Independent Risk Management
- Per-strategy loss limits
- Per-strategy consecutive loss protection
- Portfolio-wide aggregation

### 4. Easy Monitoring
- Per-strategy Prometheus metrics
- Individual strategy health tracking
- Granular performance analysis

### 5. Scalability
- Easy to add/remove strategies
- Simple to adjust per-strategy parameters
- Clean separation of concerns

---

## ⚠️ Important Considerations

### 1. API Rate Limiting
- All threads share one API connection
- ApiClient enforces rate limiting
- Minimum 0.3s between API calls

### 2. Risk Management
- Each strategy has its own limits
- Portfolio-wide balance shared
- Monitor total exposure

### 3. Database Load
- 7 threads writing to database
- Connection pooling recommended
- Monitor database performance

### 4. Resource Usage
- 7 threads + main thread + API thread
- Monitor CPU/memory usage
- Adjust scan intervals if needed

---

## 🔍 Monitoring & Debugging

### View Strategy Status

```bash
# Real-time logs
tail -f logs/strategy_threads_*.log | grep "STRATEGY STATUS"

# Per-strategy logs
tail -f logs/strategy_threads_*.log | grep "Strategy-rsi_divergence"
```

### Check Performance

```bash
# Grafana dashboard
http://localhost:3000

# Prometheus metrics
http://localhost:9090/graph

# Query specific strategy
kael_strategy_win_rate{strategy="rsi_divergence"}
```

### Database Queries

```sql
-- Strategy performance
SELECT 
    selected_strategy,
    COUNT(*) as trades,
    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
    ROUND(AVG(CASE WHEN result = 'WIN' THEN 100.0 ELSE 0.0 END), 2) as win_rate,
    ROUND(SUM(profit), 2) as total_pnl
FROM trades
WHERE entry_time >= CURRENT_DATE
GROUP BY selected_strategy
ORDER BY total_pnl DESC;
```

---

## 🎨 Customization

### Add New Strategy

1. **Implement in AdvancedStrategyEngine**
   ```python
   def my_new_strategy(self, closes, highs, lows):
       # Strategy logic
       return StrategySignal(...)
   ```

2. **Add to analyze() method**
   ```python
   result = self.my_new_strategy(closes, highs, lows)
   if result:
       strategies_results.append(result)
   ```

3. **Add to STRATEGIES_TO_RUN**
   ```python
   STRATEGIES_TO_RUN = [
       'enhanced_candle_count',
       'rsi_divergence',
       'my_new_strategy',  # Add here
       ...
   ]
   ```

### Adjust Strategy Parameters

Edit `StrategyThreadConfig`:

```python
# Per-strategy scan interval
STRATEGY_SCAN_INTERVAL = 5  # seconds

# Per-strategy risk limits
MAX_DAILY_LOSS = 50  # per strategy
MAX_CONSECUTIVE_LOSSES = 5  # per strategy
```

---

## 📝 Best Practices

1. **Monitor All Strategies**
   - Check status every hour
   - Review win rates daily
   - Analyze P&L trends

2. **Adjust Based on Performance**
   - Disable underperforming strategies
   - Increase allocation to winners
   - Tune confidence thresholds

3. **Risk Management**
   - Set conservative limits initially
   - Monitor total portfolio exposure
   - Use stop-loss per strategy

4. **Database Maintenance**
   - Regular backups
   - Archive old trades
   - Monitor disk usage

5. **Logging**
   - Keep logs for analysis
   - Monitor error rates
   - Track API failures

---

## 🎉 Summary

The **Strategy-Per-Thread** architecture provides:

✅ **7 concurrent strategies** trading independently  
✅ **True parallelism** with dedicated threads  
✅ **Independent risk management** per strategy  
✅ **Comprehensive monitoring** via Prometheus/Grafana  
✅ **Database logging** for all trades  
✅ **RESTful API** for management  
✅ **Thread-safe** shared resources  
✅ **Scalable** and maintainable design  

**Perfect for evaluating multiple strategies simultaneously!** 🚀📈
