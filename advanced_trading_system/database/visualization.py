"""
Performance Visualization System
Terminal-based charts and dashboards for trading analytics
"""
from typing import Dict, List
from datetime import datetime


class PerformanceVisualizer:
    """Create terminal-based visualizations for trading performance"""

    @staticmethod
    def create_bar_chart(data: List[Dict], key: str, value: str, width: int = 50):
        """Create horizontal bar chart"""
        if not data:
            return "No data available"

        max_val = max([d[value] for d in data if d.get(value) is not None])
        if max_val == 0:
            max_val = 1

        lines = []
        for item in data:
            label = str(item[key])[:15].ljust(15)
            val = item.get(value, 0)
            bar_len = int((val / max_val) * width)
            bar = '█' * bar_len
            lines.append(f"{label} │ {bar} {val:.2f}")

        return "\n".join(lines)

    @staticmethod
    def create_equity_curve(equity_data: List[Dict], width: int = 60, height: int = 15):
        """Create ASCII equity curve"""
        if not equity_data or len(equity_data) < 2:
            return "Insufficient data for equity curve"

        values = [p['cumulative'] for p in equity_data]
        min_val = min(values)
        max_val = max(values)
        value_range = max_val - min_val if max_val != min_val else 1

        # Normalize values to chart height
        normalized = [int((v - min_val) / value_range * (height - 1)) for v in values]

        # Create chart
        lines = []
        for y in range(height - 1, -1, -1):
            line = ""
            for x_idx, norm_val in enumerate(normalized):
                if norm_val == y:
                    line += "●"
                elif norm_val > y:
                    line += "│"
                else:
                    line += " "

            # Add y-axis label
            val_at_y = min_val + (y / (height - 1)) * value_range
            line = f"{val_at_y:7.2f} │ {line}"
            lines.append(line)

        # Add x-axis
        x_axis = "        └" + "─" * len(normalized)
        lines.append(x_axis)
        lines.append(f"         Start{' ' * (len(normalized) - 10)}End")

        return "\n".join(lines)

    @staticmethod
    def create_performance_dashboard(stats: Dict, model_comparison: Dict = None) -> str:
        """Create comprehensive performance dashboard"""
        lines = []

        lines.append("=" * 80)
        lines.append("📊 TRADING PERFORMANCE DASHBOARD")
        lines.append("=" * 80)

        # Overall stats
        overall = stats.get('overall', {})
        lines.append(f"\n📈 OVERALL PERFORMANCE")
        lines.append(f"   Total Trades: {overall.get('total_trades', 0)}")
        lines.append(f"   Wins: {overall.get('wins', 0)} | Losses: {overall.get('losses', 0)}")
        lines.append(f"   Win Rate: {overall.get('win_rate', 0):.1f}%")
        lines.append(f"   Total P/L: ${overall.get('total_profit', 0):.2f}")
        lines.append(f"   Avg Profit: ${overall.get('avg_profit', 0):.2f}")
        lines.append(f"   Max Win: ${overall.get('max_profit', 0):.2f}")
        lines.append(f"   Max Loss: ${overall.get('max_loss', 0):.2f}")
        lines.append(f"   Sharpe Ratio: {stats.get('sharpe_ratio', 0):.2f}")
        lines.append(f"   Avg Confidence: {overall.get('avg_confidence', 0):.1f}%")

        # Performance by trend
        by_trend = stats.get('by_trend', [])
        if by_trend:
            lines.append(f"\n📊 PERFORMANCE BY TREND")
            for trend in by_trend:
                wr = (trend['wins'] / trend['trades'] * 100) if trend['trades'] > 0 else 0
                lines.append(f"   {trend['trend']:10s}: {trend['trades']:3d} trades, "
                           f"{wr:5.1f}% WR, ${trend['avg_profit']:+7.2f} avg")

        # Performance by regime
        by_regime = stats.get('by_regime', [])
        if by_regime:
            lines.append(f"\n🌐 PERFORMANCE BY REGIME")
            for regime in by_regime:
                wr = (regime['wins'] / regime['trades'] * 100) if regime['trades'] > 0 else 0
                lines.append(f"   {regime['regime']:15s}: {regime['trades']:3d} trades, "
                           f"{wr:5.1f}% WR, ${regime['avg_profit']:+7.2f} avg")

        # Top pairs
        by_pair = stats.get('by_pair', [])
        if by_pair:
            lines.append(f"\n💹 TOP PERFORMING PAIRS")
            for pair in by_pair[:5]:
                wr = (pair['wins'] / pair['trades'] * 100) if pair['trades'] > 0 else 0
                lines.append(f"   {pair['pair']:12s}: {pair['trades']:3d} trades, "
                           f"{wr:5.1f}% WR, ${pair['total_profit']:+7.2f} total")

        # Best hours
        by_hour = stats.get('by_hour', [])
        if by_hour:
            sorted_hours = sorted(by_hour, key=lambda x: x.get('avg_profit', 0), reverse=True)
            lines.append(f"\n⏰ BEST TRADING HOURS (Top 5)")
            for hour_data in sorted_hours[:5]:
                hour = hour_data.get('hour_of_day')
                if hour is None:
                    continue
                trades = hour_data.get('trades', 0)
                wins = hour_data.get('wins', 0)
                avg_profit = hour_data.get('avg_profit', 0)
                wr = (wins / trades * 100) if trades > 0 else 0
                lines.append(f"   {hour:02d}:00: {trades:3d} trades, "
                           f"{wr:5.1f}% WR, ${avg_profit:+7.2f} avg")

        # AI Model comparison
        if model_comparison:
            models = model_comparison.get('models', [])
            if models:
                lines.append(f"\n🤖 AI MODEL PERFORMANCE")
                lines.append(f"   {'Model':<30s} {'Accuracy':>10s} {'Trades':>8s} {'Avg P/L':>10s}")
                lines.append(f"   {'-'*30} {'-'*10} {'-'*8} {'-'*10}")
                for model in models[:8]:  # Top 8 models
                    lines.append(
                        f"   {model['model'][:30]:<30s} "
                        f"{model['accuracy']:>9.1f}% "
                        f"{model['predictions']:>8d} "
                        f"${model['avg_profit']:>9.2f}"
                    )

        lines.append("\n" + "=" * 80)

        return "\n".join(lines)

    @staticmethod
    def create_pattern_report(patterns: List[Dict]) -> str:
        """Create winning patterns report"""
        if not patterns:
            return "No significant patterns found"

        lines = []
        lines.append("=" * 80)
        lines.append("🔍 WINNING PATTERNS DETECTED")
        lines.append("=" * 80)

        # Group by type
        by_type = {}
        for pattern in patterns:
            ptype = pattern['type']
            if ptype not in by_type:
                by_type[ptype] = []
            by_type[ptype].append(pattern)

        for ptype, plist in by_type.items():
            lines.append(f"\n📊 {ptype} Patterns:")
            for p in sorted(plist, key=lambda x: x['win_rate'], reverse=True)[:5]:
                cond_str = ", ".join([f"{k}={v}" for k, v in p['conditions'].items()])
                lines.append(
                    f"   • {cond_str:40s} │ "
                    f"WR: {p['win_rate']:5.1f}% │ "
                    f"Trades: {p['occurrences']:3d} │ "
                    f"Avg P/L: ${p['avg_profit']:+6.2f}"
                )

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)

    @staticmethod
    def create_model_comparison_chart(model_comparison: Dict) -> str:
        """Create visual model comparison"""
        models = model_comparison.get('models', [])
        if not models:
            return "No model data available"

        lines = []
        lines.append("=" * 80)
        lines.append("🤖 AI MODEL COMPARISON - ACCURACY")
        lines.append("=" * 80 + "\n")

        # Sort by accuracy
        sorted_models = sorted(models, key=lambda x: x['accuracy'], reverse=True)

        max_acc = max([m['accuracy'] for m in sorted_models]) if sorted_models else 100
        if max_acc == 0:
            max_acc = 100  # Prevent division by zero

        for model in sorted_models:
            name = model['model'][:25].ljust(25)
            acc = model['accuracy']
            pred = model['predictions']

            # Bar
            bar_len = int((acc / max_acc) * 40) if max_acc > 0 else 0
            bar = '█' * bar_len

            # Color indicator (terminal)
            if acc >= 70:
                indicator = "🟢"
            elif acc >= 60:
                indicator = "🟡"
            else:
                indicator = "🔴"

            lines.append(f"{indicator} {name} │ {bar:40s} │ {acc:5.1f}% ({pred} trades)")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)

    @staticmethod
    def create_drawdown_chart(drawdown_data: Dict, equity_curve: List[Dict]) -> str:
        """Create drawdown visualization"""
        lines = []
        lines.append("=" * 80)
        lines.append("📉 DRAWDOWN ANALYSIS")
        lines.append("=" * 80 + "\n")

        lines.append(f"Max Drawdown: ${drawdown_data.get('max_drawdown', 0):.2f} "
                    f"({drawdown_data.get('max_drawdown_pct', 0):.1f}%)")
        lines.append(f"Current Drawdown: ${drawdown_data.get('current_drawdown', 0):.2f}")
        lines.append(f"Peak Equity: ${drawdown_data.get('peak_equity', 0):.2f}")

        # Risk assessment
        max_dd_pct = drawdown_data.get('max_drawdown_pct', 0)
        if max_dd_pct < 10:
            risk_level = "🟢 LOW RISK"
        elif max_dd_pct < 20:
            risk_level = "🟡 MODERATE RISK"
        else:
            risk_level = "🔴 HIGH RISK"

        lines.append(f"\nRisk Level: {risk_level}")

        # Simple drawdown visualization
        if equity_curve and len(equity_curve) > 1:
            lines.append(f"\nEquity Curve (Last {len(equity_curve)} trades):")
            lines.append(PerformanceVisualizer.create_equity_curve(equity_curve, width=60, height=10))

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)
