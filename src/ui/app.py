\
\
\
\

import streamlit as st
from datetime import datetime
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


try:
    from treasury.config import settings, UIConfig, CSS_STYLES
    from treasury.session import init_session_state


    try:
        from treasury.logging_config import logger
    except ImportError:
        import logging
        logger = logging.getLogger(__name__)

except ImportError as e:
    st.error(f"ERROR Erreur d'import: {e}")
    st.info("Vérifiez que tous les modules Treasury sont présents")
    st.stop()


try:
    from ui.components.sidebar import render_sidebar
    from ui.components.tabs.import_tab import render_import_tab
    from ui.components.tabs.pnl_tab import render_pnl_tab
    from ui.components.tabs.risk_tab import render_risk_management_tab
    from ui.components.tabs.visuals_tab import render_visuals_tab
    from ui.components.tabs.var_tab import render_var_tab
    from ui.components.tabs.performance_tab import render_performance_tab
    from ui.components.footer import render_footer
except ImportError as e:
    st.error(f"ERROR Erreur d'import UI: {e}")
    st.info("Vérifiez la structure des dossiers ui/")
    st.stop()


def setup_streamlit_page():
    \
    st.set_page_config(**UIConfig.get_page_config())


    current_theme = st.session_state.get('ui_theme', 'liquid_glass')
    theme_css = UIConfig.get_theme_css(current_theme)
    st.markdown(theme_css, unsafe_allow_html=True)

    init_session_state()


def render_main_header():
    \
    current_theme = st.session_state.get('ui_theme', 'liquid_glass')
    header_html = UIConfig.get_header_html(current_theme)
    st.markdown(header_html, unsafe_allow_html=True)


def render_navigation_tabs():
    \
    tab_import, tab_pnl, tab_visuals, tab_var, tab_performance, tab_risk = st.tabs([
        "Import",
        "PnL",
        "Visualisations",
        "VaR",
        "Performance",
        "Risk Management"
    ])

    with tab_import:
        render_import_tab()

    with tab_pnl:
        render_pnl_tab()

    with tab_visuals:
        render_visuals_tab()

    with tab_var:
        render_var_tab()

    with tab_performance:
        render_performance_tab()

    with tab_risk:
        render_risk_management_tab()


def handle_application_error(error: Exception):
    \
    st.error(f"ERROR Erreur application: {error}")

    try:
        logger.error(f"Erreur main app: {error}")
    except:
        pass


    with st.expander("Debug Info"):
        st.exception(error)
        st.write("**Session State:**")
        st.json({
            "deals_count": len(st.session_state.get('generic_deals', [])),
            "pnl_calculated": st.session_state.get('df_pnl_enhanced') is not None,
            "config": dict(st.session_state.get('pnl_config', {}))
        })


def log_session_activity():
    \
    try:
        deals_count = len(st.session_state.get('generic_deals', []))
        logger.info(f"Session active - {deals_count} deals en mémoire")


        if st.session_state.get('df_pnl_enhanced') is not None:
            df_pnl = st.session_state.df_pnl_enhanced
            if not df_pnl.empty and 'total_pnl' in df_pnl.columns:
                total_pnl = df_pnl['total_pnl'].sum()
                logger.info(f"PnL total calculé: {total_pnl:,.0f}")
    except Exception:

        pass


def main():
    \
    try:

        setup_streamlit_page()


        render_main_header()


        render_sidebar()


        render_navigation_tabs()


        render_footer()


        log_session_activity()

    except Exception as e:
        handle_application_error(e)


if __name__ == "__main__":
    main()