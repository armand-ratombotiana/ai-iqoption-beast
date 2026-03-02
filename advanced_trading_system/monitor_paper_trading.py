#!/usr/bin/env python3
"""
Real-time Paper Trading Monitor
Displays current trading status with live updates every 5 seconds

Features:
- Live trading status display
- Running win rate
- Profit/loss tracking
- Active trades display
- Color-formatted output
- Real-time metrics updates
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import csv

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Color support for terminal output
class Colors:
    """Terminal color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    LIGHT_GRAY = '\033[37m'

    @staticmethod
    def disable():
        """Disable colors (for non-TTY output)"""
        for attr in dir(Colors):
            if not attr.startswith('_') and attr != 'disable':
                setattr(Colors, attr, '')


class PaperTradingMonitor:
    """Real-time monitor for paper trading engine"""

    def __init__(self, data_dir: str = "data", log_dir: str = "logs"):
        """Initialize monitoring system"""
        self.data_dir = Path(data_dir)
        self.log_dir = Path(log_dir)
        self.trades_file = self.data_dir / "trades.json"
        self.metrics_file = self.data_dir / "metrics.json"
        self.status_file = self.data_dir / "status.json"

        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

        # Cache for metrics
        self.current_metrics = self._load_metrics()
        self.trades_cache = self._load_trades()

        # Update interval (seconds)
        self.update_interval = 5

        # Check if terminal supports colors
        if not sys.stdout.isatty():
            Colors.disable()

    def _load_metrics(self) -> Dict:
        """Load current metrics from file"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load metrics: {e}")

        return {
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'ties': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'daily_profit': 0.0,
            'daily_loss': 0.0,
            'consecutive_losses': 0,
            'max_drawdown': 0.0,
            'trades_per_hour': 0,
            'avg_profit_per_trade': 0.0,
        }

    def _load_trades(self) -> List[Dict]:
        """Load trade history from file"""
        try:
            if self.trades_file.exists():
                with open(self.trades_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load trades: {e}")

        return []

    def _load_status(self) -> Dict:
        """Load current engine status"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load status: {e}")

        return {
            'is_running': False,
            'last_trade_time': None,
            'connected': False,
            'active_trades': 0,
        }

    def calculate_metrics(self) -> Dict:
        """Calculate current trading metrics"""
        trades = self.trades_cache

        if not trades:
            return self.current_metrics

        # Basic stats
        total_trades = len(trades)
        wins = sum(1 for t in trades if t.get('result') == 'WIN')
        losses = sum(1 for t in trades if t.get('result') == 'LOSS')
        ties = sum(1 for t in trades if t.get('result') == 'TIE')

        # Win rate
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0

        # Profit calculation
        total_profit = sum(float(t.get('profit', 0)) for t in trades)

        # Daily metrics
        today = datetime.now().date()
        today_trades = [
            t for t in trades
            if datetime.fromisoformat(t.get('timestamp', '1970-01-01')).date() == today
        ]
        daily_profit = sum(float(t.get('profit', 0)) for t in today_trades if t.get('profit', 0) > 0)
        daily_loss = sum(float(t.get('profit', 0)) for t in today_trades if t.get('profit', 0) < 0)

        # Consecutive losses
        consecutive_losses = 0
        for t in reversed(trades):
            if t.get('result') == 'LOSS':
                consecutive_losses += 1
            else:
                break

        # Max drawdown
        cumulative = 0
        peak = 0
        max_dd = 0
        for t in trades:
            profit = float(t.get('profit', 0))
            cumulative += profit
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_dd:
                max_dd = drawdown

        # Trades per hour
        if today_trades:
            first_trade = min(
                datetime.fromisoformat(t.get('timestamp', '1970-01-01'))
                for t in today_trades
            )
            hours_elapsed = (datetime.now() - first_trade).total_seconds() / 3600
            trades_per_hour = len(today_trades) / hours_elapsed if hours_elapsed > 0 else 0
        else:
            trades_per_hour = 0

        # Avg profit per trade
        avg_profit = (total_profit / total_trades) if total_trades > 0 else 0.0

        metrics = {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'win_rate': round(win_rate, 2),
            'total_profit': round(total_profit, 2),
            'daily_profit': round(daily_profit, 2),
            'daily_loss': round(abs(daily_loss), 2),
            'consecutive_losses': consecutive_losses,
            'max_drawdown': round(max_dd, 2),
            'trades_per_hour': round(trades_per_hour, 2),
            'avg_profit_per_trade': round(avg_profit, 2),
        }

        self.current_metrics = metrics
        return metrics

    def get_active_trades(self) -> List[Dict]:
        """Get currently active trades"""
        trades = self.trades_cache
        active = [t for t in trades if t.get('result') is None]
        return active[-5:] if active else []  # Show last 5 active

    def get_recent_trades(self, count: int = 5) -> List[Dict]:
        """Get recent completed trades"""
        trades = self.trades_cache
        completed = [t for t in trades if t.get('result') is not None]
        return completed[-count:] if completed else []

    def format_metric_row(self, label: str, value: str, color: str = '') -> str:
        """Format a metric row"""
        return f"{label:<30} {color}{value:>20}{Colors.RESET}"

    def print_header(self):
        """Print monitor header"""
        print("\n" + "=" * 60)
        print(f"{Colors.CYAN}{Colors.BOLD}PAPER TRADING MONITOR{Colors.RESET}")
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    def print_metrics_section(self):
        """Print current metrics section"""
        metrics = self.calculate_metrics()

        print(f"\n{Colors.BOLD}{Colors.WHITE}TRADING METRICS{Colors.RESET}")
        print("-" * 60)

        print(self.format_metric_row("Total Trades:", str(metrics['total_trades'])))

        win_color = Colors.GREEN if metrics['win_rate'] >= 50 else Colors.RED
        print(self.format_metric_row(
            "Win Rate:",
            f"{metrics['win_rate']:.2f}%",
            win_color
        ))

        print(self.format_metric_row("Wins:", f"{metrics['wins']}", Colors.GREEN))
        print(self.format_metric_row("Losses:", f"{metrics['losses']}", Colors.RED))
        print(self.format_metric_row("Ties:", f"{metrics['ties']}", Colors.YELLOW))

        profit_color = Colors.GREEN if metrics['total_profit'] >= 0 else Colors.RED
        print(self.format_metric_row(
            "Total Profit/Loss:",
            f"${metrics['total_profit']:.2f}",
            profit_color
        ))

        daily_profit_color = Colors.GREEN if metrics['daily_profit'] >= 0 else Colors.YELLOW
        print(self.format_metric_row(
            "Today's Profit:",
            f"${metrics['daily_profit']:.2f}",
            daily_profit_color
        ))

        daily_loss_color = Colors.RED if metrics['daily_loss'] > 0 else Colors.GREEN
        print(self.format_metric_row(
            "Today's Loss:",
            f"-${metrics['daily_loss']:.2f}",
            daily_loss_color
        ))

        print(self.format_metric_row(
            "Average Profit/Trade:",
            f"${metrics['avg_profit_per_trade']:.2f}"
        ))

        print(self.format_metric_row(
            "Trades/Hour:",
            f"{metrics['trades_per_hour']:.2f}"
        ))

        loss_color = Colors.RED if metrics['consecutive_losses'] > 0 else Colors.GREEN
        print(self.format_metric_row(
            "Consecutive Losses:",
            str(metrics['consecutive_losses']),
            loss_color
        ))

        dd_color = Colors.RED if metrics['max_drawdown'] > 0 else Colors.GREEN
        print(self.format_metric_row(
            "Max Drawdown:",
            f"-${metrics['max_drawdown']:.2f}",
            dd_color
        ))

    def print_status_section(self):
        """Print engine status section"""
        status = self._load_status()

        print(f"\n{Colors.BOLD}{Colors.WHITE}ENGINE STATUS{Colors.RESET}")
        print("-" * 60)

        running_color = Colors.GREEN if status.get('is_running') else Colors.RED
        running_status = "RUNNING" if status.get('is_running') else "STOPPED"
        print(self.format_metric_row("Status:", running_status, running_color))

        connected_color = Colors.GREEN if status.get('connected') else Colors.RED
        connected_status = "CONNECTED" if status.get('connected') else "DISCONNECTED"
        print(self.format_metric_row("Connection:", connected_status, connected_color))

        active_trades = status.get('active_trades', 0)
        active_color = Colors.YELLOW if active_trades > 0 else Colors.GREEN
        print(self.format_metric_row(
            "Active Trades:",
            str(active_trades),
            active_color
        ))

        last_trade = status.get('last_trade_time')
        if last_trade:
            print(self.format_metric_row("Last Trade:", last_trade))
        else:
            print(self.format_metric_row("Last Trade:", "No trades yet"))

    def print_active_trades_section(self):
        """Print active trades section"""
        active = self.get_active_trades()

        print(f"\n{Colors.BOLD}{Colors.WHITE}ACTIVE TRADES (Last 5){Colors.RESET}")
        print("-" * 60)

        if not active:
            print("No active trades")
            return

        for trade in active:
            timestamp = trade.get('timestamp', 'N/A')
            pair = trade.get('pair', 'N/A')
            signal = trade.get('signal', 'N/A')
            confidence = trade.get('confidence', 0)

            signal_color = Colors.GREEN if signal == 'CALL' else Colors.RED
            confidence_color = Colors.GREEN if confidence >= 70 else Colors.YELLOW

            print(f"  {timestamp} | {pair:12} | {signal_color}{signal:4}{Colors.RESET} | "
                  f"Confidence: {confidence_color}{confidence:.0f}%{Colors.RESET}")

    def print_recent_trades_section(self):
        """Print recent completed trades section"""
        recent = self.get_recent_trades(5)

        print(f"\n{Colors.BOLD}{Colors.WHITE}RECENT COMPLETED TRADES (Last 5){Colors.RESET}")
        print("-" * 60)

        if not recent:
            print("No completed trades yet")
            return

        for trade in recent:
            timestamp = trade.get('timestamp', 'N/A')
            pair = trade.get('pair', 'N/A')
            signal = trade.get('signal', 'N/A')
            result = trade.get('result', 'N/A')
            profit = float(trade.get('profit', 0))

            signal_color = Colors.GREEN if signal == 'CALL' else Colors.RED
            result_color = Colors.GREEN if result == 'WIN' else Colors.RED if result == 'LOSS' else Colors.YELLOW
            profit_color = Colors.GREEN if profit >= 0 else Colors.RED

            print(f"  {timestamp} | {pair:12} | {signal_color}{signal:4}{Colors.RESET} | "
                  f"{result_color}{result:4}{Colors.RESET} | "
                  f"{profit_color}${profit:+.2f}{Colors.RESET}")

    def print_dashboard(self):
        """Print complete monitoring dashboard"""
        self.trades_cache = self._load_trades()

        print("\033[2J\033[H")  # Clear screen
        self.print_header()
        self.print_metrics_section()
        self.print_status_section()
        self.print_active_trades_section()
        self.print_recent_trades_section()

        print("\n" + "=" * 60)
        print(f"{Colors.LIGHT_GRAY}Updating every {self.update_interval} seconds... "
              f"(Press Ctrl+C to exit){Colors.RESET}")
        print("=" * 60 + "\n")

    def run(self):
        """Run continuous monitoring loop"""
        print(f"{Colors.CYAN}Starting Paper Trading Monitor...{Colors.RESET}")
        time.sleep(1)

        try:
            iteration = 0
            while True:
                self.print_dashboard()
                iteration += 1

                try:
                    time.sleep(self.update_interval)
                except KeyboardInterrupt:
                    raise

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Monitor stopped by user{Colors.RESET}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Colors.RED}Error in monitor loop: {e}{Colors.RESET}")
            sys.exit(1)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Monitor paper trading engine')
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    parser.add_argument('--log-dir', default='logs', help='Log directory path')
    parser.add_argument('--interval', type=int, default=5, help='Update interval (seconds)')

    args = parser.parse_args()

    monitor = PaperTradingMonitor(data_dir=args.data_dir, log_dir=args.log_dir)
    monitor.update_interval = args.interval
    monitor.run()


if __name__ == '__main__':
    main()
