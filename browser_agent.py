"""
Browser Agent Integration with Memory Store

This module provides a browser agent that uses the memory store
to learn and adapt its behavior over time.
"""

import time
from typing import Dict, Any, Optional, List
from memory_store import MemoryStore, Memory


class BrowserAgent:
    """
    An intelligent browser agent that learns from interactions
    and personalizes behavior based on stored memories
    """
    
    def __init__(self, memory_store: MemoryStore, agent_name: str = "BrowserAgent"):
        self.memory_store = memory_store
        self.agent_name = agent_name
        self.current_context = None
        
        # Load agent preferences
        self.preferences = memory_store.get_all_preferences()
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL and record the interaction"""
        self.current_context = url
        
        action = f"navigate to {url}"
        
        # Check for recommendations based on past behavior
        recommendations = self.memory_store.get_recommendations(url)
        
        # Simulate navigation
        result = {
            'success': True,
            'url': url,
            'timestamp': time.time(),
            'recommendations': recommendations
        }
        
        # Store the interaction
        memory = Memory(
            memory_type='interaction',
            context=url,
            action=action,
            result=f"Successfully navigated to {url}",
            importance=3.0,
            tags=['navigation', 'url'],
            metadata=result
        )
        
        memory_id = self.memory_store.add_memory(memory)
        result['memory_id'] = memory_id
        
        return result
    
    def perform_action(
        self,
        action: str,
        target: Optional[str] = None,
        value: Any = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform an action on the current page
        
        Args:
            action: Action to perform (click, type, scroll, etc.)
            target: Target element or selector
            value: Value for the action (text to type, etc.)
            context: Optional context override
        """
        if context is None:
            context = self.current_context or "unknown"
        
        # Check if this action has been successful before
        recommendations = self.memory_store.get_recommendations(context, action)
        
        # Build action description
        action_desc = action
        if target:
            action_desc += f" on {target}"
        if value:
            action_desc += f" with value: {value}"
        
        # Simulate action execution
        result = {
            'success': True,
            'action': action,
            'target': target,
            'value': value,
            'context': context,
            'timestamp': time.time(),
            'recommendations_consulted': len(recommendations) > 0
        }
        
        # Determine importance based on recommendations
        if recommendations and len(recommendations) > 0:
            avg_confidence = sum(r['confidence'] for r in recommendations) / len(recommendations)
            importance = 3.0 + (avg_confidence * 5.0)  # 3-8 scale
        else:
            importance = 5.0  # New action, medium importance
        
        # Store the interaction
        memory = Memory(
            memory_type='interaction',
            context=context,
            action=action_desc,
            result=f"Action '{action}' executed successfully",
            importance=importance,
            tags=['action', action],
            metadata=result
        )
        
        memory_id = self.memory_store.add_memory(memory)
        result['memory_id'] = memory_id
        
        return result
    
    def learn_from_success(self, memory_id: int, feedback_notes: str = ""):
        """Mark an action as successful and reinforce the pattern"""
        self.memory_store.add_feedback(memory_id, 'positive')
        self.memory_store.update_memory_importance(memory_id, 8.0)
        
        print(f"✓ Learned successful pattern (memory #{memory_id})")
    
    def learn_from_failure(self, memory_id: int, error_msg: str = ""):
        """Mark an action as failed and adjust patterns"""
        self.memory_store.add_feedback(memory_id, 'negative')
        self.memory_store.update_memory_importance(memory_id, 7.0)  # Still important to remember
        
        # Store error details
        error_memory = Memory(
            memory_type='error',
            context=self.current_context or "unknown",
            action=f"Failed action from memory #{memory_id}",
            result=error_msg,
            importance=7.0,
            tags=['error', 'failure']
        )
        
        self.memory_store.add_memory(error_memory)
        print(f"✗ Learned from failure (memory #{memory_id})")
    
    def get_smart_suggestions(self, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get AI-powered suggestions based on learned patterns"""
        if context is None:
            context = self.current_context or ""
        
        recommendations = self.memory_store.get_recommendations(context)
        
        # Filter and rank by confidence
        suggestions = []
        for rec in recommendations:
            if rec['confidence'] > 0.6:  # Only suggest high-confidence actions
                suggestions.append({
                    'action': rec['action'],
                    'confidence': rec['confidence'],
                    'reason': f"Successful {rec['based_on_experiences']} times before",
                    'expected_result': rec.get('typical_result', 'Unknown')
                })
        
        return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)
    
    def set_preference(self, key: str, value: Any):
        """Set a user preference"""
        self.memory_store.set_preference(key, value)
        self.preferences[key] = {'value': value, 'confidence': 1.0}
        
        print(f"Preference set: {key} = {value}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        return self.memory_store.get_preference(key, default)
    
    def analyze_behavior(self) -> Dict[str, Any]:
        """Analyze learned behavior patterns"""
        recent_memories = self.memory_store.get_recent_memories(count=50)
        
        # Analyze action frequency
        action_counts = {}
        success_count = 0
        error_count = 0
        
        for memory in recent_memories:
            if memory.memory_type == 'interaction':
                action_counts[memory.action] = action_counts.get(memory.action, 0) + 1
            
            if memory.user_feedback == 'positive':
                success_count += 1
            elif memory.user_feedback == 'negative':
                error_count += 1
        
        # Most common actions
        most_common = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        stats = self.memory_store.get_statistics()
        
        return {
            'total_memories': stats['total_memories'],
            'recent_successes': success_count,
            'recent_failures': error_count,
            'success_rate': success_count / max(success_count + error_count, 1),
            'most_common_actions': most_common,
            'learned_patterns': stats['successful_patterns'],
            'preferences_count': stats['total_preferences']
        }
    
    def search_past_interactions(
        self,
        query: Optional[str] = None,
        context: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Memory]:
        """Search through past interactions"""
        return self.memory_store.search_memories(
            query=query,
            context=context,
            tags=tags,
            limit=20
        )
    
    def export_learned_behavior(self, filepath: str = "agent_memory_export.json") -> str:
        """Export all learned behavior to a file"""
        return self.memory_store.export_memories(filepath)
