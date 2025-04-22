import streamlit as st
import base64
from datetime import datetime

# API endpoints
EMBED_API = f"{BASE_URL}/embed"
INDEX_API = f"{BASE_URL}/index/{{collection_name}}"
SEARCH_API = f"{BASE_URL}/search"
page_title = {page_title}
# Custom theme colors
THEME = {
    "bg_color": "#0E1117",
    "secondary_bg_color": "#1E2129",
    "text_color": "#E0E0E0",
    "primary_color": "#4B56D2",
    "accent_color": "#82C3EC",
    "success_color": "#4CAF50",
    "warning_color": "#FFC107",
    "error_color": "#EF5350",
    "font_family": "Inter, sans-serif"
}

def get_base64_encoded_image(image_path):
    """Get base64 encoded version of an image for CSS background"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def custom_css():
    """Return custom CSS for the entire application"""
    return f"""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Main theme */
        :root {{
            --bg-color: {THEME["bg_color"]};
            --secondary-bg-color: {THEME["secondary_bg_color"]};
            --text-color: {THEME["text_color"]};
            --primary-color: {THEME["primary_color"]};
            --accent-color: {THEME["accent_color"]};
            --success-color: {THEME["success_color"]};
            --warning-color: {THEME["warning_color"]};
            --error-color: {THEME["error_color"]};
            --font-family: {THEME["font_family"]};
        }}
        
        /* Global styles */
        .main {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: var(--font-family);
        }}
        
        .stApp {{
            background-color: var(--bg-color);
        }}
        
        /* Header styling */
        h1, h2, h3, h4, h5, h6 {{
            color: white;
            font-weight: 600;
        }}
        
        h1 {{
            font-size: 2.5rem;
            letter-spacing: -0.5px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
        }}
        
        h2 {{
            font-size: 1.8rem;
            margin-top: 30px;
            margin-bottom: 20px;
            color: var(--accent-color);
        }}
        
        h3 {{
            font-size: 1.3rem;
            border-left: 3px solid var(--primary-color);
            padding-left: 10px;
            margin-top: 20px;
        }}
        
        /* Card styling */
        .card {{
            background-color: var(--secondary-bg-color);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        
        /* Sidebar styling */
        .css-1d391kg, .css-163ttbj, .css-1lsmgbg {{
            background-color: var(--secondary-bg-color) !important;
        }}
        
        /* Form elements */
        .stTextInput input, .stNumberInput input, .stTextArea textarea {{
            background-color: #292d3e !important;
            color: var(--text-color) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 5px !important;
        }}
        
        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 1px var(--primary-color) !important;
        }}
        
        /* Button styling */
        .stButton button {{
            border-radius: 5px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }}
        
        .stButton button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2) !important;
        }}
        
        /* Primary button */
        .stButton button[kind="primary"] {{
            background-color: var(--primary-color) !important;
            color: white !important;
            border: none !important;
        }}
        
        /* Success message */
        .element-container div[data-testid="stImage"] {{
            background-color: var(--secondary-bg-color) !important;
            padding: 5px !important;
            border-radius: 5px !important;
        }}
        
        /* Code blocks */
        .stCode {{
            border-radius: 5px !important;
        }}
        
        code {{
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.9rem !important;
            background-color: #1a1a2e !important;
            padding: 2px 5px !important;
            border-radius: 3px !important;
        }}
        
        /* Expander styling */
        .streamlit-expander {{
            background-color: var(--secondary-bg-color) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 5px !important;
        }}
        
        .streamlit-expander .streamlit-expanderHeader {{
            font-weight: 500 !important;
            color: var(--accent-color) !important;
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent !important;
            border-radius: 5px 5px 0 0 !important;
            color: var(--text-color) !important;
            padding: 10px 20px !important;
            font-weight: 500 !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-bottom: none !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: var(--secondary-bg-color) !important;
            color: var(--primary-color) !important;
            border-top: 2px solid var(--primary-color) !important;
        }}
        
        /* Data tables */
        .stDataFrame {{
            border-radius: 5px !important;
            overflow: hidden !important;
        }}
        
        .stDataFrame [data-testid="stTable"] {{
            background-color: var(--secondary-bg-color) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
        }}
        
        /* JSON display */
        .element-container div[data-testid="stJson"] {{
            background-color: #1a1a2e !important;
            border-radius: 5px !important;
            padding: 5px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
        }}
        
        /* Metrics */
        [data-testid="stMetric"] {{
            background-color: var(--secondary-bg-color);
            border-radius: 5px;
            padding: 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        [data-testid="stMetricLabel"] {{
            font-size: 0.9rem !important;
            color: var(--accent-color) !important;
        }}
        
        [data-testid="stMetricValue"] {{
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: white !important;
        }}
        
        /* Divider */
        hr {{
            border-color: rgba(255, 255, 255, 0.05) !important;
            margin: 30px 0 !important;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 20px 0;
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.5);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 40px;
        }}
        
        /* Card styles for search results */
        .result-card {{
            background-color: var(--secondary-bg-color);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .result-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }}
        
        .result-score {{
            color: var(--primary-color);
            font-weight: 600;
            font-size: 1.2rem;
        }}
        
        .result-text {{
            background-color: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 3px solid var(--primary-color);
        }}
        
        /* AI/ML specific styling for logos and branding */
        .ai-header {{
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            gap: 15px;
        }}
        
        .ai-logo {{
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: var(--primary-color);
            border-radius: 10px;
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
        }}
        
        .ai-title {{
            flex-grow: 1;
        }}
        
        .ai-title h1 {{
            margin: 0;
            padding: 0;
            border: none;
        }}
        
        .ai-title p {{
            margin: 5px 0 0 0;
            font-size: 1rem;
            opacity: 0.7;
        }}
        
        /* Animation for loading */
        @keyframes pulse {{
            0% {{ opacity: 0.6; }}
            50% {{ opacity: 0.8; }}
            100% {{ opacity: 0.6; }}
        }}
        
        .loading {{
            animation: pulse 1.5s infinite;
            background-color: var(--secondary-bg-color);
            border-radius: 5px;
            height: 20px;
        }}
    </style>
    """

def set_page_configuration():
    """Set the page configuration with custom styling"""
    st.set_page_config(
        page_title=st.session_state.get("page_title", page_title),
        page_icon=st.session_state.get("page_icon", "🧠"),
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    st.markdown(custom_css(), unsafe_allow_html=True)
    
    # Apply additional styling specifically for dark theme
    st.markdown("""
        <style>
            /* Dark Theme Fixes */
            .stSelectbox [data-baseweb=select] > div {
                background-color: #292d3e !important;
                color: #E0E0E0 !important;
            }
            
            .stRadio [data-testid=stMarkdownContainer] {
                color: #E0E0E0 !important;
            }
            
            .stCheckbox [data-testid=stMarkdownContainer] {
                color: #E0E0E0 !important;
            }
            
            [data-testid=stSelectbox] > div > div {
                background-color: #292d3e !important;
            }
            
            [data-testid=stWidgetLabel] {
                color: #C0C0C0 !important;
            }
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(0, 0, 0, 0.1);
            }
            
            ::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(255, 255, 255, 0.25);
            }
        </style>
    """, unsafe_allow_html=True)

def render_ai_header():
    """Render the AI header with logo and title"""
    st.markdown("""
        <div class="ai-header">
            <div class="ai-logo">🧠</div>
            <div class="ai-title">
                <h1>VectorDB Interface</h1>
                <p>Powerful vector database operations for AI applications</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Render the footer of the application"""
    current_year = datetime.now().year
    st.markdown(f"""
        <div class="footer">
            <div>VectorDB Interface | Powered by Syntera Marketplace  API</div>
            <div>© {current_year} | <a href="#" style="color: rgba(255, 255, 255, 0.7);">Documentation</a> | <a href="#" style="color: rgba(255, 255, 255, 0.7);">Terms of Service</a></div>
        </div>
    """, unsafe_allow_html=True)

def card_container(content_function=None):
    """Create a styled card container and optionally run a function within it"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if content_function:
        content_function()
    st.markdown('</div>', unsafe_allow_html=True)

def render_stats(title, value, description=None, delta=None, delta_color="normal"):
    """Render a stats card with title, value, and optional delta"""
    delta_html = ""
    if delta is not None:
        delta_color_class = "green" if delta_color == "normal" else "red" if delta_color == "inverse" else "gray"
        delta_symbol = "▲" if float(delta) > 0 else "▼" if float(delta) < 0 else "◆"
        delta_html = f'<span style="color: var(--{delta_color_class}); font-size: 0.9rem; margin-left: 5px;">{delta_symbol} {delta}</span>'
    
    description_html = f'<div style="font-size: 0.8rem; opacity: 0.7; margin-top: 5px;">{description}</div>' if description else ''
    
    st.markdown(f"""
        <div style="background-color: var(--secondary-bg-color); border-radius: 10px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="font-size: 0.9rem; opacity: 0.7;">{title}</div>
            <div style="font-size: 1.5rem; font-weight: 600; margin-top: 5px;">{value}{delta_html}</div>
            {description_html}
        </div>
    """, unsafe_allow_html=True)