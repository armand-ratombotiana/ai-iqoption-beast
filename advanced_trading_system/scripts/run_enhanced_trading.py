"""
Enhanced AI Trading System - Main Entry Point
Integrates all advanced AI features for optimal trading
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import TradingConfig
from database.trade_storage import TradeDatabase
from analysis.technical_indicators import TechnicalIndicators
from analysis.market_context import MarketContextAnalyzer

# AI Models
from ai_models.openai_model import OpenAIModel
from ai_models.claude_model import ClaudeModel
from ai_models.deepseek_model import DeepSeekModel
from ai_models.lstm_model import LSTMPricePredictor
from ai_models.xgboost_model import XGBoostModel
from ai_models.gemini_model import GeminiModel
from ai_models.mistral_model import MistralModel
from ai_models.ollama_model import OllamaModel

# Enhanced Systems
from ai_models.enhanced_consensus import EnhancedConsensusEngine
from ai_models.kelly_position_sizer import KellyPositionSizer
from ai_models.explainability import ExplainabilityEngine

# Database Analytics
from database.analytics_engine import TradingAnalytics
from database.visualization import PerformanceVisualizer


class EnhancedTradingSystem:
    """
    Production-ready trading system with:
    - Multi-AI consensus (5+ models)
    - Market regime detection
    - Kelly Criterion position sizing
    - Explainable AI
    - Real-time learning
    - Advanced risk management
    """

    def __init__(self, config: TradingConfig = None):
        self.config = config or TradingConfig()

        # Validate configuration
        try:
            self.config.validate()
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            sys.exit(1)

        # Initialize database
        self.db = TradeDatabase(self.config.DB_PATH)

        # Initialize AI consensus engine
        self.consensus = EnhancedConsensusEngine(
            consensus_threshold=self.config.CONSENSUS_THRESHOLD
        )

        # Add AI models
        self._initialize_ai_models()

        # Initialize advanced systems
        self.position_sizer = KellyPositionSizer(self.config.__dict__)
        self.explainability = ExplainabilityEngine()
        self.market_analyzer = MarketContextAnalyzer()

        # Performance tracking
        self.trade_count = 0
        self.win_count = 0

        print("✅ Enhanced Trading System initialized")

    def _initialize_ai_models(self):
        """Initialize all AI models with proper weights"""

        # Traditional LLM models
        if self.config.USE_OPENAI:
            openai_model = OpenAIModel(self.config.OPENAI_MODEL)
            self.consensus.add_model(openai_model, self.config.OPENAI_WEIGHT)

        if self.config.USE_CLAUDE:
            claude_model = ClaudeModel(self.config.CLAUDE_MODEL)
            self.consensus.add_model(claude_model, self.config.CLAUDE_WEIGHT)

        if self.config.USE_DEEPSEEK:
            deepseek_model = DeepSeekModel(self.config.DEEPSEEK_MODEL)
            self.consensus.add_model(deepseek_model, self.config.DEEPSEEK_WEIGHT)

        # FREE AI models
        if os.getenv('GOOGLE_API_KEY'):
            gemini_model = GeminiModel()
            self.consensus.add_model(gemini_model, weight=1.1)

        if os.getenv('MISTRAL_API_KEY'):
            mistral_model = MistralModel()
            self.consensus.add_model(mistral_model, weight=1.2)

        # Local FREE model (Ollama)
        try:
            # Check if Ollama is running
            available_models = OllamaModel.list_available_models()
            if available_models:
                # Use first available model (llama3, mistral, etc.)
                ollama_model = OllamaModel(model_name=available_models[0])
                self.consensus.add_model(ollama_model, weight=1.4)
                print(f"✅ Ollama model loaded: {available_models[0]} (FREE, local)")
        except:
            pass

        # Advanced AI models
        lstm_model = LSTMPricePredictor()
        self.consensus.add_model(lstm_model, weight=1.3)

        xgboost_model = XGBoostModel()
        self.consensus.add_model(xgboost_model, weight=1.5)

        print(f"📊 Loaded {len(self.consensus.models)} AI models")

    def execute_trade(self, pair: str = 'AUDCHF-OTC', duration: int = 1) -> Dict:
        """
        Execute a single trade with full AI enhancement

        Returns complete trade result with explainability
        """
        print("\n" + "=" * 80)
        print(f"🚀 ENHANCED TRADING SYSTEM - {pair}")
        print("=" * 80)

        # Step 1: Connect to IQOption (simulated for now)
        print("\n🔌 Connecting to IQ Option...")
        # In production: api = IQ_Option(email, password)
        balance = 10000.0  # Simulated balance
        print(f"✅ Connected")
        print(f"💰 Balance: ${balance:.2f}")

        # Step 2: Get market data
        print("\n📊 STEP 1: Analyzing Market...")

        # In production: candles = api.get_candles(pair, 100, 60)
        # For now, simulate candles
        candles = self._simulate_candles(pair, 100)

        # Calculate technical indicators
        market_data = self._calculate_indicators(candles, pair)
        print(f"✅ Calculated {len(market_data)} indicators")

        # Step 3: Get Enhanced AI Consensus
        print("\n🤖 STEP 2: Getting Enhanced AI Consensus...")
        consensus = self.consensus.get_consensus_signal(market_data, candles)

        # Print detailed consensus
        self.consensus.print_enhanced_summary(consensus)

        # Step 4: Explainability
        print("\n🔍 STEP 3: Generating Explainable AI Report...")
        explanation = self.explainability.explain_decision(
            consensus['signal'],
            consensus['confidence_calibrated'],
            market_data,
            consensus.get('feature_importance', {})
        )

        # Print XAI report
        xai_report = self.explainability.generate_report(explanation)
        print(xai_report)

        # Step 5: Validate signal
        if not consensus['consensus_reached']:
            print("\n❌ No consensus reached. Trade cancelled.")
            return {'success': False, 'reason': 'No consensus'}

        if consensus['confidence_calibrated'] < self.config.MIN_CONFIDENCE:
            print(
                f"\n❌ Calibrated confidence {consensus['confidence_calibrated']:.1f}% "
                f"below threshold {self.config.MIN_CONFIDENCE}%. Trade cancelled."
            )
            return {'success': False, 'reason': 'Low confidence'}

        # Step 6: Kelly Criterion Position Sizing
        print("\n💵 STEP 4: Calculating Optimal Position Size...")

        # Get historical performance
        recent_trades = self.db.get_recent_trades(100)
        historical_performance = self._calculate_historical_performance(recent_trades)

        position_info = self.position_sizer.calculate_position(
            confidence=consensus['confidence_calibrated'],
            balance=balance,
            ai_consensus=consensus,
            regime_info=consensus['regime'],
            historical_performance=historical_performance
        )

        print(f"✅ Position Sizing:")
        print(f"   Amount: ${position_info['amount']:.2f}")
        print(f"   Kelly %: {position_info['kelly_percentage']:.2f}%")
        print(f"   Risk %: {position_info['risk_percentage']:.2f}%")
        print(f"   Expected Value: ${position_info['expected_value']:.2f}")
        print(f"   Max Drawdown Risk: {position_info['max_drawdown_risk']:.2f}%")
        print(f"   Reasoning: {position_info['reasoning']}")

        # Step 7: Execute Trade (simulated)
        print(f"\n🚀 STEP 5: Executing {consensus['signal']} Trade...")

        trade_data = {
            'trade_id': f"TRADE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'pair': pair,
            'direction': consensus['signal'],
            'amount': position_info['amount'],
            'duration': duration,

            # AI Consensus
            'ai_signal_confidence': int(consensus['confidence_calibrated']),
            'ai_model_agreement': consensus['agreement'],
            'ai_models_count': consensus['total_models'],

            # Pre-trade indicators
            'entry_price': market_data['current_price'],
            'rsi_14': market_data['rsi_14'],
            'rsi_7': market_data['rsi_7'],
            'macd_value': market_data['macd']['macd'],
            'macd_signal': market_data['macd']['signal'],
            'macd_histogram': market_data['macd']['histogram'],
            'bb_position': market_data['bb_position'],
            'trend': market_data['trend'],
            'volatility': market_data['volatility'],

            # Regime
            'market_session': consensus['regime']['regime'],

            # Full context
            'pre_trade_context_json': str(market_data),
            'ai_models_votes_json': str(consensus['models_voted']),

            # Initially pending
            'result': 'PENDING'
        }

        # Save to database
        self.db.insert_trade(trade_data)
        print(f"✅ Trade executed!")
        print(f"   Order ID: {trade_data['trade_id']}")
        print(f"   Direction: {trade_data['direction']}")
        print(f"   Amount: ${trade_data['amount']:.2f}")

        # Step 8: Simulate result (in production, wait for actual result)
        import random
        win_probability = consensus['confidence_calibrated'] / 100
        is_win = random.random() < win_probability

        result = 'WIN' if is_win else 'LOSS'
        profit = position_info['amount'] * 0.8 if is_win else -position_info['amount']

        # Update trade result
        self.db.update_trade(trade_data['trade_id'], {
            'result': result,
            'profit': profit
        })

        # Update model performance
        current_regime = consensus['regime']['regime']
        for model_name in consensus['models_voted']:
            model_prediction = consensus['models_voted'][model_name]
            model_correct = (model_prediction['signal'] == consensus['signal']) and is_win

            self.consensus.update_model_performance(
                model_name,
                current_regime,
                model_correct,
                model_prediction['confidence']
            )

        # Update position sizer
        self.trade_count += 1
        if is_win:
            self.win_count += 1

        current_win_rate = self.win_count / self.trade_count
        self.position_sizer.update_performance(current_win_rate, 1.8)

        # Print result
        print("\n" + "=" * 80)
        print(f"📈 TRADE RESULT")
        print("=" * 80)
        print(f"{'✅ WIN!' if is_win else '❌ LOSS'}")
        print(f"   Profit/Loss: ${profit:+.2f}")
        print(f"   Balance: ${balance:.2f} → ${balance + profit:.2f} ({profit:+.2f})")
        print(f"\n   Prediction: {consensus['signal']}")
        print(f"   Actual: {'UP' if is_win else 'DOWN'}")
        print(f"   Correct: {'YES' if is_win else 'NO'}")
        print("\n" + "=" * 80)

        return {
            'success': True,
            'trade': trade_data,
            'result': result,
            'profit': profit,
            'consensus': consensus,
            'explanation': explanation,
            'position_info': position_info
        }

    def _simulate_candles(self, pair: str, count: int) -> List[Dict]:
        """Simulate candle data for testing"""
        import random

        candles = []
        base_price = 0.5685 if 'AUD' in pair else 1.0850

        for i in range(count):
            # Random walk
            change = random.uniform(-0.0005, 0.0005)
            base_price += change

            candle = {
                'open': base_price,
                'high': base_price + random.uniform(0, 0.0003),
                'low': base_price - random.uniform(0, 0.0003),
                'close': base_price + random.uniform(-0.0002, 0.0002),
                'volume': random.uniform(1000, 5000)
            }
            candles.append(candle)

        return candles

    def _calculate_indicators(self, candles: List[Dict], pair: str) -> Dict:
        """Calculate all technical indicators"""
        indicators = TechnicalIndicators()

        current_price = candles[-1]['close']

        return {
            'pair': pair,
            'current_price': current_price,
            'rsi_14': indicators.rsi(candles, 14),
            'rsi_7': indicators.rsi(candles, 7),
            'macd': indicators.macd(candles),
            'bb_position': indicators.bollinger_bands(candles)['position'],
            'stochastic': indicators.stochastic(candles),
            'adx': indicators.adx(candles),
            'atr': indicators.atr(candles),
            'cci': indicators.cci(candles),
            'williams_r': indicators.williams_r(candles),
            'trend': indicators.identify_trend(candles),
            'volatility': indicators.calculate_volatility(candles)[0],
            'volatility_value': indicators.calculate_volatility(candles)[1],
            'support': indicators.find_support_resistance(candles)[0],
            'resistance': indicators.find_support_resistance(candles)[1],
            'candlestick_pattern': indicators.detect_candlestick_pattern(candles),
            'hour': datetime.now().hour
        }

    def _calculate_historical_performance(self, trades: List[Dict]) -> Dict:
        """Calculate historical performance metrics"""
        if not trades:
            return {'win_rate': 0.55, 'avg_payout': 1.8}

        wins = sum(1 for t in trades if t.get('result') == 'WIN')
        total = len(trades)
        win_rate = wins / total if total > 0 else 0.55

        # Calculate average payout
        profits = [t.get('profit', 0) for t in trades if t.get('result') == 'WIN']
        avg_payout = sum(profits) / len(profits) if profits else 1.8

        return {
            'win_rate': win_rate,
            'avg_payout': avg_payout,
            'total_trades': total,
            'wins': wins,
            'losses': total - wins
        }

    def show_statistics(self):
        """Display advanced trading statistics with analytics"""
        # Initialize analytics
        analytics = TradingAnalytics(self.config.DB_PATH)
        visualizer = PerformanceVisualizer()

        # Get comprehensive stats
        stats = analytics.get_comprehensive_stats(days=30)
        model_comparison = analytics.get_ai_model_comparison(days=30)
        patterns = analytics.find_winning_patterns(min_occurrences=3)
        equity_curve = analytics.get_equity_curve(days=30)
        drawdown = analytics.get_drawdown_analysis()

        # Display performance dashboard
        dashboard = visualizer.create_performance_dashboard(stats, model_comparison)
        print(dashboard)

        # Display model comparison chart
        if model_comparison and model_comparison.get('models'):
            print("\n" + visualizer.create_model_comparison_chart(model_comparison))

        # Display winning patterns
        if patterns:
            print("\n" + visualizer.create_pattern_report(patterns))

        # Display drawdown analysis
        if equity_curve:
            print("\n" + visualizer.create_drawdown_chart(drawdown, equity_curve))

        # Export detailed report
        report_path = f"reports/performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('reports', exist_ok=True)
        analytics.export_performance_report(report_path, days=30)

        analytics.close()


if __name__ == "__main__":
    # Run enhanced trading system
    system = EnhancedTradingSystem()

    # Display configuration
    system.config.display()

    # Execute trade
    result = system.execute_trade(pair='AUDCHF-OTC', duration=1)

    # Show statistics
    system.show_statistics()

    print("\n✅ Enhanced trading session completed!")
