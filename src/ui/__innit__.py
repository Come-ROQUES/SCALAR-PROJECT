"""
Interface utilisateur Treasury Dashboard
Module UI principal avec composants modulaires
"""

from .app import main
from .components.sidebar import render_sidebar
from .components.footer import render_footer

__version__ = "1.0.0"
__author__ = "Treasury Team"

# Exports principaux
__all__ = [
    "main",
    "render_sidebar", 
    "render_footer"
]