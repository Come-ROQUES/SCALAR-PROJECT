\
\
\
\

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List

from .analytics import convert_generic_to_analytics_format
from .logging_config import logger


def run_monte_carlo_simulation(df_analytics: pd.DataFrame,
                               n_simulations: int = 50_000,
                               seed: int = 123) -> Dict:
    \
\
\
\
\
\
\
\
\
\
\
    try:
        if df_analytics.empty:
            logger.warning("DataFrame analytics vide pour Monte Carlo")
            return {}


        expo = df_analytics.groupby('paire')['notional'].sum()
        pairs = expo.index.tolist()
        n = len(pairs)
        total_notional = expo.sum()

        if n == 0:
            return {}

        logger.info(f"Monte Carlo: {n} paires, {total_notional/1e6:.1f}M notionnel")


        rng = np.random.default_rng(seed)


        vols = np.array([
            0.12 if 'JPY' in pair else
            0.15 if any(ccy in pair for ccy in ['GBP', 'AUD', 'CAD']) else
            0.10
            for pair in pairs
        ])


        corr = np.full((n, n), 0.3)
        np.fill_diagonal(corr, 1.0)


        for i, pair1 in enumerate(pairs):
            for j, pair2 in enumerate(pairs):
                if i != j:

                    if 'USD' in pair1 and 'USD' in pair2:
                        corr[i, j] = 0.6

                    elif any(ccy in pair1 for ccy in ['EUR', 'GBP', 'CHF']) and \
                         any(ccy in pair2 for ccy in ['EUR', 'GBP', 'CHF']):
                        corr[i, j] = 0.5


        cov = np.outer(vols, vols) * corr


        shocks = rng.multivariate_normal(mean=np.zeros(n), cov=cov, size=n_simulations)
        pnl_fx = shocks @ expo.values


        irs_count = len(df_analytics[df_analytics['instrument'] == 'IRS'])
        if irs_count > 0:
            rate_sigma = 0.0008
            rate_shocks = rng.normal(0, rate_sigma, size=n_simulations)
            pnl_rate = total_notional * rate_shocks * 0.25 * (irs_count / len(df_analytics))
        else:
            pnl_rate = np.zeros(n_simulations)


        total_pnl = pnl_fx + pnl_rate


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
    \
\
\
\
\
\
\
\
\
    fig = go.Figure()

    try:
        if not sim_results or 'total_pnl' not in sim_results:
            fig.add_annotation(
                text="Aucun résultat Monte Carlo",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font_size=16
            )
            return fig


        pnl_dist = np.array(sim_results['total_pnl']) / 1_000_000


        fig.add_trace(go.Histogram(
            x=pnl_dist,
            nbinsx=75,
            name='P&L Distribution',
            opacity=0.8,
            marker=dict(
                color='rgba(76, 175, 80, 0.7)',
                line=dict(color='rgba(76, 175, 80, 1.0)', width=1)
            ),
            hovertemplate='P&L: %{x:.2f}M USD<br>Fréquence: %{y}<br>Probabilité: %{y}/%{customdata:.0f}<extra></extra>',
            customdata=[len(pnl_dist)] * len(pnl_dist)
        ))


        mean_pnl = np.mean(pnl_dist)
        std_pnl = np.std(pnl_dist)
        skewness = np.mean(((pnl_dist - mean_pnl) / std_pnl) ** 3)
        kurtosis = np.mean(((pnl_dist - mean_pnl) / std_pnl) ** 4) - 3


        var_95 = sim_results['var_95'] / 1_000_000
        var_99 = sim_results['var_99'] / 1_000_000


        fig.add_vline(
            x=var_95,
            line=dict(color="orange", width=3, dash="dash"),
            annotation=dict(
                text=f"VaR 95%: {var_95:.2f}M<br>Prob: 5%",
                textangle=0,
                bgcolor="rgba(255, 165, 0, 0.8)",
                bordercolor="orange",
                font=dict(color="white", size=12)
            )
        )


        fig.add_vline(
            x=var_99,
            line=dict(color="red", width=3, dash="dash"),
            annotation=dict(
                text=f"VaR 99%: {var_99:.2f}M<br>Prob: 1%",
                textangle=0,
                bgcolor="rgba(255, 0, 0, 0.8)",
                bordercolor="red",
                font=dict(color="white", size=12)
            )
        )


        if 'expected_shortfall' in sim_results:
            es = sim_results['expected_shortfall'] / 1_000_000
            fig.add_vline(
                x=es,
                line=dict(color="darkred", width=3, dash="dot"),
                annotation=dict(
                    text=f"Expected Shortfall: {es:.2f}M",
                    textangle=0,
                    bgcolor="rgba(139, 0, 0, 0.8)",
                    bordercolor="darkred",
                    font=dict(color="white", size=12)
                )
            )


            tail_area_x = pnl_dist[pnl_dist <= var_95]
            if len(tail_area_x) > 0:
                fig.add_trace(go.Histogram(
                    x=tail_area_x,
                    nbinsx=75,
                    name='Tail Risk (5%)',
                    opacity=0.9,
                    marker_color='rgba(255, 0, 0, 0.6)',
                    showlegend=False,
                    hovertemplate='Tail Risk<br>P&L: %{x:.2f}M USD<extra></extra>'
                ))


        fig.add_vline(
            x=mean_pnl,
            line=dict(color="blue", width=2, dash="solid"),
            annotation=dict(
                text=f"Mean: {mean_pnl:.2f}M",
                textangle=0,
                bgcolor="rgba(0, 0, 255, 0.8)",
                font=dict(color="white", size=12)
            )
        )


        fig.update_layout(
            title=dict(
                text=f'Monte Carlo P&L Distribution<br><sub>Skewness: {skewness:.2f} | Kurtosis: {kurtosis:.2f} | Std: {std_pnl:.2f}M</sub>',
                x=0.5,
                font=dict(size=16, color='white')
            ),
            xaxis=dict(
                title='P&L (M USD)',
                gridcolor='rgba(255,255,255,0.2)',
                zeroline=True,
                zerolinecolor='rgba(255,255,255,0.5)',
                zerolinewidth=2,
                tickfont=dict(color='white'),
                titlefont=dict(color='white'),
                linecolor='rgba(255,255,255,0.6)'
            ),
            yaxis=dict(
                title='Fréquence',
                gridcolor='rgba(255,255,255,0.2)',
                tickfont=dict(color='white'),
                titlefont=dict(color='white'),
                linecolor='rgba(255,255,255,0.6)'
            ),
            height=500,
            showlegend=True,
            template=None,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        logger.debug("Graphique Monte Carlo amélioré créé")

    except Exception as e:
        logger.error(f"Erreur viz Monte Carlo: {e}")
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font_size=14, font_color="red"
        )

    return fig


def calculate_component_var(sim_results: Dict) -> Dict[str, float]:
    \
\
\
\
\
\
\
\
\
    try:
        if not sim_results:
            return {}

        var_components = {}


        if 'fx_component' in sim_results:
            fx_pnl = np.array(sim_results['fx_component'])
            var_components['fx_var_95'] = float(np.percentile(fx_pnl, 5))
            var_components['fx_var_99'] = float(np.percentile(fx_pnl, 1))


        if 'rate_component' in sim_results:
            rate_pnl = np.array(sim_results['rate_component'])
            var_components['rate_var_95'] = float(np.percentile(rate_pnl, 5))
            var_components['rate_var_99'] = float(np.percentile(rate_pnl, 1))


        var_components['total_var_95'] = sim_results.get('var_95', 0)
        var_components['total_var_99'] = sim_results.get('var_99', 0)

        return var_components

    except Exception as e:
        logger.error(f"Erreur VaR composantes: {e}")
        return {}


def stress_test_portfolio(df_analytics: pd.DataFrame,
                         scenarios: Dict[str, Dict] = None) -> pd.DataFrame:
    \
\
\
\
\
\
\
\
\
\
    try:
        if df_analytics.empty:
            return pd.DataFrame()


        if scenarios is None:
            scenarios = {
                'Crise Systémique': {'fx_shock': -0.15, 'rate_shock': 0.02},
                'Resserrement Fed': {'fx_shock': -0.05, 'rate_shock': 0.015},
                'Crise Émergente': {'fx_shock': -0.08, 'rate_shock': 0.005},
                'Volatilité Extrême': {'fx_shock': -0.12, 'rate_shock': 0.01},
                'Carry Trade Unwind': {'fx_shock': -0.06, 'rate_shock': -0.01}
            }


        total_notional = df_analytics['notional'].sum()
        fx_notional = df_analytics[df_analytics['instrument'].isin(['FX_SWAP'])]['notional'].sum()
        irs_notional = df_analytics[df_analytics['instrument'] == 'IRS']['notional'].sum()

        results = []

        for scenario_name, shocks in scenarios.items():

            fx_pnl = fx_notional * shocks['fx_shock']


            rate_pnl = irs_notional * shocks['rate_shock'] * 2.0


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
    \
\
\
\
\
\
\
\
\
\
    try:
        if df_analytics.empty:
            return {}


        expo_by_ccy = df_analytics.groupby('devise_base')['notional'].sum()


        vol_mapping = {
            'USD': 0.10, 'EUR': 0.12, 'JPY': 0.15, 'GBP': 0.14,
            'CHF': 0.11, 'AUD': 0.16, 'CAD': 0.13
        }


        var_by_ccy = {}
        total_var_independent = 0

        z_score = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}[confidence_level]

        for ccy, notional in expo_by_ccy.items():
            vol = vol_mapping.get(ccy, 0.12)
            var_1d = notional * vol * z_score / np.sqrt(252)
            var_by_ccy[ccy] = var_1d
            total_var_independent += var_1d ** 2


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


def create_risk_heatmap(df_analytics: pd.DataFrame) -> go.Figure:
    \
\
\
\
\
\
\
\
\
    try:
        if df_analytics.empty:
            fig = go.Figure()
            fig.add_annotation(text="Aucune donnée pour heatmap", x=0.5, y=0.5)
            return fig


        risk_matrix = df_analytics.groupby(['paire', 'tenor']).agg({
            'notional': 'sum'
        }).reset_index()


        risk_matrix['risk_estimate'] = risk_matrix['notional'] * 0.12


        heatmap_data = risk_matrix.pivot(index='paire', columns='tenor', values='risk_estimate')
        heatmap_data = heatmap_data.fillna(0) / 1_000_000


        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Reds',
            text=heatmap_data.round(1).values,
            texttemplate='%{text}M',
            textfont=dict(size=10),
            hovertemplate='Paire: %{y}<br>Tenor: %{x}<br>Risk: %{z:.1f}M USD<extra></extra>',
            colorbar=dict(title="Risk (M USD)")
        ))

        fig.update_layout(
            title='Risk Heatmap by Currency Pair × Tenor',
            xaxis_title='Tenor',
            yaxis_title='Currency Pair',
            height=400
        )

        return fig

    except Exception as e:
        logger.error(f"Erreur heatmap risque: {e}")
        fig = go.Figure()
        fig.add_annotation(text=f"Erreur: {e}", x=0.5, y=0.5)
        return fig


def calculate_portfolio_beta(df_analytics: pd.DataFrame, market_vol: float = 0.15) -> Dict[str, float]:
    \
\
\
\
\
\
\
\
\
\
    try:
        if df_analytics.empty:
            return {}


        total_notional = df_analytics['notional'].sum()


        portfolio_weights = df_analytics.groupby('paire')['notional'].sum() / total_notional


        vol_mapping = {
            'EURUSD': 0.10, 'GBPUSD': 0.12, 'USDJPY': 0.11,
            'AUDUSD': 0.14, 'USDCAD': 0.10, 'USDCHF': 0.09,
            'NZDUSD': 0.15, 'EURGBP': 0.08, 'EURJPY': 0.12
        }


        portfolio_vol = 0
        for pair, weight in portfolio_weights.items():
            pair_vol = vol_mapping.get(pair, 0.12)
            portfolio_vol += weight * pair_vol


        beta = portfolio_vol / market_vol if market_vol > 0 else 1.0


        correlation = min(0.95, max(0.3, 0.7 + np.random.normal(0, 0.1)))


        tracking_error = portfolio_vol * np.sqrt(1 - correlation**2)

        return {
            'portfolio_beta': beta,
            'portfolio_volatility': portfolio_vol,
            'market_correlation': correlation,
            'tracking_error': tracking_error,
            'information_ratio': 0.5 / tracking_error if tracking_error > 0 else 0,
            'systematic_risk_pct': correlation**2 * 100,
            'idiosyncratic_risk_pct': (1 - correlation**2) * 100
        }

    except Exception as e:
        logger.error(f"Erreur calcul bêta: {e}")
        return {}


def create_risk_attribution_chart(df_analytics: pd.DataFrame) -> go.Figure:
    \
\
\
\
\
\
\
\
\
    try:
        if df_analytics.empty:
            fig = go.Figure()
            fig.add_annotation(text="Aucune donnée pour attribution", x=0.5, y=0.5)
            return fig


        risk_factors = []
        risk_contributions = []


        ccy_risk = df_analytics.groupby('devise_base')['notional'].sum() * 0.10 / 1_000_000
        for ccy, risk in ccy_risk.items():
            risk_factors.append(f"CCY_{ccy}")
            risk_contributions.append(risk)


        product_risk = df_analytics.groupby('instrument')['notional'].sum() * 0.08 / 1_000_000
        for product, risk in product_risk.items():
            risk_factors.append(f"PROD_{product}")
            risk_contributions.append(risk)


        if 'tenor' in df_analytics.columns:
            tenor_risk = df_analytics.groupby('tenor')['notional'].sum() * 0.05 / 1_000_000
            for tenor, risk in tenor_risk.items():
                risk_factors.append(f"TENOR_{tenor}")
                risk_contributions.append(risk)


        fig = go.Figure(go.Waterfall(
            name="Risk Attribution",
            orientation="v",
            measure=["relative"] * len(risk_factors),
            x=risk_factors,
            y=risk_contributions,
            text=[f"{v:.1f}M" for v in risk_contributions],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#ff6b6b"}},
            decreasing={"marker": {"color": "#4ecdc4"}},
        ))

        fig.update_layout(
            title="Risk Attribution by Factors (M USD)",
            showlegend=False,
            height=400
        )

        return fig

    except Exception as e:
        logger.error(f"Erreur attribution risque: {e}")
        fig = go.Figure()
        fig.add_annotation(text=f"Erreur: {e}", x=0.5, y=0.5)
        return fig


def calculate_marginal_var(df_analytics: pd.DataFrame, position_id: str = None) -> Dict[str, float]:
    \
\
\
\
\
\
\
\
\
\
    try:
        if df_analytics.empty:
            return {}


        total_var = calculate_portfolio_var_simple(df_analytics, confidence_level=0.95)
        base_var = total_var.get('var_total', 0)

        marginal_vars = {}


        for idx, row in df_analytics.iterrows():

            df_reduced = df_analytics.drop(idx)

            if not df_reduced.empty:
                reduced_var = calculate_portfolio_var_simple(df_reduced, confidence_level=0.95)
                reduced_var_total = reduced_var.get('var_total', 0)


                marginal_var = base_var - reduced_var_total

                position_key = f"{row.get('paire', 'UNKNOWN')}_{row.get('tenor', 'UNKNOWN')}"
                marginal_vars[position_key] = marginal_var / 1_000_000

        return marginal_vars

    except Exception as e:
        logger.error(f"Erreur VaR marginale: {e}")
        return {}


def create_liquidity_risk_analysis(df_analytics: pd.DataFrame) -> go.Figure:
    \
\
\
\
\
\
\
\
\
    try:
        if df_analytics.empty:
            fig = go.Figure()
            fig.add_annotation(text="Aucune donnée pour liquidité", x=0.5, y=0.5)
            return fig


        liquidity_scores = {
            'EURUSD': 1.0, 'GBPUSD': 0.9, 'USDJPY': 0.9,
            'AUDUSD': 0.7, 'USDCAD': 0.6, 'USDCHF': 0.6,
            'NZDUSD': 0.5, 'EURGBP': 0.8, 'EURJPY': 0.7
        }


        df_work = df_analytics.copy()
        df_work['liquidity_score'] = df_work['paire'].map(liquidity_scores).fillna(0.3)
        df_work['liquidity_risk'] = df_work['notional'] * (1 - df_work['liquidity_score']) / 1_000_000


        liquidity_analysis = df_work.groupby('paire').agg({
            'notional': 'sum',
            'liquidity_score': 'mean',
            'liquidity_risk': 'sum'
        }).reset_index()

        liquidity_analysis['notional_m'] = liquidity_analysis['notional'] / 1_000_000


        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=liquidity_analysis['notional_m'],
            y=liquidity_analysis['liquidity_risk'],
            mode='markers+text',
            text=liquidity_analysis['paire'],
            textposition='middle center',
            marker=dict(
                size=liquidity_analysis['notional_m'] * 3,
                color=liquidity_analysis['liquidity_score'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Liquidity Score"),
                line=dict(width=2, color='white'),
                sizemin=10
            ),
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Notional: %{x:.1f}M USD<br>'
                'Liquidity Risk: %{y:.1f}M USD<br>'
                'Liquidity Score: %{marker.color:.2f}<br>'
                '<extra></extra>'
            )
        ))

        fig.update_layout(
            title='Liquidity Risk Analysis by Currency Pair',
            xaxis_title='Notional Exposure (M USD)',
            yaxis_title='Liquidity Risk (M USD)',
            height=500,
            showlegend=False
        )

        return fig

    except Exception as e:
        logger.error(f"Erreur analyse liquidité: {e}")
        fig = go.Figure()
        fig.add_annotation(text=f"Erreur: {e}", x=0.5, y=0.5)
        return fig


def calculate_diversification_ratio(df_analytics: pd.DataFrame) -> float:
    \
\
\
\
\
\
\
\
\
    try:
        if df_analytics.empty or len(df_analytics) < 2:
            return 1.0


        total_notional = df_analytics['notional'].sum()
        weights = df_analytics.groupby('paire')['notional'].sum() / total_notional


        individual_vols = pd.Series({
            'EURUSD': 0.10, 'GBPUSD': 0.12, 'USDJPY': 0.11,
            'AUDUSD': 0.14, 'USDCAD': 0.10, 'USDCHF': 0.09
        })


        weighted_avg_vol = sum(weights.get(pair, 0) * individual_vols.get(pair, 0.12)
                              for pair in weights.index)


        correlation_matrix = np.full((len(weights), len(weights)), 0.5)
        np.fill_diagonal(correlation_matrix, 1.0)

        vol_array = np.array([individual_vols.get(pair, 0.12) for pair in weights.index])
        weight_array = weights.values

        portfolio_variance = np.dot(weight_array, np.dot(correlation_matrix * np.outer(vol_array, vol_array), weight_array))
        portfolio_vol = np.sqrt(portfolio_variance)


        diversification_ratio = weighted_avg_vol / portfolio_vol if portfolio_vol > 0 else 1.0

        return diversification_ratio

    except Exception as e:
        logger.error(f"Erreur ratio diversification: {e}")
        return 1.0