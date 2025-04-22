import streamlit as st
import embed
import index
import search
from utils import set_page_configuration, render_ai_header, render_footer
from app_config import APP_CONFIG

if "app_config" not in st.session_state:
    st.session_state.app_config = APP_CONFIG
    st.session_state.page_title = APP_CONFIG["title"]
    st.session_state.page_subtitle = APP_CONFIG["subtitle"]
    st.session_state.page_icon = APP_CONFIG["icon"]

# Set page configuration with dark theme
set_page_configuration()

# AI-themed header
render_ai_header()

# Better structured system status and navigation
st.markdown("""
<style>
.status-container {
    background-color: #1E2129;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 20px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.status-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 15px;
}
.status-item {
    display: flex;
    align-items: center;
    flex: 1;
    min-width: 200px;
    background-color: #262b36;
    padding: 12px 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 12px;
}
.online {
    background-color: #4CAF50;
    box-shadow: 0 0 5px #4CAF50;
}
.offline {
    background-color: #F44336;
    box-shadow: 0 0 5px #F44336;
}
.warning {
    background-color: #FF9800;
    box-shadow: 0 0 5px #FF9800;
}
.status-text {
    font-weight: 500;
}
.nav-tabs {
    display: flex;
    margin-top: 25px;
    margin-bottom: 25px;
    gap: 5px;
}
.nav-tab {
    padding: 12px 20px;
    border-radius: 10px;
    background-color: #262b36;
    color: white;
    text-align: center;
    cursor: pointer;
    flex: 1;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.2s ease;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.nav-tab:hover {
    background-color: #303540;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}
.nav-tab.active {
    background-color: #4B56D2;
    border-color: #4B56D2;
}
.tab-icon {
    font-size: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# Status indicators with improved styling
st.markdown("""
<div class="status-container">
    <h4 style="margin-top: 0; margin-bottom: 15px; opacity: 0.7;">System Status</h4>
    <div class="status-row">
        <div class="status-item">
            <div class="status-indicator online"></div>
            <div>
                <div style="opacity: 0.7; font-size: 0.8rem;">Embedding Engine</div>
                <div class="status-text" style="color: #4CAF50;">Online</div>
            </div>
        </div>
        <div class="status-item">
            <div class="status-indicator online"></div>
            <div>
                <div style="opacity: 0.7; font-size: 0.8rem;">Vector Database</div>
                <div class="status-text" style="color: #4CAF50;">Connected</div>
            </div>
        </div>
        <div class="status-item">
            <div class="status-indicator online"></div>
            <div>
                <div style="opacity: 0.7; font-size: 0.8rem;">API Status</div>
                <div class="status-text" style="color: #4CAF50;">Operational</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Use a simpler approach that works reliably with Streamlit
# Initialize active tab if not set
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Create three columns for the tabs
col1, col2, col3 = st.columns(3)

# Define the styles for active and inactive tabs
active_style = """
    background-color: #4B56D2;
    border-color: #4B56D2;
    color: white;
    padding: 12px 20px;
    border-radius: 10px;
    text-align: center;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    height: 100%;
"""

inactive_style = """
    background-color: #262b36;
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: white;
    padding: 12px 20px;
    border-radius: 10px;
    text-align: center;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    height: 100%;
    transition: all 0.2s ease;
"""

# Tab 1
with col1:
    tab1_style = active_style if st.session_state.active_tab == 0 else inactive_style
    if st.button('🔄 Create Embeddings', key='tab1', use_container_width=True, 
                help="Generate vector embeddings from text"):
        st.session_state.active_tab = 0
        st.rerun()

# Tab 2
with col2:
    tab2_style = active_style if st.session_state.active_tab == 1 else inactive_style
    if st.button('📥 Index Documents', key='tab2', use_container_width=True, 
                help="Add documents to vector collections"):
        st.session_state.active_tab = 1
        st.rerun()

# Tab 3
with col3:
    tab3_style = active_style if st.session_state.active_tab == 2 else inactive_style
    if st.button('🔍 Search Collection', key='tab3', use_container_width=True, 
                help="Search for similar documents"):
        st.session_state.active_tab = 2
        st.rerun()

# Apply custom styling to buttons after they're created
st.markdown(f"""
<style>
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {{
        {tab1_style}
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {{
        {tab2_style}
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {{
        {tab3_style}
    }}
    
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button:hover,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover,
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }}
    
    /* Hide button label shadow and adjust styling */
    button[kind="secondary"] div[data-testid="stMarkdownContainer"] p {{
        margin-bottom: 0 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# Divider after tabs
st.markdown("<hr style='margin-top: 0; margin-bottom: 30px; border-color: rgba(255, 255, 255, 0.05);'>", unsafe_allow_html=True)

# Show the active tab content
if st.session_state.active_tab == 0:
    embed.render_embed_tab()
elif st.session_state.active_tab == 1:
    index.render_index_tab()
elif st.session_state.active_tab == 2:
    search.render_search_tab()

# Footer with links and copyright
render_footer()