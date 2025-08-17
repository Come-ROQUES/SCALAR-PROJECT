"""
Onglet VaR/Monte Carlo pour Treasury Dashboard
Module UI séparé pour l'analyse de risque quantitative
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

# Imports Treasury
from treasury.risk import run_monte_carlo_simulation, create_monte_carlo_distribution
from treasury.analytics import convert_generic_to_analytics_format

try:
    from treasury.logging_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def render_var_tab():
    """Onglet Monte Carlo et VaR"""
    st.subheader("🎲 Monte Carlo & VaR")
    
    df_pnl = st.session_state.get('df_pnl_enhanced')
    
    if df_pnl is None or df_pnl.empty:
        st.info("Calculez d'abord les PnL pour l'analyse VaR")
        return
    
    n_sims, confidence = _render_var_parameters()
    _render_monte_carlo_simulation(df_pnl, n_sims, confidence)


def _render_var_parameters():
    """Paramètres simulation VaR"""
    st.markdown("### ⚙️ Paramètres de Simulation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        n_sims = st.selectbox("Simulations:", [10_000, 50_000, 100_000], index=1)
    with col2:
        confidence = st.selectbox("Confiance:", [90, 95, 99], index=1)
    with col3:
        run_simulation = st.button("🔄 Calculer VaR", type="primary")
    
    return n_sims, confidence


def _render_monte_carlo_simulation(df_pnl: pd.DataFrame, n_sims: int, confidence: int):
    """Simulation Monte Carlo et résultats"""
    # Simulation Monte Carlo
    with st.spinner("🎲 Simulation Monte Carlo..."):
        try:
            sim_results = run_monte_carlo_simulation(
                convert_generic_to_analytics_format(df_pnl), 
                n_simulations=n_sims
            )
        except Exception as e:
            st.error(f"Erreur simulation Monte Carlo: {e}")
            sim_results = None
    
    if sim_results:
        _render_monte_carlo_results(sim_results, n_sims, confidence)
    else:
        st.warning("Impossible de calculer la VaR avec les données actuelles")


def _render_monte_carlo_results(sim_results: Dict[str, Any], n_sims: int, confidence: int):
    """Affichage des résultats Monte Carlo"""
    # Graphique distribution
    try:
        fig_mc = create_monte_carlo_distribution(sim_results)
        st.plotly_chart(fig_mc, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur graphique Monte Carlo: {e}")
    
    # Métriques VaR
    _render_var_metrics(sim_results)
    
    # Informations simulation
    _render_simulation_details(sim_results, n_sims, confidence)


def _render_var_metrics(sim_results: Dict[str, Any]):
    """Métriques VaR"""
    st.markdown("### 📊 Métriques VaR")
    
    col1, col2, col3 = st.columns(3)
    
    var_95 = sim_results.get('var_95', 0) / 1_000_000
    var_99 = sim_results.get('var_99', 0) / 1_000_000
    es_95 = sim_results.get('expected_shortfall', 0) / 1_000_000
    
    col1.metric("VaR 95% (1J)", f"${var_95:+.1f}M")
    col2.metric("VaR 99% (1J)", f"${var_99:+.1f}M")
    col3.metric("Expected Shortfall", f"${es_95:+.1f}M")


def _render_simulation_details(sim_results: Dict[str, Any], n_sims: int, confidence: int):
    """Détails de la simulation"""
    with st.expander("ℹ️ Détails Simulation"):
        st.write(f"**Simulations:** {n_sims:,}")
        st.write(f"**Niveau de confiance:** {confidence}%")
        if 'pairs' in sim_results:
            st.write(f"**Paires analysées:** {len(sim_results['pairs'])}")
            st.write(f"**Expositions:** {', '.join(sim_results['pairs'])}")
        
        # Statistiques additionnelles
        if 'portfolio_volatility' in sim_results:
            st.write(f"**Volatilité portfolio:** {sim_results['portfolio_volatility']:.2%}")
        
        if 'worst_case_scenario' in sim_results:
            st.write(f"**Pire scénario:** ${sim_results['worst_case_scenario']/1_000_000:.1f}M")


def render_advanced_var_analysis():
    """Analyse VaR avancée (optionnelle)"""
    st.markdown("### 📈 Analyse VaR Avancée")
    
    df_pnl = st.session_state.get('df_pnl_enhanced')
    
    if df_pnl is None or df_pnl.empty:
        st.info("Données PnL requises pour l'analyse avancée")
        return
    
    # Sélection de la méthode VaR
    var_method = st.selectbox(
        "Méthode VaR:",
        ["Historique", "Paramétrique", "Monte Carlo"],
        index=2
    )
    
    # Paramètres avancés
    with st.expander("🔧 Paramètres Avancés"):
        horizon_days = st.number_input("Horizon (jours):", min_value=1, max_value=250, value=1)
        decay_factor = st.slider("Facteur de décroissance:", 0.8, 1.0, 0.94, 0.01)
        bootstrap_samples = st.number_input("Échantillons bootstrap:", min_value=100, max_value=10000, value=1000)
    
    if st.button("🧮 Calculer VaR Avancée"):
        _calculate_advanced_var(df_pnl, var_method, horizon_days, decay_factor, bootstrap_samples)


def _calculate_advanced_var(df_pnl: pd.DataFrame, method: str, horizon: int, decay: float, samples: int):
    """Calcule la VaR avec des méthodes avancées"""
    with st.spinner(f"Calcul VaR {method}..."):
        try:
            # Simulation de calculs avancés
            import numpy as np
            
            if 'total_pnl' in df_pnl.columns:
                pnl_values = df_pnl['total_pnl'].values
                
                if method == "Historique":
                    var_95 = np.percentile(pnl_values, 5)
                    var_99 = np.percentile(pnl_values, 1)
                elif method == "Paramétrique":
                    mean_pnl = np.mean(pnl_values)
                    std_pnl = np.std(pnl_values)
                    var_95 = mean_pnl - 1.645 * std_pnl * np.sqrt(horizon)
                    var_99 = mean_pnl - 2.326 * std_pnl * np.sqrt(horizon)
                else:  # Monte Carlo
                    # Simulation simplifiée
                    sim_returns = np.random.normal(np.mean(pnl_values), np.std(pnl_values), samples)
                    var_95 = np.percentile(sim_returns, 5)
                    var_99 = np.percentile(sim_returns, 1)
                
                # Affichage des résultats
                col1, col2, col3 = st.columns(3)
                col1.metric(f"VaR 95% ({method})", f"${var_95/1_000_000:+.2f}M")
                col2.metric(f"VaR 99% ({method})", f"${var_99/1_000_000:+.2f}M")
                col3.metric("Horizon", f"{horizon} jour(s)")
                
                # Graphique comparatif des méthodes
                _create_var_comparison_chart(pnl_values, method, var_95, var_99)
                
            else:
                st.warning("Colonne 'total_pnl' manquante pour le calcul VaR")
                
        except Exception as e:
            st.error(f"Erreur calcul VaR avancée: {e}")


def _create_var_comparison_chart(pnl_values, method, var_95, var_99):
    """Crée un graphique de comparaison VaR"""
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Histogramme des PnL
    fig.add_trace(go.Histogram(
        x=pnl_values / 1_000_000,
        nbinsx=50,
        name='Distribution PnL',
        opacity=0.7,
        marker_color='lightblue'
    ))
    
    # Lignes VaR
    fig.add_vline(
        x=var_95 / 1_000_000,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"VaR 95% ({method})"
    )
    
    fig.add_vline(
        x=var_99 / 1_000_000,
        line_dash="dash", 
        line_color="red",
        annotation_text=f"VaR 99% ({method})"
    )
    
    fig.update_layout(
        title=f'Distribution PnL et VaR - Méthode {method}',
        xaxis_title='PnL (M USD)',
        yaxis_title='Fréquence',
        template='plotly_dark',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)