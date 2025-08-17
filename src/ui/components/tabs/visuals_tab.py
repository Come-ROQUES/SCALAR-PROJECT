"""
Onglets visuels pour Treasury Dashboard
Modules UI pour visualisations 3D et heatmaps
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, Optional

# Imports Treasury
from treasury.visuals import (
    create_3d_risk_surface, 
    create_liquidity_heatmap, 
    create_correlation_heatmap
)

try:
    from treasury.logging_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# ================================
# ONGLET VISUALISATIONS 3D
# ================================

def render_visuals_3d_tab():
    """Onglet 3D Visualizations"""
    st.subheader("🌊 Visualisations 3D")
    
    df_pnl = st.session_state.get('df_pnl_enhanced')
    
    if df_pnl is None or df_pnl.empty:
        st.info("Calculez d'abord les PnL pour les visualisations 3D")
        return
    
    _render_3d_surface_chart(df_pnl)


def _render_3d_surface_chart(df_pnl: pd.DataFrame):
    """Rendu du graphique 3D avec contrôles"""
    st.markdown("### 🌊 Surface de Risque 3D")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        x_var = st.selectbox("Axe X:", ['time_to_maturity_years', 'amount', 'client_rate'], index=0)
    with col2:
        y_var = st.selectbox("Axe Y:", ['client_rate', 'amount', 'time_to_maturity_years'], index=0)
    with col3:
        z_var = st.selectbox("Axe Z:", ['total_pnl', 'mtm_pnl', 'rate_pnl'], index=0)
    
    if all(col in df_pnl.columns for col in [x_var, y_var, z_var]):
        try:
            # Essayer la fonction originale
            try:
                fig_3d = create_3d_risk_surface(df_pnl, x_var, y_var, z_var)
            except (TypeError, AttributeError):
                # Fallback vers fonction de remplacement
                fig_3d = _create_3d_risk_surface_fallback(df_pnl, x_var, y_var, z_var)
            
            st.plotly_chart(fig_3d, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erreur création surface 3D: {e}")
            st.info("Vérifiez que les données sont disponibles pour les axes sélectionnés")
    else:
        missing_cols = [col for col in [x_var, y_var, z_var] if col not in df_pnl.columns]
        st.warning(f"Variables non disponibles: {missing_cols}")
        st.info("Colonnes disponibles: " + ", ".join(df_pnl.columns.tolist()))


def _create_3d_risk_surface_fallback(df, x_var, y_var, z_var):
    """Fonction de remplacement pour créer une surface 3D"""
    # Nettoyer les données
    df_clean = df[[x_var, y_var, z_var]].dropna()
    
    if len(df_clean) < 3:
        raise ValueError("Pas assez de données valides pour créer une surface 3D")
    
    # Créer un scatter 3D
    fig = go.Figure(data=[go.Scatter3d(
        x=df_clean[x_var],
        y=df_clean[y_var],
        z=df_clean[z_var],
        mode='markers',
        marker=dict(
            size=8,
            color=df_clean[z_var],
            colorscale='Viridis',
            colorbar=dict(title=z_var),
            showscale=True
        ),
        text=[f'Deal {i}' for i in range(len(df_clean))],
        hovertemplate=f'<b>%{{text}}</b><br>{x_var}: %{{x}}<br>{y_var}: %{{y}}<br>{z_var}: %{{z}}<extra></extra>'
    )])
    
    fig.update_layout(
        title=f'Visualisation 3D: {z_var} vs {x_var} & {y_var}',
        scene=dict(
            xaxis_title=x_var,
            yaxis_title=y_var,
            zaxis_title=z_var,
            camera=dict(eye=dict(x=1.2, y=1.2, z=1.2)),
            bgcolor='rgba(68, 1, 84, 0.1)'
        ),
        template='plotly_dark',
        height=600
    )
    return fig


# ================================
# ONGLET HEATMAPS
# ================================

def render_heatmaps_tab():
    """Onglet Heatmaps"""
    st.subheader("🔥 Heatmaps Analytiques")
    
    df_pnl = st.session_state.get('df_pnl_enhanced')
    
    if df_pnl is None or df_pnl.empty:
        st.info("Calculez d'abord les PnL pour les heatmaps")
        return
    
    _render_liquidity_heatmap(df_pnl)
    st.markdown("---")
    _render_correlation_heatmap(df_pnl)


def _render_liquidity_heatmap(df_pnl: pd.DataFrame):
    """Heatmap de liquidité"""
    st.markdown("### 💧 Heatmap Liquidité")
    
    try:
        # Essayer la fonction originale
        try:
            fig_liquidity = create_liquidity_heatmap(df_pnl)
        except (TypeError, AttributeError):
            # Fallback vers fonction de remplacement
            fig_liquidity = _create_liquidity_heatmap_fallback(df_pnl)
        
        st.plotly_chart(fig_liquidity, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur heatmap liquidité: {e}")
        st.info("Données disponibles: " + ", ".join(df_pnl.columns.tolist()))


def _render_correlation_heatmap(df_pnl: pd.DataFrame):
    """Heatmap de corrélations"""
    st.markdown("### 🔗 Heatmap Corrélations")
    
    # Sélection des variables pour corrélation
    numeric_cols = df_pnl.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    if len(numeric_cols) >= 2:
        selected_vars = st.multiselect(
            "Variables à corréler:",
            numeric_cols,
            default=numeric_cols[:5] if len(numeric_cols) >= 5 else numeric_cols
        )
        
        if len(selected_vars) >= 2:
            try:
                # Essayer la fonction originale
                try:
                    fig_corr = create_correlation_heatmap(df_pnl[selected_vars])
                except (TypeError, AttributeError):
                    # Fallback vers fonction de remplacement
                    fig_corr = _create_correlation_heatmap_fallback(df_pnl[selected_vars])
                
                st.plotly_chart(fig_corr, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur heatmap corrélations: {e}")
        else:
            st.info("Sélectionnez au moins 2 variables pour la corrélation")
    else:
        st.warning("Pas assez de variables numériques pour la corrélation")


def _create_liquidity_heatmap_fallback(df):
    """Fonction de remplacement pour heatmap liquidité"""
    # Créer des buckets de liquidité
    df_work = df.copy()
    
    # Buckets de montant
    if 'amount' in df.columns:
        df_work['amount_bucket'] = pd.cut(df_work['amount'], bins=5, labels=['Très Petit', 'Petit', 'Moyen', 'Grand', 'Très Grand'])
    else:
        df_work['amount_bucket'] = 'N/A'
    
    # Buckets de maturité
    if 'time_to_maturity_years' in df.columns:
        df_work['maturity_bucket'] = pd.cut(df_work['time_to_maturity_years'], bins=5, labels=['<1Y', '1-2Y', '2-3Y', '3-4Y', '>4Y'])
    else:
        df_work['maturity_bucket'] = 'N/A'
    
    # Agréger par buckets
    if 'total_pnl' in df.columns:
        heatmap_data = df_work.groupby(['amount_bucket', 'maturity_bucket'])['total_pnl'].mean().unstack(fill_value=0)
    else:
        heatmap_data = df_work.groupby(['amount_bucket', 'maturity_bucket']).size().unstack(fill_value=0)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis',
        text=heatmap_data.round(0).values,
        texttemplate="%{text}",
        textfont={"size": 10},
        hovertemplate='Maturité: %{x}<br>Montant: %{y}<br>Valeur: %{z:.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Heatmap de Liquidité (Montant vs Maturité)',
        xaxis_title='Bucket Maturité',
        yaxis_title='Bucket Montant',
        template='plotly_dark',
        height=500
    )
    
    return fig


def _create_correlation_heatmap_fallback(df):
    """Fonction de remplacement pour heatmap corrélation"""
    if df.empty or len(df.columns) < 2:
        raise ValueError("Pas assez de données pour créer une heatmap de corrélation")
    
    # Calculer la matrice de corrélation
    corr_matrix = df.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.round(2).values,
        texttemplate="%{text}",
        textfont={"size": 10},
        hovertemplate='%{x} vs %{y}<br>Corrélation: %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Matrice de Corrélation',
        template='plotly_dark',
        height=500,
        width=500
    )
    
    return fig