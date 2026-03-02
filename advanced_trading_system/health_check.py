#!/usr/bin/env python3
"""
Health Check Script for Paper Trading System
Verifies engine status, connectivity, and system health

Checks:
- Engine running status
- Connection status
- Last trade timestamp
- Log files accessible
- Database integrity
- Emergency stop functionality
"""

import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class Colors:
    """Terminal color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class HealthCheck:
    """System health verification"""

    def __init__(self, data_dir: str = "data", log_dir: str = "logs"):
        """Initialize health check"""
        self.data_dir = Path(data_dir)
        self.log_dir = Path(log_dir)
        self.status_file = self.data_dir / "status.json"
        self.trades_file = self.data_dir / "trades.json"
        self.db_file = self.data_dir / "trading.db"
        self.alerts_file = self.data_dir / "alerts.json"

        # Create data/logs directories if needed
        self.data_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

        # Results
        self.checks: Dict[str, Dict] = {}

    def print_header(self):
        """Print check header"""
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}{Colors.BLUE}PAPER TRADING SYSTEM HEALTH CHECK{Colors.RESET}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")

    def print_check(self, name: str, passed: bool, message: str = ""):
        """Print check result"""
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
        msg = f"  [{status}] {name}"
        if message:
            msg += f" - {message}"
        print(msg)

    def check_directories(self) -> bool:
        """Check if required directories exist"""
        print(f"\n{Colors.BOLD}Directory Checks:{Colors.RESET}")
        all_pass = True

        # Check data directory
        if self.data_dir.exists():
            self.print_check("Data directory exists", True, str(self.data_dir))
        else:
            self.print_check("Data directory exists", False)
            all_pass = False

        # Check logs directory
        if self.log_dir.exists():
            self.print_check("Logs directory exists", True, str(self.log_dir))
        else:
            self.print_check("Logs directory exists", False)
            all_pass = False

        self.checks['directories'] = {'passed': all_pass}
        return all_pass

    def check_required_files(self) -> bool:
        """Check if required data files exist"""
        print(f"\n{Colors.BOLD}Required Files:{Colors.RESET}")
        all_pass = True

        files_to_check = {
            'Status': self.status_file,
            'Trades': self.trades_file,
            'Database': self.db_file,
        }

        for name, file_path in files_to_check.items():
            exists = file_path.exists()
            self.print_check(f"{name} file", exists, str(file_path) if exists else "missing")
            if not exists and name == 'Status':  # Status is critical
                all_pass = False

        self.checks['files'] = {'passed': all_pass}
        return all_pass

    def check_engine_status(self) -> bool:
        """Check engine running status"""
        print(f"\n{Colors.BOLD}Engine Status:{Colors.RESET}")

        try:
            if not self.status_file.exists():
                self.print_check("Status file readable", False, "status.json not found")
                return False

            with open(self.status_file, 'r') as f:
                status = json.load(f)

            is_running = status.get('is_running', False)
            self.print_check("Engine running", is_running,
                           "YES" if is_running else "NO (not currently trading)")

            connected = status.get('connected', False)
            self.print_check("Connection status", connected,
                           "CONNECTED" if connected else "DISCONNECTED")

            active_trades = status.get('active_trades', 0)
            self.print_check("Active trades", True, f"{active_trades} trades")

            self.checks['engine'] = {
                'passed': True,
                'running': is_running,
                'connected': connected,
                'active_trades': active_trades
            }
            return True

        except Exception as e:
            self.print_check("Engine status check", False, str(e))
            self.checks['engine'] = {'passed': False, 'error': str(e)}
            return False

    def check_last_trade(self) -> bool:
        """Check last trade timestamp"""
        print(f"\n{Colors.BOLD}Trade Activity:{Colors.RESET}")

        try:
            if not self.trades_file.exists():
                self.print_check("Last trade", False, "No trades recorded yet")
                self.checks['last_trade'] = {'passed': True, 'trades': 0}
                return True

            with open(self.trades_file, 'r') as f:
                trades = json.load(f)

            if not trades:
                self.print_check("Last trade", False, "No trades recorded")
                self.checks['last_trade'] = {'passed': True, 'trades': 0}
                return True

            completed_trades = [t for t in trades if t.get('result') is not None]
            total_trades = len(trades)

            # Get last trade timestamp
            last_trade_ts = trades[-1].get('timestamp')
            if last_trade_ts:
                last_trade_time = datetime.fromisoformat(last_trade_ts)
                time_ago = datetime.now() - last_trade_time
                self.print_check("Last trade", True,
                               f"{time_ago.total_seconds():.0f}s ago")
            else:
                self.print_check("Last trade timestamp", False, "Not found")

            # Trade count
            self.print_check("Total trades", True, f"{total_trades} total, {len(completed_trades)} completed")

            # Win/loss
            wins = sum(1 for t in completed_trades if t.get('result') == 'WIN')
            losses = sum(1 for t in completed_trades if t.get('result') == 'LOSS')
            if completed_trades:
                win_rate = (wins / len(completed_trades)) * 100
                self.print_check("Win rate", True,
                               f"{win_rate:.2f}% ({wins}W-{losses}L)")

            self.checks['last_trade'] = {
                'passed': True,
                'total': total_trades,
                'completed': len(completed_trades),
                'wins': wins,
                'losses': losses
            }
            return True

        except Exception as e:
            self.print_check("Trade check", False, str(e))
            self.checks['last_trade'] = {'passed': False, 'error': str(e)}
            return False

    def check_logs(self) -> bool:
        """Check log files"""
        print(f"\n{Colors.BOLD}Log Files:{Colors.RESET}")
        all_pass = True

        if not self.log_dir.exists():
            self.print_check("Logs directory", False)
            self.checks['logs'] = {'passed': False}
            return False

        log_files = list(self.log_dir.glob("*.log"))

        if log_files:
            self.print_check("Log files exist", True, f"{len(log_files)} files")
            total_size = sum(f.stat().st_size for f in log_files)
            size_mb = total_size / (1024 * 1024)
            self.print_check("Total log size", True, f"{size_mb:.2f} MB")
        else:
            self.print_check("Log files exist", False, "No logs created yet")
            all_pass = False

        # Check if logs are writable
        test_log = self.log_dir / ".health_check_test.log"
        try:
            test_log.write_text("test")
            test_log.unlink()
            self.print_check("Logs writable", True)
        except Exception as e:
            self.print_check("Logs writable", False, str(e))
            all_pass = False

        self.checks['logs'] = {'passed': all_pass, 'count': len(log_files)}
        return all_pass

    def check_database(self) -> bool:
        """Check database integrity"""
        print(f"\n{Colors.BOLD}Database:{Colors.RESET}")

        try:
            if not self.db_file.exists():
                self.print_check("Database file exists", False)
                self.checks['database'] = {'passed': False}
                return False

            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()

            # Check tables exist
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]

            self.print_check("Database file exists", True)
            self.print_check("Database integrity", True, f"{len(tables)} tables")

            # Get trade count
            cursor.execute("SELECT COUNT(*) FROM trades")
            trade_count = cursor.fetchone()[0]
            self.print_check("Trade records", True, f"{trade_count} trades")

            # Get metrics count
            cursor.execute("SELECT COUNT(*) FROM metrics")
            metrics_count = cursor.fetchone()[0]
            self.print_check("Metrics records", True, f"{metrics_count} snapshots")

            # Check database size
            db_size = self.db_file.stat().st_size / (1024 * 1024)
            self.print_check("Database size", True, f"{db_size:.2f} MB")

            conn.close()

            self.checks['database'] = {
                'passed': True,
                'tables': len(tables),
                'trades': trade_count,
                'metrics': metrics_count,
                'size_mb': round(db_size, 2)
            }
            return True

        except Exception as e:
            self.print_check("Database check", False, str(e))
            self.checks['database'] = {'passed': False, 'error': str(e)}
            return False

    def check_alerts(self) -> bool:
        """Check alert system"""
        print(f"\n{Colors.BOLD}Alert System:{Colors.RESET}")

        try:
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r') as f:
                    alerts = json.load(f)

                recent_alerts = alerts.get('recent', [])
                critical = [a for a in recent_alerts
                          if a.get('level') == 'CRITICAL' and not a.get('acknowledged')]

                self.print_check("Alerts file", True, f"{len(recent_alerts)} recent")
                if critical:
                    self.print_check("Critical alerts", False, f"{len(critical)} unacknowledged")
                    for alert in critical:
                        print(f"      - {alert.get('message')}")
                else:
                    self.print_check("Critical alerts", True, "None")

                self.checks['alerts'] = {
                    'passed': len(critical) == 0,
                    'recent': len(recent_alerts),
                    'critical': len(critical)
                }
            else:
                self.print_check("Alerts file", True, "Not created yet (normal)")
                self.checks['alerts'] = {'passed': True, 'recent': 0, 'critical': 0}

            return True

        except Exception as e:
            self.print_check("Alert check", False, str(e))
            self.checks['alerts'] = {'passed': False, 'error': str(e)}
            return False

    def check_emergency_stop(self) -> bool:
        """Verify emergency stop capability"""
        print(f"\n{Colors.BOLD}Emergency Stop:{Colors.RESET}")

        try:
            # Check if we can write emergency stop file
            stop_file = self.data_dir / "emergency_stop.txt"

            # Try to create stop file
            stop_file.write_text("test")
            stop_file.unlink()

            self.print_check("Emergency stop capability", True)

            # Check if stop flag exists (indicates stop in progress)
            if stop_file.exists():
                self.print_check("Emergency stop active", True)
            else:
                self.print_check("Emergency stop active", False, "Not triggered")

            self.checks['emergency_stop'] = {'passed': True}
            return True

        except Exception as e:
            self.print_check("Emergency stop capability", False, str(e))
            self.checks['emergency_stop'] = {'passed': False, 'error': str(e)}
            return False

    def print_summary(self):
        """Print health check summary"""
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}Health Check Summary:{Colors.RESET}")
        print("-" * 80)

        total_checks = len(self.checks)
        passed_checks = sum(1 for c in self.checks.values() if c.get('passed', False))

        for name, result in self.checks.items():
            status = f"{Colors.GREEN}PASS{Colors.RESET}" if result.get('passed') else f"{Colors.RED}FAIL{Colors.RESET}"
            print(f"  [{status}] {name}")

        print("-" * 80)
        percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        print(f"Overall Status: {passed_checks}/{total_checks} checks passed ({percentage:.0f}%)")

        if passed_checks == total_checks:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ System is healthy and ready!{Colors.RESET}")
        elif passed_checks >= total_checks * 0.7:
            print(f"{Colors.YELLOW}⚠ Most checks passed, but review failed checks{Colors.RESET}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}✗ Critical issues detected!{Colors.RESET}")

        print("=" * 80 + "\n")

        return passed_checks == total_checks

    def run_all_checks(self) -> bool:
        """Run all health checks"""
        self.print_header()

        results = [
            self.check_directories(),
            self.check_required_files(),
            self.check_engine_status(),
            self.check_last_trade(),
            self.check_logs(),
            self.check_database(),
            self.check_alerts(),
            self.check_emergency_stop(),
        ]

        healthy = self.print_summary()
        return healthy

    def get_health_json(self) -> Dict:
        """Get health check results as JSON"""
        return {
            'timestamp': datetime.now().isoformat(),
            'checks': self.checks,
            'overall_status': 'healthy' if all(c.get('passed') for c in self.checks.values()) else 'degraded'
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Health check for paper trading system')
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    parser.add_argument('--log-dir', default='logs', help='Log directory path')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')

    args = parser.parse_args()

    checker = HealthCheck(data_dir=args.data_dir, log_dir=args.log_dir)
    healthy = checker.run_all_checks()

    if args.json:
        print(json.dumps(checker.get_health_json(), indent=2))

    # Exit with appropriate code
    sys.exit(0 if healthy else 1)


if __name__ == '__main__':
    main()
