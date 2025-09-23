from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union
from functools import lru_cache
import os


try:
    from .assets import get_image_b64
except ImportError:
    def get_image_b64(filename: str) -> Optional[str]:
        \
        return None

@dataclass(frozen=True)
class Settings:
    \
    APP_TITLE: str = "SCALAR"
    APP_SUBTITLE: str = "Advanced Treasury & Risk Analytics"


    def __post_init__(self):
        object.__setattr__(self, '_page_icon', None)

    @property
    def PAGE_ICON(self) -> str:
        \
        if self._page_icon is None:
            icon = get_image_b64("logo.png") if get_image_b64 else None
            object.__setattr__(self, '_page_icon', icon or "💎")
        return self._page_icon

    MAX_FILE_SIZE_MB: int = 10
    MAX_ROWS_PER_SHEET: int = 10_000


    LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "collapsed"


    DEFAULT_VAR_LIMIT: float = 1_000_000
    DEFAULT_MAX_NOTIONAL_PER_PAIR: float = 500_000_000
    DEFAULT_MAX_TENOR_CONCENTRATION: float = 0.40


    CACHE_TTL_SECONDS: int = 3600
    MAX_CACHE_SIZE: int = 128
    ENABLE_ANIMATIONS: bool = True


settings = Settings()


@lru_cache(maxsize=16)
def get_cached_image_b64(filename: str) -> Optional[str]:
    \
    return get_image_b64(filename) if get_image_b64 else None


background_image_b64 = get_cached_image_b64("background.png")


class ColorScheme:
\


    VIRIDIS = {
        'deep_purple': '#440154',
        'purple': '#482878',
        'blue_purple': '#3e4989',
        'blue': '#31688e',
        'teal': '#277f8e',
        'cyan': '#1f9e89',
        'green': '#35b779',
        'lime': '#6ece58',
        'yellow_green': '#b5de2b',
        'yellow': '#fde725',
    }


    GLASS = {
        'white': 'rgba(255, 255, 255, 0.05)',
        'border': 'rgba(255, 255, 255, 0.1)',
        'hover': 'rgba(255, 255, 255, 0.08)',
        'shadow': 'rgba(68, 1, 84, 0.2)',
    }


    BASE = {
        'background': '#0a0e1a',
        'surface': 'rgba(20, 25, 40, 0.6)',
        'surface_solid': '#141928',
        'text_primary': '#ffffff',
        'text_secondary': 'rgba(255, 255, 255, 0.7)',
        'text_muted': 'rgba(255, 255, 255, 0.5)'
    }


    MAIN = {
        'primary': '#1f968b',
        'secondary': '#35b779',
        'accent': '#29B6F6',
        'dark': '#440154',
        'light': '#ffffff',
        'glass_bg': 'rgba(255, 255, 255, 0.05)',
        'glass_border': 'rgba(255, 255, 255, 0.2)',
        'glass_hover': 'rgba(255, 255, 255, 0.1)',
        'success': '#35b779',
        'warning': '#fde725',
        'error': '#e74c3c',
        'info': '#3498db',
        'text_primary': '#ffffff',
        'text_secondary': 'rgba(255, 255, 255, 0.85)',
        'text_muted': 'rgba(255, 255, 255, 0.7)',
        'shadow': 'rgba(0, 0, 0, 0.25)'
    }


colors = ColorScheme()


VIRIDIS_COLORS = colors.VIRIDIS | colors.GLASS | colors.BASE
COLORS = colors.MAIN


class CSSGenerator:
\

    @staticmethod
    @lru_cache(maxsize=4)
    def get_css_variables(theme: str = 'liquid') -> str:
        \
        if theme == 'liquid':
            vars_dict = colors.MAIN
        else:
            vars_dict = {
                'primary': '#2563eb',
                'secondary': '#64748b',
                'accent': '#0ea5e9',
                'dark': '#0f172a',
                'light': '#ffffff',
                'bg_primary': '#0f172a',
                'bg_secondary': '#1e293b',
                'bg_tertiary': '#334155',
                'text_primary': '#f8fafc',
                'text_secondary': '#cbd5e1',
                'text_muted': '#94a3b8',
                'border': '#334155',
                'border_light': '#475569',
            }

        css_vars = "\n".join([f"    --{key.replace('_', '-')}: {value};" for key, value in vars_dict.items()])

        return f"""
:root {{
{css_vars}
    --radius: {'18px' if theme == 'liquid' else '8px'};
    --blur: 16px;
    --transition: {'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)' if theme == 'liquid' else 'all 0.2s ease'};
    --shadow-color: rgba(0, 0, 0, 0.15);
    --shadow-elevation-low: 0 2px 10px var(--shadow-color);
    --shadow-elevation-medium: 0 8px 24px var(--shadow-color);
    --shadow-elevation-high: 0 16px 48px var(--shadow-color);
}}"""

    @staticmethod
    @lru_cache(maxsize=2)
    def get_base_styles() -> str:
        \
        return """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Animations optimisées */
@keyframes text-gradient-animation {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

@keyframes fade-in-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes shimmer-effect {
    0% { transform: translateX(-100%) skewX(-25deg); }
    100% { transform: translateX(200%) skewX(-25deg); }
}

/* Reset optimisé */
*, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Amélioration lisibilité */
h1, h2, h3, p, div, span, .stMarkdown {
    text-shadow: 0 1px 3px rgba(0,0,0,0.2);
}"""


@lru_cache(maxsize=2)
def get_optimized_css(theme: str = 'liquid_glass') -> str:
\

    base_styles = CSSGenerator.get_base_styles()
    css_vars = CSSGenerator.get_css_variables('liquid' if theme == 'liquid_glass' else 'professional')

    if theme == 'liquid_glass':
        bg_image = f'background-image: url("{background_image_b64}");' if background_image_b64 else ''

        theme_specific = f"""
.stApp {{
    {bg_image}
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    font-family: 'Inter', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: var(--text-primary);
}}

.stApp::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 50%, var(--accent) 100%);
    opacity: 0.75;
    z-index: -2;
}}

/* Force texte blanc (haute lisibilité en mode liquid glass) */
.stApp, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp p, .stApp span, .stApp label, .stApp li, .stApp a, .stApp code, .stApp pre, .stApp small, .stApp strong, .stApp em {{
    color: var(--text-primary) !important;
}}
.stApp .stMarkdown, .stApp .stText, .stApp .stDataFrame, .stApp .stCaption, .stApp .stAlert {{
    color: var(--text-primary) !important;
}}

/* Header compact optimisé */
.liquid-header {{
    position: relative;
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur));
    border-radius: var(--radius);
    padding: 0.25rem 0.75rem;
    margin-bottom: 0.125rem;
    text-align: center;
    overflow: hidden;
    transition: var(--transition);
    box-shadow: var(--shadow-elevation-medium), inset 0 0 0 1px var(--glass-border);
}}

.liquid-header::after {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 50%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
    animation: shimmer-effect 4s ease-in-out infinite;
    animation-delay: 1.5s;
}}

.liquid-header h1 {{
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(90deg, var(--accent), var(--light), var(--secondary), var(--accent));
    background-size: 400% 400%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: text-gradient-animation 10s ease infinite;
    margin-bottom: 0.0625rem;
}}

.liquid-header p {{
    color: var(--text-secondary);
    font-size: 0.9rem;
    animation: fade-in-up 0.8s ease-out 0.3s forwards;
    opacity: 0;
}}

.liquid-header .author {{
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0.125rem;
    animation: fade-in-up 0.8s ease-out 0.6s forwards;
    opacity: 0;
}}

/* Glass components */
.glass-card {{
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur));
    -webkit-backdrop-filter: blur(var(--blur));
    border-radius: var(--radius);
    padding: 2rem;
    margin: 1rem 0;
    transition: var(--transition);
    box-shadow: var(--shadow-elevation-low), inset 0 0 0 1px var(--glass-border);
}}

.metric-card {{
    position: relative;
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur));
    border-radius: var(--radius);
    padding: 2rem;
    text-align: center;
    transition: var(--transition);
    box-shadow: var(--shadow-elevation-low), inset 0 0 0 1px var(--glass-border);
    overflow: hidden;
}}

.metric-value {{
    font-size: 3rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.5rem;
}}

.metric-label {{
    font-size: 1rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}

/* Alertes */
.alert {{
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur));
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
    border-left: 5px solid;
    box-shadow: var(--shadow-elevation-low), inset 0 0 0 1px var(--glass-border);
}}

.alert-success {{ border-left-color: var(--success); }}
.alert-warning {{ border-left-color: var(--warning); }}
.alert-error {{ border-left-color: var(--error); }}
.alert-info {{ border-left-color: var(--info); }}

/* Status badges */
.status-badge {{
    display: inline-block;
    padding: 0.5em 1em;
    font-size: 0.85rem;
    font-weight: 600;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 2em;
    color: var(--dark);
}}

.status-badge-success {{ background-color: var(--success); }}
.status-badge-warning {{ background-color: var(--warning); }}
.status-badge-error {{ background-color: var(--error); color: var(--light); }}
.status-badge-info {{ background-color: var(--info); }}"""

    else:
        theme_specific = """
.stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

.professional-header {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.25rem 0.5rem;
    margin-bottom: 0.125rem;
    text-align: center;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.professional-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.03125rem;
}

.professional-header p {
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin-bottom: 0;
}

.professional-header .author {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.125rem;
}

.professional-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin: 1rem 0;
    transition: var(--transition);
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.professional-metric {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    text-align: center;
    transition: var(--transition);
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.professional-metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 0.5rem;
}

.professional-metric-label {
    font-size: 0.9rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 500;
}

.professional-alert {
    background: var(--bg-secondary);
    border: 1px solid;
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin: 1rem 0;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.professional-alert-success { border-color: #22c55e; }
.professional-alert-warning { border-color: #eab308; }
.professional-alert-error { border-color: #ef4444; }
.professional-alert-info { border-color: var(--primary); }

.professional-badge {
    display: inline-block;
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
    font-weight: 500;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    border-radius: calc(var(--radius) / 2);
    border: 1px solid transparent;
}

.professional-badge-success { background-color: #22c55e; color: white; }
.professional-badge-warning { background-color: #eab308; color: #0f172a; }
.professional-badge-error { background-color: #ef4444; color: white; }
.professional-badge-info { background-color: var(--primary); color: white; }"""

    return f"<style>\n{base_styles}\n{css_vars}\n{theme_specific}\n</style>"


CSS_STYLES = get_optimized_css('liquid_glass')
PROFESSIONAL_DARK_CSS = get_optimized_css('professional_dark')


@dataclass(frozen=True)
class ThemeConfig:
    \
    name: str
    description: str
    background_image: bool
    glass_effects: bool
    performance_mode: bool = False

    def get(self, key: str, default=None):
        \
        return getattr(self, key, default)

    def __getitem__(self, key: str):
        \
        return getattr(self, key)

    def __contains__(self, key: str) -> bool:
        \
        return hasattr(self, key)

    def keys(self):
        \
        return ['name', 'description', 'background_image', 'glass_effects', 'performance_mode']

    def items(self):
        \
        return [(key, getattr(self, key)) for key in self.keys()]

    def to_dict(self) -> Dict[str, Any]:
        \
        return {
            'name': self.name,
            'description': self.description,
            'background_image': self.background_image,
            'glass_effects': self.glass_effects,
            'performance_mode': self.performance_mode
        }


THEME_CONFIGS = {
    'liquid_glass': ThemeConfig(
        name='Liquid Glass',
        description='Modern glass effect with background image',
        background_image=True,
        glass_effects=True
    ),
    'professional_dark': ThemeConfig(
        name='Professional Dark',
        description='Clean minimal dark theme',
        background_image=False,
        glass_effects=False,
        performance_mode=True
    )
}


class UIConfig:
\

    @staticmethod
    @lru_cache(maxsize=1)
    def get_page_config() -> Dict[str, Any]:
        \
        return {
            "page_title": settings.APP_TITLE,
            "page_icon": settings.PAGE_ICON,
            "layout": settings.LAYOUT,
            "initial_sidebar_state": settings.INITIAL_SIDEBAR_STATE
        }

    @staticmethod
    @lru_cache(maxsize=2)
    def get_theme_css(theme_name: str = 'liquid_glass') -> str:
        \
        return get_optimized_css(theme_name)

    @staticmethod
    @lru_cache(maxsize=2)
    def get_header_html(theme_name: str = 'liquid_glass') -> str:
        \
        header_class = "professional-header" if theme_name == 'professional_dark' else "liquid-header"

        return f"""
        <div class="{header_class}">
            <h1>{settings.APP_TITLE}</h1>
            <p>{settings.APP_SUBTITLE}</p>
            <p class="author">by Côme ROQUES</p>
        </div>
        """

    @staticmethod
    def get_metric_card_html(title: str, value: str, delta: Optional[str] = None,
                            delta_color: str = "normal", theme_name: str = 'liquid_glass') -> str:
        \
        is_professional = theme_name == 'professional_dark'

        card_class = "professional-metric" if is_professional else "metric-card"
        value_class = "professional-metric-value" if is_professional else "metric-value"
        label_class = "professional-metric-label" if is_professional else "metric-label"

        delta_html = f'<div style="font-size: 0.9rem; margin-top: 0.5rem; color: var(--text-secondary);">{delta}</div>' if delta else ""

        return f"""
        <div class="{card_class}">
            <div class="{value_class}">{value}</div>
            <div class="{label_class}">{title}</div>
            {delta_html}
        </div>
        """

    @staticmethod
    def get_alert_html(alert_type: str, title: str, message: str = "", theme_name: str = 'liquid_glass') -> str:
        \
        alert_class = f"professional-alert professional-alert-{alert_type}" if theme_name == 'professional_dark' else f"alert alert-{alert_type}"

        return f"""
        <div class="{alert_class}">
            <strong style="color: var(--text-primary);">{title}</strong>
            {f"<div style='margin-top: 0.5rem; color: var(--text-secondary);'>{message}</div>" if message else ""}
        </div>
        """

    @staticmethod
    def get_card_html(content: str, title: str = None, theme_name: str = 'liquid_glass') -> str:
        \
        title_html = f"<h3 style='color: var(--text-primary); margin-bottom: 1rem;'>{title}</h3>" if title else ""
        card_class = "professional-card" if theme_name == 'professional_dark' else "glass-card"

        return f"""
        <div class="{card_class}">
            {title_html}
            {content}
        </div>
        """

    @staticmethod
    def get_status_badge_html(status: str, text: str, theme_name: str = 'liquid_glass') -> str:
        \
        if theme_name == 'professional_dark':
            return f'<span class="professional-badge professional-badge-{status}">{text}</span>'
        else:
            return f'<span class="status-badge status-badge-{status}">{text}</span>'

    @staticmethod
    def get_kpi_grid_html(kpis: List[Dict[str, Any]]) -> str:
        cards = ""
        for kpi in kpis:
            cards += f"""
            <div class="metric-card">
                <div class="metric-value">{kpi['value']}</div>
                <div class="metric-label">{kpi['title']}</div>
            </div>
            """
        return f'<div class="kpi-grid">{cards}</div>'

    @staticmethod
    def get_main_header_html() -> str:
        \
        return UIConfig.get_header_html()

    @staticmethod
    def get_loading_html(message: str = "Processing...") -> str:
        \
        return f"""
        <div style="text-align: center; padding: 3rem;">
            <div style="color: var(--accent); font-size: 1.2rem; margin-bottom: 1rem;">
                ⚡ Processing...
            </div>
            <div style="color: var(--text-secondary);">{message}</div>
        </div>
        """

    @staticmethod
    def get_section_divider_html(title: Optional[str] = None) -> str:
        \
        if title:
            return f"""
            <div style="text-align: center; margin: 2rem 0;">
                <span style="color: var(--text-secondary); padding: 0 1rem; background: var(--glass-bg); border-radius: 10px;">
                    {title}
                </span>
            </div>
            """
        return '<div style="height: 1px; background: var(--glass-border); margin: 2rem 0;"></div>'

    @staticmethod
    def get_info_panel_html(title: str, content: str, icon: str = "ℹ") -> str:
        \
        return f"""
        <div class="glass-card">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 1.2rem;">{icon}</span>
                <h4 style="margin: 0; color: var(--text-primary);">{title}</h4>
            </div>
            <div style="color: var(--text-secondary);">{content}</div>
        </div>
        """

    @staticmethod
    def get_progress_bar_html(value: float, max_value: float = 100, label: str = "",
                             color_scheme: str = "default") -> str:
        \
        percentage = (value / max_value) * 100
        return f"""
        <div style="margin: 1rem 0;">
            {f'<div style="color: var(--text-secondary); margin-bottom: 0.5rem;">{label}</div>' if label else ''}
            <div style="background: var(--glass-bg); border-radius: 10px; padding: 2px; overflow: hidden;">
                <div style="width: {percentage}%; height: 8px; background: var(--accent); border-radius: 8px; transition: width 0.6s ease;"></div>
            </div>
        </div>
        """

    @staticmethod
    def get_tooltip_html(content: str, tooltip_text: str) -> str:
        \
        return f'<span title="{tooltip_text}" style="cursor: help; text-decoration: underline dotted;">{content}</span>'


@dataclass
class SessionConfig:
    \
    generic_deals: List = None
    df_pnl_enhanced: Any = None
    pnl_config: Dict[str, Any] = None
    risk_limits: Dict[str, float] = None
    ui_theme: str = 'liquid_glass'
    animations_enabled: bool = True

    def __post_init__(self):
        if self.generic_deals is None:
            self.generic_deals = []
        if self.pnl_config is None:
            self.pnl_config = {
                'calculate_accrued': True,
                'calculate_mtm': True,
                'calculate_rate': True,
                'calculate_liquidity': True,
                'ois_rate_override': None,
            }
        if self.risk_limits is None:
            self.risk_limits = {
                'max_notional_per_pair': settings.DEFAULT_MAX_NOTIONAL_PER_PAIR,
                'max_tenor_concentration': settings.DEFAULT_MAX_TENOR_CONCENTRATION,
                'var_limit': settings.DEFAULT_VAR_LIMIT
            }


DEFAULT_SESSION_STATE = SessionConfig().__dict__


ALLOWED_EXTENSIONS = (".xlsx", ".xls")


STREAMLIT_THEME = {
    'primaryColor': colors.MAIN['primary'],
    'backgroundColor': colors.MAIN['dark'],
    'secondaryBackgroundColor': colors.MAIN['glass_bg'],
    'textColor': colors.MAIN['text_primary'],
    'font': 'Inter'
}


PLOTLY_CONFIG = {
    'theme': 'plotly_dark',
    'color_palette': [
        colors.MAIN['primary'],
        colors.MAIN['secondary'],
        colors.MAIN['accent'],
        colors.MAIN['dark'],
        colors.MAIN['success'],
        colors.MAIN['warning']
    ],
    'font_color': colors.MAIN['text_primary'],
    'background_color': colors.MAIN['glass_bg'],
    'font_family': 'Inter',
    'responsive': True,
    'displayModeBar': False
}

# New: global Plotly defaults for liquid_glass
def _apply_plotly_liquid_defaults() -> None:
    try:
        import plotly.io as pio
        import plotly.graph_objects as go
        import plotly.express as px

        base = pio.templates.get('plotly_dark')
        overlay = go.layout.Template(
            layout=go.Layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=PLOTLY_CONFIG['font_color'], family=PLOTLY_CONFIG['font_family']),
                legend=dict(font=dict(color=PLOTLY_CONFIG['font_color'])),
                xaxis=dict(
                    titlefont=dict(color=PLOTLY_CONFIG['font_color']),
                    tickfont=dict(color=PLOTLY_CONFIG['font_color']),
                    gridcolor='rgba(255,255,255,0.2)',
                    zerolinecolor='rgba(255,255,255,0.3)',
                    linecolor='rgba(255,255,255,0.6)'
                ),
                yaxis=dict(
                    titlefont=dict(color=PLOTLY_CONFIG['font_color']),
                    tickfont=dict(color=PLOTLY_CONFIG['font_color']),
                    gridcolor='rgba(255,255,255,0.2)',
                    zerolinecolor='rgba(255,255,255,0.3)',
                    linecolor='rgba(255,255,255,0.6)'
                )
            )
        )
        pio.templates['liquid_glass_dark'] = base + overlay
        pio.templates.default = 'liquid_glass_dark'
        px.defaults.template = 'liquid_glass_dark'
        px.defaults.color_discrete_sequence = PLOTLY_CONFIG['color_palette']
    except Exception:
        pass

# Apply at import so all figures inherit styling
_apply_plotly_liquid_defaults()


def initialize_session_state() -> None:
    \
    import streamlit as st

    for key, value in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value

def apply_liquid_theme() -> None:
    \
    import streamlit as st


    st.markdown(get_optimized_css('liquid_glass'), unsafe_allow_html=True)


    page_config = UIConfig.get_page_config()


    initialize_session_state()

def create_liquid_alert(alert_type: str, title: str, message: str = "") -> str:
    \
    return UIConfig.get_alert_html(alert_type, title, message)

def create_liquid_card(content: str, title: Optional[str] = None) -> str:
    \
    return UIConfig.get_card_html(content, title)


@lru_cache(maxsize=settings.MAX_CACHE_SIZE)
def get_theme_config(theme_name: str = 'liquid_glass') -> Dict[str, Any]:
    \
    return {
        'name': theme_name,
        'colors': colors.MAIN,
        'viridis_colors': colors.VIRIDIS,
        'css': get_optimized_css(theme_name),
        'plotly': PLOTLY_CONFIG,
        'ui_config': UIConfig
    }

@lru_cache(maxsize=8)
def create_liquid_metric(title: str, value: str, delta: Optional[str] = None,
                        delta_color: str = "normal", theme: str = 'liquid_glass') -> str:
    \
    return UIConfig.get_metric_card_html(title, value, delta, delta_color, theme)


class OptimizedThemeManager:
\

    def __init__(self):
        self._current_theme = 'liquid_glass'
        self._config_cache = {}

    @property
    def current_theme(self) -> str:
        return self._current_theme

    @current_theme.setter
    def current_theme(self, theme: str):
        if theme not in THEME_CONFIGS:
            raise ValueError(f"Thème non supporté: {theme}")
        self._current_theme = theme
        self._config_cache.clear()

    @lru_cache(maxsize=16)
    def get_color(self, color_name: str) -> str:
        \
        return colors.MAIN.get(color_name, colors.MAIN['text_primary'])

    def create_component(self, component_type: str, **kwargs) -> str:
        \
        if component_type not in ['metric', 'alert', 'card', 'loading', 'badge']:
            raise ValueError(f"Type de composant non supporté: {component_type}")


        cache_key = f"{component_type}_{hash(str(sorted(kwargs.items())))}"

        if cache_key not in self._config_cache:
            method_map = {
                'metric': UIConfig.get_metric_card_html,
                'alert': UIConfig.get_alert_html,
                'card': UIConfig.get_card_html,
                'loading': UIConfig.get_loading_html,
                'badge': UIConfig.get_status_badge_html,
            }
            self._config_cache[cache_key] = method_map[component_type](**kwargs)

        return self._config_cache[cache_key]


theme_manager = OptimizedThemeManager()


@lru_cache(maxsize=1)
def validate_config() -> bool:
    \
    required = ['primary', 'secondary', 'accent', 'text_primary']
    missing = [color for color in required if color not in colors.MAIN]

    if missing:
        raise ValueError(f"Couleurs manquantes: {', '.join(missing)}")


    for theme_name, theme_config in THEME_CONFIGS.items():
        if not isinstance(theme_config, ThemeConfig):
            raise ValueError(f"Configuration thème invalide: {theme_name}")

    return True


class PerformanceMonitor:
\

    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        \
        return {
            'get_optimized_css': get_optimized_css.cache_info(),
            'get_theme_config': get_theme_config.cache_info(),
            'validate_config': validate_config.cache_info(),
            'ui_page_config': UIConfig.get_page_config.cache_info(),
            'ui_theme_css': UIConfig.get_theme_css.cache_info(),
            'ui_header_html': UIConfig.get_header_html.cache_info(),
        }

    @staticmethod
    def clear_all_caches():
        \
        caches = [
            get_optimized_css, get_theme_config, validate_config,
            UIConfig.get_page_config, UIConfig.get_theme_css, UIConfig.get_header_html
        ]
        for cache_func in caches:
            cache_func.cache_clear()


@lru_cache(maxsize=2)
def get_complete_css(theme: str = 'liquid_glass') -> str:
\

    base_styles = CSSGenerator.get_base_styles()
    css_vars = CSSGenerator.get_css_variables('liquid' if theme == 'liquid_glass' else 'professional')

    if theme == 'liquid_glass':
        bg_image = f'background-image: url("{background_image_b64}");' if background_image_b64 else ''

        theme_specific = f"""
.stApp {{
    {bg_image}
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    font-family: 'Inter', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: var(--text-primary);
}}

.stApp::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 50%, var(--accent) 100%);
    opacity: 0.75;
    z-index: -2;
}}

/* Force texte blanc (haute lisibilité en mode liquid glass) */
.stApp, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp p, .stApp span, .stApp label, .stApp li, .stApp a, .stApp code, .stApp pre, .stApp small, .stApp strong, .stApp em {{
    color: var(--text-primary) !important;
}}
.stApp .stMarkdown, .stApp .stText, .stApp .stDataFrame, .stApp .stCaption, .stApp .stAlert {{
    color: var(--text-primary) !important;
}}

/* Header compact optimisé */
.liquid-header {{
    position: relative;
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur));
    border-radius: var(--radius);
    padding: 0.25rem 0.75rem;
    margin-bottom: 0.125rem;
    text-align: center;
    overflow: hidden;
    transition: var(--transition);
    box-shadow: var(--shadow-elevation-medium), inset 0 0 0 1px var(--glass-border);
}}

.liquid-header::after {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 50%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
    animation: shimmer-effect 4s ease-in-out infinite;
    animation-delay: 1.5s;
}}

.liquid-header h1 {{
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(90deg, var(--accent), var(--light), var(--secondary), var(--accent));
    background-size: 400% 400%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: text-gradient-animation 10s ease infinite;
    margin-bottom: 0.0625rem;
}}

.liquid-header p {{
    color: var(--text-secondary);
    font-size: 0.9rem;
    animation: fade-in-up 0.8s ease-out 0.3s forwards;
    opacity: 0;
}}

.liquid-header .author {{
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0.125rem;
    animation: fade-in-up 0.8s ease-out 0.6s forwards;
    opacity: 0;
}}

/* Glass components */
.glass-card {{
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur));
    -webkit-backdrop-filter: blur(var(--blur));
    border-radius: var(--radius);
    padding: 2rem;
    margin: 1rem 0;
    transition: var(--transition);
    box-shadow: var(--shadow-elevation-low), inset 0 0 0 1px var(--glass-border);
}}

.metric-card {{
    position: relative;
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur));
    border-radius: var(--radius);
    padding: 2rem;
    text-align: center;
    transition: var(--transition);
    box-shadow: var(--shadow-elevation-low), inset 0 0 0 1px var(--glass-border);
    overflow: hidden;
}}

.metric-value {{
    font-size: 3rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.5rem;
}}

.metric-label {{
    font-size: 1rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}

/* Alertes */
.alert {{
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur));
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
    border-left: 5px solid;
    box-shadow: var(--shadow-elevation-low), inset 0 0 0 1px var(--glass-border);
}}

.alert-success {{ border-left-color: var(--success); }}
.alert-warning {{ border-left-color: var(--warning); }}
.alert-error {{ border-left-color: var(--error); }}
.alert-info {{ border-left-color: var(--info); }}

/* Status badges */
.status-badge {{
    display: inline-block;
    padding: 0.5em 1em;
    font-size: 0.85rem;
    font-weight: 600;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 2em;
    color: var(--dark);
}}

.status-badge-success {{ background-color: var(--success); }}
.status-badge-warning {{ background-color: var(--warning); }}
.status-badge-error {{ background-color: var(--error); color: var(--light); }}
.status-badge-info {{ background-color: var(--info); }}"""

    else:
        theme_specific = """
.stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

.professional-header {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.25rem 0.5rem;
    margin-bottom: 0.125rem;
    text-align: center;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.professional-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.03125rem;
}

.professional-header p {
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin-bottom: 0;
}

.professional-header .author {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.125rem;
}

.professional-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin: 1rem 0;
    transition: var(--transition);
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.professional-metric {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    text-align: center;
    transition: var(--transition);
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.professional-metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 0.5rem;
}

.professional-metric-label {
    font-size: 0.9rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 500;
}

.professional-alert {
    background: var(--bg-secondary);
    border: 1px solid;
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin: 1rem 0;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.professional-alert-success { border-color: #22c55e; }
.professional-alert-warning { border-color: #eab308; }
.professional-alert-error { border-color: #ef4444; }
.professional-alert-info { border-color: var(--primary); }

.professional-badge {
    display: inline-block;
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
    font-weight: 500;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    border-radius: calc(var(--radius) / 2);
    border: 1px solid transparent;
}

.professional-badge-success { background-color: #22c55e; color: white; }
.professional-badge-warning { background-color: #eab308; color: #0f172a; }
.professional-badge-error { background-color: #ef4444; color: white; }
.professional-badge-info { background-color: var(--primary); color: white; }"""

    return f"<style>\n{base_styles}\n{css_vars}\n{theme_specific}\n</style>"


CSS_STYLES = get_complete_css('liquid_glass')
PROFESSIONAL_DARK_CSS = get_complete_css('professional_dark')

get_optimized_css = get_complete_css


validate_config()