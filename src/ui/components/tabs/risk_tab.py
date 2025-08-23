"""
Onglet Risk Management pour Treasury Dashboard
Module UI séparé pour la gestion des risques
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any

try:
    from treasury.logging_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def render_risk_management_tab():
    """Onglet Risk Management principal"""
    st.subheader("🚨 Gestion des Risques")
    
    deals = st.session_state.get('generic_deals', [])
    
    if not deals:
        st.info("Importez d'abord des deals pour l'analyse des risques")
        return
    
    _render_risk_limits_configuration()
    _render_violations_analysis()
    _render_stress_tests()


def _render_risk_limits_configuration():
    """Configuration des limites de risque"""
    st.markdown("### Configuration des Limites")
    
    # Initialisation des limites par défaut
    _initialize_risk_limits()
    
    rl = st.session_state.risk_limits
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rl['max_notional_per_pair'] = st.number_input(
            "Max Notionnel/Paire (M)",
            value=rl['max_notional_per_pair'] / 1_000_000,
            step=10.0,
            min_value=1.0
        ) * 1_000_000
    
    with col2:
        rl['max_tenor_concentration'] = st.number_input(
            "Max Concentration (%)",
            value=rl['max_tenor_concentration'] * 100,
            step=5.0,
            min_value=1.0,
            max_value=100.0
        ) / 100
    
    with col3:
        rl['var_limit'] = st.number_input(
            "Limite VaR (M)",
            value=rl['var_limit'] / 1_000_000,
            step=1.0,
            min_value=0.1
        ) * 1_000_000
    
    with col4:
        rl['max_deals_per_trader'] = st.number_input(
            "Max Deals/Trader",
            value=rl.get('max_deals_per_trader', 50),
            step=5,
            min_value=1
        )


def _initialize_risk_limits():
    """Initialise les limites de risque par défaut"""
    if 'risk_limits' not in st.session_state:
        st.session_state.risk_limits = {
            'max_notional_per_pair': 100_000_000,  # 100M
            'max_tenor_concentration': 0.3,  # 30%
            'var_limit': 5_000_000,  # 5M
            'max_deals_per_trader': 50
        }
    
    # Assurer la compatibilité avec les anciennes sessions
    if 'max_deals_per_trader' not in st.session_state.risk_limits:
        st.session_state.risk_limits['max_deals_per_trader'] = 50


def _render_violations_analysis():
    """Analyse des violations de limites"""
    st.markdown("### 🔍 Analyse des Violations")
    
    df_pnl = st.session_state.get('df_pnl_enhanced')
    deals = st.session_state.get('generic_deals', [])
    violations = _detect_violations(df_pnl, deals)
    
    # Affichage des violations
    if violations:
        st.markdown("### ⚠️ Violations Détectées")
        for v in violations:
            alert_class = 'error' if v['severity'] == 'error' else 'warning'
            st.markdown(f"""
            <div class="alert-modern alert-{alert_class}">
                <strong>{v['type']}</strong><br>
                {v['detail']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-modern alert-success">
            <strong>✅ TOUTES LIMITES RESPECTÉES</strong><br>
            Aucune violation détectée
        </div>
        """, unsafe_allow_html=True)


def _detect_violations(df_pnl, deals) -> List[Dict[str, str]]:
    """Détecte les violations de limites"""
    violations = []
    rl = st.session_state.risk_limits
    
    if df_pnl is not None and not df_pnl.empty:
        # Vérification concentration par devise
        violations.extend(_check_currency_concentration(df_pnl, rl))
        
        # Vérification limites notionnelles par paire
        violations.extend(_check_notional_limits(df_pnl, rl))
    
    # Vérification nombre de deals par trader
    if deals:
        violations.extend(_check_trader_limits(deals, rl))
    
    return violations


def _check_currency_concentration(df_pnl, rl) -> List[Dict[str, str]]:
    """Vérifie la concentration par devise"""
    violations = []
    
    if 'base_currency' in df_pnl.columns and 'amount' in df_pnl.columns:
        total_notional = df_pnl['amount'].sum()
        ccy_concentrations = df_pnl.groupby('base_currency')['amount'].sum() / total_notional
        
        for ccy, concentration in ccy_concentrations.items():
            if concentration > rl['max_tenor_concentration']:
                violations.append({
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
        
        # Scénarios prédéfinis
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
        
        # Impact approximatif par type
        impacts = _compute_shock_impacts(df_pnl, fx_shock, rate_shock, credit_shock, total_notional)
        
        # Affichage métriques
        _display_stress_metrics(impacts, rl)
        
        # Visualisation
        _create_stress_visualization(impacts, fx_shock, rate_shock, credit_shock)


def _compute_shock_impacts(df_pnl, fx_shock, rate_shock, credit_shock, total_notional):
    """Calcule les impacts par composante"""
    fx_impact = 0
    rate_impact = 0
    credit_impact = 0
    
    if 'product' in df_pnl.columns:
        # Impact FX
        fx_products = ['FX_SWAP', 'FX_FORWARD']
        fx_notional = df_pnl[df_pnl['product'].isin(fx_products)]['amount'].sum()
        fx_impact = fx_notional * fx_shock
        
        # Impact taux
        rate_products = ['IRS', 'DEPOSIT', 'LOAN']
        rate_sensitive_notional = df_pnl[df_pnl['product'].isin(rate_products)]['amount'].sum()
        rate_impact = rate_sensitive_notional * rate_shock * 2.0  # Duration moyenne
        
        # Impact crédit
        credit_impact = total_notional * credit_shock * 0.1  # Sensibilité crédit
    
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
    
    # Alerte VaR
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
    global_limit = rl['max_notional_per_pair'] * 5  # Limite globale = 5x limite par paire
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
    # Calcul score composite
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
    
    # Facteur utilisation
    if 'amount' in df_pnl.columns:
        total_notional = df_pnl['amount'].sum()
        global_limit = rl['max_notional_per_pair'] * 5
        utilization = (total_notional / global_limit * 100) if global_limit > 0 else 0
        
        if utilization > 80:
            risk_score += 40
        elif utilization > 60:
            risk_score += 20
    
    # Facteur échéances urgentes
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
    
    # Facteur concentration
    if 'base_currency' in df_pnl.columns and 'amount' in df_pnl.columns:
        total_notional = df_pnl['amount'].sum()
        ccy_expo = df_pnl.groupby('base_currency')['amount'].sum()
        max_concentration = (ccy_expo.max() / total_notional) if total_notional > 0 else 0
        
        if max_concentration > rl['max_tenor_concentration']:
            risk_score += 30
        elif max_concentration > rl['max_tenor_concentration'] * 0.8:
            risk_score += 15
    
    return min(risk_score, 100)  # Cap à 100