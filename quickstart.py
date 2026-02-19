#!/usr/bin/env python3
"""
Quick Start Demo - Get started with the Memory Store in seconds!
"""

from memory_store import MemoryStore, Memory
from browser_agent import BrowserAgent


def quick_demo():
    """A quick 30-second demo of the memory store capabilities"""
    
    print("\n" + "🎯 " * 20)
    print("\n  MEMORY STORE QUICK START DEMO")
    print("\n" + "🎯 " * 20 + "\n")
    
    # Step 1: Create memory store
    print("Step 1: Creating memory store...")
    store = MemoryStore("quickstart_demo.db")
    print("✓ Memory store initialized\n")
    
    # Step 2: Create intelligent agent
    print("Step 2: Creating browser agent...")
    agent = BrowserAgent(store, "QuickStartAgent")
    print("✓ Agent created\n")
    
    # Step 3: Simulate some actions
    print("Step 3: Agent performing actions and learning...")
    
    # First visit
    result1 = agent.navigate("https://example.com")
    action1 = agent.perform_action(action="click login button", context="https://example.com")
    agent.learn_from_success(action1['memory_id'])
    
    # Second visit
    result2 = agent.navigate("https://example.com")
    action2 = agent.perform_action(action="click login button", context="https://example.com")
    agent.learn_from_success(action2['memory_id'])
    
    # Third visit with recommendation
    result3 = agent.navigate("https://example.com")
    
    print("✓ Agent learned from 3 interactions\n")
    
    # Step 4: Get smart suggestions
    print("Step 4: Agent providing smart suggestions...")
    suggestions = agent.get_smart_suggestions("https://example.com")
    
    if suggestions:
        print("\n💡 Agent suggests:")
        for i, sugg in enumerate(suggestions[:3], 1):
            print(f"   {i}. {sugg['action']}")
            print(f"      Confidence: {sugg['confidence']:.1%}")
            print(f"      {sugg['reason']}\n")
    
    # Step 5: Set preferences
    print("Step 5: Setting user preferences...")
    agent.set_preference('auto_login', True)
    agent.set_preference('remember_me', True)
    print("✓ Preferences saved\n")
    
    # Step 6: Analyze behavior
    print("Step 6: Analyzing learned behavior...")
    analysis = agent.analyze_behavior()
    
    print(f"\n📊 Quick Stats:")
    print(f"   • Total memories: {analysis['total_memories']}")
    print(f"   • Success rate: {analysis['success_rate']:.0%}")
    print(f"   • Learned patterns: {analysis['learned_patterns']}")
    
    # Step 7: Search memories
    print("\n\nStep 7: Searching memory...")
    memories = agent.search_past_interactions(query="login")
    print(f"✓ Found {len(memories)} memories about 'login'\n")
    
    # Cleanup
    store.close()
    
    # Success message
    print("\n" + "=" * 60)
    print("🎉 SUCCESS! Your agent is learning and adapting!")
    print("=" * 60)
    
    print("\n📚 Next Steps:")
    print("   1. Read: README.md for detailed documentation")
    print("   2. Test: python test_memory_store.py")
    print("   3. Explore: memory_store.py and browser_agent.py")
    
    print("\n💡 Core Files:")
    print("   • memory_store.py - Core memory system (18KB)")
    print("   • browser_agent.py - Intelligent agent (8KB)")
    print("   • test_memory_store.py - 14 unit tests")
    
    print("\n" + "🎯 " * 20 + "\n")


if __name__ == "__main__":
    quick_demo()
