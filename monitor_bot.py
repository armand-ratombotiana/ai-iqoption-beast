#!/usr/bin/env python3
"""
Real-time Trading Bot Monitor
Continuously monitors the bot's health, performance, and makes dynamic adjustments
"""
import time
import requests
import json
from datetime import datetime
from typing import Dict, Optional
import sys

class BotMonitor:
    """Monitor and adjust trading bot in real-time"""

    def __init__(self, health_url: str = "http://localhost:5001"):
        self.health_url = health_url
        self.last_stats = None
        self.adjustment_history = []

    def get_health(self) -> Optional[Dict]:
        """Get bot health status"""
        try:
            response = requests.get(f"{self.health_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        return None

    def get_statistics(self) -> Optional[Dict]:
        """Get bot statistics"""
        try:
            response = requests.get(f"{self.health_url}/statistics", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Statistics fetch failed: {e}")
        return None

    def analyze_performance(self, stats: Dict) -> Dict:
        """Analyze performance and generate insights"""
        insights = {
            'status': 'healthy',
            'warnings': [],
            'recommendations': []
        }

        # Check win rate
        win_rate = stats.get('win_rate', 0)
        if win_rate < 45:
            insights['warnings'].append(f"⚠️  Low win rate: {win_rate:.1f}%")
            insights['recommendations'].append("Consider increasing MIN_AI_CONFIDENCE")
            insights['status'] = 'warning'
        elif win_rate > 55:
            insights['recommendations'].append(f"✅ Good win rate: {win_rate:.1f}%")

        # Check daily P&L
        daily_net = stats.get('daily_net', 0)
        if daily_net < -20:
            insights['warnings'].append(f"⚠️  Significant daily loss: ${daily_net:.2f}")
            insights['recommendations'].append("Consider reducing position sizes")
            insights['status'] = 'warning'
        elif daily_net > 20:
            insights['recommendations'].append(f"✅ Strong daily profit: ${daily_net:.2f}")

        # Check active instruments
        active_count = stats.get('active_count', 0)
        max_concurrent = 5  # From config
        if active_count >= max_concurrent:
            insights['warnings'].append(f"⚠️  Max concurrent instruments: {active_count}")

        # Check trades today
        trades_today = stats.get('trades_today', 0)
        if trades_today == 0:
            insights['warnings'].append("⚠️  No trades executed today")
            insights['status'] = 'warning'

        # Check balance
        balance = stats.get('balance', 0)
        start_balance = stats.get('start_balance', 0)
        if balance < start_balance * 0.9:
            insights['warnings'].append(f"⚠️  Balance down 10%+: ${balance:.2f}")
            insights['status'] = 'critical'

        return insights

    def print_dashboard(self, stats: Dict, insights: Dict):
        """Print monitoring dashboard"""
        print("\n" + "="*80)
        print(f"🤖 KAEL TRADING BOT MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Status
        status_emoji = "✅" if insights['status'] == 'healthy' else "⚠️" if insights['status'] == 'warning' else "🔴"
        print(f"\n{status_emoji} Status: {insights['status'].upper()}")
        print(f"Mode: {stats.get('mode', 'unknown').upper()}")
        print(f"Operation: {stats.get('operation_mode', 'unknown')}")

        # Performance
        print(f"\n📊 PERFORMANCE")
        print(f"├─ Balance: ${stats.get('balance', 0):.2f} (Start: ${stats.get('start_balance', 0):.2f})")
        print(f"├─ Daily P&L: ${stats.get('daily_net', 0):+.2f} (Profit: ${stats.get('daily_profit', 0):.2f}, Loss: ${stats.get('daily_loss', 0):.2f})")
        print(f"├─ Trades Today: {stats.get('trades_today', 0)} (W:{stats.get('wins_today', 0)} / L:{stats.get('losses_today', 0)})")
        print(f"├─ Win Rate: {stats.get('win_rate', 0):.1f}%")
        print(f"├─ Active Instruments: {stats.get('active_count', 0)}/{5}")
        print(f"├─ Total Risk Allocated: ${stats.get('total_risk_allocated', 0):.2f}")
        print(f"└─ Uptime: {stats.get('uptime_hours', 0):.2f} hours")

        # System metrics
        print(f"\n⚙️  SYSTEM METRICS")
        print(f"├─ Avg Scan Time: {stats.get('avg_scan_time_ms', 0):.0f}ms")
        print(f"├─ Avg Execution Time: {stats.get('avg_execution_time_ms', 0):.0f}ms")
        print(f"├─ Reconnect Count: {stats.get('reconnect_count', 0)}")
        print(f"└─ Total Trades (All-Time): {stats.get('total_trades_all_time', 0)}")

        # Top instruments
        instrument_stats = stats.get('instrument_stats', [])
        if instrument_stats:
            print(f"\n🎯 TOP INSTRUMENTS")
            for i, inst in enumerate(instrument_stats[:5], 1):
                print(f"{i}. {inst['instrument']}: ${inst['profit']:+.2f} ({inst['wins']}/{inst['losses']}) - {inst['win_rate']:.1f}% WR")

        # Warnings
        if insights['warnings']:
            print(f"\n⚠️  WARNINGS")
            for warning in insights['warnings']:
                print(f"   {warning}")

        # Recommendations
        if insights['recommendations']:
            print(f"\n💡 RECOMMENDATIONS")
            for rec in insights['recommendations']:
                print(f"   {rec}")

        print("\n" + "="*80)

    def monitor_loop(self, interval: int = 30):
        """Main monitoring loop"""
        print("🚀 Starting bot monitor...")
        print(f"📡 Monitoring: {self.health_url}")
        print(f"🔄 Update interval: {interval}s")
        print("Press Ctrl+C to stop\n")

        consecutive_failures = 0
        max_failures = 5

        while True:
            try:
                # Get health status
                health = self.get_health()
                if not health:
                    consecutive_failures += 1
                    print(f"❌ Health check failed ({consecutive_failures}/{max_failures})")

                    if consecutive_failures >= max_failures:
                        print(f"\n🔴 CRITICAL: Bot not responding for {consecutive_failures} checks!")
                        print("   Consider restarting the Docker container")

                    time.sleep(10)
                    continue

                consecutive_failures = 0

                # Get statistics
                stats = self.get_statistics()
                if not stats:
                    print("⚠️  Could not fetch statistics")
                    time.sleep(10)
                    continue

                # Analyze performance
                insights = self.analyze_performance(stats)

                # Print dashboard
                self.print_dashboard(stats, insights)

                # Store for comparison
                self.last_stats = stats

                # Wait for next update
                time.sleep(interval)

            except KeyboardInterrupt:
                print("\n\n🛑 Monitor stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(10)

def main():
    """Main entry point"""
    health_url = "http://localhost:5001"
    interval = 30  # seconds

    if len(sys.argv) > 1:
        interval = int(sys.argv[1])

    monitor = BotMonitor(health_url)
    monitor.monitor_loop(interval)

if __name__ == '__main__':
    main()
