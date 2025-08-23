from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from .assets import get_image_b64


@dataclass(frozen=True)
class Settings:
    """Configuration principale de l'application"""
    APP_TITLE: str = "SCALAR"
    APP_SUBTITLE: str = "Advanced Treasury & Risk Analytics"
    PAGE_ICON: str = get_image_b64("logo.png") or "💎"
    MAX_FILE_SIZE_MB: int = 10
    MAX_ROWS_PER_SHEET: int = 10_000
    
    # Configuration Streamlit
    LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "collapsed"
    
    # Limites par défaut
    DEFAULT_VAR_LIMIT: float = 1_000_000
    DEFAULT_MAX_NOTIONAL_PER_PAIR: float = 500_000_000
    DEFAULT_MAX_TENOR_CONCENTRATION: float = 0.40


# Instance globale des settings
settings = Settings()

# Charge l'image de fond en base64
# Assurez-vous d'avoir un fichier 'background.png' dans static/images/
background_image_b64 = get_image_b64("background.png")

# Palette de couleurs améliorée par le designer
COLORS = {
    # Couleurs de base (Viridis)
    'primary': '#1f968b',      # Teal
    'secondary': '#35b779',    # Vert
    'accent': '#29B6F6',       # Bleu électrique
    'dark': '#440154',         # Violet profond
    'light': '#ffffff',
    
    # Effet Glass affiné
    'glass_bg': 'rgba(255, 255, 255, 0.05)',
    'glass_border': 'rgba(255, 255, 255, 0.2)',
    'glass_hover': 'rgba(255, 255, 255, 0.1)',
    
    # Couleurs sémantiques
    'success': '#35b779',
    'warning': '#fde725',
    'error': '#e74c3c', # Rouge plus doux
    'info': '#3498db',  # Bleu clair
    
    # Typographie
    'text_primary': 'rgba(255, 255, 255, 0.95)',
    'text_secondary': 'rgba(255, 255, 255, 0.7)',
    'text_muted': 'rgba(255, 255, 255, 0.5)',
    
    # Ombres
    'shadow': 'rgba(0, 0, 0, 0.25)'
}


# CSS de niveau "Apple Liquid Glass"
CSS_STYLES = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Animations & Keyframes */
@keyframes text-gradient-animation {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

@keyframes fade-in-up {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes shimmer-effect {{
    0% {{ transform: translateX(-100%) skewX(-25deg); }}
    100% {{ transform: translateX(200%) skewX(-25deg); }}
}}

/* Variables CSS pour un design system cohérent */
:root {{
    --primary: {COLORS['primary']};
    --secondary: {COLORS['secondary']};
    --accent: {COLORS['accent']};
    --dark: {COLORS['dark']};
    --light: {COLORS['light']};
    
    --glass-bg: {COLORS['glass_bg']};
    --glass-border: {COLORS['glass_border']};
    --glass-hover: {COLORS['glass_hover']};
    
    --text-primary: {COLORS['text_primary']};
    --text-secondary: {COLORS['text_secondary']};
    --text-muted: {COLORS['text_muted']};
    
    --radius: 18px; /* Rayon plus arrondi, style Apple */
    --blur: 16px;   /* Flou subtil */
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); /* Transition fluide */
    
    --shadow-color: rgba(0, 0, 0, 0.15);
    --shadow-elevation-low: 0 2px 10px var(--shadow-color);
    --shadow-elevation-medium: 0 8px 24px var(--shadow-color);
    --shadow-elevation-high: 0 16px 48px var(--shadow-color);
}}

/* Reset et styles globaux */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

.stApp {{
    background-image: url("{background_image_b64}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    font-family: 'Inter', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

.stApp::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, {COLORS['dark']} 0%, {COLORS['primary']} 50%, {COLORS['accent']} 100%);
    opacity: 0.75;
    z-index: -2;
}}

/* Amélioration de la lisibilité du texte */
h1, h2, h3, p, div, span, .stMarkdown {{
    text-shadow: 0 1px 3px rgba(0,0,0,0.2);
}}

/* Composant "Glass Card" amélioré */
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

.glass-card:hover {{
    background: var(--glass-hover);
    transform: translateY(-4px) scale(1.01);
    box-shadow: var(--shadow-elevation-medium), inset 0 0 0 1px var(--glass-border);
}}

/* Header Premium */
.liquid-header {{
    position: relative;
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur));
    border-radius: var(--radius);
    padding: 4rem 2rem;
    margin-bottom: 2rem;
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
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, var(--accent), var(--light), var(--secondary), var(--accent));
    background-size: 400% 400%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: text-gradient-animation 10s ease infinite;
    margin-bottom: 0.75rem;
}}

.liquid-header p {{
    color: var(--text-secondary);
    font-size: 1.2rem;
    animation: fade-in-up 0.8s ease-out 0.3s forwards;
    opacity: 0;
}}

.liquid-header .author {{
    font-size: 1rem;
    color: var(--text-muted);
    margin-top: 1.5rem;
    animation: fade-in-up 0.8s ease-out 0.6s forwards;
    opacity: 0;
}}

/* Cartes Métriques "Apple-like" */
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

.metric-card:hover {{
    transform: translateY(-6px) scale(1.03);
    box-shadow: var(--shadow-elevation-high), inset 0 0 0 1px var(--glass-border);
}}

.metric-card:hover::before {{
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 40%);
    transform: scale(0);
    animation: pulse 1s ease-out;
}}

@keyframes pulse {{
    from {{ transform: scale(0); opacity: 1; }}
    to {{ transform: scale(1); opacity: 0; }}
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

/* Grille de KPIs */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}}

/* Alertes stylisées */
.alert {{
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur));
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
    border-left: 5px solid;
    box-shadow: var(--shadow-elevation-low), inset 0 0 0 1px var(--glass-border);
}}

.alert-success {{ border-left-color: {COLORS['success']}; }}
.alert-warning {{ border-left-color: {COLORS['warning']}; }}
.alert-error {{ border-left-color: {COLORS['error']}; }}
.alert-info {{ border-left-color: {COLORS['info']}; }}

/* Badges de statut */
.status-badge {{
    display: inline-block;
    padding: 0.5em 1em;
    font-size: 0.85rem;
    font-weight: 600;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 2em; /* Pill shape */
    color: var(--dark);
}}

.status-badge-success {{ background-color: {COLORS['success']}; }}
.status-badge-warning {{ background-color: {COLORS['warning']}; }}
.status-badge-error {{ background-color: {COLORS['error']}; color: var(--light); }}
.status-badge-info {{ background-color: {COLORS['info']}; }}
.status-badge-ok {{ background-color: {COLORS['secondary']}; }}

/* Améliorations des composants Streamlit natifs */
.stButton > button {{
    border-radius: var(--radius) !important;
    transition: var(--transition) !important;
    background: var(--glass-bg) !important;
    backdrop-filter: blur(var(--blur)) !important;
    box-shadow: var(--shadow-elevation-low) !important;
    border: 1px solid var(--glass-border) !important;
}}

.stButton > button:hover {{
    background: var(--glass-hover) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-elevation-medium) !important;
}}

.stTextInput > div > div > input {{
    border-radius: var(--radius) !important;
    transition: var(--transition) !important;
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
}}

.stTextInput > div > div > input:focus {{
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px var(--primary) !important;
}}

/* Responsive Design */
@media (max-width: 768px) {{
    .liquid-header h1 {{ font-size: 2.5rem; }}
    .liquid-header {{ padding: 3rem 1.5rem; }}
    .kpi-grid {{ grid-template-columns: 1fr; }}
    .glass-card, .metric-card {{ padding: 1.5rem; }}
}}
</style>
"""


class UIConfig:
    """Configuration UI pour un style "Apple Liquid Glass" premium."""
    
    @staticmethod
    def get_page_config() -> Dict[str, Any]:
        return {
            "page_title": settings.APP_TITLE,
            "page_icon": settings.PAGE_ICON,
            "layout": settings.LAYOUT,
            "initial_sidebar_state": settings.INITIAL_SIDEBAR_STATE
        }
    
    @staticmethod
    def get_header_html() -> str:
        return f"""
        <div class="liquid-header">
            <h1>{settings.APP_TITLE}</h1>
            <p>{settings.APP_SUBTITLE}</p>
            <p class="author">by Côme ROQUES</p>
        </div>
        """
    
    @staticmethod
    def get_metric_html(title: str, value: str) -> str:
        return f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{title}</div>
        </div>
        """
    
    @staticmethod
    def get_alert_html(alert_type: str, title: str, message: str = "") -> str:
        return f"""
        <div class="alert alert-{alert_type}">
            <strong style="color: var(--text-primary);">{title}</strong>
            {f"<div style='margin-top: 0.5rem; color: var(--text-secondary);'>{message}</div>" if message else ""}
        </div>
        """
    
    @staticmethod
    def get_card_html(content: str, title: str = None) -> str:
        title_html = f"<h3 style='color: var(--text-primary); margin-bottom: 1rem;'>{title}</h3>" if title else ""
        return f"""
        <div class="glass-card">
            {title_html}
            {content}
        </div>
        """
    
    @staticmethod
    def get_status_badge_html(status: str, text: str) -> str:
        """Génère un badge de statut HTML."""
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


# Configuration par défaut simplifiée
DEFAULT_SESSION_STATE = {
    'generic_deals': [],
    'df_pnl_enhanced': None,
    'pnl_config': {
        'calculate_accrued': True,
        'calculate_mtm': True,
        'calculate_rate': True,
        'calculate_liquidity': True,
        'ois_rate_override': None,
    },
    'risk_limits': {
        'max_notional_per_pair': settings.DEFAULT_MAX_NOTIONAL_PER_PAIR,
        'max_tenor_concentration': settings.DEFAULT_MAX_TENOR_CONCENTRATION,
        'var_limit': settings.DEFAULT_VAR_LIMIT
    },
    'ui_theme': 'liquid_glass',
    'animations_enabled': True
}

# Extensions autorisées
ALLOWED_EXTENSIONS = (".xlsx", ".xls")

# Configuration Plotly simplifiée
PLOTLY_CONFIG = {
    'theme': 'plotly_dark',
    'color_palette': [
        COLORS['primary'], COLORS['secondary'], COLORS['accent'], 
        COLORS['dark'], COLORS['success'], COLORS['warning']
    ],
    'font_color': COLORS['text_primary'],
    'background_color': COLORS['glass_bg'],
    'font_family': 'Inter'
}

# Thème Streamlit
STREAMLIT_THEME = {
    'primaryColor': COLORS['primary'],
    'backgroundColor': COLORS['dark'],
    'secondaryBackgroundColor': COLORS['glass_bg'],
    'textColor': COLORS['text_primary'],
    'font': 'Inter'
}

# Validation simple
def validate_config():
    """Valide la configuration"""
    required = ['primary', 'secondary', 'accent', 'text_primary']
    for color in required:
        if color not in COLORS:
            raise ValueError(f"Couleur manquante: {color}")
    return True

validate_config()