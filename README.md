# Searchable, Self-Updating Memory Store for Personalized Browser Agent Behaviour

A powerful, production-ready memory system that enables browser agents to learn, adapt, and personalize their behavior over time through intelligent pattern recognition and searchable memory storage.

## 🌟 Features

### Core Capabilities
- **📊 Persistent Memory Storage**: SQLite-based storage for all agent interactions, preferences, and learned patterns
- **🔍 Advanced Search**: Multi-dimensional search with keyword, context, tags, and importance filtering
- **🤖 Auto-Learning**: Automatically updates patterns and success rates based on outcomes
- **🎯 Personalization**: Adapts behavior based on user preferences and historical patterns
- **💡 Smart Recommendations**: Suggests actions based on past successful interactions
- **📈 Pattern Recognition**: Tracks success/failure rates for context-action pairs
- **🗂️ Preference Management**: Stores and retrieves user preferences with confidence scores
- **📉 Statistics & Analytics**: Comprehensive insights into agent behavior and learning
- **🧹 Memory Cleanup**: Automatic removal of old, low-importance memories
- **💾 Export/Import**: Full memory export to JSON for backup or analysis

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser Agent                        │
│  (Learns from interactions & provides suggestions)     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   Memory Store                          │
├─────────────────────────────────────────────────────────┤
│  • Memory Storage    • Pattern Learning                 │
│  • Search Engine     • Personalization                  │
│  • Preferences       • Statistics                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              SQLite Database                            │
│  • memories table   • preferences table                 │
│  • patterns table   • indexes for fast search           │
└─────────────────────────────────────────────────────────┘
```

## 📦 Installation

No external dependencies required! Uses only Python standard library:
- `sqlite3` - Database storage
- `json` - Data serialization
- `dataclasses` - Data structures
- `typing` - Type hints

Simply copy the files to your project:

```bash
# Clone or download the files
memory_store.py       # Core memory storage system
browser_agent.py      # Browser agent with learning
example_usage.py      # Examples and demos
test_memory_store.py  # Unit tests
```

## 🚀 Quick Start

### Basic Usage

```python
from memory_store import MemoryStore, Memory

# Initialize the memory store
store = MemoryStore("my_agent_memory.db")

# Add a memory
memory = Memory(
    memory_type='interaction',
    context='https://example.com',
    action='click search button',
    result='Search modal opened',
    importance=5.0,
    tags=['search', 'ui']
)
store.add_memory(memory)

# Search memories
results = store.search_memories(query='search', limit=10)

# Get recommendations
recommendations = store.get_recommendations('https://example.com')

# Set preferences
store.set_preference('theme', 'dark')

store.close()
```

### Browser Agent Usage

```python
from memory_store import MemoryStore
from browser_agent import BrowserAgent

# Create agent with memory
store = MemoryStore("agent_memory.db")
agent = BrowserAgent(store, agent_name="MyAgent")

# Navigate and perform actions
result = agent.navigate("https://github.com/trending")
action = agent.perform_action(
    action="click",
    target="first repository",
    context="https://github.com/trending"
)

# Learn from outcomes
agent.learn_from_success(action['memory_id'])

# Get smart suggestions
suggestions = agent.get_smart_suggestions("https://github.com/trending")
for suggestion in suggestions:
    print(f"{suggestion['action']} - Confidence: {suggestion['confidence']:.2%}")

# Analyze behavior
analysis = agent.analyze_behavior()
print(f"Success rate: {analysis['success_rate']:.2%}")

store.close()
```

## 📚 API Reference

### MemoryStore

#### Core Methods
- `add_memory(memory: Memory) -> int` - Add a new memory
- `search_memories(query, memory_type, context, tags, min_importance, limit) -> List[Memory]` - Search with filters
- `get_recent_memories(count, memory_type) -> List[Memory]` - Get recent memories
- `get_recommendations(context, action) -> List[Dict]` - Get AI recommendations

#### Preference Management
- `set_preference(key, value, confidence)` - Set user preference
- `get_preference(key, default)` - Get user preference
- `get_all_preferences() -> Dict` - Get all preferences

#### Memory Management
- `update_memory_importance(memory_id, new_importance)` - Update importance
- `add_feedback(memory_id, feedback)` - Add user feedback
- `cleanup_old_memories(days, min_importance) -> int` - Clean old memories

#### Analytics
- `get_statistics() -> Dict` - Get comprehensive statistics
- `export_memories(filepath) -> str` - Export to JSON

### BrowserAgent

#### Navigation & Actions
- `navigate(url) -> Dict` - Navigate to URL
- `perform_action(action, target, value, context) -> Dict` - Perform action

#### Learning
- `learn_from_success(memory_id, feedback_notes)` - Mark success
- `learn_from_failure(memory_id, error_msg)` - Mark failure

#### Intelligence
- `get_smart_suggestions(context) -> List[Dict]` - Get suggestions
- `analyze_behavior() -> Dict` - Analyze patterns
- `search_past_interactions(query, context, tags) -> List[Memory]` - Search history

#### Preferences
- `set_preference(key, value)` - Set preference
- `get_preference(key, default)` - Get preference
- `export_learned_behavior(filepath) -> str` - Export knowledge

## 🎯 Use Cases

1. **Web Automation**: Learn optimal sequences for form filling, navigation
2. **Testing Bots**: Remember successful test patterns, avoid known failures
3. **Personal Assistants**: Adapt to user preferences and common workflows
4. **Data Scraping**: Learn reliable extraction patterns for different sites
5. **QA Agents**: Track bugs, successful fixes, and testing strategies
6. **Customer Support Bots**: Remember successful resolution patterns

## 🧪 Running Tests

```python
python test_memory_store.py
```

Tests cover:
- Memory storage and retrieval
- Search functionality
- Pattern learning
- Recommendation system
- Preference management
- Statistics generation
- Agent behavior

## 📊 Example Output

Running the examples:

```bash
python example_usage.py
```

Output:
```
=============================================================
SEARCHABLE, SELF-UPDATING MEMORY STORE DEMO
For Personalized Browser Agent Behaviour
=============================================================

Example 1: Basic Memory Store Usage
✓ Added memory #1
✓ Set user preferences
✓ Found 1 memories matching 'search'
✓ Statistics: {'total_memories': 1, 'by_type': {...}, ...}

Example 2: Browser Agent with Learning
Navigated to: https://github.com/trending
Performed action: click
✓ Learned successful pattern (memory #2)

✨ Smart Suggestions (2):
  1. click on first repository link
     Confidence: 100.00%
     Reason: Successful 1 times before
  ...
```

## 🔧 Configuration

### Database Location
```python
# Custom database path
store = MemoryStore("/path/to/custom/memory.db")
```

### Memory Retention
```python
# Cleanup memories older than 90 days with importance < 3.0
store.cleanup_old_memories(days=90, min_importance=3.0)
```

### Search Limits
```python
# Adjust search result limits
results = store.search_memories(query="test", limit=100)
```

## 🎨 Memory Types

- `interaction` - Standard user/agent interactions
- `preference` - User preferences and settings
- `learned_behavior` - Discovered patterns
- `error` - Failed actions or errors
- `success` - Successful outcomes

## 📈 Importance Scoring

Importance scale: 0.0 to 10.0
- `0-3`: Low importance (candidates for cleanup)
- `3-6`: Medium importance (standard interactions)
- `6-8`: High importance (successful patterns)
- `8-10`: Critical importance (major successes/failures)

## 🔒 Thread Safety

The MemoryStore uses SQLite with `check_same_thread=False` for multi-threaded access. For production use with high concurrency, consider using connection pooling or PostgreSQL.

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Vector embeddings for semantic search
- Redis/PostgreSQL backend options
- Real-time pattern streaming
- Machine learning integration
- Multi-agent coordination
- Privacy controls & encryption

## 📄 License

Open source - use freely in your projects!

## 🎓 Learn More

See `example_usage.py` for comprehensive examples demonstrating:
- Basic memory operations
- Agent learning and adaptation
- Personalization features
- Advanced search capabilities
- Export and analysis

---

**Built with ❤️ for intelligent browser automation**
