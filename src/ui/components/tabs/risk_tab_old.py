"""
Onglet Risk Management Moderne pour Treasury Dashboard
Interface complète de gestion des risques avec analytics avancés
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

try:
    from treasury.logging_config import logger
    from treasury.risk import (
        run_monte_carlo_simulation,
        calculate_component_var,
        stress_test_portfolio,
        calculate_portfolio_var_simple
    )
    from treasury.analytics import convert_generic_to_analytics_format
    from treasury.utils.dates import VAL_DATE
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def render_risk_management_tab():
    """
    Onglet Risk Management principal - Version moderne et complète

    Structure:
    1. Dashboard Executive Summary
    2. Limites et Violations
    3. VaR Analysis (Monte Carlo + Analytique)
    4. Stress Testing
    5. Risk Decomposition
    """


    st.markdown(_get_risk_css(), unsafe_allow_html=True)


    st.markdown("""
    <div class="risk-header">
        <h2>🛡️ Risk Management Dashboard</h2>
        <p>Surveillance en temps réel des risques de marché</p>
    </div>
    """, unsafe_allow_html=True)


    df_pnl = st.session_state.get('df_pnl_enhanced')
    deals = st.session_state.get('generic_deals', [])

    if not deals or df_pnl is None or df_pnl.empty:
        _render_no_data_state()
        return


    _initialize_risk_parameters()


    df_analytics = convert_generic_to_analytics_format(df_pnl)


    tab_summary, tab_limits, tab_var, tab_stress, tab_decomp = st.tabs([
        "📊 Executive Summary",
        "⚠️ Limits & Violations",
        "📈 VaR Analysis",
        "💥 Stress Testing",
        "🧩 Risk Decomposition"
    ])

    with tab_summary:
        _render_executive_summary(df_pnl, df_analytics)

    with tab_limits:
        _render_limits_and_violations(df_pnl, deals)

    with tab_var:
        _render_var_analysis(df_analytics)

    with tab_stress:
        _render_stress_testing(df_analytics)

    with tab_decomp:
        _render_risk_decomposition(df_pnl, df_analytics)


def _get_risk_css() -> str:
    """CSS moderne pour l'onglet risk"""
    return """
    <style>
    .risk-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
    }

    .risk-metric-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }

    .risk-metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }

    .risk-metric-label {
        font-size: 12px;
        color: #7f8c8d;
        text-transform: uppercase;
    }

    .risk-alert {
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid;
    }

    .risk-alert-critical {
        background-color: #fdf2f2;
        border-color: #e53e3e;
        color: #c53030;
    }

    .risk-alert-warning {
        background-color: #fffbf0;
        border-color: #f6ad55;
        color: #c05621;
    }

    .risk-alert-info {
        background-color: #f0f9ff;
        border-color: #4299e1;
        color: #2b6cb0;
    }

    .risk-alert-success {
        background-color: #f0fff4;
        border-color: #48bb78;
        color: #2f855a;
    }

    .risk-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    </style>
    """


def _render_no_data_state():
    """Affichage quand pas de données"""
    st.markdown("""
    <div class="risk-alert risk-alert-info">
        <h3>📊 Données Required</h3>
        <p>Importez des deals et calculez les PnL pour accéder aux analyses de risque.</p>
        <ul>
            <li>Minimum 5 deals requis pour l'analyse VaR</li>
            <li>PnL Enhanced nécessaire pour la décomposition</li>
            <li>Données de marché requises pour les stress tests</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def _initialize_risk_parameters():
    """Initialise les paramètres de risque par défaut"""
    if 'risk_params' not in st.session_state:
        st.session_state.risk_params = {

            'global_var_limit_m': 10.0,
            'max_concentration_pct': 25.0,
            'max_notional_per_ccy_m': 50.0,


            'var_confidence_levels': [0.95, 0.99],
            'monte_carlo_simulations': 10000,
            'var_horizon_days': 1,


            'stress_scenarios': {
                'Market Crash 2008': {'fx_shock': -0.20, 'rate_shock': 0.03, 'vol_mult': 3.0},
                'COVID-19 2020': {'fx_shock': -0.15, 'rate_shock': -0.02, 'vol_mult': 2.5},
                'Fed Tightening': {'fx_shock': -0.08, 'rate_shock': 0.02, 'vol_mult': 1.5},
                'EM Crisis': {'fx_shock': -0.12, 'rate_shock': 0.01, 'vol_mult': 2.0},
                'European Crisis': {'fx_shock': -0.10, 'rate_shock': 0.015, 'vol_mult': 1.8}
            },


            'alert_thresholds': {
                'var_usage_warning': 0.8,
                'var_usage_critical': 0.95,
                'concentration_warning': 0.20,
                'concentration_critical': 0.25
            }
        }


def _render_executive_summary(df_pnl: pd.DataFrame, df_analytics: pd.DataFrame):
    """Dashboard executive summary avec KPIs principaux"""
    st.markdown("### 📊 Risk Dashboard - Vue d'ensemble")


    total_exposure = df_pnl['amount'].sum() if 'amount' in df_pnl.columns else 0
    total_pnl = df_pnl['total_pnl'].sum() if 'total_pnl' in df_pnl.columns else 0
    num_positions = len(df_pnl)


    var_simple = calculate_portfolio_var_simple(df_analytics, confidence_level=0.95)
    current_var = var_simple.get('var_total_m', 0)
    var_limit = st.session_state.risk_params['global_var_limit_m']
    var_usage = (current_var / var_limit) * 100 if var_limit > 0 else 0


    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="risk-metric-card">
            <div class="risk-metric-label">Total Exposure</div>
            <div class="risk-metric-value">${total_exposure/1e6:.1f}M</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        pnl_color = "#27ae60" if total_pnl >= 0 else "#e74c3c"
        st.markdown(f"""
        <div class="risk-metric-card">
            <div class="risk-metric-label">Current PnL</div>
            <div class="risk-metric-value" style="color: {pnl_color}">
                ${total_pnl/1e6:+.2f}M
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        var_color = "#e74c3c" if var_usage > 95 else "#f39c12" if var_usage > 80 else "#27ae60"
        st.markdown(f"""
        <div class="risk-metric-card">
            <div class="risk-metric-label">VaR 95% (1D)</div>
            <div class="risk-metric-value" style="color: {var_color}">
                ${current_var:.2f}M
            </div>
            <small style="color: {var_color};">{var_usage:.1f}% of limit</small>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="risk-metric-card">
            <div class="risk-metric-label">Active Positions</div>
            <div class="risk-metric-value">{num_positions}</div>
        </div>
        """, unsafe_allow_html=True)


    col_left, col_right = st.columns(2)

    with col_left:

        if 'base_currency' in df_pnl.columns:
            fig_expo = _create_currency_exposure_chart(df_pnl)
            st.plotly_chart(fig_expo, use_container_width=True)

    with col_right:

        if 'total_pnl' in df_pnl.columns:
            fig_pnl_dist = _create_pnl_distribution_chart(df_pnl)
            st.plotly_chart(fig_pnl_dist, use_container_width=True)


def _render_limits_and_violations(df_pnl: pd.DataFrame, deals: List[Dict]):
    """Configuration des limites et détection des violations"""
    st.markdown("### ⚠️ Risk Limits Configuration & Monitoring")


    with st.expander("🔧 Configure Risk Limits", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.session_state.risk_params['global_var_limit_m'] = st.number_input(
                "Global VaR Limit (M USD)",
                value=st.session_state.risk_params['global_var_limit_m'],
                min_value=1.0, step=1.0
            )

        with col2:
            st.session_state.risk_params['max_concentration_pct'] = st.number_input(
                "Max Currency Concentration (%)",
                value=st.session_state.risk_params['max_concentration_pct'],
                min_value=5.0, max_value=100.0, step=5.0
            )

        with col3:
            st.session_state.risk_params['max_notional_per_ccy_m'] = st.number_input(
                "Max Notional per Currency (M USD)",
                value=st.session_state.risk_params['max_notional_per_ccy_m'],
                min_value=1.0, step=5.0
            )


    violations = _detect_modern_violations(df_pnl, deals)

    if violations:
        st.markdown("#### 🚨 Active Violations")
        for violation in violations:
            alert_class = f"risk-alert-{violation['severity']}"
            st.markdown(f"""
            <div class="risk-alert {alert_class}">
                <strong>{violation['type']}</strong><br>
                {violation['message']}<br>
                <small>Current: {violation['current']} | Limit: {violation['limit']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="risk-alert risk-alert-success">
            <strong>✅ All Limits Respected</strong><br>
            No violations detected across all risk categories.
        </div>
        """, unsafe_allow_html=True)


    if violations:
        fig_compliance = _create_compliance_dashboard(violations)
        st.plotly_chart(fig_compliance, use_container_width=True)


def _render_var_analysis(df_analytics: pd.DataFrame):
    """Analyse VaR complète avec Monte Carlo et méthodes analytiques"""
    st.markdown("### 📈 Value-at-Risk Analysis")


    col_param1, col_param2, col_param3 = st.columns(3)

    with col_param1:
        confidence_level = st.selectbox(
            "Confidence Level",
            [0.90, 0.95, 0.99],
            index=1,
            format_func=lambda x: f"{x*100:.0f}%"
        )

    with col_param2:
        horizon_days = st.selectbox("Time Horizon", [1, 5, 10], index=0)

    with col_param3:
        n_simulations = st.selectbox(
            "Monte Carlo Simulations",
            [1000, 5000, 10000, 50000],
            index=2
        )

    if st.button("🔄 Calculate VaR", type="primary"):
        with st.spinner("Running VaR calculations..."):

            mc_results = run_monte_carlo_simulation(
                df_analytics,
                n_simulations=n_simulations
            )


            var_analytical = calculate_portfolio_var_simple(
                df_analytics,
                confidence_level=confidence_level
            )


            st.session_state['var_results'] = {
                'monte_carlo': mc_results,
                'analytical': var_analytical,
                'params': {
                    'confidence': confidence_level,
                    'horizon': horizon_days,
                    'simulations': n_simulations
                }
            }


    if 'var_results' in st.session_state:
        _display_var_results(st.session_state['var_results'])


def _render_stress_testing(df_analytics: pd.DataFrame):
    """Module de stress testing avec scénarios prédéfinis et custom"""
    st.markdown("### 💥 Stress Testing & Scenario Analysis")


    scenarios = st.session_state.risk_params['stress_scenarios']

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_scenarios = st.multiselect(
            "Select Stress Scenarios",
            list(scenarios.keys()),
            default=list(scenarios.keys())[:3]
        )

    with col2:
        if st.button("🚀 Run Stress Tests", type="primary"):
            if selected_scenarios:
                with st.spinner("Running stress tests..."):

                    filtered_scenarios = {k: v for k, v in scenarios.items() if k in selected_scenarios}


                    stress_results = stress_test_portfolio(df_analytics, filtered_scenarios)
                    st.session_state['stress_results'] = stress_results


    with st.expander("🎛️ Custom Scenario Builder"):
        col_cust1, col_cust2, col_cust3 = st.columns(3)

        with col_cust1:
            custom_fx_shock = st.slider("FX Shock (%)", -50, 50, -10, 1) / 100

        with col_cust2:
            custom_rate_shock = st.slider("Rate Shock (bps)", -500, 500, 100, 25) / 10000

        with col_cust3:
            custom_vol_mult = st.slider("Volatility Multiplier", 0.5, 5.0, 1.5, 0.1)

        if st.button("Test Custom Scenario"):
            custom_scenario = {
                'Custom': {
                    'fx_shock': custom_fx_shock,
                    'rate_shock': custom_rate_shock,
                    'vol_mult': custom_vol_mult
                }
            }
            custom_results = stress_test_portfolio(df_analytics, custom_scenario)
            st.session_state['custom_stress_results'] = custom_results


    if 'stress_results' in st.session_state:
        _display_stress_results(st.session_state['stress_results'])

    if 'custom_stress_results' in st.session_state:
        st.markdown("#### Custom Scenario Results")
        _display_stress_results(st.session_state['custom_stress_results'])


def _render_risk_decomposition(df_pnl: pd.DataFrame, df_analytics: pd.DataFrame):
    """Décomposition détaillée des risques par facteur"""
    st.markdown("### 🧩 Risk Factor Decomposition")


    col1, col2 = st.columns(2)

    with col1:

        if 'base_currency' in df_pnl.columns and 'amount' in df_pnl.columns:
            fig_risk_ccy = _create_risk_by_currency_chart(df_pnl)
            st.plotly_chart(fig_risk_ccy, use_container_width=True)

    with col2:

        if 'maturity_date' in df_pnl.columns:
            fig_risk_maturity = _create_risk_by_maturity_chart(df_pnl)
            st.plotly_chart(fig_risk_maturity, use_container_width=True)


    if 'var_results' in st.session_state and st.session_state['var_results']['monte_carlo']:
        mc_results = st.session_state['var_results']['monte_carlo']
        component_var = calculate_component_var(mc_results)

        if component_var:
            fig_var_decomp = _create_var_decomposition_chart(component_var)
            st.plotly_chart(fig_var_decomp, use_container_width=True)


    with st.expander("📊 Risk Sensitivities (Greeks Approximation)"):
        _render_risk_sensitivities(df_pnl, df_analytics)


def _detect_modern_violations(df_pnl: pd.DataFrame, deals: List[Dict]) -> List[Dict]:
    """Détection moderne des violations avec contexte enrichi"""
    violations = []
    params = st.session_state.risk_params

    if df_pnl.empty:
        return violations


    if 'var_results' in st.session_state:
        var_result = st.session_state['var_results']['analytical']
        current_var = var_result.get('var_total_m', 0)
        var_limit = params['global_var_limit_m']

        if current_var > var_limit:
            violations.append({
                'type': 'VaR Limit Breach',
                'severity': 'critical',
                'message': f'Portfolio VaR exceeds authorized limit',
                'current': f'{current_var:.2f}M',
                'limit': f'{var_limit:.2f}M'
            })
        elif current_var > var_limit * params['alert_thresholds']['var_usage_warning']:
            violations.append({
                'type': 'VaR Usage Warning',
                'severity': 'warning',
                'message': f'Portfolio VaR approaching limit',
                'current': f'{current_var:.2f}M',
                'limit': f'{var_limit:.2f}M'
            })


    if 'base_currency' in df_pnl.columns and 'amount' in df_pnl.columns:
        total_exposure = df_pnl['amount'].sum()
        ccy_exposures = df_pnl.groupby('base_currency')['amount'].sum()

        for ccy, exposure in ccy_exposures.items():
            concentration_pct = (exposure / total_exposure) * 100
            max_concentration = params['max_concentration_pct']

            if concentration_pct > max_concentration:
                violations.append({
                    'type': f'Currency Concentration - {ccy}',
                    'severity': 'warning',
                    'message': f'Excessive concentration in {ccy}',
                    'current': f'{concentration_pct:.1f}%',
                    'limit': f'{max_concentration:.1f}%'
                })

    return violations




def _create_currency_exposure_chart(df_pnl: pd.DataFrame) -> go.Figure:
    """Graphique d'exposition par devise"""
    if 'base_currency' not in df_pnl.columns or 'amount' not in df_pnl.columns:
        return go.Figure().add_annotation(text="Data not available", x=0.5, y=0.5)

    ccy_expo = df_pnl.groupby('base_currency')['amount'].sum() / 1e6

    fig = px.pie(
        values=ccy_expo.values,
        names=ccy_expo.index,
        title="Exposure by Currency (M USD)"
    )
    fig.update_layout(height=300, showlegend=True)
    return fig


def _create_pnl_distribution_chart(df_pnl: pd.DataFrame) -> go.Figure:
    """Distribution des PnL par position"""
    if 'total_pnl' not in df_pnl.columns:
        return go.Figure().add_annotation(text="PnL data not available", x=0.5, y=0.5)

    fig = px.histogram(
        df_pnl,
        x='total_pnl',
        nbins=20,
        title="PnL Distribution"
    )
    fig.update_xaxes(title="PnL (USD)")
    fig.update_yaxes(title="Count")
    fig.update_layout(height=300)
    return fig


def _create_compliance_dashboard(violations: List[Dict]) -> go.Figure:
    """Dashboard de compliance"""
    severity_counts = {}
    for v in violations:
        severity_counts[v['severity']] = severity_counts.get(v['severity'], 0) + 1

    fig = px.bar(
        x=list(severity_counts.keys()),
        y=list(severity_counts.values()),
        title="Violations by Severity",
        color=list(severity_counts.keys()),
        color_discrete_map={
            'critical': '#e74c3c',
            'warning': '#f39c12',
            'info': '#3498db'
        }
    )
    fig.update_layout(height=300, showlegend=False)
    return fig


def _display_var_results(var_results: Dict):
    """Affichage des résultats VaR"""
    mc_results = var_results.get('monte_carlo', {})
    analytical = var_results.get('analytical', {})

    if mc_results:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Monte Carlo VaR")
            var_95_mc = mc_results.get('var_95', 0) / 1e6
            var_99_mc = mc_results.get('var_99', 0) / 1e6

            st.metric("VaR 95%", f"${var_95_mc:.2f}M")
            st.metric("VaR 99%", f"${var_99_mc:.2f}M")

            if 'expected_shortfall' in mc_results:
                es = mc_results['expected_shortfall'] / 1e6
                st.metric("Expected Shortfall", f"${es:.2f}M")

        with col2:
            st.markdown("#### Analytical VaR")
            if analytical:
                var_analytical = analytical.get('var_total_m', 0)
                st.metric("VaR Analytical", f"${var_analytical:.2f}M")


        if 'total_pnl' in mc_results:
            from treasury.risk import create_monte_carlo_distribution
            fig_mc = create_monte_carlo_distribution(mc_results)
            st.plotly_chart(fig_mc, use_container_width=True)


def _display_stress_results(stress_results: pd.DataFrame):
    """Affichage des résultats de stress testing"""
    if stress_results.empty:
        st.warning("No stress test results available")
        return


    fig = px.bar(
        stress_results,
        x='Scenario',
        y='Total_PnL_M',
        title="Stress Test Results",
        color='Total_PnL_M',
        color_continuous_scale='RdYlGn_r'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


    st.dataframe(
        stress_results.round(2),
        use_container_width=True
    )


def _create_risk_by_currency_chart(df_pnl: pd.DataFrame) -> go.Figure:
    """Risk attribution par devise"""
    if 'base_currency' not in df_pnl.columns:
        return go.Figure().add_annotation(text="Currency data not available", x=0.5, y=0.5)


    risk_by_ccy = df_pnl.groupby('base_currency')['amount'].sum() / 1e6

    fig = px.bar(
        x=risk_by_ccy.index,
        y=risk_by_ccy.values,
        title="Risk Exposure by Currency (M USD)"
    )
    fig.update_layout(height=300)
    return fig


def _create_risk_by_maturity_chart(df_pnl: pd.DataFrame) -> go.Figure:
    """Risk attribution par maturité"""
    if 'maturity_date' not in df_pnl.columns:
        return go.Figure().add_annotation(text="Maturity data not available", x=0.5, y=0.5)


    df_temp = df_pnl.copy()
    df_temp['days_to_maturity'] = (pd.to_datetime(df_temp['maturity_date']) - VAL_DATE).dt.days

    bins = [0, 30, 90, 180, 365, 999999]
    labels = ['0-30d', '30-90d', '90-180d', '180d-1Y', '1Y+']
    df_temp['maturity_bucket'] = pd.cut(df_temp['days_to_maturity'], bins=bins, labels=labels)

    risk_by_maturity = df_temp.groupby('maturity_bucket')['amount'].sum() / 1e6

    fig = px.bar(
        x=risk_by_maturity.index,
        y=risk_by_maturity.values,
        title="Risk Exposure by Maturity (M USD)"
    )
    fig.update_layout(height=300)
    return fig


def _create_var_decomposition_chart(component_var: Dict) -> go.Figure:
    """Décomposition de la VaR par composante"""
    components = []
    values = []

    for key, value in component_var.items():
        if 'var_95' in key:
            component_name = key.replace('_var_95', '').replace('_', ' ').title()
            components.append(component_name)
            values.append(abs(value) / 1e6)

    if not components:
        return go.Figure().add_annotation(text="VaR components not available", x=0.5, y=0.5)

    fig = px.bar(
        x=components,
        y=values,
        title="VaR Decomposition by Risk Factor (M USD)"
    )
    fig.update_layout(height=300)
    return fig


def _render_risk_sensitivities(df_pnl: pd.DataFrame, df_analytics: pd.DataFrame):
    """Affichage des sensibilités aux risques (Greeks approximation)"""
    st.markdown("#### Greeks Approximation")


    if 'amount' in df_pnl.columns:
        total_notional = df_pnl['amount'].sum()


        delta_1pct = total_notional * 0.01


        avg_duration = 2.0
        dv01 = total_notional * avg_duration * 0.0001

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Delta (1% FX move)",
                f"${delta_1pct/1e6:.2f}M",
                help="Approximate P&L impact of 1% FX move"
            )

        with col2:
            st.metric(
                "DV01 (1bp rate move)",
                f"${dv01/1e6:.3f}M",
                help="Approximate P&L impact of 1bp rate move"
            )

        with col3:

            if 'total_pnl' in df_pnl.columns and len(df_pnl) > 1:
                portfolio_vol = df_pnl['total_pnl'].std()
                st.metric(
                    "Portfolio Volatility",
                    f"${portfolio_vol/1e6:.2f}M",
                    help="Historical PnL volatility"
                )
                    'type': 'Concentration Devise',
                    'detail': f"{ccy}: {concentration:.1%} > {rl['max_tenor_concentration']:.1%}",
                    'severity': 'error'
                })

    return violations


def _check_notional_limits(df_pnl, rl) -> List[Dict[str, str]]:
    """Vérifie les limites notionnelles par paire"""
    violations = []

    if 'pair_currency' in df_pnl.columns and 'amount' in df_pnl.columns:
        pair_notionals = df_pnl.groupby('pair_currency')['amount'].sum()

        for pair, notional in pair_notionals.items():
            if notional > rl['max_notional_per_pair']:
                violations.append({
                    'type': 'Limite Notionnelle',
                    'detail': f"{pair}: ${notional/1_000_000:.1f}M > ${rl['max_notional_per_pair']/1_000_000:.1f}M",
                    'severity': 'error'
                })

    return violations


def _check_trader_limits(deals, rl) -> List[Dict[str, str]]:
    """Vérifie les limites par trader"""
    violations = []

    if hasattr(deals[0], 'trader_id'):
        trader_counts = {}
        for deal in deals:
            trader_id = getattr(deal, 'trader_id', 'Unknown')
            trader_counts[trader_id] = trader_counts.get(trader_id, 0) + 1

        max_deals_limit = rl.get('max_deals_per_trader', 50)
        for trader, count in trader_counts.items():
            if count > max_deals_limit:
                violations.append({
                    'type': 'Limite Deals/Trader',
                    'detail': f"{trader}: {count} deals > {max_deals_limit}",
                    'severity': 'warning'
                })

    return violations


def _render_stress_tests():
    """Section stress tests interactifs"""
    st.markdown("---")
    st.markdown("### 🧪 Stress Tests Interactifs")

    df_pnl = st.session_state.get('df_pnl_enhanced')

    if df_pnl is None or df_pnl.empty:
        st.info("Calculez d'abord les PnL pour les stress tests")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**Paramètres de Choc:**")
        fx_shock = st.slider("Choc FX (%)", -30, 30, -10, step=1, key="fx_shock_risk") / 100
        rate_shock = st.slider("Choc Taux (bps)", -200, 200, 50, step=10, key="rate_shock_risk") / 10000
        credit_shock = st.slider("Choc Crédit (bps)", -100, 300, 25, step=5, key="credit_shock_risk") / 10000


        _render_predefined_scenarios()

    with col2:
        if st.button("🧪 Calculer Stress", type="primary", key="stress_button_risk"):
            _calculate_stress_impact(df_pnl, fx_shock, rate_shock, credit_shock)


def _render_predefined_scenarios():
    """Affiche les scénarios prédéfinis"""
    st.markdown("**Scénarios Prédéfinis:**")
    scenarios = {
        "Crise Systémique": {"fx": -0.15, "rate": 0.02, "credit": 0.02},
        "Resserrement Fed": {"fx": -0.05, "rate": 0.015, "credit": 0.005},
        "Crise Émergente": {"fx": -0.08, "rate": 0.005, "credit": 0.015},
        "Volatilité Extrême": {"fx": -0.12, "rate": 0.01, "credit": 0.01},
        "Carry Trade Unwind": {"fx": -0.06, "rate": -0.01, "credit": 0.005}
    }

    selected_scenario = st.selectbox(
        "Choisir un scénario:",
        ["Personnalisé"] + list(scenarios.keys()),
        key="scenario_selector"
    )

    if selected_scenario != "Personnalisé":
        scenario_data = scenarios[selected_scenario]
        st.info(f"""Scénario '{selected_scenario}':
        FX {scenario_data['fx']:.1%},
        Taux {scenario_data['rate']*10000:.0f}bp,
        Crédit {scenario_data['credit']*10000:.0f}bp""")


def _calculate_stress_impact(df_pnl, fx_shock, rate_shock, credit_shock):
    """Calcule l'impact des stress tests"""
    with st.spinner("Calcul stress tests..."):
        total_notional = df_pnl['amount'].sum() if 'amount' in df_pnl.columns else 0
        rl = st.session_state.risk_limits


        impacts = _compute_shock_impacts(df_pnl, fx_shock, rate_shock, credit_shock, total_notional)


        _display_stress_metrics(impacts, rl)


        _create_stress_visualization(impacts, fx_shock, rate_shock, credit_shock)


def _compute_shock_impacts(df_pnl, fx_shock, rate_shock, credit_shock, total_notional):
    """Calcule les impacts par composante"""
    fx_impact = 0
    rate_impact = 0
    credit_impact = 0

    if 'product' in df_pnl.columns:

        fx_products = ['FX_SWAP', 'FX_FORWARD']
        fx_notional = df_pnl[df_pnl['product'].isin(fx_products)]['amount'].sum()
        fx_impact = fx_notional * fx_shock


        rate_products = ['IRS', 'DEPOSIT', 'LOAN']
        rate_sensitive_notional = df_pnl[df_pnl['product'].isin(rate_products)]['amount'].sum()
        rate_impact = rate_sensitive_notional * rate_shock * 2.0


        credit_impact = total_notional * credit_shock * 0.1

    total_impact = fx_impact + rate_impact + credit_impact

    return {
        'fx': fx_impact,
        'rate': rate_impact,
        'credit': credit_impact,
        'total': total_impact
    }


def _display_stress_metrics(impacts, rl):
    """Affiche les métriques de stress"""
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Impact FX", f"${impacts['fx']/1_000_000:+.1f}M")
    col_b.metric("Impact Taux", f"${impacts['rate']/1_000_000:+.1f}M")
    col_c.metric("Impact Crédit", f"${impacts['credit']/1_000_000:+.1f}M")
    col_d.metric("Impact Total", f"${impacts['total']/1_000_000:+.1f}M")


    if abs(impacts['total']) > rl['var_limit']:
        st.markdown(f"""
        <div class="alert-modern alert-error">
            🚨 STRESS DÉPASSE LIMITE VaR: ${abs(impacts['total'])/1_000_000:.1f}M > ${rl['var_limit']/1_000_000:.1f}M
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-modern alert-success">
            ✅ Stress dans les limites VaR: ${abs(impacts['total'])/1_000_000:.1f}M ≤ ${rl['var_limit']/1_000_000:.1f}M
        </div>
        """, unsafe_allow_html=True)


def _create_stress_visualization(impacts, fx_shock, rate_shock, credit_shock):
    """Crée la visualisation des stress tests"""
    fig_stress = go.Figure()
    fig_stress.add_trace(go.Bar(
        name='Impact par Composante',
        x=['FX Shock', 'Rate Shock', 'Credit Shock', 'Total'],
        y=[impacts['fx']/1_000_000, impacts['rate']/1_000_000,
           impacts['credit']/1_000_000, impacts['total']/1_000_000],
        marker_color=['#440154', '#31688e', '#35b779', '#fde725'],
        text=[f"{impacts['fx']/1_000_000:+.1f}M", f"{impacts['rate']/1_000_000:+.1f}M",
              f"{impacts['credit']/1_000_000:+.1f}M", f"{impacts['total']/1_000_000:+.1f}M"],
        textposition='auto'
    ))
    fig_stress.update_layout(
        title=f'🧪 Impact Stress Test: FX {fx_shock:.1%}, Taux {rate_shock*10000:.0f}bp, Crédit {credit_shock*10000:.0f}bp',
        yaxis_title='Impact (M USD)',
        height=400,
        showlegend=False,
        template='plotly_dark'
    )
    st.plotly_chart(fig_stress, use_container_width=True, key="stress_interactive_chart")


def _render_real_time_monitoring():
    """Section monitoring temps réel"""
    st.markdown("---")
    st.markdown("### Monitoring Temps Réel")

    df_pnl = st.session_state.get('df_pnl_enhanced')

    if df_pnl is None or df_pnl.empty:
        st.info("Calculez d'abord les PnL pour le monitoring")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        _render_global_utilization_card(df_pnl)

    with col2:
        _render_urgent_deals_card(df_pnl)

    with col3:
        _render_concentration_card(df_pnl)

    with col4:
        _render_risk_score_card(df_pnl)


def _render_global_utilization_card(df_pnl):
    """Carte utilisation globale"""
    rl = st.session_state.risk_limits
    total_notional = df_pnl['amount'].sum() if 'amount' in df_pnl.columns else 0
    global_limit = rl['max_notional_per_pair'] * 5
    utilization = (total_notional / global_limit * 100) if global_limit > 0 else 0

    if utilization > 80:
        color, text = '#ff6b6b', '🚨 CRITIQUE'
    elif utilization > 60:
        color, text = '#ffa726', '⚠️ ATTENTION'
    else:
        color, text = '#35b779', '✅ OK'

    st.markdown(f"""
    <div class="modern-card" style="background:{color};color:white;text-align:center">
        <h4>Utilisation Globale</h4>
        <h2>{utilization:.1f}%</h2>
        <p>{text}</p>
    </div>
    """, unsafe_allow_html=True)


def _render_urgent_deals_card(df_pnl):
    """Carte deals urgents"""
    urgent_count = 0

    if 'maturity_date' in df_pnl.columns:
        try:
            from treasury.utils.dates import VAL_DATE
        except ImportError:
            VAL_DATE = pd.Timestamp.now()

        df_temp = df_pnl.copy()
        df_temp['days_to_maturity'] = (pd.to_datetime(df_temp['maturity_date']) - VAL_DATE).dt.days
        urgent_count = len(df_temp[df_temp['days_to_maturity'] <= 7])

    if urgent_count > 5:
        color, text = '#ff6b6b', '🚨 URGENT'
    elif urgent_count > 2:
        color, text = '#ffa726', '⚠️ SURVEILLER'
    else:
        color, text = '#35b779', '✅ SOUS CONTRÔLE'

    st.markdown(f"""
    <div class="modern-card" style="background:{color};color:white;text-align:center">
        <h4>Échéances ≤ 7j</h4>
        <h2>{urgent_count}</h2>
        <p>{text}</p>
    </div>
    """, unsafe_allow_html=True)


def _render_concentration_card(df_pnl):
    """Carte concentration maximale"""
    rl = st.session_state.risk_limits
    max_concentration = 0

    if 'base_currency' in df_pnl.columns and 'amount' in df_pnl.columns:
        total_notional = df_pnl['amount'].sum()
        ccy_expo = df_pnl.groupby('base_currency')['amount'].sum()
        max_concentration = (ccy_expo.max() / total_notional * 100) if total_notional > 0 else 0

    if max_concentration > rl['max_tenor_concentration'] * 100:
        color, text = '#ff6b6b', '🚨 LIMITE DÉPASSÉE'
    elif max_concentration > rl['max_tenor_concentration'] * 80:
        color, text = '#ffa726', '⚠️ PROCHE LIMITE'
    else:
        color, text = '#35b779', '✅ OK'

    st.markdown(f"""
    <div class="modern-card" style="background:{color};color:white;text-align:center">
        <h4>Concentration Max</h4>
        <h2>{max_concentration:.1f}%</h2>
        <p>{text}</p>
    </div>
    """, unsafe_allow_html=True)


def _render_risk_score_card(df_pnl):
    """Carte score de risque global"""

    risk_score = _calculate_composite_risk_score(df_pnl)

    if risk_score >= 70:
        color, text = '#ff6b6b', '🚨 RISQUE ÉLEVÉ'
    elif risk_score >= 40:
        color, text = '#ffa726', '⚠️ RISQUE MODÉRÉ'
    else:
        color, text = '#35b779', '✅ RISQUE FAIBLE'

    st.markdown(f"""
    <div class="modern-card" style="background:{color};color:white;text-align:center">
        <h4>Score Risque Global</h4>
        <h2>{risk_score}/100</h2>
        <p>{text}</p>
    </div>
    """, unsafe_allow_html=True)


def _calculate_composite_risk_score(df_pnl) -> int:
    """Calcule un score de risque composite"""
    risk_score = 0
    rl = st.session_state.risk_limits


    if 'amount' in df_pnl.columns:
        total_notional = df_pnl['amount'].sum()
        global_limit = rl['max_notional_per_pair'] * 5
        utilization = (total_notional / global_limit * 100) if global_limit > 0 else 0

        if utilization > 80:
            risk_score += 40
        elif utilization > 60:
            risk_score += 20


    if 'maturity_date' in df_pnl.columns:
        try:
            from treasury.utils.dates import VAL_DATE
            df_temp = df_pnl.copy()
            df_temp['days_to_maturity'] = (pd.to_datetime(df_temp['maturity_date']) - VAL_DATE).dt.days
            urgent_count = len(df_temp[df_temp['days_to_maturity'] <= 7])

            if urgent_count > 5:
                risk_score += 30
            elif urgent_count > 2:
                risk_score += 15
        except:
            pass


    if 'base_currency' in df_pnl.columns and 'amount' in df_pnl.columns:
        total_notional = df_pnl['amount'].sum()
        ccy_expo = df_pnl.groupby('base_currency')['amount'].sum()
        max_concentration = (ccy_expo.max() / total_notional) if total_notional > 0 else 0

        if max_concentration > rl['max_tenor_concentration']:
            risk_score += 30
        elif max_concentration > rl['max_tenor_concentration'] * 0.8:
            risk_score += 15

    return min(risk_score, 100)