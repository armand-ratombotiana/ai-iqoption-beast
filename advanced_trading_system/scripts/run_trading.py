"""
Advanced Binary Options Trading System - Main Runner
Complete implementation with AI Consensus, Market Analysis, and Data Storage

Usage:
    cd /app/app/KAEL/KAEL/advanced_trading_system
    python scripts/run_trading.py
"""
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from iqoptionapi.stable_api import IQ_Option
from database.trade_storage import TradeDatabase
from analysis.market_context import MarketContextAnalyzer
from ai_models import OpenAIModel, ClaudeModel, DeepSeekModel, AIConsensusEngine
from config.settings import TradingConfig


class AdvancedTradingSystem:
    """Complete trading system with AI consensus and market analysis"""

    def __init__(self, config: TradingConfig):
        self.config = config

        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

        self.db = TradeDatabase(config.DB_PATH)
        self.market_analyzer = MarketContextAnalyzer()
        self.consensus_engine = AIConsensusEngine(config.CONSENSUS_THRESHOLD)
        self._setup_ai_models()

    def _setup_ai_models(self):
        """Initialize and register AI models"""
        print("\n🤖 Initializing AI Models...")

        if self.config.USE_OPENAI:
            try:
                openai_model = OpenAIModel(self.config.OPENAI_MODEL)
                self.consensus_engine.add_model(openai_model, weight=self.config.OPENAI_WEIGHT)
            except Exception as e:
                print(f"⚠️  OpenAI not available: {e}")

        if self.config.USE_CLAUDE:
            try:
                claude_model = ClaudeModel(self.config.CLAUDE_MODEL)
                self.consensus_engine.add_model(claude_model, weight=self.config.CLAUDE_WEIGHT)
            except Exception as e:
                print(f"⚠️  Claude not available: {e}")

        if self.config.USE_DEEPSEEK:
            try:
                deepseek_model = DeepSeekModel(self.config.DEEPSEEK_MODEL)
                self.consensus_engine.add_model(deepseek_model, weight=self.config.DEEPSEEK_WEIGHT)
            except Exception as e:
                print(f"⚠️  DeepSeek not available: {e}")

        # Show summary
        summary = self.consensus_engine.get_model_summary()
        print(f"\n✅ {summary['total_models']} AI models active")
        print(f"   Consensus threshold: {summary['consensus_threshold']:.0f}%")

    def execute_trade(self, pair: str, duration: int = None) -> dict:
        """Execute complete trade with AI consensus and full market analysis"""

        if duration is None:
            duration = self.config.DEFAULT_DURATION

        print("\n" + "=" * 70)
        print(f"🚀 ADVANCED TRADING SYSTEM - {pair}")
        print("=" * 70)

        # Connect to IQ Option
        print("\n🔌 Connecting to IQ Option...")
        api = IQ_Option(self.config.EMAIL, self.config.PASSWORD)
        check, reason = api.connect()

        if not check:
            print(f"❌ Connection failed: {reason}")
            return None

        print("✅ Connected")
        api.change_balance('PRACTICE' if self.config.ACCOUNT_TYPE == 'demo' else 'REAL')

        balance = api.get_balance()
        print(f"💰 Balance: ${balance:.2f}")

        # Step 1: Capture Pre-Trade Market Context
        print("\n📊 STEP 1: Capturing Market Context...")
        pre_context = self.market_analyzer.capture_pre_trade_context(api, pair)

        if 'error' in pre_context:
            print(f"❌ {pre_context['error']}")
            return None

        print(f"✅ Captured {len(pre_context)} market indicators")
        print(f"   Trend: {pre_context.get('trend', 'unknown')}")
        print(f"   RSI(14): {pre_context.get('rsi_14', 'N/A')}")
        print(f"   Volatility: {pre_context.get('volatility', 'unknown')}")
        print(f"   Pattern: {pre_context.get('candlestick_pattern', 'none')}")

        # Step 2: Get AI Consensus Signal
        print("\n🤖 STEP 2: Getting AI Consensus...")
        consensus = self.consensus_engine.get_consensus_signal(pre_context)

        self.consensus_engine.print_consensus_summary(consensus)

        # Check if consensus reached
        if not consensus['consensus_reached']:
            print(f"\n❌ No consensus reached (agreement: {consensus['agreement']:.1f}%)")
            print(f"   Required: {self.config.CONSENSUS_THRESHOLD * 100:.0f}%")
            return None

        # Check confidence threshold
        if consensus['confidence'] < self.config.MIN_CONFIDENCE:
            print(f"\n❌ Confidence too low: {consensus['confidence']:.1f}%")
            print(f"   Required: {self.config.MIN_CONFIDENCE}%")
            return None

        signal = consensus['signal']
        confidence = consensus['confidence']

        print(f"\n✅ Trading Signal: {signal}")
        print(f"   Confidence: {confidence:.1f}%")
        print(f"   Agreement: {consensus['agreement']:.1f}%")

        # Step 3: Calculate Trade Amount
        print("\n💵 STEP 3: Position Sizing...")

        # Simple confidence-based sizing
        amount = self.config.BASE_AMOUNT * (confidence / 100)
        amount = max(self.config.MIN_AMOUNT, min(amount, self.config.MAX_AMOUNT))
        amount = round(amount, 2)

        print(f"   Base amount: ${self.config.BASE_AMOUNT}")
        print(f"   Confidence factor: {confidence:.1f}%")
        print(f"   Final amount: ${amount}")

        if amount > balance:
            print(f"❌ Insufficient balance: ${balance:.2f} < ${amount}")
            return None

        # Step 4: Execute Trade
        print(f"\n🚀 STEP 4: Executing Trade...")
        print(f"   {signal} on {pair}")
        print(f"   Amount: ${amount}")
        print(f"   Duration: {duration}m")

        try:
            status, order_id = api.buy(amount, pair, signal.lower(), duration)

            if not status or order_id is None:
                print(f"❌ Trade execution failed")
                return None

            print(f"✅ Trade executed!")
            print(f"   Order ID: {order_id}")
            print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

        # Step 5: Store Trade with Pre-Context
        trade_id = str(order_id)

        trade_data = {
            'trade_id': trade_id,
            'timestamp': datetime.now().isoformat(),
            'pair': pair,
            'direction': signal,
            'amount': amount,
            'duration': duration,
            'result': 'PENDING',
            'ai_signal_confidence': int(confidence),
            'ai_model_agreement': consensus['agreement'],
            'ai_models_count': consensus['total_models'],
            'entry_price': pre_context.get('current_price'),
            'rsi_14': pre_context.get('rsi_14'),
            'rsi_7': pre_context.get('rsi_7'),
            'macd_value': pre_context.get('macd_value'),
            'macd_signal': pre_context.get('macd_signal'),
            'macd_histogram': pre_context.get('macd_histogram'),
            'bb_upper': pre_context.get('bb_upper'),
            'bb_middle': pre_context.get('bb_middle'),
            'bb_lower': pre_context.get('bb_lower'),
            'bb_position': pre_context.get('bb_position'),
            'ema_12': pre_context.get('ema_12'),
            'ema_26': pre_context.get('ema_26'),
            'sma_20': pre_context.get('sma_20'),
            'sma_50': pre_context.get('sma_50'),
            'atr': pre_context.get('atr'),
            'stochastic_k': pre_context.get('stochastic_k'),
            'stochastic_d': pre_context.get('stochastic_d'),
            'adx': pre_context.get('adx'),
            'cci': pre_context.get('cci'),
            'williams_r': pre_context.get('williams_r'),
            'trend': pre_context.get('trend'),
            'volatility': pre_context.get('volatility'),
            'volatility_value': pre_context.get('volatility_value'),
            'support_level': pre_context.get('support_level'),
            'resistance_level': pre_context.get('resistance_level'),
            'volume_ma': pre_context.get('volume_ma'),
            'volume_trend': pre_context.get('volume_trend'),
            'hour_of_day': pre_context.get('hour_of_day'),
            'day_of_week': pre_context.get('day_of_week'),
            'market_session': pre_context.get('market_session'),
            'candlestick_pattern': pre_context.get('candlestick_pattern'),
            'chart_pattern': pre_context.get('chart_pattern'),
            'pre_trade_context_json': json.dumps(pre_context),
            'ai_models_votes_json': json.dumps(consensus['models_voted']),
            'strategy_version': 'advanced_v1.0'
        }

        self.db.insert_trade(trade_data)
        print(f"\n💾 Trade data saved to database")

        # Step 6: Wait and Capture Post-Trade Context
        print("\n⏳ STEP 5: Waiting for trade result...")
        post_context = self.market_analyzer.capture_post_trade_context(
            api, pair, pre_context, duration
        )

        print(f"\n📈 Post-Trade Analysis:")
        print(f"   Entry: ${post_context.get('entry_price', 0):.6f}")
        print(f"   Exit: ${post_context.get('exit_price', 0):.6f}")
        print(f"   Change: {post_context.get('price_change_percent', 0):+.2f}%")
        print(f"   Direction: {post_context.get('actual_direction', 'unknown')}")

        # Step 7: Get Result
        print("\n📊 STEP 6: Checking Result...")

        profit = None
        for attempt in range(20):
            try:
                profit = api.check_win_v3(order_id)
                if profit is not None:
                    print(f"✅ Result retrieved")
                    break
            except:
                pass
            time.sleep(0.5)

        if profit is None:
            print(f"❌ Result not available")
            return None

        # Determine if prediction was correct
        prediction_correct = (
            (signal == 'CALL' and post_context.get('actual_direction') == 'UP') or
            (signal == 'PUT' and post_context.get('actual_direction') == 'DOWN')
        )

        # Update trade with results
        result_data = {
            'result': 'WIN' if profit > 0 else 'LOSS',
            'profit': profit,
            'exit_price': post_context.get('exit_price'),
            'price_change': post_context.get('price_change'),
            'price_change_percent': post_context.get('price_change_percent'),
            'highest_price': post_context.get('highest_price'),
            'lowest_price': post_context.get('lowest_price'),
            'price_range': post_context.get('price_range'),
            'actual_direction': post_context.get('actual_direction'),
            'prediction_correct': prediction_correct,
            'rsi_14_post': post_context.get('rsi_14_post'),
            'macd_value_post': post_context.get('macd_value_post'),
            'trend_post': post_context.get('trend_post'),
            'volatility_post': post_context.get('volatility_post'),
            'volatility_spike': post_context.get('volatility_spike'),
            'trend_reversal': post_context.get('trend_reversal'),
            'post_trade_context_json': json.dumps(post_context)
        }

        self.db.update_trade(trade_id, result_data)

        # Update AI model performance
        for model_name in consensus['models_voted'].keys():
            model_vote = consensus['models_voted'][model_name]
            vote_correct = (model_vote['signal'] == signal and prediction_correct)
            weight = self.consensus_engine.model_weights.get(model_name, 1.0)

            self.db.update_ai_model_performance(
                model_name, vote_correct, model_vote['confidence'], weight
            )

        # Display Result
        print("\n" + "=" * 70)
        print("📈 TRADE RESULT")
        print("=" * 70)

        if profit > 0:
            print(f"✅ WIN!")
            print(f"   Profit: +${profit:.2f}")
        else:
            print(f"❌ LOSS!")
            print(f"   Loss: ${abs(profit):.2f}")

        print(f"\n   Prediction: {signal}")
        print(f"   Actual: {post_context.get('actual_direction')}")
        print(f"   Correct: {'YES' if prediction_correct else 'NO'}")

        new_balance = api.get_balance()
        print(f"\n💰 Balance: ${balance:.2f} → ${new_balance:.2f} ({new_balance - balance:+.2f})")

        print("\n" + "=" * 70)

        return {
            'order_id': order_id,
            'signal': signal,
            'confidence': confidence,
            'amount': amount,
            'profit': profit,
            'result': 'WIN' if profit > 0 else 'LOSS',
            'prediction_correct': prediction_correct
        }

    def show_statistics(self):
        """Display trading statistics"""
        stats = self.db.get_statistics('all')

        print("\n" + "=" * 70)
        print("📊 TRADING STATISTICS")
        print("=" * 70)

        print(f"\nOverall Performance:")
        print(f"   Total Trades: {stats.get('total_trades', 0)}")
        print(f"   Wins: {stats.get('wins', 0)}")
        print(f"   Losses: {stats.get('losses', 0)}")
        print(f"   Win Rate: {stats.get('win_rate', 0):.1f}%")
        print(f"   Total P/L: ${stats.get('total_profit', 0):.2f}")

        print(f"\nBy Trend:")
        for trend_stat in stats.get('by_trend', []):
            print(f"   {trend_stat['trend']}: {trend_stat['win_rate']:.1f}% ({trend_stat['trades']} trades)")

        print(f"\nAI Models Performance:")
        models = self.db.get_all_models_performance()
        for model in models:
            print(f"   {model['model_name']}: {model['accuracy']:.1f}% ({model['total_predictions']} predictions)")

        print("\n" + "=" * 70)


def main():
    """Main execution"""
    # Validate and display config
    TradingConfig.validate()
    TradingConfig.display()

    # Create system
    system = AdvancedTradingSystem(TradingConfig)

    print("\n" + "=" * 70)
    print("🤖 ADVANCED BINARY OPTIONS TRADING SYSTEM")
    print("=" * 70)
    print(f"\nFeatures:")
    print(f"  ✅ Multi-AI Consensus (OpenAI + Claude + DeepSeek)")
    print(f"  ✅ 20+ Technical Indicators")
    print(f"  ✅ Pre/Post-Trade Market Analysis")
    print(f"  ✅ Complete Data Persistence")
    print(f"  ✅ Performance Tracking")

    # Execute test trades
    test_trades = [
        {'pair': 'AUDCHF-OTC', 'duration': 1},
    ]

    for trade_config in test_trades:
        result = system.execute_trade(
            pair=trade_config['pair'],
            duration=trade_config.get('duration')
        )

        if result:
            print(f"\n✅ Trade completed successfully")
        else:
            print(f"\n❌ Trade was not executed")

        # Wait before next trade
        time.sleep(5)

    # Show statistics
    system.show_statistics()

    print(f"\n✅ Session complete!")
    print(f"📁 Database: {TradingConfig.DB_PATH}")


if __name__ == '__main__':
    main()
