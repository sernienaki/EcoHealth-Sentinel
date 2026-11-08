"""Centralized accessible theme and responsive layout styles for EcoHealth Sentinel."""
import streamlit as st


THEMES = {
    "light": {
        "background": "#F7F9FC",
        "surface": "#FFFFFF",
        "surface_alt": "#F0F4F7",
        "text": "#172B3A",
        "muted": "#526575",
        "border": "#D8E1E8",
        "accent": "#087E78",
        "accent_hover": "#066A65",
        "input": "#FFFFFF",
        "focus": "#0B8F87",
        "sidebar": "#F0F4F7",
    },
    "dark": {
        "background": "#101820",
        "surface": "#182530",
        "surface_alt": "#202F3B",
        "text": "#F1F5F8",
        "muted": "#B6C4CE",
        "border": "#344653",
        "accent": "#63C7BD",
        "accent_hover": "#83D8CF",
        "input": "#202F3B",
        "focus": "#83D8CF",
        "sidebar": "#15212B",
    },
}


def get_theme_css(theme="light"):
    """Return theme-aware CSS without overriding icon fonts or SVG artwork."""
    palette = THEMES.get(theme, THEMES["light"])
    tokens = "\n".join(f"  --eco-{key.replace('_', '-')}: {value};" for key, value in palette.items())
    return f"""
    <style>
    :root {{
    {tokens}
      color-scheme: {"dark" if theme == "dark" else "light"};
    }}
    .stApp {{
      background: var(--eco-background);
      color: var(--eco-text);
    }}
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
      background: var(--eco-background);
    }}
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div {{
      background: var(--eco-sidebar);
    }}
    .block-container {{
      width: 100%;
      max-width: 1480px;
      padding-top: 1.4rem;
      padding-bottom: 3rem;
    }}
    h1, h2, h3, h4, h5, h6,
    p, label, legend, li, blockquote,
    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"],
    [data-testid="stWidgetLabel"],
    [data-testid="stTable"],
    [data-testid="stDataFrame"] {{
      color: var(--eco-text);
    }}
    h1, h2, h3, h4 {{
      letter-spacing: -0.018em;
      font-family: "Times New Roman", Times, serif;
    }}
    [data-testid="stCaptionContainer"],
    small, .stCaption {{
      color: var(--eco-muted) !important;
    }}
    [data-testid="stMetric"] {{
      background: var(--eco-surface);
      border: 1px solid var(--eco-border);
      border-radius: 12px;
      padding: 0.9rem 1rem;
      box-shadow: none;
    }}
    [data-testid="stExpander"],
    [data-testid="stContainer"] {{
      border-color: var(--eco-border);
    }}
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    [data-baseweb="select"] > div,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input {{
      background: var(--eco-input);
      border-color: var(--eco-border);
      color: var(--eco-text);
    }}
    input, textarea {{
      color: var(--eco-text) !important;
      background: var(--eco-input) !important;
      caret-color: var(--eco-accent);
    }}
    input::placeholder, textarea::placeholder {{
      color: var(--eco-muted) !important;
      opacity: 1;
    }}
    [data-baseweb="select"] * {{
      color: var(--eco-text);
    }}
    [data-testid="stTabs"] [role="tab"] {{
      color: var(--eco-muted);
      font-weight: 600;
      white-space: nowrap;
    }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
      color: var(--eco-accent);
      border-bottom-color: var(--eco-accent);
    }}
    [data-testid="stTabs"] [data-baseweb="tab-list"] {{
      gap: 0.35rem;
    }}
    .stButton > button, .stDownloadButton > button,
    [data-testid="stLinkButton"] a {{
      min-height: 2.55rem;
      border-radius: 9px;
      font-weight: 600;
    }}
    .stButton > button:focus-visible,
    input:focus-visible, textarea:focus-visible,
    [role="combobox"]:focus-visible {{
      outline: 2px solid var(--eco-focus) !important;
      outline-offset: 2px;
    }}
    [data-testid="stAlert"] {{
      border-radius: 10px;
    }}
    [data-testid="stDataFrame"], [data-testid="stTable"] {{
      max-width: 100%;
      overflow-x: auto;
    }}
    [data-testid="stPlotlyChart"], [data-testid="stVegaLiteChart"],
    [data-testid="stDeckGlJsonChart"] {{
      max-width: 100%;
      min-width: 0;
    }}
    iframe {{
      max-width: 100%;
    }}
    @media (max-width: 767px) {{
      .block-container {{
        padding: 0.8rem 0.75rem 2rem;
      }}
      h1 {{ font-size: 1.7rem; }}
      h2 {{ font-size: 1.4rem; }}
      h3 {{ font-size: 1.18rem; }}
      [data-testid="stMetric"] {{
        padding: 0.7rem;
        border-radius: 9px;
      }}
      [data-testid="stTabs"] [data-baseweb="tab-list"] {{
        overflow-x: auto;
        flex-wrap: nowrap;
        scrollbar-width: thin;
      }}
      [data-testid="stTabs"] [role="tab"] {{
        flex: 0 0 auto;
        padding-left: 0.65rem;
        padding-right: 0.65rem;
      }}
      [data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap;
        gap: 0.65rem;
      }}
      [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
        min-width: min(100%, 220px);
        flex: 1 1 220px;
      }}
      .stButton > button, .stDownloadButton > button,
      [data-testid="stLinkButton"] a {{
        width: 100%;
      }}
    }}
    @media (min-width: 768px) and (max-width: 1023px) {{
      .block-container {{
        padding-left: 1.25rem;
        padding-right: 1.25rem;
      }}
    }}
    </style>
    """


def apply_theme(theme="light"):
    """Inject the selected theme once per Streamlit rerun."""
    st.markdown(get_theme_css(theme), unsafe_allow_html=True)
