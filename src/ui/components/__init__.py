\
\
\
\

from .sidebar import render_sidebar, get_portfolio_summary
from .footer import render_footer, render_system_health_indicator


def get_current_theme():
    \
    import streamlit as st
    return st.session_state.get('ui_theme', 'liquid_glass')

def apply_theme_to_component(component_html: str, theme_name: str = None):
    \
    if theme_name is None:
        theme_name = get_current_theme()


    return component_html

__all__ = [
    "render_sidebar",
    "get_portfolio_summary",
    "render_footer",
    "render_system_health_indicator",
    "get_current_theme",
    "apply_theme_to_component"
]