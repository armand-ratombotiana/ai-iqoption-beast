#!/usr/bin/env python3
"""
2-Hour Live Monitoring Script
Tracks bot performance, logs all metrics, generates comprehensive report
"""

import requests
import time
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
from typing import Dict, List

# Configuration
MONITORING_DURATION_HOURS = 2
CHECK_INTERVAL_SECONDS = 300  # 5 minutes
STATS_URL = "http://localhost:5001/statistics"
LOG_DIR = Path("logs/monitoring")
SESSION_START = datetime.now().strftime("%Y%m%d_%H%M%S")

# Create log directory
LOG_DIR.mkdir(parents=True, exist_ok=True)

# File paths
LOG_FILE = LOG_DIR / f"session_{SESSION_START}.log"
STATS_CSV = LOG_DIR / f"stats_{SESSION_START}.csv"
TRADES_CSV = LOG_DIR / f"trades_{SESSION_START}.csv"

# Metrics tracking
metrics_history = []
trades_history = []
errors_detected = []


def log(message: str):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE, 'a') as f:
        f.write(log_message + "\n")


def get_stats() -> Dict:
    """Fetch current statistics from bot API"""
    try:
        response = requests.get(STATS_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log(f"❌ Error fetching stats: {e}")
        return None


def check_docker_health() -> bool:
    """Check if Docker container is running"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=kael-parallel-trading-bot', '--format', '{{.Status}}'],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except:
        return False


def check_errors() -> List[str]:
    """Check Docker logs for recent errors"""
    try:
        result = subprocess.run(
            ['docker', 'logs', 'kael-parallel-trading-bot', '--since', '5m'],
            capture_output=True,
            text=True
        )
        errors = []
        for line in result.stderr.splitlines():
            if any(word in line.lower() for word in ['error', 'warning', 'failed', 'buy late']):
                errors.append(line)
        return errors[-5:]  # Last 5 errors
    except:
        return []


def save_metrics_csv(stats: Dict, iteration: int):
    """Save metrics to CSV"""
    row = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'iteration': iteration,
        'balance': stats.get('balance', 0),
        'trades_today': stats.get('trades_today', 0),
        'win_rate': stats.get('win_rate', 0),
        'daily_profit': stats.get('daily_net', 0),
        'active_count': stats.get('active_count', 0),
        'reconnect_count': stats.get('reconnect_count', 0),
        'status': stats.get('status', 'unknown'),
        'avg_execution_ms': stats.get('avg_execution_time_ms', 0),
    }

    # Write header if file doesn't exist
    file_exists = STATS_CSV.exists()
    with open(STATS_CSV, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    metrics_history.append(row)


def save_trades_csv(stats: Dict):
    """Save individual trade data to CSV"""
    instrument_stats = stats.get('instrument_stats', [])

    file_exists = TRADES_CSV.exists()
    with open(TRADES_CSV, 'a', newline='') as f:
        fieldnames = ['timestamp', 'instrument', 'total_trades', 'wins', 'losses',
                     'win_rate', 'profit', 'avg_execution_ms', 'avg_payout_ratio']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for inst in instrument_stats:
            row = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'instrument': inst.get('instrument', 'unknown'),
                'total_trades': inst.get('total_trades', 0),
                'wins': inst.get('wins', 0),
                'losses': inst.get('losses', 0),
                'win_rate': inst.get('win_rate', 0),
                'profit': inst.get('profit', 0),
                'avg_execution_ms': inst.get('avg_execution_ms', 0),
                'avg_payout_ratio': inst.get('avg_payout_ratio', 0),
            }
            writer.writerow(row)


def generate_summary_report():
    """Generate comprehensive summary report"""
    report_file = LOG_DIR / f"summary_{SESSION_START}.txt"

    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("2-HOUR MONITORING SESSION - COMPREHENSIVE REPORT\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Session Start: {SESSION_START}\n")
        f.write(f"Session End: {datetime.now().strftime('%Y%m%d_%H%M%S')}\n")
        f.write(f"Duration: {MONITORING_DURATION_HOURS} hours\n\n")

        if metrics_history:
            start_metrics = metrics_history[0]
            end_metrics = metrics_history[-1]

            f.write("PERFORMANCE SUMMARY:\n")
            f.write("-" * 80 + "\n")
            f.write(f"Starting Balance: ${start_metrics['balance']:.2f}\n")
            f.write(f"Ending Balance: ${end_metrics['balance']:.2f}\n")
            f.write(f"Total Profit/Loss: ${end_metrics['balance'] - start_metrics['balance']:.2f}\n")
            f.write(f"ROI: {((end_metrics['balance'] / start_metrics['balance']) - 1) * 100:.2f}%\n\n")

            f.write(f"Total Trades: {end_metrics['trades_today']}\n")
            f.write(f"Final Win Rate: {end_metrics['win_rate']:.1f}%\n")
            f.write(f"Average Execution Time: {end_metrics['avg_execution_ms']:.0f}ms\n")
            f.write(f"Reconnections: {end_metrics['reconnect_count']}\n\n")

        f.write("METRICS COLLECTED:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Checks: {len(metrics_history)}\n")
        f.write(f"Errors Detected: {len(errors_detected)}\n\n")

        if errors_detected:
            f.write("ERRORS:\n")
            f.write("-" * 80 + "\n")
            for error in errors_detected[-20:]:  # Last 20 errors
                f.write(f"{error}\n")
            f.write("\n")

        f.write("FILES GENERATED:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Session Log: {LOG_FILE}\n")
        f.write(f"Metrics CSV: {STATS_CSV}\n")
        f.write(f"Trades CSV: {TRADES_CSV}\n")
        f.write(f"Summary Report: {report_file}\n")
        f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")

    log(f"📊 Summary report generated: {report_file}")


def main():
    """Main monitoring loop"""
    log("=" * 80)
    log("🚀 2-HOUR MONITORING SESSION STARTED")
    log("=" * 80)
    log(f"Duration: {MONITORING_DURATION_HOURS} hours")
    log(f"Check Interval: {CHECK_INTERVAL_SECONDS} seconds")
    log(f"Statistics URL: {STATS_URL}")
    log("=" * 80)

    end_time = datetime.now() + timedelta(hours=MONITORING_DURATION_HOURS)
    iteration = 0

    try:
        while datetime.now() < end_time:
            iteration += 1
            remaining = (end_time - datetime.now()).total_seconds() / 60
            log("")
            log(f"{'=' * 80}")
            log(f"CHECK #{iteration} | {remaining:.1f} minutes remaining")
            log(f"{'=' * 80}")

            # Check Docker health
            if not check_docker_health():
                log("🚨 CRITICAL: Container is not running!")
                break

            # Fetch statistics
            stats = get_stats()
            if stats:
                balance = stats.get('balance', 0)
                trades = stats.get('trades_today', 0)
                win_rate = stats.get('win_rate', 0)
                profit = stats.get('daily_net', 0)

                log(f"💰 Balance: ${balance:.2f}")
                log(f"📊 Trades: {trades}")
                log(f"🎯 Win Rate: {win_rate:.1f}%")
                log(f"💵 Daily P&L: ${profit:.2f}")

                # Save to CSV
                save_metrics_csv(stats, iteration)
                save_trades_csv(stats)
            else:
                log("⚠️  Failed to fetch statistics")

            # Check for errors
            errors = check_errors()
            if errors:
                log(f"⚠️  {len(errors)} recent errors detected:")
                for error in errors:
                    log(f"   {error[:100]}")
                    errors_detected.append(f"[Check #{iteration}] {error}")

            # Sleep until next check
            if datetime.now() < end_time:
                log(f"⏳ Sleeping for {CHECK_INTERVAL_SECONDS}s...")
                time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        log("\n🛑 Monitoring stopped by user")
    except Exception as e:
        log(f"❌ Error in monitoring loop: {e}")
        import traceback
        log(traceback.format_exc())

    # Generate final report
    log("")
    log("=" * 80)
    log("📊 GENERATING FINAL REPORT...")
    log("=" * 80)

    final_stats = get_stats()
    if final_stats:
        log(f"\n📈 FINAL STATISTICS:")
        log(json.dumps(final_stats, indent=2))

    generate_summary_report()

    log("")
    log("=" * 80)
    log("✅ 2-HOUR MONITORING SESSION COMPLETED")
    log("=" * 80)
    log(f"Log File: {LOG_FILE}")
    log(f"Stats CSV: {STATS_CSV}")
    log(f"Trades CSV: {TRADES_CSV}")
    log("=" * 80)


if __name__ == "__main__":
    main()
