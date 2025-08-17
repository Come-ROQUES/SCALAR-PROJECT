"""
Configuration centralisée pour le Treasury Dashboard
Version moderne avec thème Viridis minimaliste
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class Settings:
    """Configuration principale de l'application"""
    APP_TITLE: str = "Treasury Analytics"
    APP_SUBTITLE: str = "Modern Portfolio Management"
    PAGE_ICON: str = "📊"
    MAX_FILE_SIZE_MB: int = 10
    MAX_ROWS_PER_SHEET: int = 10_000
    
    # Configuration Streamlit
    LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "collapsed"  # Plus moderne : sidebar cachée par défaut
    
    # Limites par défaut
    DEFAULT_VAR_LIMIT: float = 1_000_000
    DEFAULT_MAX_NOTIONAL_PER_PAIR: float = 500_000_000
    DEFAULT_MAX_TENOR_CONCENTRATION: float = 0.40


# Instance globale des settings
settings = Settings()


# Palette Viridis pour cohérence visuelle
VIRIDIS_COLORS = {
    'primary': '#440154',      # Violet foncé
    'secondary': '#31688e',    # Bleu-vert foncé
    'accent': '#35b779',       # Vert
    'light': '#fde725',        # Jaune-vert clair
    'dark': '#0d1421',         # Presque noir
    'surface': '#1a1d29',      # Gris très foncé
    'surface_light': '#2a2d3a', # Gris foncé
    'text_primary': '#ffffff',  # Blanc
    'text_secondary': '#b8bcc8', # Gris clair
    'success': '#35b779',
    'warning': '#fde725',
    'error': '#ff6b6b',
    'info': '#31688e'
}


# Configuration CSS moderne et minimaliste
CSS_STYLES = f"""
<style>
/* Variables CSS pour cohérence */
:root {{
    --primary: {VIRIDIS_COLORS['primary']};
    --secondary: {VIRIDIS_COLORS['secondary']};
    --accent: {VIRIDIS_COLORS['accent']};
    --light: {VIRIDIS_COLORS['light']};
    --surface: {VIRIDIS_COLORS['surface']};
    --surface-light: {VIRIDIS_COLORS['surface_light']};
    --text-primary: {VIRIDIS_COLORS['text_primary']};
    --text-secondary: {VIRIDIS_COLORS['text_secondary']};
    --border-radius: 12px;
    --shadow: 0 4px 20px rgba(68, 1, 84, 0.15);
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}

/* Reset et base */
.main > div {{
    padding-top: 2rem;
    padding-bottom: 2rem;
}}

/* Header moderne */
.modern-header {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    padding: 2.5rem 2rem;
    border-radius: var(--border-radius);
    color: var(--text-primary);
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
}}

.modern-header::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--light));
}}

.modern-header h1 {{
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.025em;
}}

.modern-header p {{
    font-size: 1.1rem;
    opacity: 0.9;
    margin: 0;
    font-weight: 300;
}}

/* Cards modernes */
.modern-card {{
    background: var(--surface);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: var(--transition);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}}

.modern-card:hover {{
    transform: translateY(-2px);
    box-shadow: var(--shadow);
    border-color: rgba(255, 255, 255, 0.2);
}}

/* Métriques redesignées */
.metric-modern {{
    background: linear-gradient(135deg, var(--surface) 0%, var(--surface-light) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    text-align: center;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
}}

.metric-modern::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--light));
}}

.metric-modern:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(68, 1, 84, 0.2);
}}

.metric-value {{
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}}

.metric-label {{
    font-size: 0.875rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 500;
}}

/* Alertes modernes */
.alert-modern {{
    border-radius: var(--border-radius);
    padding: 1rem 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid;
    backdrop-filter: blur(10px);
    position: relative;
}}

.alert-success {{
    background: rgba(53, 183, 121, 0.1);
    border-left-color: var(--accent);
    color: var(--accent);
}}

.alert-warning {{
    background: rgba(253, 231, 37, 0.1);
    border-left-color: var(--light);
    color: var(--light);
}}

.alert-error {{
    background: rgba(255, 107, 107, 0.1);
    border-left-color: #ff6b6b;
    color: #ff6b6b;
}}

.alert-info {{
    background: rgba(49, 104, 142, 0.1);
    border-left-color: var(--secondary);
    color: var(--secondary);
}}

/* Boutons modernes */
.btn-modern {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: var(--text-primary);
    border: none;
    border-radius: var(--border-radius);
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: var(--transition);
    box-shadow: 0 2px 8px rgba(68, 1, 84, 0.3);
}}

.btn-modern:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(68, 1, 84, 0.4);
}}

/* Sidebar moderne */
.css-1d391kg {{
    background: var(--surface);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}}

/* Dataframes modernes */
.dataframe {{
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--shadow);
    background: var(--surface);
}}

/* Progress bars */
.stProgress > div > div > div {{
    background: linear-gradient(90deg, var(--accent), var(--light));
    border-radius: 10px;
}}

/* Selectbox et inputs */
.stSelectbox > div > div {{
    background: var(--surface-light);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius);
}}

.stTextInput > div > div > input {{
    background: var(--surface-light);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius);
    color: var(--text-primary);
}}

/* Tabs modernes */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.5rem;
}}

.stTabs [data-baseweb="tab"] {{
    background: var(--surface);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius);
    color: var(--text-secondary);
    padding: 0.75rem 1.5rem;
    transition: var(--transition);
}}

.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-color: var(--accent);
    color: var(--text-primary);
}}

/* Animation de chargement */
@keyframes pulse-viridis {{
    0% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.7; transform: scale(1.02); }}
    100% {{ opacity: 1; transform: scale(1); }}
}}

.loading-animation {{
    animation: pulse-viridis 2s ease-in-out infinite;
}}

/* Responsive design */
@media (max-width: 768px) {{
    .modern-header {{
        padding: 1.5rem 1rem;
    }}
    
    .modern-header h1 {{
        font-size: 2rem;
    }}
    
    .metric-modern {{
        margin-bottom: 1rem;
    }}
}}

/* Scrollbar personnalisée */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: var(--surface);
}}

::-webkit-scrollbar-thumb {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: linear-gradient(135deg, var(--secondary), var(--accent));
}}
</style>
"""


class UIConfig:
    """Configuration pour l'interface utilisateur moderne"""
    
    @staticmethod
    def get_page_config() -> Dict[str, Any]:
        """Configuration Streamlit page"""
        return {
            "page_title": settings.APP_TITLE,
            "page_icon": settings.PAGE_ICON,
            "layout": settings.LAYOUT,
            "initial_sidebar_state": settings.INITIAL_SIDEBAR_STATE
        }
    
    @staticmethod
    def get_main_header_html() -> str:
        """HTML pour l'en-tête principal moderne"""
        return f"""
        <div class="modern-header">
            <h1>{settings.APP_TITLE}</h1>
            <p>{settings.APP_SUBTITLE}</p>
        </div>
        """
    
    @staticmethod
    def get_metric_card_html(title: str, value: str, delta: str = None, delta_color: str = "normal") -> str:
        """Génère une carte métrique moderne"""
        delta_html = ""
        if delta:
            delta_class = f"metric-delta metric-delta-{delta_color}"
            delta_html = f'<div class="{delta_class}">{delta}</div>'
        
        return f"""
        <div class="metric-modern">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{title}</div>
            {delta_html}
        </div>
        """
    
    @staticmethod
    def get_alert_html(alert_type: str, title: str, message: str = "") -> str:
        """Génère une alerte moderne"""
        return f"""
        <div class="alert-modern alert-{alert_type}">
            <strong>{title}</strong>
            {f"<br><span style='opacity: 0.9;'>{message}</span>" if message else ""}
        </div>
        """
    
    @staticmethod
    def get_card_html(content: str, title: str = None) -> str:
        """Génère une carte moderne"""
        title_html = f"<h3 style='margin-top: 0; color: var(--text-primary);'>{title}</h3>" if title else ""
        return f"""
        <div class="modern-card">
            {title_html}
            {content}
        </div>
        """
    
    @staticmethod
    def get_loading_html(message: str = "Loading...") -> str:
        """Génère un indicateur de chargement"""
        return f"""
        <div class="loading-animation" style="text-align: center; padding: 2rem;">
            <div style="font-size: 1.1rem; color: var(--text-secondary);">{message}</div>
        </div>
        """
    
    @staticmethod
    def get_status_badge_html(status: str, text: str) -> str:
        """Génère un badge de status moderne"""
        status_colors = {
            'success': 'var(--accent)',
            'warning': 'var(--light)', 
            'error': '#ff6b6b',
            'info': 'var(--secondary)',
            'default': 'var(--text-secondary)'
        }
        
        color = status_colors.get(status, status_colors['default'])
        
        return f"""
        <span class="status-badge-modern" style="
            background: {color}20;
            color: {color};
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: 1px solid {color}40;
            display: inline-block;
        ">{text}</span>
        """


# Configuration par défaut du session state
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
    'ui_theme': 'viridis_modern'  # Nouveau : thème UI
}


# Extensions de fichiers autorisées
ALLOWED_EXTENSIONS = (".xlsx", ".xls")


# Configuration logging moderne
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    'max_logs_in_session': 100,
    'use_colors': True
}


# Configuration des graphiques Plotly avec thème Viridis
PLOTLY_CONFIG = {
    'theme': 'plotly_dark',
    'color_palette': [
        VIRIDIS_COLORS['primary'],
        VIRIDIS_COLORS['secondary'], 
        VIRIDIS_COLORS['accent'],
        VIRIDIS_COLORS['light'],
        '#8e44ad',  # Violet
        '#e74c3c',  # Rouge
        '#f39c12',  # Orange
        '#2ecc71'   # Vert
    ],
    'background_color': VIRIDIS_COLORS['surface'],
    'grid_color': 'rgba(255, 255, 255, 0.1)',
    'font_color': VIRIDIS_COLORS['text_primary']
}


# Configuration des composants Streamlit
STREAMLIT_THEME = {
    'primaryColor': VIRIDIS_COLORS['accent'],
    'backgroundColor': VIRIDIS_COLORS['dark'],
    'secondaryBackgroundColor': VIRIDIS_COLORS['surface'],
    'textColor': VIRIDIS_COLORS['text_primary'],
    'font': 'sans serif'
}