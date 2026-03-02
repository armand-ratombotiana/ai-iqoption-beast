"""
Agent Orchestrator
Coordinates all AI agents in the trading system
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.base.agent import BaseAgent, AgentState
from agents.base.message import Message, MessageType, MessagePriority
from agents.communication.message_bus import MessageBus
from agents.communication.blackboard import Blackboard


class AgentOrchestrator:
    """
    Orchestrates all AI agents in the system
    
    Features:
    - Agent registration and lifecycle management
    - Trading cycle coordination
    - Error handling and recovery
    - Performance monitoring
    - Health checks
    """
    
    def __init__(self):
        """Initialize orchestrator"""
        # Communication infrastructure
        self.message_bus = MessageBus()
        self.blackboard = Blackboard()
        
        # Agent registry
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_groups: Dict[str, List[str]] = {
            'analysis': [],
            'decision': [],
            'execution': [],
            'learning': []
        }
        
        # State
        self.is_running = False
        self.total_cycles = 0
        self.successful_cycles = 0
        self.failed_cycles = 0
        
        # Logging
        self.logger = logging.getLogger("Orchestrator")
        
        self.logger.info("✅ AgentOrchestrator initialized")
    
    # ========================================================================
    # Agent Registration
    # ========================================================================
    
    async def register_agent(
        self,
        agent: BaseAgent,
        group: Optional[str] = None
    ) -> None:
        """
        Register agent with orchestrator
        
        Args:
            agent: Agent to register
            group: Agent group (analysis, decision, execution, learning)
        """
        # Set communication infrastructure
        agent.message_bus = self.message_bus
        agent.blackboard = self.blackboard
        
        # Register agent
        self.agents[agent.name] = agent
        
        # Add to group
        if group and group in self.agent_groups:
            self.agent_groups[group].append(agent.name)
        
        # Start agent
        await agent.start()
        
        self.logger.info(f"✅ Registered agent: {agent.name} ({agent.role})")
    
    async def unregister_agent(self, agent_name: str) -> None:
        """Unregister agent"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            await agent.stop()
            
            # Remove from groups
            for group_agents in self.agent_groups.values():
                if agent_name in group_agents:
                    group_agents.remove(agent_name)
            
            del self.agents[agent_name]
            self.logger.info(f"❌ Unregistered agent: {agent_name}")
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(agent_name)
    
    def get_agents_by_group(self, group: str) -> List[BaseAgent]:
        """Get all agents in a group"""
        agent_names = self.agent_groups.get(group, [])
        return [self.agents[name] for name in agent_names if name in self.agents]
    
    # ========================================================================
    # Trading Cycle
    # ========================================================================
    
    async def run_trading_cycle(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute one complete trading cycle
        
        Args:
            market_data: Current market data
            
        Returns:
            Cycle results
        """
        self.total_cycles += 1
        cycle_start = datetime.now()
        
        try:
            self.logger.info(f"\n{'='*70}")
            self.logger.info(f"🔄 Trading Cycle #{self.total_cycles}")
            self.logger.info(f"{'='*70}")
            
            # Prepare environment
            environment = {
                'market_data': market_data,
                'timestamp': datetime.now().isoformat(),
                'cycle_number': self.total_cycles
            }
            
            # Phase 1: Analysis (parallel)
            self.logger.info("\n📊 Phase 1: Analysis")
            analysis_results = await self._run_analysis_phase(environment)
            
            # Phase 2: Decision (sequential)
            self.logger.info("\n🤔 Phase 2: Decision Making")
            decision_results = await self._run_decision_phase(environment, analysis_results)
            
            # Phase 3: Execution (sequential)
            self.logger.info("\n⚡ Phase 3: Execution")
            execution_results = await self._run_execution_phase(environment, decision_results)
            
            # Phase 4: Learning (async)
            self.logger.info("\n📚 Phase 4: Learning")
            learning_results = await self._run_learning_phase(environment, execution_results)
            
            # Calculate cycle time
            cycle_time = (datetime.now() - cycle_start).total_seconds()
            
            self.successful_cycles += 1
            
            result = {
                'success': True,
                'cycle_number': self.total_cycles,
                'cycle_time': cycle_time,
                'analysis': analysis_results,
                'decision': decision_results,
                'execution': execution_results,
                'learning': learning_results,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"\n✅ Cycle #{self.total_cycles} completed in {cycle_time:.2f}s")
            self.logger.info(f"{'='*70}\n")
            
            return result
            
        except Exception as e:
            self.failed_cycles += 1
            self.logger.error(f"\n❌ Cycle #{self.total_cycles} failed: {e}")
            
            return {
                'success': False,
                'cycle_number': self.total_cycles,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _run_analysis_phase(self, environment: Dict) -> Dict[str, Any]:
        """Run analysis agents in parallel"""
        analysis_agents = self.get_agents_by_group('analysis')
        
        if not analysis_agents:
            self.logger.warning("⚠️  No analysis agents registered")
            return {}
        
        # Run all analysis agents in parallel
        tasks = [agent.run_cycle(environment) for agent in analysis_agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        analysis_results = {}
        for agent, result in zip(analysis_agents, results):
            if isinstance(result, Exception):
                self.logger.error(f"❌ {agent.name} failed: {result}")
                analysis_results[agent.name] = {'error': str(result)}
            else:
                analysis_results[agent.name] = result
                self.logger.info(f"✅ {agent.name}: {result.get('decision', {})}")
        
        return analysis_results
    
    async def _run_decision_phase(
        self,
        environment: Dict,
        analysis_results: Dict
    ) -> Dict[str, Any]:
        """Run decision agents sequentially"""
        decision_agents = self.get_agents_by_group('decision')
        
        if not decision_agents:
            self.logger.warning("⚠️  No decision agents registered")
            return {}
        
        # Add analysis results to environment
        environment['analysis_results'] = analysis_results
        
        # Run decision agents sequentially
        decision_results = {}
        for agent in decision_agents:
            result = await agent.run_cycle(environment)
            decision_results[agent.name] = result
            self.logger.info(f"✅ {agent.name}: {result.get('decision', {})}")
            
            # Add to environment for next agent
            environment[f'{agent.name}_decision'] = result.get('decision', {})
        
        return decision_results
    
    async def _run_execution_phase(
        self,
        environment: Dict,
        decision_results: Dict
    ) -> Dict[str, Any]:
        """Run execution agents sequentially"""
        execution_agents = self.get_agents_by_group('execution')
        
        if not execution_agents:
            self.logger.warning("⚠️  No execution agents registered")
            return {}
        
        # Add decision results to environment
        environment['decision_results'] = decision_results
        
        # Run execution agents sequentially
        execution_results = {}
        for agent in execution_agents:
            result = await agent.run_cycle(environment)
            execution_results[agent.name] = result
            self.logger.info(f"✅ {agent.name}: {result.get('action', {})}")
        
        return execution_results
    
    async def _run_learning_phase(
        self,
        environment: Dict,
        execution_results: Dict
    ) -> Dict[str, Any]:
        """Run learning agents asynchronously"""
        learning_agents = self.get_agents_by_group('learning')
        
        if not learning_agents:
            return {}
        
        # Add execution results to environment
        environment['execution_results'] = execution_results
        
        # Run learning agents in parallel (async)
        tasks = [agent.run_cycle(environment) for agent in learning_agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        learning_results = {}
        for agent, result in zip(learning_agents, results):
            if isinstance(result, Exception):
                self.logger.error(f"❌ {agent.name} failed: {result}")
                learning_results[agent.name] = {'error': str(result)}
            else:
                learning_results[agent.name] = result
        
        return learning_results
    
    # ========================================================================
    # Lifecycle Management
    # ========================================================================
    
    async def start(self) -> None:
        """Start orchestrator and all agents"""
        self.is_running = True
        
        # Start communication infrastructure
        await self.message_bus.start()
        await self.blackboard.start_cleanup_task()
        
        # Start all agents
        for agent in self.agents.values():
            await agent.start()
        
        self.logger.info("▶️  Orchestrator started")
    
    async def stop(self) -> None:
        """Stop orchestrator and all agents"""
        self.is_running = False
        
        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()
        
        # Stop communication infrastructure
        await self.message_bus.stop()
        await self.blackboard.stop_cleanup_task()
        
        self.logger.info("⏸️  Orchestrator stopped")
    
    async def reset(self) -> None:
        """Reset orchestrator"""
        # Reset all agents
        for agent in self.agents.values():
            await agent.reset()
        
        # Reset communication
        await self.message_bus.reset()
        await self.blackboard.clear()
        
        # Reset statistics
        self.total_cycles = 0
        self.successful_cycles = 0
        self.failed_cycles = 0
        
        self.logger.info("🔄 Orchestrator reset")
    
    # ========================================================================
    # Health & Monitoring
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all agents"""
        health = {
            'orchestrator': {
                'is_running': self.is_running,
                'total_agents': len(self.agents),
                'total_cycles': self.total_cycles,
                'success_rate': (self.successful_cycles / self.total_cycles * 100) if self.total_cycles > 0 else 0
            },
            'agents': {}
        }
        
        for agent_name, agent in self.agents.items():
            health['agents'][agent_name] = {
                'state': agent.state.value,
                'is_active': agent.is_active,
                'performance': agent.get_performance()
            }
        
        return health
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            'total_cycles': self.total_cycles,
            'successful_cycles': self.successful_cycles,
            'failed_cycles': self.failed_cycles,
            'success_rate': (self.successful_cycles / self.total_cycles * 100) if self.total_cycles > 0 else 0,
            'total_agents': len(self.agents),
            'agents_by_group': {
                group: len(agents) for group, agents in self.agent_groups.items()
            },
            'message_bus': self.message_bus.get_statistics(),
            'blackboard': self.blackboard.get_statistics()
        }
    
    def print_status(self) -> None:
        """Print orchestrator status"""
        stats = self.get_statistics()
        
        print("\n" + "="*70)
        print("🎯 ORCHESTRATOR STATUS")
        print("="*70)
        
        print(f"\n📊 Cycles:")
        print(f"   Total: {stats['total_cycles']}")
        print(f"   Successful: {stats['successful_cycles']}")
        print(f"   Failed: {stats['failed_cycles']}")
        print(f"   Success Rate: {stats['success_rate']:.1f}%")
        
        print(f"\n🤖 Agents:")
        print(f"   Total: {stats['total_agents']}")
        for group, count in stats['agents_by_group'].items():
            print(f"   {group.capitalize()}: {count}")
        
        print(f"\n📨 MessageBus:")
        mb_stats = stats['message_bus']
        print(f"   Sent: {mb_stats['total_sent']}")
        print(f"   Delivered: {mb_stats['total_delivered']}")
        print(f"   Delivery Rate: {mb_stats['delivery_rate']:.1f}%")
        
        print(f"\n📝 Blackboard:")
        bb_stats = stats['blackboard']
        print(f"   Entries: {bb_stats['total_entries']}")
        print(f"   Writes: {bb_stats['total_writes']}")
        print(f"   Reads: {bb_stats['total_reads']}")
        
        print("\n" + "="*70 + "\n")
    
    # ========================================================================
    # String Representation
    # ========================================================================
    
    def __repr__(self) -> str:
        return f"<AgentOrchestrator(agents={len(self.agents)}, cycles={self.total_cycles})>"
    
    def __str__(self) -> str:
        return f"Orchestrator: {len(self.agents)} agents, {self.total_cycles} cycles"