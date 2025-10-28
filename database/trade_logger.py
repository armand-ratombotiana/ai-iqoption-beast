"""
Comprehensive Trade Logger
Logs all trade details, AI predictions, and market context
Following PROJECT_FOCUS_GUIDELINES: "Log everything"
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from .db_manager import DatabaseManager


class TradeLogger:
    """Comprehensive trade and market data logger"""

    def __init__(self, db_path: str = "logs/kael_trading.db"):
        """
        Initialize trade logger

        Args:
            db_path: Path to database file
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db = DatabaseManager(db_path)
        self.logger.info("✅ TradeLogger initialized")

    def log_trade_entry(self, trade_data: Dict[str, Any]) -> str:
        """
        Log trade entry with full details

        Args:
            trade_data: Complete trade information

        Returns:
            trade_id
        """
        try:
            # Ensure required fields
            if 'trade_id' not in trade_data:
                trade_data['trade_id'] = f"{trade_data['instrument']}_{int(datetime.now().timestamp()*1000)}"

            if 'entry_time' not in trade_data:
                trade_data['entry_time'] = datetime.now().isoformat()

            # Insert into database
            trade_id = self.db.insert_trade(trade_data)

            self.logger.info(f"✅ Logged trade entry: {trade_id}")
            return trade_id

        except Exception as e:
            # Log full exception with traceback for debugging, and include a safe preview of the trade data
            try:
                preview = json.dumps(trade_data if isinstance(trade_data, dict) else {}, default=str)[:2000]
            except Exception:
                preview = str(type(trade_data))
            self.logger.exception(f"❌ Failed to log trade entry. trade_id={trade_data.get('trade_id')} preview={preview}")
            return trade_data.get('trade_id', 'unknown')

    def log_trade_result(self, trade_id: str, result: str, profit: float,
                         exit_price: Optional[float] = None,
                         balance_after: Optional[float] = None):
        """
        Log trade result after completion

        Args:
            trade_id: Trade identifier
            result: WIN/LOSS/DRAW
            profit: Profit or loss amount
            exit_price: Exit price
            balance_after: Balance after trade
        """
        try:
            self.db.update_trade_result(trade_id, result, profit, exit_price, balance_after)
            self.logger.info(f"✅ Logged trade result: {trade_id} -> {result} (${profit:+.2f})")

        except Exception:
            self.logger.exception(f"❌ Failed to log trade result for {trade_id}")

    def log_ai_predictions(self, trade_id: str, predictions: List[Dict[str, Any]],
                          consensus: Optional[Dict[str, Any]] = None):
        """
        Log AI model predictions

        Args:
            trade_id: Trade identifier
            predictions: List of individual model predictions
            consensus: Consensus prediction (if available)
        """
        try:
            # Log individual predictions
            for pred in predictions:
                prediction_data = {
                    'trade_id': trade_id,
                    'model_name': pred.get('model', 'unknown'),
                    'model_version': pred.get('version', '1.0'),
                    'direction': pred.get('signal', 'NEUTRAL'),
                    'confidence': pred.get('confidence', 0),
                    'signal_strength': pred.get('strength', 0),
                    'primary_indicator': pred.get('primary_indicator'),
                    'indicators_used': json.dumps(pred.get('indicators', [])),
                    'reasoning': pred.get('reasoning', ''),
                    'is_consensus': False,
                    'consensus_weight': pred.get('weight', 1.0)
                }
                self.db.insert_ai_prediction(prediction_data)

            # Log consensus if provided
            if consensus:
                consensus_data = {
                    'trade_id': trade_id,
                    'model_name': 'CONSENSUS',
                    'model_version': '1.0',
                    'direction': consensus.get('signal', 'NEUTRAL'),
                    'confidence': consensus.get('confidence', 0),
                    'signal_strength': consensus.get('strength', 0),
                    'primary_indicator': 'ENSEMBLE',
                    'indicators_used': json.dumps(consensus.get('contributing_models', [])),
                    'reasoning': consensus.get('reasoning', ''),
                    'is_consensus': True,
                    'consensus_weight': 1.0
                }
                self.db.insert_ai_prediction(consensus_data)

            self.logger.info(f"✅ Logged {len(predictions)} AI predictions for {trade_id}")

        except Exception as e:
            self.logger.error(f"❌ Failed to log AI predictions for {trade_id}: {e}")

    def log_strategy_votes(self, trade_id: str, breakdown: List[Dict[str, Any]],
                           executed_direction: Optional[str] = None,
                           trade_result: Optional[str] = None,
                           profit: float = 0.0):
        """
        Log per-strategy votes/outcomes into the strategy_votes table.

        Args:
            trade_id: Trade identifier
            breakdown: List of dicts with {'strategy': name, 'vote': 'CALL'|'PUT'|'NEUTRAL', 'score': float}
            executed_direction: The direction that was executed for the trade
            trade_result: 'WIN'|'LOSS'|'DRAW'|'PENDING'|'FAILED'
            profit: Profit amount (float)
        """
        try:
            for b in breakdown:
                name = b.get('strategy') or 'unknown'
                vote = b.get('vote') or 'NEUTRAL'
                voted_for_executed = (executed_direction is not None and vote == executed_direction)
                vote_data = {
                    'trade_id': trade_id,
                    'strategy_name': name,
                    'voted_direction': vote,
                    'voted_for_executed': voted_for_executed,
                    'trade_result': trade_result,
                    'profit': profit
                }
                self.db.insert_strategy_vote(vote_data)

            self.logger.info(f"✅ Logged {len(breakdown)} strategy votes for {trade_id}")
        except Exception as e:
            self.logger.error(f"❌ Failed to log strategy votes for {trade_id}: {e}")

    def log_market_context(self, trade_id: str, context: Dict[str, Any]):
        """
        Log comprehensive market context

        Args:
            trade_id: Trade identifier
            context: Market context data
        """
        try:
            context_data = {
                'trade_id': trade_id,

                # Candlesticks (serialize to JSON)
                'candles_1m': json.dumps(context.get('candles_1m', [])),
                'candles_5m': json.dumps(context.get('candles_5m', [])),
                'candles_15m': json.dumps(context.get('candles_15m', [])),

                # Technical Indicators
                'rsi_14': context.get('rsi_14'),
                'rsi_7': context.get('rsi_7'),
                'macd_value': context.get('macd', {}).get('value'),
                'macd_signal': context.get('macd', {}).get('signal'),
                'macd_histogram': context.get('macd', {}).get('histogram'),

                # Bollinger Bands
                'bb_upper': context.get('bollinger', {}).get('upper'),
                'bb_middle': context.get('bollinger', {}).get('middle'),
                'bb_lower': context.get('bollinger', {}).get('lower'),
                'bb_width': context.get('bollinger', {}).get('width'),

                # Volatility
                'atr_14': context.get('atr'),
                'historical_volatility': context.get('volatility'),

                # Volume
                'volume_current': context.get('volume', {}).get('current'),
                'volume_avg_20': context.get('volume', {}).get('avg_20'),
                'volume_ratio': context.get('volume', {}).get('ratio'),

                # Trend
                'ema_9': context.get('ema_9'),
                'ema_21': context.get('ema_21'),
                'ema_50': context.get('ema_50'),
                'trend_direction': context.get('trend', {}).get('direction'),
                'trend_strength': context.get('trend', {}).get('strength'),

                # Support/Resistance
                'support_level': context.get('support'),
                'resistance_level': context.get('resistance'),
                'distance_to_support': context.get('distance_to_support'),
                'distance_to_resistance': context.get('distance_to_resistance'),

                # Market Session
                'session': context.get('session'),
                'is_high_impact_news': context.get('high_impact_news', False)
            }

            self.db.insert_market_context(context_data)
            self.logger.debug(f"✅ Logged market context for {trade_id}")

        except Exception as e:
            self.logger.error(f"❌ Failed to log market context for {trade_id}: {e}")

    def log_system_event(self, event_type: str, message: str,
                         severity: str = 'INFO', details: Optional[Dict] = None):
        """
        Log system event

        Args:
            event_type: Type of event (CONNECTION, ERROR, etc.)
            message: Event message
            severity: Severity level
            details: Additional details dictionary
        """
        try:
            details_json = json.dumps(details) if details else None
            self.db.log_system_event(event_type, message, severity, details_json)

        except Exception as e:
            self.logger.error(f"❌ Failed to log system event: {e}")

    def log_complete_trade(self, trade_data: Dict[str, Any],
                          ai_predictions: Optional[List[Dict]] = None,
                          market_context: Optional[Dict] = None,
                          consensus: Optional[Dict] = None) -> str:
        """
        Log complete trade with all associated data

        Args:
            trade_data: Trade information
            ai_predictions: AI model predictions
            market_context: Market context data
            consensus: Consensus prediction

        Returns:
            trade_id
        """
        try:
            # Log trade entry
            trade_id = self.log_trade_entry(trade_data)

            # Log AI predictions if provided
            if ai_predictions:
                self.log_ai_predictions(trade_id, ai_predictions, consensus)

            # Log market context if provided
            if market_context:
                self.log_market_context(trade_id, market_context)

            return trade_id

        except Exception as e:
            self.logger.error(f"❌ Failed to log complete trade: {e}")
            return trade_data.get('trade_id', 'unknown')

    def get_recent_performance(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get recent performance metrics

        Args:
            limit: Number of recent trades to analyze

        Returns:
            Performance summary dictionary
        """
        try:
            recent_trades = self.db.get_recent_trades(limit)

            if not recent_trades:
                return {'message': 'No trades found'}

            total = len(recent_trades)
            wins = sum(1 for t in recent_trades if t.get('result') == 'WIN')
            losses = sum(1 for t in recent_trades if t.get('result') == 'LOSS')
            win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

            total_profit = sum(t.get('profit', 0) for t in recent_trades)
            avg_confidence = sum(t.get('avg_ai_confidence', 0) for t in recent_trades) / total if total > 0 else 0

            return {
                'total_trades': total,
                'wins': wins,
                'losses': losses,
                'win_rate': round(win_rate, 2),
                'total_profit': round(total_profit, 2),
                'avg_ai_confidence': round(avg_confidence, 2),
                'trades': recent_trades
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to get performance metrics: {e}")
            return {'error': str(e)}

    def get_instrument_performance(self) -> List[Dict]:
        """Get performance breakdown by instrument"""
        try:
            return self.db.get_instrument_performance()
        except Exception as e:
            self.logger.error(f"❌ Failed to get instrument performance: {e}")
            return []

    def get_ai_model_performance(self) -> List[Dict]:
        """Get AI model performance comparison"""
        try:
            return self.db.get_ai_model_performance()
        except Exception as e:
            self.logger.error(f"❌ Failed to get AI model performance: {e}")
            return []

    def export_to_csv(self, output_path: str, limit: int = 1000) -> bool:
        """
        Export trades to CSV for analysis

        Args:
            output_path: Output CSV file path
            limit: Number of trades to export

        Returns:
            Success status
        """
        try:
            import csv

            trades = self.db.get_recent_trades(limit)

            with open(output_path, 'w', newline='') as csvfile:
                if not trades:
                    return False

                fieldnames = trades[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerows(trades)

            self.logger.info(f"✅ Exported {len(trades)} trades to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to export to CSV: {e}")
            return False

    def close(self):
        """Close database connection"""
        self.db.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
