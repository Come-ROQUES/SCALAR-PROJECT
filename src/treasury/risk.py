"""
Module de gestion des risques et Monte Carlo
Extrait du monolithe app.py
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List

from .analytics import convert_generic_to_analytics_format
from .logging_config import logger


def run_monte_carlo_simulation(df_analytics: pd.DataFrame, 
                               n_simulations: int = 50_000, 
                               seed: int = 123) -> Dict:
    """
    FONCTION À PERSONNALISER : Simulation Monte Carlo avec corrélations réalistes
    
    Args:
        df_analytics: DataFrame format analytics
        n_simulations: Nombre de simulations
        seed: Graine aléatoire
        
    Returns:
        Dict: Résultats de simulation
    """
    try:
        if df_analytics.empty:
            logger.warning("DataFrame analytics vide pour Monte Carlo")
            return {}
        
        # Exposition par paire
        expo = df_analytics.groupby('paire')['notional'].sum()
        pairs = expo.index.tolist()
        n = len(pairs)
        total_notional = expo.sum()
        
        if n == 0:
            return {}
        
        logger.info(f"Monte Carlo: {n} paires, {total_notional/1e6:.1f}M notionnel")
        
        # Générateur aléatoire
        rng = np.random.default_rng(seed)
        
        # Volatilités par paire (à calibrer selon votre modèle)
        vols = np.array([
            0.12 if 'JPY' in pair else
            0.15 if any(ccy in pair for ccy in ['GBP', 'AUD', 'CAD']) else
            0.10
            for pair in pairs
        ])
        
        # Matrice de corrélation (à améliorer avec vos données historiques)
        corr = np.full((n, n), 0.3)  # Corrélation de base 30%
        np.fill_diagonal(corr, 1.0)
        
        # Corrélations spécifiques
        for i, pair1 in enumerate(pairs):
            for j, pair2 in enumerate(pairs):
                if i != j:
                    # Paires USD : corrélation plus forte
                    if 'USD' in pair1 and 'USD' in pair2:
                        corr[i, j] = 0.6
                    # Devises européennes
                    elif any(ccy in pair1 for ccy in ['EUR', 'GBP', 'CHF']) and \
                         any(ccy in pair2 for ccy in ['EUR', 'GBP', 'CHF']):
                        corr[i, j] = 0.5
        
        # Matrice de covariance
        cov = np.outer(vols, vols) * corr
        
        # Simulation chocs FX
        shocks = rng.multivariate_normal(mean=np.zeros(n), cov=cov, size=n_simulations)
        pnl_fx = shocks @ expo.values
        
        # Composante taux (si deals IRS présents)
        irs_count = len(df_analytics[df_analytics['instrument'] == 'IRS'])
        if irs_count > 0:
            rate_sigma = 0.0008  # 8bp volatilité taux
            rate_shocks = rng.normal(0, rate_sigma, size=n_simulations)
            pnl_rate = total_notional * rate_shocks * 0.25 * (irs_count / len(df_analytics))
        else:
            pnl_rate = np.zeros(n_simulations)
        
        # PnL total
        total_pnl = pnl_fx + pnl_rate
        
        # Calcul métriques VaR
        var_95 = np.percentile(total_pnl, 5)
        var_99 = np.percentile(total_pnl, 1)
        expected_shortfall = total_pnl[total_pnl <= var_95].mean()
        
        results = {
            'total_pnl': total_pnl.tolist(),
            'var_95': float(var_95),
            'var_99': float(var_99),
            'expected_shortfall': float(expected_shortfall),
            'fx_component': pnl_fx.tolist(),
            'rate_component': pnl_rate.tolist(),
            'pairs': pairs,
            'exposures': expo.values.tolist(),
            'simulation_params': {
                'n_simulations': n_simulations,
                'seed': seed,
                'volatilities': vols.tolist(),
                'correlation_matrix': corr.tolist()
            }
        }
        
        logger.info(f"Monte Carlo terminé: VaR95={var_95/1e6:.1f}M, VaR99={var_99/1e6:.1f}M")
        return results
        
    except Exception as e:
        logger.error(f"Erreur Monte Carlo: {e}")
        return {}


def create_monte_carlo_distribution(sim_results: Dict) -> go.Figure:
    """
    Graphique de distribution Monte Carlo avec VaR
    
    Args:
        sim_results: Résultats de simulation
        
    Returns:
        go.Figure: Graphique de distribution
    """
    fig = go.Figure()
    
    try:
        if not sim_results or 'total_pnl' not in sim_results:
            fig.add_annotation(
                text="Aucun résultat Monte Carlo",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font_size=16
            )
            return fig
        
        # Distribution PnL
        pnl_dist = np.array(sim_results['total_pnl']) / 1_000_000
        
        # Histogramme
        fig.add_trace(go.Histogram(
            x=pnl_dist,
            nbinsx=50,
            name='Distribution P&L',
            opacity=0.7,
            marker_color='#4ecdc4',
            hovertemplate='P&L: %{x:.1f}M USD<br>Fréquence: %{y}<extra></extra>'
        ))
        
        # Lignes VaR
        var_95 = sim_results['var_95'] / 1_000_000
        var_99 = sim_results['var_99'] / 1_000_000
        
        fig.add_vline(
            x=var_95, 
            line_dash="dash", 
            line_color="orange",
            annotation_text=f"VaR 95%: {var_95:.1f}M"
        )
        
        fig.add_vline(
            x=var_99, 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"VaR 99%: {var_99:.1f}M"
        )
        
        # Expected Shortfall
        if 'expected_shortfall' in sim_results:
            es = sim_results['expected_shortfall'] / 1_000_000
            fig.add_vline(
                x=es,
                line_dash="dot",
                line_color="darkred",
                annotation_text=f"ES: {es:.1f}M"
            )
        
        fig.update_layout(
            title='Distribution Monte Carlo P&L',
            xaxis_title='P&L (M USD)',
            yaxis_title='Fréquence',
            height=420,
            showlegend=False
        )
        
        logger.debug("Graphique Monte Carlo créé")
        
    except Exception as e:
        logger.error(f"Erreur viz Monte Carlo: {e}")
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font_size=14, font_color="red"
        )
    
    return fig


def calculate_component_var(sim_results: Dict) -> Dict[str, float]:
    """
    Calcule la VaR par composante (FX, Taux, etc.)
    
    Args:
        sim_results: Résultats Monte Carlo
        
    Returns:
        Dict: VaR par composante
    """
    try:
        if not sim_results:
            return {}
        
        var_components = {}
        
        # VaR FX
        if 'fx_component' in sim_results:
            fx_pnl = np.array(sim_results['fx_component'])
            var_components['fx_var_95'] = float(np.percentile(fx_pnl, 5))
            var_components['fx_var_99'] = float(np.percentile(fx_pnl, 1))
        
        # VaR Taux
        if 'rate_component' in sim_results:
            rate_pnl = np.array(sim_results['rate_component'])
            var_components['rate_var_95'] = float(np.percentile(rate_pnl, 5))
            var_components['rate_var_99'] = float(np.percentile(rate_pnl, 1))
        
        # VaR Total
        var_components['total_var_95'] = sim_results.get('var_95', 0)
        var_components['total_var_99'] = sim_results.get('var_99', 0)
        
        return var_components
        
    except Exception as e:
        logger.error(f"Erreur VaR composantes: {e}")
        return {}


def stress_test_portfolio(df_analytics: pd.DataFrame, 
                         scenarios: Dict[str, Dict] = None) -> pd.DataFrame:
    """
    Tests de stress sur le portefeuille
    
    Args:
        df_analytics: DataFrame analytics
        scenarios: Scénarios de stress custom
        
    Returns:
        pd.DataFrame: Résultats stress tests
    """
    try:
        if df_analytics.empty:
            return pd.DataFrame()
        
        # Scénarios par défaut
        if scenarios is None:
            scenarios = {
                'Crise Systémique': {'fx_shock': -0.15, 'rate_shock': 0.02},
                'Resserrement Fed': {'fx_shock': -0.05, 'rate_shock': 0.015},
                'Crise Émergente': {'fx_shock': -0.08, 'rate_shock': 0.005},
                'Volatilité Extrême': {'fx_shock': -0.12, 'rate_shock': 0.01},
                'Carry Trade Unwind': {'fx_shock': -0.06, 'rate_shock': -0.01}
            }
        
        # Notionnels par type
        total_notional = df_analytics['notional'].sum()
        fx_notional = df_analytics[df_analytics['instrument'].isin(['FX_SWAP'])]['notional'].sum()
        irs_notional = df_analytics[df_analytics['instrument'] == 'IRS']['notional'].sum()
        
        results = []
        
        for scenario_name, shocks in scenarios.items():
            # Impact FX
            fx_pnl = fx_notional * shocks['fx_shock']
            
            # Impact Taux
            rate_pnl = irs_notional * shocks['rate_shock'] * 2.0  # Duration approximative
            
            # Impact Total
            total_impact = fx_pnl + rate_pnl
            
            results.append({
                'Scenario': scenario_name,
                'FX_Shock_pct': shocks['fx_shock'] * 100,
                'Rate_Shock_bps': shocks['rate_shock'] * 10000,
                'FX_PnL_M': fx_pnl / 1_000_000,
                'Rate_PnL_M': rate_pnl / 1_000_000,
                'Total_PnL_M': total_impact / 1_000_000,
                'Total_Notional_M': total_notional / 1_000_000
            })
        
        df_stress = pd.DataFrame(results)
        logger.info(f"Stress tests calculés: {len(scenarios)} scénarios")
        
        return df_stress
        
    except Exception as e:
        logger.error(f"Erreur stress tests: {e}")
        return pd.DataFrame()


def calculate_portfolio_var_simple(df_analytics: pd.DataFrame, 
                                  confidence_level: float = 0.95) -> Dict[str, float]:
    """
    Calcul VaR simplifié sans Monte Carlo (approximation analytique)
    
    Args:
        df_analytics: DataFrame analytics
        confidence_level: Niveau de confiance (0.95 pour 95%)
        
    Returns:
        Dict: Métriques VaR approximatives
    """
    try:
        if df_analytics.empty:
            return {}
        
        # Notionnel par devise
        expo_by_ccy = df_analytics.groupby('devise_base')['notional'].sum()
        
        # Volatilités approximatives
        vol_mapping = {
            'USD': 0.10, 'EUR': 0.12, 'JPY': 0.15, 'GBP': 0.14,
            'CHF': 0.11, 'AUD': 0.16, 'CAD': 0.13
        }
        
        # VaR par devise (indépendante)
        var_by_ccy = {}
        total_var_independent = 0
        
        z_score = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}[confidence_level]
        
        for ccy, notional in expo_by_ccy.items():
            vol = vol_mapping.get(ccy, 0.12)
            var_1d = notional * vol * z_score / np.sqrt(252)  # VaR 1 jour
            var_by_ccy[ccy] = var_1d
            total_var_independent += var_1d ** 2
        
        # VaR totale (hypothèse indépendance)
        total_var = np.sqrt(total_var_independent)
        
        results = {
            'var_total': total_var,
            'var_total_m': total_var / 1_000_000,
            'confidence_level': confidence_level,
            'var_by_currency': var_by_ccy,
            'total_notional': expo_by_ccy.sum(),
            'var_as_pct_notional': total_var / expo_by_ccy.sum() * 100
        }
        
        logger.info(f"VaR analytique {confidence_level*100}%: {total_var/1e6:.1f}M")
        return results
        
    except Exception as e:
        logger.error(f"Erreur VaR analytique: {e}")
        return {}