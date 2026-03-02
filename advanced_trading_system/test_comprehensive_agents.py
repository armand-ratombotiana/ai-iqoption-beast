"""
Comprehensive Agent System Test
Tests all methods with simplest features to maximize functionality
"""

import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s'
)

from agents import (
    BaseAgent, AgentState,
    Message, MessageType, MessagePriority, MessageBuilder,
    AgentMemory,
    MessageBus, Blackboard,
    AgentOrchestrator
)


# ============================================================================
# Simple Test Agent
# ============================================================================

class SimpleAgent(BaseAgent):
    """Simplest possible agent for testing"""
    
    async def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Simply return the environment data"""
        return {'data': environment.get('data', 'no data')}
    
    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Simply echo the perception"""
        return {'decision': perception['data']}
    
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Simply return the decision"""
        return {'action': decision['decision']}


# ============================================================================
# Test Functions
# ============================================================================

async def test_agent_basic():
    """Test 1: Basic agent creation and info"""
    print("\n" + "="*70)
    print("TEST 1: Basic Agent Creation")
    print("="*70)
    
    agent = SimpleAgent("test_agent", "testing", "A simple test agent")
    
    # Test get_info
    info = agent.get_info()
    print(f"✅ Agent Info: {info['name']} - {info['role']}")
    assert info['name'] == "test_agent"
    assert info['role'] == "testing"
    assert info['state'] == "idle"
    
    # Test get_performance
    perf = agent.get_performance()
    print(f"✅ Performance: {perf['total_cycles']} cycles, {perf['success_rate']}% success")
    assert perf['total_cycles'] == 0
    
    # Test get_status
    status = agent.get_status()
    print(f"✅ Status: {status['state']}, Active: {status['is_active']}")
    assert status['is_active'] == True
    
    print("✅ TEST 1 PASSED\n")


async def test_agent_lifecycle():
    """Test 2: Agent lifecycle (start, stop, reset)"""
    print("\n" + "="*70)
    print("TEST 2: Agent Lifecycle")
    print("="*70)
    
    agent = SimpleAgent("lifecycle_agent", "testing")
    
    # Test start
    await agent.start()
    print(f"✅ Started: State = {agent.state.value}")
    assert agent.is_active == True
    assert agent.state == AgentState.IDLE
    
    # Test stop
    await agent.stop()
    print(f"✅ Stopped: State = {agent.state.value}")
    assert agent.is_active == False
    assert agent.state == AgentState.STOPPED
    
    # Test reset
    await agent.reset()
    print(f"✅ Reset: Cycles = {agent.total_cycles}")
    assert agent.total_cycles == 0
    
    print("✅ TEST 2 PASSED\n")


async def test_agent_cycle():
    """Test 3: Agent PRAL cycle"""
    print("\n" + "="*70)
    print("TEST 3: Agent PRAL Cycle")
    print("="*70)
    
    agent = SimpleAgent("cycle_agent", "testing")
    await agent.start()
    
    # Run cycle
    environment = {'data': 'test_data'}
    result = await agent.run_cycle(environment)
    
    print(f"✅ Cycle Success: {result['success']}")
    print(f"✅ Perception: {result['perception']}")
    print(f"✅ Decision: {result['decision']}")
    print(f"✅ Action: {result['action']}")
    print(f"✅ Execution Time: {result['execution_time']:.3f}s")
    
    assert result['success'] == True
    assert result['perception']['data'] == 'test_data'
    assert agent.total_cycles == 1
    assert agent.successful_cycles == 1
    
    print("✅ TEST 3 PASSED\n")


async def test_message_creation():
    """Test 4: Message creation and serialization"""
    print("\n" + "="*70)
    print("TEST 4: Message Creation")
    print("="*70)
    
    # Test direct creation
    msg = Message(
        from_agent="agent1",
        to_agent="agent2",
        message_type=MessageType.SIGNAL,
        data={'signal': 'CALL'}
    )
    
    print(f"✅ Message ID: {msg.message_id}")
    print(f"✅ From: {msg.from_agent} -> To: {msg.to_agent}")
    print(f"✅ Type: {msg.message_type.value}")
    print(f"✅ Priority: {msg.priority.value}")
    
    # Test MessageBuilder
    msg2 = (MessageBuilder()
            .from_agent("agent1")
            .to_agent("agent2")
            .signal({'signal': 'PUT'})
            .high_priority()
            .build())
    
    print(f"✅ Builder Message: {msg2.message_type.value}, Priority: {msg2.priority.value}")
    
    # Test serialization
    json_data = msg.to_json()
    msg3 = Message.from_json(json_data)
    print(f"✅ Serialization: {msg3.message_id == msg.message_id}")
    
    assert msg3.message_id == msg.message_id
    assert msg2.priority == MessagePriority.HIGH
    
    print("✅ TEST 4 PASSED\n")


async def test_memory():
    """Test 5: Agent memory"""
    print("\n" + "="*70)
    print("TEST 5: Agent Memory")
    print("="*70)
    
    memory = AgentMemory()
    
    # Test add perception
    memory.add_perception({'data': 'test1'})
    print(f"✅ Added perception")
    
    # Test add decision
    memory.add_decision({'decision': 'CALL'})
    print(f"✅ Added decision")
    
    # Test add action
    memory.add_action({'action': 'executed'})
    print(f"✅ Added action")
    
    # Test retrieve recent
    recent = memory.get_recent_memories(limit=3)
    print(f"✅ Recent memories: {len(recent)} items")
    assert len(recent) == 3
    
    # Test search
    results = memory.search('test1')
    print(f"✅ Search results: {len(results)} items")
    assert len(results) > 0
    
    # Test consolidation
    memory.consolidate(importance_threshold=0.5)
    print(f"✅ Consolidated memories")
    
    # Test clear
    memory.clear()
    recent = memory.get_recent_memories()
    print(f"✅ Cleared: {len(recent)} items remaining")
    assert len(recent) == 0
    
    print("✅ TEST 5 PASSED\n")


async def test_message_bus():
    """Test 6: MessageBus"""
    print("\n" + "="*70)
    print("TEST 6: MessageBus")
    print("="*70)
    
    bus = MessageBus()
    await bus.start()
    
    # Test subscribe
    await bus.subscribe("agent1", "test_topic")
    print(f"✅ Subscribed agent1 to test_topic")
    
    # Test send
    msg = Message(
        from_agent="agent2",
        to_agent="agent1",
        message_type=MessageType.SIGNAL,
        data={'signal': 'CALL'}
    )
    await bus.send(msg)
    print(f"✅ Sent message to agent1")
    
    # Test receive
    received = await bus.receive("agent1")
    print(f"✅ Received message: {received.message_type.value if received else 'None'}")
    assert received is not None
    assert received.message_id == msg.message_id
    
    # Test broadcast
    msg2 = Message(
        from_agent="agent2",
        to_agent="ALL",
        message_type=MessageType.INFO,
        data={'info': 'broadcast'}
    )
    await bus.broadcast(msg2)
    print(f"✅ Broadcast message")
    
    # Test statistics
    stats = bus.get_statistics()
    print(f"✅ Stats: {stats['total_sent']} sent, {stats['total_delivered']} delivered")
    assert stats['total_sent'] >= 2
    
    await bus.stop()
    print("✅ TEST 6 PASSED\n")


async def test_blackboard():
    """Test 7: Blackboard"""
    print("\n" + "="*70)
    print("TEST 7: Blackboard")
    print("="*70)
    
    bb = Blackboard()
    await bb.start_cleanup_task()
    
    # Test write
    await bb.write("signal", "CALL", "agent1")
    print(f"✅ Wrote signal to blackboard")
    
    # Test read
    value = await bb.read("signal")
    print(f"✅ Read signal: {value}")
    assert value == "CALL"
    
    # Test write with TTL
    await bb.write("temp_data", "test", "agent1", ttl=1)
    print(f"✅ Wrote temp_data with TTL=1s")
    
    # Test query
    results = await bb.query("sig*")
    print(f"✅ Query 'sig*': {len(results)} results")
    assert len(results) > 0
    
    # Test query by author
    results = await bb.query_by_author("agent1")
    print(f"✅ Query by author 'agent1': {len(results)} results")
    assert len(results) >= 2
    
    # Test statistics
    stats = bb.get_statistics()
    print(f"✅ Stats: {stats['total_writes']} writes, {stats['total_reads']} reads")
    assert stats['total_writes'] >= 2
    
    # Test clear
    await bb.clear()
    value = await bb.read("signal")
    print(f"✅ Cleared: signal = {value}")
    assert value is None
    
    await bb.stop_cleanup_task()
    print("✅ TEST 7 PASSED\n")


async def test_orchestrator():
    """Test 8: Orchestrator"""
    print("\n" + "="*70)
    print("TEST 8: Orchestrator")
    print("="*70)
    
    orchestrator = AgentOrchestrator()
    
    # Create agents
    agent1 = SimpleAgent("agent1", "analysis", "Test agent 1")
    agent2 = SimpleAgent("agent2", "decision", "Test agent 2")
    
    # Test register
    await orchestrator.register_agent(agent1, group='analysis')
    await orchestrator.register_agent(agent2, group='decision')
    print(f"✅ Registered 2 agents")
    
    # Test get_agent
    retrieved = orchestrator.get_agent("agent1")
    print(f"✅ Retrieved agent: {retrieved.name if retrieved else 'None'}")
    assert retrieved is not None
    assert retrieved.name == "agent1"
    
    # Test get_agents_by_group
    analysis_agents = orchestrator.get_agents_by_group('analysis')
    print(f"✅ Analysis agents: {len(analysis_agents)}")
    assert len(analysis_agents) == 1
    
    # Test start
    await orchestrator.start()
    print(f"✅ Orchestrator started")
    
    # Test run_trading_cycle
    market_data = {'data': 'test_market_data'}
    result = await orchestrator.run_trading_cycle(market_data)
    print(f"✅ Trading cycle: Success = {result['success']}")
    assert result['success'] == True
    
    # Test health_check
    health = await orchestrator.health_check()
    print(f"✅ Health check: {health['orchestrator']['total_agents']} agents")
    assert health['orchestrator']['total_agents'] == 2
    
    # Test get_statistics
    stats = orchestrator.get_statistics()
    print(f"✅ Stats: {stats['total_cycles']} cycles, {stats['success_rate']:.1f}% success")
    assert stats['total_cycles'] == 1
    
    # Test stop
    await orchestrator.stop()
    print(f"✅ Orchestrator stopped")
    
    print("✅ TEST 8 PASSED\n")


async def test_agent_communication():
    """Test 9: Agent-to-agent communication"""
    print("\n" + "="*70)
    print("TEST 9: Agent Communication")
    print("="*70)
    
    # Create infrastructure
    bus = MessageBus()
    bb = Blackboard()
    await bus.start()
    await bb.start_cleanup_task()
    
    # Create agents
    agent1 = SimpleAgent("sender", "testing")
    agent1.message_bus = bus
    agent1.blackboard = bb
    
    agent2 = SimpleAgent("receiver", "testing")
    agent2.message_bus = bus
    agent2.blackboard = bb
    
    await agent1.start()
    await agent2.start()
    
    # Subscribe receiver
    await bus.subscribe("receiver", "test_topic")
    
    # Test send_message
    await agent1.send_message(
        to="receiver",
        message_type="SIGNAL",
        data={'signal': 'CALL'},
        priority="HIGH"
    )
    print(f"✅ Sent message from sender to receiver")
    
    # Receive message
    msg = await bus.receive("receiver")
    print(f"✅ Received message: {msg.data if msg else 'None'}")
    assert msg is not None
    
    # Test broadcast_message
    await agent1.broadcast_message(
        message_type="INFO",
        data={'info': 'broadcast test'}
    )
    print(f"✅ Broadcast message from sender")
    
    # Test write_to_blackboard
    await agent1.write_to_blackboard("test_key", "test_value")
    print(f"✅ Wrote to blackboard")
    
    # Test read_from_blackboard
    value = await agent2.read_from_blackboard("test_key")
    print(f"✅ Read from blackboard: {value}")
    assert value == "test_value"
    
    await bus.stop()
    await bb.stop_cleanup_task()
    
    print("✅ TEST 9 PASSED\n")


async def test_performance():
    """Test 10: Performance and stress test"""
    print("\n" + "="*70)
    print("TEST 10: Performance Test")
    print("="*70)
    
    agent = SimpleAgent("perf_agent", "testing")
    await agent.start()
    
    # Run multiple cycles
    num_cycles = 10
    print(f"Running {num_cycles} cycles...")
    
    for i in range(num_cycles):
        environment = {'data': f'test_{i}'}
        result = await agent.run_cycle(environment)
        assert result['success'] == True
    
    # Check performance
    perf = agent.get_performance()
    print(f"✅ Total cycles: {perf['total_cycles']}")
    print(f"✅ Success rate: {perf['success_rate']}%")
    print(f"✅ Avg execution time: {perf['avg_execution_time']:.3f}s")
    
    assert perf['total_cycles'] == num_cycles
    assert perf['success_rate'] == 100.0
    assert perf['avg_execution_time'] < 0.1  # Should be fast
    
    print("✅ TEST 10 PASSED\n")


# ============================================================================
# Main Test Runner
# ============================================================================

async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 COMPREHENSIVE AGENT SYSTEM TEST")
    print("Testing all methods with simplest features")
    print("="*70)
    
    tests = [
        ("Basic Agent Creation", test_agent_basic),
        ("Agent Lifecycle", test_agent_lifecycle),
        ("Agent PRAL Cycle", test_agent_cycle),
        ("Message Creation", test_message_creation),
        ("Agent Memory", test_memory),
        ("MessageBus", test_message_bus),
        ("Blackboard", test_blackboard),
        ("Orchestrator", test_orchestrator),
        ("Agent Communication", test_agent_communication),
        ("Performance Test", test_performance),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Final summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    print("="*70)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is working perfectly!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review errors above.")
    
    print("\n" + "="*70)
    print("✅ COMPREHENSIVE TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())