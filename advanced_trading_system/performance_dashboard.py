#!/usr/bin/env python3
"""
Performance Dashboard for Paper Trading
Tracks detailed metrics including indicator performance and pair analysis

Features:
- Detailed performance analytics
- Indicator accuracy tracking
- Best/worst performing pairs
- Drawdown analysis
- Statistical summaries
- Export capabilities
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import statistics

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class PerformanceDashboard:
    """Detailed performance analytics for paper trading"""

    def __init__(self, data_dir: str = "data"):
        """Initialize performance dashboard"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.trades_file = self.data_dir / "trades.json"

    def load_trades(self) -> List[Dict]:
        """Load trade history"""
        try:
            if self.trades_file.exists():
                with open(self.trades_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load trades: {e}")
        return []

    def get_pair_statistics(self) -> Dict[str, Dict]:
        """Analyze performance by currency pair"""
        trades = self.load_trades()

        pair_stats = defaultdict(lambda: {
            'total': 0,
            'wins': 0,
            'losses': 0,
            'ties': 0,
            'profit': 0.0,
            'trades_list': []
        })

        for trade in trades:
            if trade.get('result') is None:
                continue

            pair = trade.get('pair', 'UNKNOWN')
            pair_stats[pair]['total'] += 1
            pair_stats[pair]['trades_list'].append(trade)

            result = trade.get('result')
            if result == 'WIN':
                pair_stats[pair]['wins'] += 1
            elif result == 'LOSS':
                pair_stats[pair]['losses'] += 1
            elif result == 'TIE':
                pair_stats[pair]['ties'] += 1

            profit = float(trade.get('profit', 0))
            pair_stats[pair]['profit'] += profit

        # Calculate win rates and ROI
        stats = {}
        for pair, data in pair_stats.items():
            total = data['total']
            win_rate = (data['wins'] / total * 100) if total > 0 else 0

            stats[pair] = {
                'total_trades': total,
                'wins': data['wins'],
                'losses': data['losses'],
                'ties': data['ties'],
                'win_rate': round(win_rate, 2),
                'total_profit': round(data['profit'], 2),
                'avg_profit': round(data['profit'] / total, 2) if total > 0 else 0,
            }

        return stats

    def get_indicator_performance(self) -> Dict[str, Dict]:
        """Analyze which indicators are most accurate"""
        trades = self.load_trades()

        indicator_stats = defaultdict(lambda: {
            'correct': 0,
            'incorrect': 0,
            'values': []
        })

        # Indicators to track
        indicators = ['rsi', 'macd_histogram', 'stoch_k', 'adx', 'bb_position']

        for trade in trades:
            if trade.get('result') is None:
                continue

            result = trade.get('result')
            correct = (result == 'WIN')

            for indicator in indicators:
                if indicator in trade:
                    indicator_stats[indicator]['values'].append({
                        'value': trade[indicator],
                        'correct': correct
                    })
                    if correct:
                        indicator_stats[indicator]['correct'] += 1
                    else:
                        indicator_stats[indicator]['incorrect'] += 1

        # Calculate accuracy
        stats = {}
        for indicator, data in indicator_stats.items():
            total = data['correct'] + data['incorrect']
            accuracy = (data['correct'] / total * 100) if total > 0 else 0

            stats[indicator] = {
                'accuracy': round(accuracy, 2),
                'correct_signals': data['correct'],
                'incorrect_signals': data['incorrect'],
                'total_signals': total,
                'avg_value': round(statistics.mean(
                    [v['value'] for v in data['values']]
                ), 2) if data['values'] else 0,
            }

        return stats

    def calculate_drawdown_analysis(self) -> Dict:
        """Analyze drawdown and recovery periods"""
        trades = self.load_trades()

        if not trades:
            return {
                'max_drawdown': 0.0,
                'avg_drawdown': 0.0,
                'recovery_time': 0,
                'drawdown_periods': []
            }

        # Calculate running profit
        cumulative = 0
        peak = 0
        drawdowns = []
        current_dd_start = None
        current_dd_amount = 0

        for trade in trades:
            if trade.get('result') is None:
                continue

            profit = float(trade.get('profit', 0))
            cumulative += profit

            if cumulative > peak:
                peak = cumulative
                if current_dd_start is not None:
                    drawdowns.append({
                        'start': current_dd_start,
                        'amount': current_dd_amount,
                        'end': trade.get('timestamp')
                    })
                current_dd_start = None
                current_dd_amount = 0
            else:
                drawdown = peak - cumulative
                if current_dd_start is None:
                    current_dd_start = trade.get('timestamp')
                current_dd_amount = max(current_dd_amount, drawdown)

        max_dd = max([d['amount'] for d in drawdowns], default=0)
        avg_dd = statistics.mean([d['amount'] for d in drawdowns]) if drawdowns else 0

        return {
            'max_drawdown': round(max_dd, 2),
            'avg_drawdown': round(avg_dd, 2),
            'drawdown_count': len(drawdowns),
            'largest_dd_trades': len([t for t in trades if t.get('result') == 'LOSS'])
        }

    def get_hourly_statistics(self) -> Dict[int, Dict]:
        """Analyze trading by hour of day"""
        trades = self.load_trades()

        hourly = defaultdict(lambda: {
            'total': 0,
            'wins': 0,
            'losses': 0,
            'profit': 0.0
        })

        for trade in trades:
            if trade.get('result') is None:
                continue

            try:
                timestamp = datetime.fromisoformat(trade.get('timestamp', ''))
                hour = timestamp.hour
            except:
                continue

            hourly[hour]['total'] += 1
            if trade.get('result') == 'WIN':
                hourly[hour]['wins'] += 1
            elif trade.get('result') == 'LOSS':
                hourly[hour]['losses'] += 1

            hourly[hour]['profit'] += float(trade.get('profit', 0))

        # Calculate stats
        stats = {}
        for hour in range(24):
            data = hourly[hour]
            total = data['total']
            win_rate = (data['wins'] / total * 100) if total > 0 else 0

            stats[hour] = {
                'total_trades': total,
                'wins': data['wins'],
                'losses': data['losses'],
                'win_rate': round(win_rate, 2),
                'profit': round(data['profit'], 2),
            }

        return stats

    def get_confidence_distribution(self) -> Dict:
        """Analyze signal confidence levels"""
        trades = self.load_trades()

        confidence_ranges = {
            '50-60%': {'count': 0, 'wins': 0},
            '60-70%': {'count': 0, 'wins': 0},
            '70-80%': {'count': 0, 'wins': 0},
            '80-90%': {'count': 0, 'wins': 0},
            '90-100%': {'count': 0, 'wins': 0},
        }

        for trade in trades:
            confidence = float(trade.get('confidence', 0))
            result = trade.get('result')

            if confidence < 60:
                bucket = '50-60%'
            elif confidence < 70:
                bucket = '60-70%'
            elif confidence < 80:
                bucket = '70-80%'
            elif confidence < 90:
                bucket = '80-90%'
            else:
                bucket = '90-100%'

            confidence_ranges[bucket]['count'] += 1
            if result == 'WIN':
                confidence_ranges[bucket]['wins'] += 1

        # Calculate win rates
        for bucket in confidence_ranges:
            count = confidence_ranges[bucket]['count']
            wins = confidence_ranges[bucket]['wins']
            win_rate = (wins / count * 100) if count > 0 else 0
            confidence_ranges[bucket]['win_rate'] = round(win_rate, 2)

        return confidence_ranges

    def generate_report(self) -> str:
        """Generate a comprehensive performance report"""
        trades = self.load_trades()

        if not trades:
            return "No trades to analyze yet."

        report = []
        report.append("\n" + "=" * 80)
        report.append("PERFORMANCE DASHBOARD REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)

        # Overall metrics
        completed_trades = [t for t in trades if t.get('result') is not None]
        total = len(completed_trades)
        wins = sum(1 for t in completed_trades if t.get('result') == 'WIN')
        losses = sum(1 for t in completed_trades if t.get('result') == 'LOSS')
        total_profit = sum(float(t.get('profit', 0)) for t in completed_trades)

        report.append("\nOVERALL METRICS:")
        report.append(f"  Total Trades Completed: {total}")
        report.append(f"  Wins: {wins}")
        report.append(f"  Losses: {losses}")
        report.append(f"  Win Rate: {(wins/total*100 if total > 0 else 0):.2f}%")
        report.append(f"  Total Profit/Loss: ${total_profit:.2f}")
        report.append(f"  Average Profit/Trade: ${total_profit/total if total > 0 else 0:.2f}")

        # Pair analysis
        pair_stats = self.get_pair_statistics()
        report.append("\n" + "-" * 80)
        report.append("PAIR PERFORMANCE:")
        for pair, stats in sorted(pair_stats.items(), key=lambda x: x[1]['total_profit'], reverse=True):
            report.append(f"  {pair}:")
            report.append(f"    Trades: {stats['total_trades']}")
            report.append(f"    Win Rate: {stats['win_rate']:.2f}%")
            report.append(f"    Total Profit: ${stats['total_profit']:.2f}")
            report.append(f"    Avg Profit/Trade: ${stats['avg_profit']:.2f}")

        # Indicator performance
        indicator_perf = self.get_indicator_performance()
        report.append("\n" + "-" * 80)
        report.append("INDICATOR ACCURACY:")
        for indicator, stats in sorted(indicator_perf.items(), key=lambda x: x[1]['accuracy'], reverse=True):
            report.append(f"  {indicator.upper()}:")
            report.append(f"    Accuracy: {stats['accuracy']:.2f}%")
            report.append(f"    Signals: {stats['total_signals']}")
            report.append(f"    Avg Value: {stats['avg_value']}")

        # Drawdown analysis
        dd_stats = self.calculate_drawdown_analysis()
        report.append("\n" + "-" * 80)
        report.append("DRAWDOWN ANALYSIS:")
        report.append(f"  Max Drawdown: ${dd_stats['max_drawdown']:.2f}")
        report.append(f"  Avg Drawdown: ${dd_stats['avg_drawdown']:.2f}")
        report.append(f"  Drawdown Periods: {dd_stats['drawdown_count']}")

        # Confidence distribution
        conf_dist = self.get_confidence_distribution()
        report.append("\n" + "-" * 80)
        report.append("SIGNAL CONFIDENCE DISTRIBUTION:")
        for bucket, stats in conf_dist.items():
            report.append(f"  {bucket}: {stats['count']} signals, "
                         f"{stats['win_rate']:.2f}% win rate")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def export_to_csv(self, output_file: Optional[str] = None) -> str:
        """Export detailed analytics to CSV"""
        if output_file is None:
            output_file = self.data_dir / "performance_report.csv"
        else:
            output_file = Path(output_file)

        try:
            pair_stats = self.get_pair_statistics()

            with open(output_file, 'w', newline='') as f:
                f.write("Pair,Total Trades,Wins,Losses,Ties,Win Rate %,Total Profit,Avg Profit\n")

                for pair, stats in sorted(pair_stats.items()):
                    f.write(f"{pair},{stats['total_trades']},{stats['wins']},{stats['losses']},"
                           f"{stats['ties']},{stats['win_rate']},{stats['total_profit']},{stats['avg_profit']}\n")

            return str(output_file)
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return ""


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Performance dashboard for paper trading')
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    parser.add_argument('--export', help='Export performance data to CSV file')
    parser.add_argument('--pairs', action='store_true', help='Show pair statistics')
    parser.add_argument('--indicators', action='store_true', help='Show indicator performance')
    parser.add_argument('--drawdown', action='store_true', help='Show drawdown analysis')
    parser.add_argument('--hourly', action='store_true', help='Show hourly statistics')
    parser.add_argument('--all', action='store_true', help='Show all analytics')

    args = parser.parse_args()

    dashboard = PerformanceDashboard(data_dir=args.data_dir)

    # Show report
    print(dashboard.generate_report())

    # Show specific analyses
    if args.pairs or args.all:
        print("\nDETAILED PAIR STATISTICS:")
        pair_stats = dashboard.get_pair_statistics()
        for pair, stats in sorted(pair_stats.items()):
            print(f"  {pair}: {stats}")

    if args.indicators or args.all:
        print("\nDETAILED INDICATOR PERFORMANCE:")
        ind_perf = dashboard.get_indicator_performance()
        for ind, stats in sorted(ind_perf.items()):
            print(f"  {ind}: {stats}")

    if args.drawdown or args.all:
        print("\nDETAILED DRAWDOWN ANALYSIS:")
        dd = dashboard.calculate_drawdown_analysis()
        for key, val in dd.items():
            print(f"  {key}: {val}")

    if args.hourly or args.all:
        print("\nHOURLY STATISTICS:")
        hourly = dashboard.get_hourly_statistics()
        for hour in sorted(hourly.keys()):
            stats = hourly[hour]
            if stats['total_trades'] > 0:
                print(f"  {hour:02d}:00 - {stats}")

    # Export if requested
    if args.export:
        output = dashboard.export_to_csv(args.export)
        print(f"\nData exported to: {output}")


if __name__ == '__main__':
    main()
