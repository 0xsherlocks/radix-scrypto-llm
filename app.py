#!/usr/bin/env python3
"""
RadixDLT RAG App - Modern Developer-Focused Interface
Beautiful, interactive Streamlit app for RadixDLT/Scrypto development
"""

import streamlit as st
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from rag_system_openrouter import RadixRAGSystemOpenRouter
except ImportError:
    st.error("❌ Could not import rag_system_openrouter.py. Make sure it's in the same directory.")
    st.stop()

# Page config with custom theme
st.set_page_config(
    page_title="RadixDLT AI Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-username/radix-rag',
        'Report a bug': 'https://github.com/your-username/radix-rag/issues',
        'About': "RadixDLT AI Assistant powered by OpenRouter"
    }
)

# Custom CSS for developer-focused dark theme with enhanced effects
st.markdown("""
<style>
    /* Dark theme with Radix colors and animations */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a2332 50%, #0f1419 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating particles effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(16, 185, 129, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(168, 85, 247, 0.05) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Main header styling with glow effect */
    .main-header {
        background: linear-gradient(90deg, #00d4ff 0%, #0066cc 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
        animation: pulse 3s ease-in-out infinite alternate;
    }
    
    @keyframes pulse {
        0% { filter: brightness(1) drop-shadow(0 0 5px rgba(0, 212, 255, 0.3)); }
        100% { filter: brightness(1.2) drop-shadow(0 0 20px rgba(0, 212, 255, 0.6)); }
    }
    
    .sub-header {
        color: #64748b;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        animation: fadeInUp 1s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Enhanced chat message styling */
    .user-message {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-left: 4px solid #00d4ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        color: #e2e8f0;
        transform: translateX(-10px);
        animation: slideInLeft 0.5s ease-out forwards;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    @keyframes slideInLeft {
        to { transform: translateX(0); }
    }
    
    .ai-message {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        color: #e2e8f0;
        transform: translateX(10px);
        animation: slideInRight 0.5s ease-out forwards;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    @keyframes slideInRight {
        to { transform: translateX(0); }
    }
    
    /* Enhanced code block styling */
    .code-block {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 0.5rem;
        padding: 1rem;
        font-family: 'Fira Code', 'Courier New', monospace;
        overflow-x: auto;
        position: relative;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        animation: codeAppear 0.8s ease-out;
    }
    
    @keyframes codeAppear {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* Enhanced source citation styling */
    .source-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .source-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.1), transparent);
        transition: left 0.5s ease;
    }
    
    .source-card:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.15);
        border-color: #00d4ff;
    }
    
    .source-card:hover::before {
        left: 100%;
    }
    
    /* Enhanced button styling */
    .quick-question-btn {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #00d4ff;
        color: #00d4ff;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin: 0.25rem;
        font-family: 'Fira Code', monospace;
        position: relative;
        overflow: hidden;
    }
    
    .quick-question-btn::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: radial-gradient(circle, #00d4ff 0%, transparent 70%);
        transition: all 0.3s ease;
        transform: translate(-50%, -50%);
    }
    
    .quick-question-btn:hover {
        background: linear-gradient(135deg, #00d4ff 0%, #0066cc 100%);
        color: #0f1419;
        transform: scale(1.05) translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4);
    }
    
    .quick-question-btn:hover::before {
        width: 300px;
        height: 300px;
        opacity: 0.1;
    }
    
    /* Enhanced metrics styling */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00d4ff, #10b981, #f59e0b);
        transform: translateX(-100%);
        animation: progress 2s ease-in-out forwards;
    }
    
    @keyframes progress {
        to { transform: translateX(0); }
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* Status indicators with animations */
    .status-online {
        color: #10b981;
        font-weight: bold;
        animation: statusPulse 2s ease-in-out infinite;
    }
    
    @keyframes statusPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    .status-thinking {
        color: #f59e0b;
        font-weight: bold;
        animation: thinking 1.5s ease-in-out infinite;
    }
    
    @keyframes thinking {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Sidebar styling with glassmorphism */
    .sidebar-content {
        background: rgba(15, 20, 25, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(71, 85, 105, 0.3);
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        animation: fadeIn 0.8s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Enhanced typing animation */
    @keyframes typing {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
    
    .typing-indicator {
        animation: typing 1.5s infinite;
        color: #00d4ff;
    }
    
    /* Model selector styling */
    .model-selector {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #00d4ff;
        border-radius: 0.5rem;
        color: #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .model-selector:hover {
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
    }
    
    /* Welcome screen animations */
    .welcome-container {
        animation: welcomeFloat 6s ease-in-out infinite;
    }
    
    @keyframes welcomeFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Loading spinner enhancement */
    .stSpinner > div {
        border-color: #00d4ff !important;
        border-top-color: transparent !important;
        animation: spin 1s linear infinite, colorShift 3s ease-in-out infinite;
    }
    
    @keyframes colorShift {
        0%, 100% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(180deg); }
    }
    
    /* Hover effects for interactive elements */
    .stButton > button {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
        border: 1px solid #00d4ff !important;
        color: #00d4ff !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00d4ff 0%, #0066cc 100%) !important;
        color: #0f1419 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4) !important;
    }
    
    /* Input field enhancements */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
        border: 1px solid #475569 !important;
        color: #e2e8f0 !important;
        border-radius: 0.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3) !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00d4ff 0%, #10b981 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #0066cc 0%, #059669 100%);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_rag_system(model_name):
    """Load and cache the RAG system with selected model."""
    try:
        return RadixRAGSystemOpenRouter(model_name=model_name)
    except Exception as e:
        st.error(f"❌ Failed to load RAG system: {e}")
        return None

def display_code_block(code, language="rust"):
    """Display code with copy button and enhanced styling."""
    st.code(code, language=language)
    if st.button(f"📋 Copy {language.title()} Code", key=f"copy_{hash(code)}"):
        st.success("✅ Code copied to clipboard!")
        time.sleep(1)  # Brief pause for user feedback

def display_typing_effect(text, delay=0.02):
    """Simulate typing effect for AI responses with enhanced animation."""
    placeholder = st.empty()
    displayed_text = ""
    
    for i, char in enumerate(text):
        displayed_text += char
        # Add some randomness to typing speed for more natural feel
        actual_delay = delay + (0.01 if char in '.,!?' else 0)
        placeholder.markdown(f'''
        <div class="ai-message">
            <strong>🤖 Answer:</strong><br>
            {displayed_text}<span class="typing-indicator">|</span>
        </div>
        ''', unsafe_allow_html=True)
        time.sleep(actual_delay)
    
    # Final display without cursor
    placeholder.markdown(f'''
    <div class="ai-message">
        <strong>🤖 Answer:</strong><br>{displayed_text}
    </div>
    ''', unsafe_allow_html=True)

def main():
    # Initialize session state early to avoid undefined variable errors
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_model' not in st.session_state:
        st.session_state.current_model = None
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    
    # Header with enhanced gradient effect
    st.markdown('<div class="main-header">🚀 RadixDLT AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your intelligent companion for Scrypto development and RadixDLT blockchain</div>', unsafe_allow_html=True)
    
    # Sidebar with developer tools - Initialize sidebar variables first
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown("## 🛠️ Developer Tools")
        
        # Model selector with real-time switching
        st.markdown("### 🤖 AI Model")
        model_options = {
            "💰 Llama 3.1 8B (Budget)": "meta-llama/llama-3.1-8b-instruct",
            "⚡ Claude 3 Haiku (Balanced)": "anthropic/claude-3-haiku", 
            "🔥 Claude 3.5 Sonnet (Premium)": "anthropic/claude-3.5-sonnet",
            "🧠 Llama 3.1 70B (Smart)": "meta-llama/llama-3.1-70b-instruct"
        }
        
        selected_model_name = st.selectbox(
            "Choose your AI model:",
            options=list(model_options.keys()),
            index=0,  # Default to budget model
            help="Budget models save credits, premium models give better answers",
            key="model_selector"
        )
        selected_model = model_options[selected_model_name]
        
        # Model info with enhanced styling
        cost_info = {
            "meta-llama/llama-3.1-8b-instruct": "~$0.05/1M tokens",
            "anthropic/claude-3-haiku": "~$0.25/1M tokens",
            "anthropic/claude-3.5-sonnet": "~$3/1M tokens",
            "meta-llama/llama-3.1-70b-instruct": "~$0.52/1M tokens"
        }
        
        if selected_model in cost_info:
            st.info(f"💰 Cost: {cost_info[selected_model]}")
        
        st.markdown("---")
        
        # Quick actions with enhanced buttons
        st.markdown("### ⚡ Quick Actions")
        
        # Topic categories
        st.markdown("#### 📚 Learning Topics")
        quick_topics = {
            "🏗️ Blueprints": "How do I create and deploy a blueprint in Scrypto?",
            "🎯 Components": "What are components in RadixDLT and how do I use them?",
            "💎 Tokens": "Show me how to create and manage tokens in Scrypto",
            "🔐 Access Control": "How do I implement access control with badges?",
            "📦 Resources": "What are resources in RadixDLT?",
            "🔄 Transactions": "How do transactions work in RadixDLT?"
        }
        
        for topic, question in quick_topics.items():
            if st.button(topic, key=f"topic_{topic}", help=f"Ask: {question}"):
                st.session_state.quick_question = question
        
        st.markdown("#### 💻 Code Examples")
        code_topics = {
            "🦀 Rust Basics": "Show me basic Rust patterns used in Scrypto",
            "📝 Blueprint Template": "Give me a complete Scrypto blueprint template",
            "🧪 Testing": "How do I test Scrypto blueprints?",
            "🚀 Deployment": "Show me how to deploy to RadixDLT testnet"
        }
        
        for topic, question in code_topics.items():
            if st.button(topic, key=f"code_{topic}", help=f"Ask: {question}"):
                st.session_state.quick_question = question
        
        st.markdown("---")
        
        # Settings - Define these variables in session state
        st.markdown("### ⚙️ Settings")
        show_sources = st.checkbox("Show source documents", value=True, help="Display which documents were used to answer", key="show_sources_cb")
        max_sources = st.slider("Max sources to show", 1, 10, 3, help="Limit number of source documents shown", key="max_sources_slider")
        enable_typing_effect = st.checkbox("Typing animation", value=True, help="Animate AI responses", key="typing_effect_cb")
        
        # Store in session state for access outside sidebar
        st.session_state.show_sources = show_sources
        st.session_state.max_sources = max_sources
        st.session_state.enable_typing_effect = enable_typing_effect
        st.session_state.selected_model_name = selected_model_name
        
        # Enhanced stats with animations
        st.markdown("### 📊 Session Stats")
        if st.session_state.chat_history:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Questions Asked", len(st.session_state.chat_history))
            with col2:
                if st.session_state.chat_history:
                    avg_sources = sum(len(chat.get('sources', [])) for chat in st.session_state.chat_history) / len(st.session_state.chat_history)
                    st.metric("Avg Sources", f"{avg_sources:.1f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Load RAG system with selected model
    if st.session_state.rag_system is None or st.session_state.current_model != selected_model:
        with st.spinner('🔄 Loading RadixDLT AI Assistant...'):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            st.session_state.rag_system = load_rag_system(selected_model)
            st.session_state.current_model = selected_model
            progress_bar.empty()
    
    # Handle quick question clicks
    if hasattr(st.session_state, 'quick_question'):
        st.session_state.current_question = st.session_state.quick_question
        delattr(st.session_state, 'quick_question')
    
    # Check if RAG system loaded successfully
    if not st.session_state.rag_system:
        st.error("❌ RAG system could not be loaded. Please check your setup and API key.")
        return
    
    # Main chat interface with enhanced layout
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Status indicator with animation
        st.markdown('<div class="status-online">🟢 AI Assistant Online</div>', unsafe_allow_html=True)
        
        # Question input with enhanced styling
        question = st.text_input(
            "Ask your RadixDLT question:",
            placeholder="How do I create a token in Scrypto?",
            value=getattr(st.session_state, 'current_question', ''),
            key="question_input",
            help="Ask anything about RadixDLT, Scrypto, or blockchain development"
        )
        
        # Clear the current_question after using it
        if hasattr(st.session_state, 'current_question'):
            delattr(st.session_state, 'current_question')
    
    with col2:
        ask_col, clear_col = st.columns(2)
        with ask_col:
            ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
        with clear_col:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    # Handle clear button
    if clear_button:
        st.session_state.chat_history = []
        st.success("🧹 Chat history cleared!")
        time.sleep(1)
        st.rerun()
    
    # Process question
    if (ask_button or question) and question.strip():
        # Show enhanced thinking status
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown('''
        <div class="status-thinking">
            🤔 AI is analyzing your question... 
            <span class="typing-indicator">⚡</span>
        </div>
        ''', unsafe_allow_html=True)
        
        try:
            # Show progress during processing
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, step in enumerate(["Searching knowledge base", "Processing documents", "Generating response"]):
                    status_text.text(f"🔄 {step}...")
                    time.sleep(0.5)  # Simulate processing time
                    progress_bar.progress((i + 1) * 33)
                
                response = st.session_state.rag_system.ask(question)
                progress_bar.progress(100)
                time.sleep(0.5)
                
                # Clear progress indicators
                progress_container.empty()
            
            thinking_placeholder.empty()
            
            # Add to chat history with enhanced metadata
            st.session_state.chat_history.append({
                'question': question,
                'answer': response['answer'],
                'sources': response['sources'],
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'model': st.session_state.selected_model_name,
                'response_time': datetime.now()
            })
            
            # Success feedback
            st.success("✅ Response generated successfully!")
            time.sleep(1)
            
        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"❌ Error processing question: {e}")
            st.info("💡 Try rephrasing your question or check your API key.")
    
    # Display chat history with enhanced animations (most recent first)
    if st.session_state.chat_history:
        st.markdown("## 💬 Conversation History")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.container():
                # Question with enhanced timestamp and model info
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 You asked:</strong> {chat['question']}
                    <br><small>🕐 {chat['timestamp']} • 🤖 {chat['model']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Answer with conditional typing effect
                if st.session_state.enable_typing_effect and i == 0:  # Only for most recent
                    display_typing_effect(chat['answer'])
                else:
                    st.markdown(f'''
                    <div class="ai-message">
                        <strong>🤖 Answer:</strong><br>{chat["answer"]}
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Enhanced code extraction (if answer contains code)
                if "```" in chat['answer']:
                    code_blocks = chat['answer'].split("```")
                    for j, block in enumerate(code_blocks):
                        if j % 2 == 1 and block.strip():  # Odd indices are code blocks
                            lines = block.strip().split('\n')
                            language = lines[0] if lines[0] in ['rust', 'python', 'javascript', 'json', 'toml'] else 'rust'
                            code_content = '\n'.join(lines[1:]) if lines[0] == language else block.strip()
                            if code_content:
                                st.markdown("#### 📝 Code Example:")
                                display_code_block(code_content, language)
                
                # Sources with enhanced cards and animations
                if st.session_state.show_sources and chat['sources']:
                    with st.expander(f"📚 Sources ({len(chat['sources'])} files used)", expanded=False):
                        for j, source in enumerate(chat['sources'][:st.session_state.max_sources]):
                            st.markdown(f"""
                            <div class="source-card">
                                <strong>📄 {j+1}. {source['filename']}</strong>
                                <span style="color: #64748b;">({source['content_type']})</span>
                                <br>
                                <small style="color: #94a3b8; line-height: 1.4;">{source['snippet']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("---")
    
    else:
        # Enhanced welcome screen with animations
        st.markdown("""
        <div class="welcome-container" style="text-align: center; padding: 3rem 0;">
            <h2 style="color: #64748b; margin-bottom: 1rem;">👋 Welcome to your RadixDLT AI Assistant!</h2>
            <p style="color: #94a3b8; font-size: 1.1rem; line-height: 1.6; max-width: 600px; margin: 0 auto;">
                Ask questions about Scrypto development, RadixDLT blockchain, or click a quick topic in the sidebar to get started.
                Your AI assistant is powered by advanced language models and a comprehensive knowledge base.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show enhanced knowledge base stats with animated metrics
        if st.session_state.rag_system and hasattr(st.session_state.rag_system, 'vectorstore'):
            try:
                # Try to get document count
                doc_count = 0
                if hasattr(st.session_state.rag_system.vectorstore, '_collection'):
                    doc_count = st.session_state.rag_system.vectorstore._collection.count()
                elif hasattr(st.session_state.rag_system.vectorstore, 'get'):
                    # Alternative method for different vector stores
                    try:
                        all_docs = st.session_state.rag_system.vectorstore.get()
                        doc_count = len(all_docs.get('ids', []))
                    except:
                        doc_count = "N/A"
                
                # Display metrics with enhanced styling
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #00d4ff; margin-bottom: 0.5rem;">📊 {doc_count:,}</h3>
                        <p style="color: #94a3b8; margin: 0;">Knowledge Chunks</p>
                        <small style="color: #64748b;">Ready to search</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    model_emoji = {
                        "💰": "💰",
                        "⚡": "⚡", 
                        "🔥": "🔥",
                        "🧠": "🧠"
                    }
                    emoji = next((emoji for emoji, _ in model_emoji.items() if emoji in st.session_state.selected_model_name), "🤖")
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #10b981; margin-bottom: 0.5rem;">{emoji} {st.session_state.selected_model_name.split()[0]}</h3>
                        <p style="color: #94a3b8; margin: 0;">AI Model Active</p>
                        <small style="color: #64748b;">Processing queries</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #f59e0b; margin-bottom: 0.5rem;">⚡ Ready</h3>
                        <p style="color: #94a3b8; margin: 0;">System Status</p>
                        <small style="color: #64748b;">All systems go!</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.success("📊 Knowledge base loaded successfully")
                st.info(f"💡 Tip: The system is ready to answer your RadixDLT and Scrypto questions!")
        
        # Add some helpful quick start tips
        st.markdown("---")
        st.markdown("### 🌟 Quick Start Tips")
        
        tip_cols = st.columns(3)
        
        with tip_cols[0]:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                        border-left: 4px solid #00d4ff; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
                <h4 style="color: #00d4ff; margin-top: 0;">🏗️ Blueprints</h4>
                <p style="color: #e2e8f0; font-size: 0.9rem; margin-bottom: 0;">
                    Learn how to create, deploy, and interact with Scrypto blueprints
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with tip_cols[1]:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                        border-left: 4px solid #10b981; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
                <h4 style="color: #10b981; margin-top: 0;">💎 Tokens</h4>
                <p style="color: #e2e8f0; font-size: 0.9rem; margin-bottom: 0;">
                    Discover token creation, management, and advanced features
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with tip_cols[2]:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                        border-left: 4px solid #a855f7; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
                <h4 style="color: #a855f7; margin-top: 0;">🧪 Testing</h4>
                <p style="color: #e2e8f0; font-size: 0.9rem; margin-bottom: 0;">
                    Master testing strategies and best practices for Scrypto
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer with additional information and animations
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.markdown("""
        <div style="text-align: center; color: #64748b;">
            <h4>🚀 Powered by</h4>
            <p>OpenRouter API<br>Advanced AI Models</p>
        </div>
        """, unsafe_allow_html=True)
    
    with footer_col2:
        st.markdown("""
        <div style="text-align: center; color: #64748b;">
            <h4>📚 Knowledge Base</h4>
            <p>RadixDLT Documentation<br>Scrypto Examples</p>
        </div>
        """, unsafe_allow_html=True)
    
    with footer_col3:
        st.markdown("""
        <div style="text-align: center; color: #64748b;">
            <h4>💡 Features</h4>
            <p>Smart Search<br>Code Generation</p>
        </div>
        """, unsafe_allow_html=True)

# Enhanced error handling and startup checks
def check_dependencies():
    """Check if all required dependencies are available."""
    try:
        # Check for API key
        if not os.getenv("OPENROUTER_API_KEY"):
            return False, "OPENROUTER_API_KEY environment variable not set"
        
        # Check if RAG system can be imported
        from rag_system_openrouter import RadixRAGSystemOpenRouter
        return True, "All dependencies OK"
        
    except ImportError as e:
        return False, f"Import error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

# Enhanced main execution
if __name__ == "__main__":
    # Check dependencies with enhanced error handling
    deps_ok, deps_msg = check_dependencies()
    
    if not deps_ok:
        st.error(f"❌ Dependency Error: {deps_msg}")
        
        if "OPENROUTER_API_KEY" in deps_msg:
            st.markdown("""
            ### 🔑 API Key Setup
            You need to set your OpenRouter API key as an environment variable:
            
            **Windows (PowerShell):**
            ```powershell
            $env:OPENROUTER_API_KEY="your-api-key-here"
            ```
            
            **Windows (Command Prompt):**
            ```cmd
            set OPENROUTER_API_KEY=your-api-key-here
            ```
            
            **macOS/Linux:**
            ```bash
            export OPENROUTER_API_KEY="your-api-key-here"
            ```
            
            **Or create a `.env` file:**
            ```
            OPENROUTER_API_KEY=your-api-key-here
            ```
            """)
        
        if "rag_system_openrouter" in deps_msg:
            st.markdown("""
            ### 📁 File Structure
            Make sure `rag_system_openrouter.py` is in the same directory as this app.
            
            Expected structure:
            ```
            your-project/
            ├── app.py (this file)
            ├── rag_system_openrouter.py
            └── your-knowledge-base-files/
            ```
            """)
        
        st.stop()
    
    # Add startup animation
    startup_container = st.container()
    with startup_container:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🚀</div>
            <div style="color: #00d4ff;">Initializing RadixDLT AI Assistant...</div>
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(1)
        startup_container.empty()
    
    # Run the main application
    main()