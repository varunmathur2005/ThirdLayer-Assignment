"""
Unit tests for the Memory Store and Browser Agent
"""

import unittest
import os
import time
from memory_store import MemoryStore, Memory
from browser_agent import BrowserAgent


class TestMemoryStore(unittest.TestCase):
    """Test cases for MemoryStore"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db = "test_memory.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.store = MemoryStore(self.test_db)
    
    def tearDown(self):
        """Clean up test database"""
        self.store.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_add_memory(self):
        """Test adding a memory"""
        memory = Memory(
            memory_type='interaction',
            context='test_context',
            action='test_action',
            result='test_result',
            importance=5.0
        )
        
        memory_id = self.store.add_memory(memory)
        self.assertIsNotNone(memory_id)
        self.assertGreater(memory_id, 0)
    
    def test_search_memories(self):
        """Test searching memories"""
        # Add test memories
        for i in range(5):
            memory = Memory(
                memory_type='interaction',
                context=f'context_{i}',
                action=f'action_{i}',
                result=f'result_{i}',
                importance=float(i)
            )
            self.store.add_memory(memory)
        
        # Search all
        results = self.store.search_memories(limit=10)
        self.assertEqual(len(results), 5)
        
        # Search with importance filter
        important = self.store.search_memories(min_importance=3.0)
        self.assertEqual(len(important), 2)
        
        # Search by query
        specific = self.store.search_memories(query='action_2')
        self.assertEqual(len(specific), 1)
        self.assertEqual(specific[0].action, 'action_2')
    
    def test_preferences(self):
        """Test preference management"""
        # Set preference
        self.store.set_preference('test_key', 'test_value')
        
        # Get preference
        value = self.store.get_preference('test_key')
        self.assertEqual(value, 'test_value')
        
        # Get non-existent preference
        default_value = self.store.get_preference('nonexistent', 'default')
        self.assertEqual(default_value, 'default')
    
    def test_pattern_learning(self):
        """Test pattern learning and recommendations"""
        context = 'test_page'
        action = 'test_action'
        
        # Add successful memory
        memory = Memory(
            memory_type='success',
            context=context,
            action=action,
            result='success',
            user_feedback='positive',
            importance=8.0
        )
        self.store.add_memory(memory)
        
        # Get recommendations
        recommendations = self.store.get_recommendations(context, action)
        self.assertGreater(len(recommendations), 0)
        
        # Should have positive confidence
        if recommendations:
            self.assertGreater(recommendations[0]['confidence'], 0.5)
    
    def test_feedback_updates(self):
        """Test adding feedback to memories"""
        memory = Memory(
            memory_type='interaction',
            context='test',
            action='test',
            result='test'
        )
        
        memory_id = self.store.add_memory(memory)
        
        # Add positive feedback
        self.store.add_feedback(memory_id, 'positive')
        
        # Retrieve and verify
        results = self.store.search_memories(limit=1)
        self.assertEqual(results[0].user_feedback, 'positive')
    
    def test_statistics(self):
        """Test statistics generation"""
        # Add various memories
        for mem_type in ['interaction', 'success', 'error']:
            memory = Memory(
                memory_type=mem_type,
                context='test',
                action='test',
                result='test'
            )
            self.store.add_memory(memory)
        
        stats = self.store.get_statistics()
        
        self.assertEqual(stats['total_memories'], 3)
        self.assertIn('by_type', stats)
        self.assertGreater(stats['by_type']['interaction'], 0)
    
    def test_cleanup(self):
        """Test cleanup of old memories"""
        # Add old low-importance memory
        old_memory = Memory(
            memory_type='interaction',
            context='old',
            action='old',
            result='old',
            importance=1.0
        )
        old_memory.timestamp = time.time() - (100 * 24 * 60 * 60)  # 100 days ago
        
        self.store.add_memory(old_memory)
        
        # Cleanup
        deleted = self.store.cleanup_old_memories(days=90, min_importance=3.0)
        self.assertEqual(deleted, 1)


class TestBrowserAgent(unittest.TestCase):
    """Test cases for BrowserAgent"""
    
    def setUp(self):
        """Set up test agent"""
        self.test_db = "test_agent.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.store = MemoryStore(self.test_db)
        self.agent = BrowserAgent(self.store, "TestAgent")
    
    def tearDown(self):
        """Clean up"""
        self.store.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_navigate(self):
        """Test navigation"""
        result = self.agent.navigate("https://test.com")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['url'], "https://test.com")
        self.assertIn('memory_id', result)
    
    def test_perform_action(self):
        """Test performing an action"""
        self.agent.navigate("https://test.com")
        
        result = self.agent.perform_action(
            action='click',
            target='button',
            value='submit'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'click')
        self.assertIn('memory_id', result)
    
    def test_learning(self):
        """Test learning from success and failure"""
        result = self.agent.perform_action(action='test_action')
        memory_id = result['memory_id']
        
        # Learn from success
        self.agent.learn_from_success(memory_id)
        
        # Verify memory was updated
        memories = self.store.search_memories(limit=10)
        success_memory = next((m for m in memories if m.id == memory_id), None)
        self.assertIsNotNone(success_memory)
        self.assertEqual(success_memory.user_feedback, 'positive')
    
    def test_suggestions(self):
        """Test smart suggestions"""
        url = "https://test.com"
        
        # Perform and mark successful
        result = self.agent.perform_action(action='test_click', context=url)
        self.agent.learn_from_success(result['memory_id'])
        
        # Get suggestions
        suggestions = self.agent.get_smart_suggestions(url)
        
        # Should have suggestions after learning
        self.assertIsInstance(suggestions, list)
    
    def test_preferences(self):
        """Test preference management through agent"""
        self.agent.set_preference('test_pref', 'test_value')
        value = self.agent.get_preference('test_pref')
        
        self.assertEqual(value, 'test_value')
    
    def test_behavior_analysis(self):
        """Test behavior analysis"""
        # Perform several actions
        for i in range(5):
            result = self.agent.perform_action(action=f'action_{i}')
            if i % 2 == 0:
                self.agent.learn_from_success(result['memory_id'])
        
        # Analyze
        analysis = self.agent.analyze_behavior()
        
        self.assertIn('total_memories', analysis)
        self.assertIn('success_rate', analysis)
        self.assertGreater(analysis['total_memories'], 0)
    
    def test_search_interactions(self):
        """Test searching past interactions"""
        # Add some interactions
        self.agent.perform_action(action='search_test')
        
        # Search
        results = self.agent.search_past_interactions(query='search_test')
        
        self.assertGreater(len(results), 0)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
