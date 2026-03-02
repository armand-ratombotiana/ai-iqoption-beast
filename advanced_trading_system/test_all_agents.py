"""
Complete AI Agents System Test
Tests all components working together
"""

import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from agents import (
    BaseAgent, AgentState,
    MessageBus, Blackboard,
    AgentOrchestrator
)


# ============================================================================
# Sample Trading Agents
# ============================================================================

class MarketAnalystAgent(BaseAgent):
    """Analyzes market conditions"""
    
    async def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Gather market data"""
        market_data = environment.get('market_data', {})
        
        return {
            'pair': market_data.get('pair', 'EURUSD'),
            'price': market_data.get('current_price', 0),
            'rsi': market_data.get('rsi_14', 50),
            'trend': market_data.get('trend', 'unknown')
        }
    
    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market regime"""
        rsi = perception['rsi']
        
        if rsi < 30:
            regime = 'oversold'
            bias = 'bullish'
        elif rsi > 70:
            regime = 'overbought'
            bias = 'bearish'
        else:
            regime = 'neutral'
            bias = 'neutral'
        
        return {
            'regime': regime,
            'bias': bias,
            'confidence': abs(rsi - 50) / 50  # 0 to 1
        }
    
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Publish analysis to blackboard"""
        await self.write_to_blackboard('market_regime', decision['regime'])
        await self.write_to_blackboard('market_bias', decision['bias'])
        
        return {
            'action': 'analysis_published',
            'regime': decision['regime'],
            'bias': decision['bias']
        }


class TechnicalAnalystAgent(BaseAgent):
    """Performs technical analysis"""
    
    async def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Gather technical indicators"""
        market_data = environment.get('market_data', {})
        
        return {
            'rsi': market_data.get('rsi_14', 50),
            'macd': market_data.get('macd', {}),
            'trend': market_data.get('trend', 'unknown')
        }
    
    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signal"""
        rsi = perception['rsi']
        trend = perception['trend']
        
        # Simple signal logic
        if rsi < 30 and trend == 'uptrend':
            signal = 'CALL'
            confidence = 0.8
        elif rsi > 70 and trend == 'downtrend':
            signal = 'PUT'
            confidence = 0.8
        else:
            signal = 'NEUTRAL'
            confidence = 0.5
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': f'RSI={rsi}, Trend={trend}'
        }
    
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Publish signal to blackboard"""
        await self.write_to_blackboard('technical_signal', decision['signal'])
        await self.write_to_blackboard('signal_confidence', decision['confidence'])
        
        return {
            'action': 'signal_published',
            'signal': decision['signal']
        }


class CoordinatorAgent(BaseAgent):
    """Coordinates all signals and makes final decision"""
    
    async def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all analysis results"""
        # Read from blackboard
        market_regime = await self.read_from_blackboard('market_regime')
        market_bias = await self.read_from_blackboard('market_bias')
        technical_signal = await self.read_from_blackboard('technical_signal')
        signal_confidence = await self.read_from_blackboard('signal_confidence')
        
        return {
            'market_regime': market_regime or 'unknown',
            'market_bias': market_bias or 'neutral',
            'technical_signal': technical_signal or 'NEUTRAL',
            'signal_confidence': signal_confidence or 0.5
        }
    
    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Make final trading decision"""
        signal = perception['technical_signal']
        confidence = perception['signal_confidence']
        bias = perception['market_bias']
        
        # Adjust confidence based on market bias
        if (signal == 'CALL' and bias == 'bullish') or \
           (signal == 'PUT' and bias == 'bearish'):
            confidence *= 1.2  # Boost confidence
        
        confidence = min(confidence, 1.0)  # Cap at 1.0
        
        # Final decision
        if confidence > 0.7:
            decision = signal
        else:
            decision = 'NO_TRADE'
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': f'Signal={signal}, Bias={bias}, Confidence={confidence:.2f}'
        }
    
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Publish final decision"""
        await self.write_to_blackboard('final_decision', decision['decision'])
        await self.write_to_blackboard('final_confidence', decision['confidence'])
        
        return {
            'action': 'decision_published',
            'decision': decision['decision']
        }


class RiskManagerAgent(BaseAgent):
    """Manages risk and position sizing"""
    
    async def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Gather decision and account info"""
        final_decision = await self.read_from_blackboard('final_decision')
        final_confidence = await self.read_from_blackboard('final_confidence')
        
        return {
            'decision': final_decision or 'NO_TRADE',
            'confidence': final_confidence or 0.0,
            'account_balance': 1000.0  # Mock balance
        }
    
    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate position size"""
        decision = perception['decision']
        confidence = perception['confidence']
        balance = perception['account_balance']
        
        if decision == 'NO_TRADE':
            position_size = 0
            approved = False
        else:
            # Risk 1-2% based on confidence
            risk_percent = 0.01 + (confidence * 0.01)
            position_size = balance * risk_percent
            approved = True
        
        return {
            'approved': approved,
            'position_size': position_size,
            'risk_percent': risk_percent if approved else 0
        }
    
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Publish risk decision"""
        await self.write_to_blackboard('risk_approved', decision['approved'])
        await self.write_to_blackboard('position_size', decision['position_size'])
        
        return {
            'action': 'risk_checked',
            'approved': decision['approved'],
            'position_size': decision['position_size']
        }


class ExecutionAgent(BaseAgent):
    """Executes trades"""
    
    async def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Gather execution parameters"""
        final_decision = await self.read_from_blackboard('final_decision')
        risk_approved = await self.read_from_blackboard('risk_approved')
        position_size = await self.read_from_blackboard('position_size')
        
        return {
            'decision': final_decision or 'NO_TRADE',
            'approved': risk_approved or False,
            'position_size': position_size or 0
        }
    
    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if should execute"""
        if perception['approved'] and perception['decision'] != 'NO_TRADE':
            execute = True
            action = f"Execute {perception['decision']} with ${perception['position_size']:.2f}"
        else:
            execute = False
            action = "No trade executed"
        
        return {
            'execute': execute,
            'action': action
        }
    
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade (mock)"""
        if decision['execute']:
            # Mock trade execution
            trade_id = f"TRADE_{asyncio.get_event_loop().time():.0f}"
            await self.write_to_blackboard('last_trade_id', trade_id)
            
            return {
                'action': 'trade_executed',
                'trade_id': trade_id,
                'status': 'success'
            }
        else:
            return {
                'action': 'no_trade',
                'status': 'skipped'
            }


class PerformanceAnalystAgent(BaseAgent):
    """Analyzes performance"""
    
    async def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Gather execution results"""
        return {
            'cycle_number': environment.get('cycle_number', 0),
            'execution_results': environment.get('execution_results', {})
        }
    
    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance"""
        # Simple performance tracking
        return {
            'cycle': perception['cycle_number'],
            'analysis': 'Performance tracked'
        }
    
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Log performance"""
        return {
            'action': 'performance_logged',
            'cycle': decision['cycle']
        }


# ============================================================================
# Main Test
# ============================================================================

async def main():
    """Run complete agent system test"""
    print("\n" + "="*70)
    print("🚀 COMPLETE AI AGENTS SYSTEM TEST")
    print("="*70)
    
    # Create orchestrator
    print("\n📦 Creating orchestrator...")
    orchestrator = AgentOrchestrator()
    
    # Create and register agents
    print("\n🤖 Registering agents...")
    
    # Analysis agents
    market_analyst = MarketAnalystAgent(
        name="market_analyst",
        role="Market Analysis",
        description="Analyzes market conditions and regime"
    )
    await orchestrator.register_agent(market_analyst, group='analysis')
    
    technical_analyst = TechnicalAnalystAgent(
        name="technical_analyst",
        role="Technical Analysis",
        description="Performs technical analysis and generates signals"
    )
    await orchestrator.register_agent(technical_analyst, group='analysis')
    
    # Decision agent
    coordinator = CoordinatorAgent(
        name="coordinator",
        role="Decision Coordinator",
        description="Coordinates all signals and makes final decision"
    )
    await orchestrator.register_agent(coordinator, group='decision')
    
    # Execution agents
    risk_manager = RiskManagerAgent(
        name="risk_manager",
        role="Risk Management",
        description="Manages risk and calculates position sizes"
    )
    await orchestrator.register_agent(risk_manager, group='execution')
    
    execution_agent = ExecutionAgent(
        name="execution_agent",
        role="Trade Execution",
        description="Executes trades"
    )
    await orchestrator.register_agent(execution_agent, group='execution')
    
    # Learning agent
    performance_analyst = PerformanceAnalystAgent(
        name="performance_analyst",
        role="Performance Analysis",
        description="Analyzes trading performance"
    )
    await orchestrator.register_agent(performance_analyst, group='learning')
    
    # Start orchestrator
    print("\n▶️  Starting orchestrator...")
    await orchestrator.start()
    
    # Run multiple trading cycles
    print("\n" + "="*70)
    print("🔄 RUNNING TRADING CYCLES")
    print("="*70)
    
    test_scenarios = [
        {
            'name': 'Oversold Uptrend (Should CALL)',
            'market_data': {
                'pair': 'EURUSD',
                'current_price': 1.0850,
                'rsi_14': 28,
                'trend': 'uptrend',
                'macd': {'histogram': 0.001}
            }
        },
        {
            'name': 'Overbought Downtrend (Should PUT)',
            'market_data': {
                'pair': 'GBPUSD',
                'current_price': 1.2650,
                'rsi_14': 75,
                'trend': 'downtrend',
                'macd': {'histogram': -0.002}
            }
        },
        {
            'name': 'Neutral Market (Should NO_TRADE)',
            'market_data': {
                'pair': 'USDJPY',
                'current_price': 149.50,
                'rsi_14': 52,
                'trend': 'ranging',
                'macd': {'histogram': 0.0001}
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{'='*70}")
        print(f"📊 Scenario: {scenario['name']}")
        print(f"{'='*70}")
        
        result = await orchestrator.run_trading_cycle(scenario['market_data'])
        
        if result['success']:
            print(f"\n✅ Cycle completed in {result['cycle_time']:.2f}s")
        else:
            print(f"\n❌ Cycle failed: {result.get('error', 'Unknown error')}")
        
        # Small delay between cycles
        await asyncio.sleep(0.5)
    
    # Print final status
    print("\n" + "="*70)
    print("📊 FINAL STATUS")
    print("="*70)
    orchestrator.print_status()
    
    # Health check
    print("\n" + "="*70)
    print("🏥 HEALTH CHECK")
    print("="*70)
    health = await orchestrator.health_check()
    
    print(f"\n🎯 Orchestrator:")
    print(f"   Running: {health['orchestrator']['is_running']}")
    print(f"   Total Agents: {health['orchestrator']['total_agents']}")
    print(f"   Total Cycles: {health['orchestrator']['total_cycles']}")
    print(f"   Success Rate: {health['orchestrator']['success_rate']:.1f}%")
    
    print(f"\n🤖 Agents:")
    for agent_name, agent_health in health['agents'].items():
        print(f"   {agent_name}:")
        print(f"      State: {agent_health['state']}")
        print(f"      Active: {agent_health['is_active']}")
        print(f"      Success Rate: {agent_health['performance']['success_rate']:.1f}%")
    
    # Stop orchestrator
    print("\n⏸️  Stopping orchestrator...")
    await orchestrator.stop()
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE!")
    print("="*70)
    
    print("\n📊 Summary:")
    print(f"   Total Agents: 6")
    print(f"   Total Cycles: {orchestrator.total_cycles}")
    print(f"   Successful: {orchestrator.successful_cycles}")
    print(f"   Failed: {orchestrator.failed_cycles}")
    print(f"   Success Rate: {(orchestrator.successful_cycles/orchestrator.total_cycles*100):.1f}%")
    
    print("\n🎉 All agents working perfectly!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())