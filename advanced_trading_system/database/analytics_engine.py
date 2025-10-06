"""
Advanced Database Analytics Engine
Pattern recognition, performance analysis, and predictive insights
"""
import sqlite3
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np


class TradingAnalytics:
    """
    Advanced analytics for trading database with:
    - Pattern recognition from historical trades
    - AI model performance comparison
    - Market condition analysis
    - Predictive insights
    - Trade replay capabilities
    """

    def __init__(self, db_path: str = "data/trades_advanced.db"):
        self.db_path = db_path
        self.conn = None
        self._connect()

    def _connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def get_comprehensive_stats(self, days: int = 30) -> Dict:
        """Get comprehensive trading statistics"""
        cursor = self.conn.cursor()

        # Date filter
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        stats = {}

        # Overall performance
        cursor.execute("""
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
                SUM(profit) as total_profit,
                AVG(profit) as avg_profit,
                MAX(profit) as max_profit,
                MIN(profit) as max_loss,
                AVG(ai_signal_confidence) as avg_confidence
            FROM trades
            WHERE timestamp >= ?
        """, (cutoff_date,))

        overall = dict(cursor.fetchone())
        overall['win_rate'] = (overall['wins'] / overall['total_trades'] * 100) if overall['total_trades'] > 0 else 0
        stats['overall'] = overall

        # Performance by hour
        cursor.execute("""
            SELECT
                hour_of_day,
                COUNT(*) as trades,
                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                AVG(profit) as avg_profit
            FROM trades
            WHERE timestamp >= ?
            GROUP BY hour_of_day
            ORDER BY hour_of_day
        """, (cutoff_date,))
        stats['by_hour'] = [dict(row) for row in cursor.fetchall()]

        # Performance by pair
        cursor.execute("""
            SELECT
                pair,
                COUNT(*) as trades,
                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                AVG(profit) as avg_profit,
                SUM(profit) as total_profit
            FROM trades
            WHERE timestamp >= ?
            GROUP BY pair
            ORDER BY total_profit DESC
            LIMIT 10
        """, (cutoff_date,))
        stats['by_pair'] = [dict(row) for row in cursor.fetchall()]

        # Performance by trend
        cursor.execute("""
            SELECT
                trend,
                COUNT(*) as trades,
                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                AVG(profit) as avg_profit
            FROM trades
            WHERE timestamp >= ? AND trend IS NOT NULL
            GROUP BY trend
        """, (cutoff_date,))
        stats['by_trend'] = [dict(row) for row in cursor.fetchall()]

        # Performance by market regime
        cursor.execute("""
            SELECT
                market_session as regime,
                COUNT(*) as trades,
                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                AVG(profit) as avg_profit
            FROM trades
            WHERE timestamp >= ? AND market_session IS NOT NULL
            GROUP BY market_session
        """, (cutoff_date,))
        stats['by_regime'] = [dict(row) for row in cursor.fetchall()]

        # Calculate Sharpe Ratio
        cursor.execute("""
            SELECT profit FROM trades
            WHERE timestamp >= ? AND result IS NOT NULL
        """, (cutoff_date,))
        profits = [row[0] for row in cursor.fetchall() if row[0] is not None]
        if profits:
            avg_return = np.mean(profits)
            std_return = np.std(profits)
            sharpe = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
            stats['sharpe_ratio'] = round(sharpe, 2)
        else:
            stats['sharpe_ratio'] = 0

        return stats

    def get_ai_model_comparison(self, days: int = 30) -> Dict:
        """Compare AI model performance"""
        cursor = self.conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT
                ai_models_votes_json,
                result,
                profit,
                direction,
                market_session
            FROM trades
            WHERE timestamp >= ? AND ai_models_votes_json IS NOT NULL
        """, (cutoff_date,))

        model_stats = defaultdict(lambda: {
            'predictions': 0,
            'correct': 0,
            'total_profit': 0,
            'by_regime': defaultdict(lambda: {'predictions': 0, 'correct': 0})
        })

        for row in cursor.fetchall():
            try:
                votes_str = row[0].replace("'", '"')  # Fix Python dict to JSON
                votes = json.loads(votes_str)
                result = row[1]
                profit = row[2] or 0
                direction = row[3]
                regime = row[4] or 'unknown'

                for model_name, vote in votes.items():
                    model_stats[model_name]['predictions'] += 1

                    # Check if model's prediction was correct
                    model_signal = vote.get('signal', '')
                    was_correct = (result == 'WIN' and model_signal == direction)

                    if was_correct:
                        model_stats[model_name]['correct'] += 1
                        model_stats[model_name]['total_profit'] += profit

                    # By regime
                    model_stats[model_name]['by_regime'][regime]['predictions'] += 1
                    if was_correct:
                        model_stats[model_name]['by_regime'][regime]['correct'] += 1

            except Exception as e:
                continue

        # Calculate accuracy
        comparison = []
        for model_name, stats in model_stats.items():
            accuracy = (stats['correct'] / stats['predictions'] * 100) if stats['predictions'] > 0 else 0

            regime_performance = {}
            for regime, regime_stats in stats['by_regime'].items():
                regime_acc = (regime_stats['correct'] / regime_stats['predictions'] * 100) if regime_stats['predictions'] > 0 else 0
                regime_performance[regime] = {
                    'accuracy': round(regime_acc, 1),
                    'predictions': regime_stats['predictions']
                }

            comparison.append({
                'model': model_name,
                'predictions': stats['predictions'],
                'correct': stats['correct'],
                'accuracy': round(accuracy, 1),
                'total_profit': round(stats['total_profit'], 2),
                'avg_profit': round(stats['total_profit'] / stats['predictions'], 2) if stats['predictions'] > 0 else 0,
                'regime_performance': regime_performance
            })

        # Sort by accuracy
        comparison.sort(key=lambda x: x['accuracy'], reverse=True)

        return {
            'models': comparison,
            'best_model': comparison[0]['model'] if comparison else None,
            'best_accuracy': comparison[0]['accuracy'] if comparison else 0
        }

    def find_winning_patterns(self, min_occurrences: int = 5) -> List[Dict]:
        """Identify patterns that lead to wins"""
        cursor = self.conn.cursor()

        patterns = []

        # Pattern 1: RSI + Trend combinations
        cursor.execute("""
            SELECT
                CASE
                    WHEN rsi_14 < 30 THEN 'RSI_OVERSOLD'
                    WHEN rsi_14 > 70 THEN 'RSI_OVERBOUGHT'
                    ELSE 'RSI_NEUTRAL'
                END as rsi_state,
                trend,
                COUNT(*) as occurrences,
                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                AVG(profit) as avg_profit
            FROM trades
            WHERE result IS NOT NULL AND rsi_14 IS NOT NULL AND trend IS NOT NULL
            GROUP BY rsi_state, trend
            HAVING occurrences >= ?
            ORDER BY wins DESC
        """, (min_occurrences,))

        for row in cursor.fetchall():
            win_rate = (row[3] / row[2] * 100) if row[2] > 0 else 0
            if win_rate > 60:  # Only patterns with >60% win rate
                patterns.append({
                    'type': 'RSI_TREND',
                    'conditions': {'rsi': row[0], 'trend': row[1]},
                    'occurrences': row[2],
                    'wins': row[3],
                    'win_rate': round(win_rate, 1),
                    'avg_profit': round(row[4], 2)
                })

        # Pattern 2: Market regime + Hour combinations
        cursor.execute("""
            SELECT
                market_session,
                hour_of_day,
                COUNT(*) as occurrences,
                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                AVG(profit) as avg_profit
            FROM trades
            WHERE result IS NOT NULL AND market_session IS NOT NULL
            GROUP BY market_session, hour_of_day
            HAVING occurrences >= ?
            ORDER BY wins DESC
        """, (min_occurrences,))

        for row in cursor.fetchall():
            win_rate = (row[3] / row[2] * 100) if row[2] > 0 else 0
            if win_rate > 60:
                patterns.append({
                    'type': 'REGIME_HOUR',
                    'conditions': {'regime': row[0], 'hour': row[1]},
                    'occurrences': row[2],
                    'wins': row[3],
                    'win_rate': round(win_rate, 1),
                    'avg_profit': round(row[4], 2)
                })

        # Pattern 3: Confidence levels
        cursor.execute("""
            SELECT
                CASE
                    WHEN ai_signal_confidence < 65 THEN 'LOW'
                    WHEN ai_signal_confidence < 75 THEN 'MEDIUM'
                    WHEN ai_signal_confidence < 85 THEN 'HIGH'
                    ELSE 'VERY_HIGH'
                END as confidence_bucket,
                COUNT(*) as occurrences,
                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                AVG(profit) as avg_profit
            FROM trades
            WHERE result IS NOT NULL AND ai_signal_confidence IS NOT NULL
            GROUP BY confidence_bucket
            HAVING occurrences >= ?
        """, (min_occurrences,))

        for row in cursor.fetchall():
            win_rate = (row[2] / row[1] * 100) if row[1] > 0 else 0
            patterns.append({
                'type': 'CONFIDENCE',
                'conditions': {'confidence': row[0]},
                'occurrences': row[1],
                'wins': row[2],
                'win_rate': round(win_rate, 1),
                'avg_profit': round(row[3], 2)
            })

        return patterns

    def get_equity_curve(self, days: int = 30) -> List[Dict]:
        """Get equity curve data"""
        cursor = self.conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT timestamp, profit
            FROM trades
            WHERE timestamp >= ? AND result IS NOT NULL
            ORDER BY timestamp ASC
        """, (cutoff_date,))

        equity = []
        cumulative_profit = 0

        for row in cursor.fetchall():
            cumulative_profit += row[1] or 0
            equity.append({
                'timestamp': row[0],
                'profit': row[1],
                'cumulative': round(cumulative_profit, 2)
            })

        return equity

    def get_drawdown_analysis(self) -> Dict:
        """Calculate maximum drawdown"""
        equity_curve = self.get_equity_curve(days=365)  # Last year

        if not equity_curve:
            return {'max_drawdown': 0, 'max_drawdown_pct': 0, 'current_drawdown': 0}

        peak = 0
        max_drawdown = 0
        cumulative = [point['cumulative'] for point in equity_curve]

        for value in cumulative:
            if value > peak:
                peak = value
            drawdown = peak - value
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        current_drawdown = peak - cumulative[-1] if cumulative else 0
        max_drawdown_pct = (max_drawdown / peak * 100) if peak > 0 else 0

        return {
            'max_drawdown': round(max_drawdown, 2),
            'max_drawdown_pct': round(max_drawdown_pct, 2),
            'current_drawdown': round(current_drawdown, 2),
            'peak_equity': round(peak, 2)
        }

    def predict_next_trade_outcome(self, market_conditions: Dict) -> Dict:
        """Predict next trade outcome based on historical patterns"""
        cursor = self.conn.cursor()

        # Find similar conditions
        similar_trades = []

        # RSI similarity
        rsi = market_conditions.get('rsi_14', 50)
        cursor.execute("""
            SELECT result, profit
            FROM trades
            WHERE rsi_14 BETWEEN ? AND ?
            AND result IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 50
        """, (rsi - 10, rsi + 10))

        similar_trades.extend([dict(row) for row in cursor.fetchall()])

        if similar_trades:
            wins = sum(1 for t in similar_trades if t['result'] == 'WIN')
            win_rate = wins / len(similar_trades) * 100
            avg_profit = np.mean([t['profit'] for t in similar_trades])

            return {
                'predicted_win_rate': round(win_rate, 1),
                'predicted_avg_profit': round(avg_profit, 2),
                'similar_trades': len(similar_trades),
                'confidence': 'HIGH' if len(similar_trades) > 30 else 'MEDIUM' if len(similar_trades) > 10 else 'LOW'
            }

        return {
            'predicted_win_rate': 50,
            'predicted_avg_profit': 0,
            'similar_trades': 0,
            'confidence': 'UNKNOWN'
        }

    def export_performance_report(self, filepath: str, days: int = 30):
        """Export comprehensive performance report"""
        stats = self.get_comprehensive_stats(days)
        model_comparison = self.get_ai_model_comparison(days)
        patterns = self.find_winning_patterns()
        drawdown = self.get_drawdown_analysis()

        report = {
            'generated': datetime.now().isoformat(),
            'period_days': days,
            'statistics': stats,
            'model_comparison': model_comparison,
            'winning_patterns': patterns,
            'drawdown_analysis': drawdown
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📊 Performance report exported to {filepath}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
