#!/usr/bin/env python3
"""
Test Script for Monitoring System
Tests all monitoring components and creates sample data

Tests:
- Logging configuration
- Metrics collection
- Alert system
- Health checks
- Monitor display
- Performance dashboard
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logging_config import LoggingConfig
from metrics_collector import MetricsCollector
from alert_system import AlertSystem, AlertType, AlertLevel
from health_check import HealthCheck


def create_sample_trades(collector: MetricsCollector, count: int = 20):
    """Create sample trades for testing"""
    print(f"\nCreating {count} sample trades...")

    pairs = ['EURUSD-OTC', 'GBPUSD-OTC', 'USDJPY-OTC']
    signals = ['CALL', 'PUT']

    for i in range(count):
        # Create trade
        timestamp = (datetime.now() - timedelta(minutes=count-i)).isoformat()
        pair = random.choice(pairs)
        signal = random.choice(signals)
        confidence = random.uniform(60, 95)

        trade = {
            'timestamp': timestamp,
            'pair': pair,
            'signal': signal,
            'confidence': round(confidence, 2),
            'amount': 2.0,
            'duration': 1,
            'entry_price': random.uniform(1.0, 150.0),
            'payout': random.uniform(70, 90),
            'rsi': random.uniform(20, 80),
            'macd_histogram': random.uniform(-0.1, 0.1),
            'stoch_k': random.uniform(10, 90),
            'adx': random.uniform(20, 50),
            'bb_position': random.uniform(0, 1),
        }

        collector.record_trade(trade)

        # Add result to some trades
        if random.random() < 0.7:  # 70% of trades completed
            result = random.choices(
                ['WIN', 'LOSS', 'TIE'],
                weights=[55, 40, 5],  # 55% win rate
                k=1
            )[0]

            profit = random.uniform(-2, 3) if result == 'WIN' else random.uniform(-3, -0.5)
            if result == 'TIE':
                profit = 0

            trade['result'] = result
            trade['profit'] = round(profit, 2)
            trade['order_id'] = random.randint(10000, 99999)
            trade['exit_price'] = random.uniform(1.0, 150.0)

            collector.update_trade_result(timestamp, trade)

    print(f"✓ Created {count} sample trades")


def create_sample_status(data_dir: str = "data"):
    """Create sample status file"""
    print("\nCreating sample status...")

    status = {
        'is_running': True,
        'connected': True,
        'active_trades': random.randint(0, 3),
        'last_trade_time': (datetime.now() - timedelta(minutes=5)).isoformat(),
        'uptime_seconds': 3600,
    }

    status_file = Path(data_dir) / "status.json"
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)

    print(f"✓ Created status file")


def test_logging():
    """Test logging configuration"""
    print("\n" + "=" * 80)
    print("TEST: LOGGING CONFIGURATION")
    print("=" * 80)

    config = LoggingConfig(log_dir="logs")

    # Test all loggers
    print("\nTesting loggers...")
    loggers = [
        ('Trading', config.get_trading_logger()),
        ('Analysis', config.get_analysis_logger()),
        ('Error', config.get_error_logger()),
        ('Alert', config.get_alert_logger()),
        ('Metrics', config.get_metrics_logger()),
    ]

    for name, logger in loggers:
        logger.info(f"Test log message from {name}")
        print(f"  ✓ {name} logger working")

    # Verify logs
    print("\nVerifying log files...")
    if config.verify_logs():
        print("  ✓ All log files created successfully")
    else:
        print("  ✗ Log file verification failed")

    # Show log files
    print("\nLog files:")
    files = config.get_log_files()
    for name, info in sorted(files.items()):
        print(f"  {name}: {info['size_bytes']} bytes")

    return len(files) > 0


def test_metrics_collection():
    """Test metrics collection system"""
    print("\n" + "=" * 80)
    print("TEST: METRICS COLLECTION")
    print("=" * 80)

    collector = MetricsCollector(data_dir="data")

    # Create sample trades
    create_sample_trades(collector, count=20)

    # Save metrics
    print("\nSaving metrics...")
    metrics = {
        'total_trades': 20,
        'wins': 11,
        'losses': 8,
        'ties': 1,
        'win_rate': 55.0,
        'total_profit': 5.50,
        'daily_profit': 3.50,
        'daily_loss': -2.00,
        'consecutive_losses': 1,
        'max_drawdown': 5.50,
        'trades_per_hour': 4.2,
        'avg_profit_per_trade': 0.275,
    }

    if collector.save_metrics(metrics):
        print("  ✓ Metrics saved")
    else:
        print("  ✗ Metrics save failed")

    # Save status
    create_sample_status()

    # Show data size
    print("\nData file sizes:")
    sizes = collector.get_data_size()
    for name, size in sizes.items():
        print(f"  {name}: {size} MB")

    # Get database stats
    print("\nDatabase statistics:")
    stats = collector.get_db_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    return len(sizes) > 0


def test_alert_system():
    """Test alert system"""
    print("\n" + "=" * 80)
    print("TEST: ALERT SYSTEM")
    print("=" * 80)

    alert_system = AlertSystem(data_dir="data", log_dir="logs")

    print("\nTesting alerts...")

    # Create sample alerts
    alerts_to_test = [
        (AlertType.CONSECUTIVE_LOSSES, AlertLevel.CRITICAL, "3 consecutive losses detected"),
        (AlertType.DAILY_LOSS_LIMIT, AlertLevel.WARNING, "Daily loss limit 80% reached"),
        (AlertType.CONNECTION_ISSUE, AlertLevel.INFO, "Connection restored"),
        (AlertType.LOW_SIGNAL_QUALITY, AlertLevel.WARNING, "Low signal quality detected"),
    ]

    for alert_type, level, message in alerts_to_test:
        alert = alert_system.trigger_alert(alert_type, level, message)
        print(f"  ✓ {alert_type.value} alert triggered")

    # Print active alerts
    print("\nActive alerts:")
    alert_system.print_alerts()

    # Run checks
    print("\nRunning alert system checks...")
    results = alert_system.run_checks()
    for check, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {check}: {status}")

    return True


def test_health_check():
    """Test health check system"""
    print("\n" + "=" * 80)
    print("TEST: HEALTH CHECK")
    print("=" * 80)

    checker = HealthCheck(data_dir="data", log_dir="logs")

    # Run all checks
    print("\nRunning health checks...")
    healthy = checker.run_all_checks()

    return healthy


def test_monitor_script():
    """Test monitor script functionality"""
    print("\n" + "=" * 80)
    print("TEST: MONITOR SCRIPT")
    print("=" * 80)

    from monitor_paper_trading import PaperTradingMonitor

    monitor = PaperTradingMonitor(data_dir="data", log_dir="logs")

    print("\nCalculating metrics...")
    metrics = monitor.calculate_metrics()

    print("Metrics calculated:")
    for key, value in sorted(metrics.items()):
        print(f"  {key}: {value}")

    print("\nGetting active trades...")
    active = monitor.get_active_trades()
    print(f"  Active trades: {len(active)}")

    print("\nGetting recent trades...")
    recent = monitor.get_recent_trades(5)
    print(f"  Recent completed trades: {len(recent)}")

    return True


def test_performance_dashboard():
    """Test performance dashboard"""
    print("\n" + "=" * 80)
    print("TEST: PERFORMANCE DASHBOARD")
    print("=" * 80)

    from performance_dashboard import PerformanceDashboard

    dashboard = PerformanceDashboard(data_dir="data")

    print("\nAnalyzing pair performance...")
    pair_stats = dashboard.get_pair_statistics()
    print(f"  Pairs analyzed: {len(pair_stats)}")
    for pair, stats in list(pair_stats.items())[:3]:
        print(f"    {pair}: {stats['total_trades']} trades, {stats['win_rate']:.1f}% win rate")

    print("\nAnalyzing indicator performance...")
    indicators = dashboard.get_indicator_performance()
    print(f"  Indicators analyzed: {len(indicators)}")
    for ind, stats in list(indicators.items())[:3]:
        print(f"    {ind}: {stats['accuracy']:.1f}% accuracy")

    print("\nAnalyzing drawdown...")
    dd = dashboard.calculate_drawdown_analysis()
    print(f"  Max drawdown: ${dd['max_drawdown']:.2f}")
    print(f"  Avg drawdown: ${dd['avg_drawdown']:.2f}")

    print("\nAnalyzing confidence distribution...")
    conf = dashboard.get_confidence_distribution()
    for bucket, stats in conf.items():
        if stats['count'] > 0:
            print(f"  {bucket}: {stats['count']} signals, {stats['win_rate']:.1f}% win rate")

    # Generate report
    print("\n" + "-" * 80)
    print("Performance Report:")
    print("-" * 80)
    report = dashboard.generate_report()
    print(report)

    return True


def run_all_tests():
    """Run all monitoring system tests"""
    print("\n" + "=" * 80)
    print("MONITORING SYSTEM TEST SUITE")
    print("=" * 80)

    results = {}

    try:
        results['logging'] = test_logging()
    except Exception as e:
        print(f"\n✗ Logging test failed: {e}")
        results['logging'] = False

    try:
        results['metrics'] = test_metrics_collection()
    except Exception as e:
        print(f"\n✗ Metrics test failed: {e}")
        results['metrics'] = False

    try:
        results['alerts'] = test_alert_system()
    except Exception as e:
        print(f"\n✗ Alert system test failed: {e}")
        results['alerts'] = False

    try:
        results['health_check'] = test_health_check()
    except Exception as e:
        print(f"\n✗ Health check test failed: {e}")
        results['health_check'] = False

    try:
        results['monitor'] = test_monitor_script()
    except Exception as e:
        print(f"\n✗ Monitor script test failed: {e}")
        results['monitor'] = False

    try:
        results['dashboard'] = test_performance_dashboard()
    except Exception as e:
        print(f"\n✗ Dashboard test failed: {e}")
        results['dashboard'] = False

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"  [{symbol}] {test}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All monitoring system tests PASSED!")
        return True
    else:
        print(f"\n✗ {total - passed} test(s) FAILED")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Test monitoring system components')
    parser.add_argument('--logging', action='store_true', help='Test logging')
    parser.add_argument('--metrics', action='store_true', help='Test metrics collection')
    parser.add_argument('--alerts', action='store_true', help='Test alert system')
    parser.add_argument('--health', action='store_true', help='Test health check')
    parser.add_argument('--monitor', action='store_true', help='Test monitor script')
    parser.add_argument('--dashboard', action='store_true', help='Test dashboard')
    parser.add_argument('--all', action='store_true', help='Run all tests')

    args = parser.parse_args()

    # Run all tests if no specific test selected or --all specified
    if args.all or not any(vars(args).values()):
        success = run_all_tests()
    else:
        # Run specific tests
        success = True
        if args.logging:
            success = test_logging() and success
        if args.metrics:
            success = test_metrics_collection() and success
        if args.alerts:
            success = test_alert_system() and success
        if args.health:
            success = test_health_check() and success
        if args.monitor:
            success = test_monitor_script() and success
        if args.dashboard:
            success = test_performance_dashboard() and success

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
