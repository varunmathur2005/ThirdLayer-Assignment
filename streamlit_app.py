"""
Streamlit Web App for Memory Store Demo
Run: streamlit run streamlit_app.py
"""

import streamlit as st  # type: ignore
import sys
import time
from memory_store import MemoryStore, Memory
from browser_agent import BrowserAgent

# Page config
st.set_page_config(
    page_title="Memory Store Demo",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'store' not in st.session_state:
    st.session_state.store = MemoryStore("streamlit_demo.db")
    st.session_state.agent = BrowserAgent(st.session_state.store, "StreamlitAgent")

store = st.session_state.store
agent = st.session_state.agent

# Header
st.title("🧠 Memory Store for Browser Agents")
st.markdown("### Searchable, Self-Updating, Personalized")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📊 Statistics")
    stats = store.get_statistics()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Memories", stats['total_memories'])
        st.metric("Patterns", stats['total_patterns'])
    with col2:
        st.metric("Preferences", stats['total_preferences'])
        st.metric("Successful", stats['successful_patterns'])
    
    st.markdown("---")
    
    # Quick actions
    st.header("⚡ Quick Actions")
    if st.button("🗑️ Clear All Data"):
        st.session_state.store.cleanup_old_memories(days=0, min_importance=0)
        st.success("All data cleared!")
        st.rerun()
    
    if st.button("📊 Show Full Stats"):
        st.session_state.show_stats = True

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Quick Demo", 
    "🤖 Agent Actions", 
    "🔍 Search", 
    "⚙️ Preferences",
    "📈 Analytics"
])

# Tab 1: Quick Demo
with tab1:
    st.header("Quick Demo")
    st.markdown("See the memory store in action with one click!")
    
    if st.button("🚀 Run Demo", type="primary"):
        with st.spinner("Running demo..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Navigate
            status_text.text("Step 1/4: Navigating to GitHub...")
            result = agent.navigate("https://github.com/trending")
            progress_bar.progress(25)
            time.sleep(0.3)
            
            # Step 2: Perform action
            status_text.text("Step 2/4: Performing action...")
            action = agent.perform_action("search repositories", context="https://github.com/trending")
            agent.learn_from_success(action['memory_id'])
            progress_bar.progress(50)
            time.sleep(0.3)
            
            # Step 3: Get suggestions
            status_text.text("Step 3/4: Getting suggestions...")
            suggestions = agent.get_smart_suggestions("https://github.com/trending")
            progress_bar.progress(75)
            time.sleep(0.3)
            
            # Step 4: Analyze
            status_text.text("Step 4/4: Analyzing behavior...")
            analysis = agent.analyze_behavior()
            progress_bar.progress(100)
            time.sleep(0.3)
            
            status_text.empty()
            progress_bar.empty()
            
            st.success("✅ Demo completed!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Memories Created:** {2}")
                st.info(f"**Success Rate:** {analysis['success_rate']:.0%}")
            with col2:
                st.info(f"**Suggestions:** {len(suggestions)}")
                st.info(f"**Total Memories:** {analysis['total_memories']}")

# Tab 2: Agent Actions
with tab2:
    st.header("🤖 Agent Actions")
    st.markdown("Teach the agent by performing actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        url = st.text_input("URL/Context", "https://example.com")
        action = st.text_input("Action", "click button")
        importance = st.slider("Importance", 0.0, 10.0, 5.0, 0.5)
        
        if st.button("➕ Add Memory", type="primary"):
            memory = Memory(
                memory_type='interaction',
                context=url,
                action=action,
                result="Action completed",
                importance=importance
            )
            mem_id = store.add_memory(memory)
            st.success(f"✅ Memory #{mem_id} created!")
    
    with col2:
        st.subheader("Recent Actions")
        recent = store.get_recent_memories(5)
        for mem in recent:
            emoji = "✅" if mem.user_feedback == "positive" else "❌" if mem.user_feedback == "negative" else "⚪"
            st.text(f"{emoji} {mem.action[:40]}...")
            st.caption(f"Importance: {mem.importance:.1f} | {mem.context[:30]}...")
    
    st.markdown("---")
    
    # Smart suggestions
    st.subheader("💡 Smart Suggestions")
    context_input = st.text_input("Get suggestions for context:", "https://github.com")
    
    if st.button("Get Suggestions"):
        suggestions = agent.get_smart_suggestions(context_input)
        if suggestions:
            for i, sugg in enumerate(suggestions[:5], 1):
                st.info(f"**{i}. {sugg['action']}**  \nConfidence: {sugg['confidence']:.1%}  \n{sugg['reason']}")
        else:
            st.warning("No suggestions yet. Teach the agent some actions first!")

# Tab 3: Search
with tab3:
    st.header("🔍 Search Memories")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Search query", "")
    with col2:
        search_context = st.text_input("Context filter", "")
    with col3:
        min_importance = st.slider("Min importance", 0.0, 10.0, 0.0)
    
    if st.button("🔍 Search", type="primary"):
        results = store.search_memories(
            query=search_query if search_query else None,  # type: ignore
            context=search_context if search_context else None,  # type: ignore
            min_importance=min_importance,
            limit=20
        )
        
        st.subheader(f"Found {len(results)} results")
        
        for mem in results:
            with st.expander(f"[{mem.importance:.1f}] {mem.action}"):
                st.write(f"**Context:** {mem.context}")
                st.write(f"**Result:** {mem.result}")
                st.write(f"**Type:** {mem.memory_type}")
                st.write(f"**Feedback:** {mem.user_feedback or 'None'}")
                st.write(f"**Tags:** {', '.join(mem.tags) if mem.tags else 'None'}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"👍 Mark Success", key=f"success_{mem.id}"):
                        if mem.id is not None:
                            store.add_feedback(mem.id, 'positive')
                            st.success("Feedback added!")
                with col2:
                    if st.button(f"👎 Mark Failure", key=f"failure_{mem.id}"):
                        if mem.id is not None:
                            store.add_feedback(mem.id, 'negative')
                            st.success("Feedback added!")

# Tab 4: Preferences
with tab4:
    st.header("⚙️ Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Set Preference")
        pref_key = st.text_input("Preference Key", "theme")
        pref_value = st.text_input("Preference Value", "dark")
        
        if st.button("💾 Save Preference", type="primary"):
            agent.set_preference(pref_key, pref_value)
            st.success(f"✅ Saved: {pref_key} = {pref_value}")
    
    with col2:
        st.subheader("Saved Preferences")
        all_prefs = agent.memory_store.get_all_preferences()
        
        if all_prefs:
            for key, data in all_prefs.items():
                st.text(f"• {key}: {data['value']}")
                st.caption(f"  Confidence: {data['confidence']:.1%}")
        else:
            st.info("No preferences set yet")

# Tab 5: Analytics
with tab5:
    st.header("📈 Analytics")
    
    analysis = agent.analyze_behavior()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Memories", analysis['total_memories'])
    with col2:
        st.metric("Success Rate", f"{analysis['success_rate']:.0%}")
    with col3:
        st.metric("Recent Successes", analysis['recent_successes'])
    with col4:
        st.metric("Recent Failures", analysis['recent_failures'])
    
    st.markdown("---")
    
    # Most common actions
    st.subheader("📊 Most Common Actions")
    if analysis['most_common_actions']:
        for action, count in analysis['most_common_actions'][:10]:
            st.progress(count / max([c for _, c in analysis['most_common_actions']]))
            st.text(f"{action}: {count} times")
    else:
        st.info("No actions recorded yet")
    
    st.markdown("---")
    
    # Memory breakdown
    st.subheader("📁 Memory Type Breakdown")
    stats = store.get_statistics()
    if stats['by_type']:
        for mem_type, count in stats['by_type'].items():
            percentage = (count / stats['total_memories'] * 100) if stats['total_memories'] > 0 else 0
            st.text(f"{mem_type}: {count} ({percentage:.1f}%)")
            st.progress(percentage / 100)
    
    st.markdown("---")
    
    # Export
    st.subheader("💾 Export Data")
    if st.button("📦 Export to JSON", type="primary"):
        export_data = agent.export_learned_behavior("export.json")
        st.download_button(
            label="⬇️ Download Export",
            data=export_data,
            file_name="memory_export.json",
            mime="application/json"
        )
        st.success("Export ready for download!")

# Footer
st.markdown("---")
st.markdown("**Memory Store Demo** | Built with Streamlit")
