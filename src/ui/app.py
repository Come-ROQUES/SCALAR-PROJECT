"""
Application principale Treasury Dashboard - Version modularisée
Point d'entrée principal avec imports des composants UI
"""

import streamlit as st
from datetime import datetime
import sys
import os

# Ajouter le dossier parent au path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Imports des modules Treasury
try:
    from treasury.config import settings, UIConfig, CSS_STYLES
    from treasury.session import init_session_state
    
    # Logging optionnel
    try:
        from treasury.logging_config import logger
    except ImportError:
        import logging
        logger = logging.getLogger(__name__)
    
except ImportError as e:
    st.error(f"ERROR Erreur d'import: {e}")
    st.info("Vérifiez que tous les modules Treasury sont présents")
    st.stop()

# Imports des composants UI modularisés - IMPORTS ABSOLUS
try:
    from ui.components.sidebar import render_sidebar
    from ui.components.tabs.import_tab import render_import_tab
    from ui.components.tabs.pnl_tab import render_pnl_tab
    from ui.components.tabs.risk_tab import render_risk_management_tab
    from ui.components.tabs.visuals_tab import render_visuals_3d_tab, render_heatmaps_tab
    from ui.components.tabs.var_tab import render_var_tab
    from ui.components.tabs.performance_tab import render_performance_tab
    from ui.components.footer import render_footer
except ImportError as e:
    st.error(f"ERROR Erreur d'import UI: {e}")
    st.info("Vérifiez la structure des dossiers ui/")
    st.stop()


def setup_streamlit_page():
    """Configuration initiale de la page Streamlit"""
    st.set_page_config(**UIConfig.get_page_config())
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    init_session_state()


def render_main_header():
    """Affichage de l'en-tête principal moderne"""
    st.markdown(UIConfig.get_header_html(), unsafe_allow_html=True)


def render_navigation_tabs():
    """Rendu des onglets de navigation principaux"""
    tab_import, tab_pnl, tab_3d, tab_heatmaps, tab_var, tab_performance, tab_risk = st.tabs([
        "Import", 
        "PnL", 
        "3D", 
        "Heatmaps",
        "VaR",
        "Performance",
        "Risk Management"
    ])
    
    with tab_import:
        render_import_tab()
    
    with tab_pnl:
        render_pnl_tab()
    
    with tab_3d:
        render_visuals_3d_tab()
    
    with tab_heatmaps:
        render_heatmaps_tab()
    
    with tab_var:
        render_var_tab()
    
    with tab_performance:
        render_performance_tab()
    
    with tab_risk:
        render_risk_management_tab()


def handle_application_error(error: Exception):
    """Gestion centralisée des erreurs d'application"""
    st.error(f"ERROR Erreur application: {error}")
    
    try:
        logger.error(f"Erreur main app: {error}")
    except:
        pass  # En cas de problème de logging
    
    # Affichage debug en cas d'erreur
    with st.expander("Debug Info"):
        st.exception(error)
        st.write("**Session State:**")
        st.json({
            "deals_count": len(st.session_state.get('generic_deals', [])),
            "pnl_calculated": st.session_state.get('df_pnl_enhanced') is not None,
            "config": dict(st.session_state.get('pnl_config', {}))
        })


def log_session_activity():
    """Log de l'activité de session"""
    try:
        deals_count = len(st.session_state.get('generic_deals', []))
        logger.info(f"Session active - {deals_count} deals en mémoire")
        
        # Log des métriques de base
        if st.session_state.get('df_pnl_enhanced') is not None:
            df_pnl = st.session_state.df_pnl_enhanced
            if not df_pnl.empty and 'total_pnl' in df_pnl.columns:
                total_pnl = df_pnl['total_pnl'].sum()
                logger.info(f"PnL total calculé: {total_pnl:,.0f}")
    except Exception:
        # Log silencieux en cas d'erreur
        pass


def main():
    """Fonction principale de l'application modularisée"""
    try:
        # 1. Setup initial
        setup_streamlit_page()
        
        # 2. Header principal
        render_main_header()
        
        # 3. Sidebar avec contrôles
        render_sidebar()
        
        # 4. Navigation et onglets
        render_navigation_tabs()
        
        # 5. Footer avec statut
        render_footer()
        
        # 6. Logging de session
        log_session_activity()
        
    except Exception as e:
        handle_application_error(e)


if __name__ == "__main__":
    main()