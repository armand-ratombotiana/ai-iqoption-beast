Grafana: Strategy Performance Dashboard

This file contains a ready-to-use SQL query and a small panel JSON snippet to visualize per-strategy P&L and win-rate.

1) Recommended Grafana datasource
- For production use, point Grafana to the PostgreSQL/TimescaleDB `kael` database (datasource name: `Postgres`).
- For quick local testing you can export SQLite data and import into Postgres, or use the bot's Prometheus metrics (preferred for real-time).

2) Useful SQL (Postgres / TimescaleDB)

-- Per-strategy P&L over time (time bucketed)
SELECT
  time_bucket('1 hour', ts) AS time,
  strategy_name,
  sum(total_profit) AS profit
FROM v_strategy_performance
WHERE $__timeFilter(ts)
GROUP BY 1, 2
ORDER BY 1 ASC

-- Win rate per strategy
SELECT
  strategy_name,
  (sum(wins)::float / NULLIF(sum(wins)+sum(losses),0)) * 100 AS win_rate
FROM v_strategy_performance
WHERE $__timeFilter(ts)
GROUP BY strategy_name
ORDER BY win_rate DESC;

3) Minimal Grafana panel JSON snippet (use in a dashboard's `panels` array)

{
  "type": "timeseries",
  "title": "Per-strategy P&L (1h)",
  "datasource": "Postgres",
  "targets": [
    {
      "format": "time_series",
      "rawSql": "SELECT time_bucket('1 hour', ts) AS time, strategy_name, sum(total_profit) AS profit FROM v_strategy_performance WHERE $__timeFilter(ts) GROUP BY 1,2 ORDER BY 1",
      "refId": "A"
    }
  ],
  "fieldConfig": { "defaults": {}, "overrides": [] }
}

4) Next steps
- If you want me to provision this dashboard automatically, I can create Grafana provisioning files (YAML + JSON) under `monitoring/grafana/provisioning/dashboards/` so Grafana loads it on startup. Tell me if you want that and which datasource name Grafana should use (default: `Postgres`).

Notes:
- Currently the bot is using local SQLite fallback (no `strategy_votes` table in Postgres). To enable Postgres logging point `DATABASE_URL` to TimescaleDB and restart the bot, or I can run a small migration to move local SQLite trade logs to Postgres.
