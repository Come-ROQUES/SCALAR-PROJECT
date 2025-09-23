\
\
\
\

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List


from treasury.config import settings, UIConfig
from treasury.cache import cache_manager, get_cache_status, clear_all_caches

try:
    from treasury.logging_config import get_recent_logs
except ImportError:
    def get_recent_logs(n): return []


def render_sidebar():
    \
    st.sidebar.markdown(
        """
        <style>
        section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:
        _render_theme_selector()
        _render_portfolio_status()
        _render_pnl_configuration()
        _render_cache_monitoring()
        _render_real_time_monitoring()
        _render_debug_section()


def _render_theme_selector():
    \
    st.markdown("### 🎨 Theme")


    from treasury.config import THEME_CONFIGS


    theme_options = {
        'liquid_glass': '✨ Liquid Glass',
        'professional_dark': '🏢 Professional Dark'
    }

    current_theme = st.session_state.get('ui_theme', 'liquid_glass')

    selected_theme = st.selectbox(
        "Style Interface",
        options=list(theme_options.keys()),
        format_func=lambda x: theme_options[x],
        index=list(theme_options.keys()).index(current_theme),
        help="Choisissez le style de l'interface"
    )


    if selected_theme != current_theme:
        st.session_state.ui_theme = selected_theme
        st.success(f"Thème changé: {theme_options[selected_theme]}")
        st.rerun()


    theme_config = THEME_CONFIGS.get(selected_theme, {})
    if theme_config.get('description'):
        st.caption(theme_config['description'])

    st.markdown("---")


def _render_portfolio_status():
    \
    st.markdown("### Status Portfolio")
    deals = st.session_state.get('generic_deals', [])
    deal_count = len(deals)

    if deal_count > 0:
        st.markdown(
            UIConfig.get_status_badge_html("success", f"Total: {deal_count} deals"),
            unsafe_allow_html=True
        )


        deal_types = {}
        for deal in deals:
            deal_types[deal.product] = deal_types.get(deal.product, 0) + 1

        for product, count in deal_types.items():
            st.markdown(
                UIConfig.get_status_badge_html("info", f"{product}: {count}"),
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            UIConfig.get_status_badge_html("error", "Aucun deal"),
            unsafe_allow_html=True
        )


def _render_pnl_configuration():
    \
    st.markdown("---")
    st.subheader("Configuration PnL")

    with st.expander("Paramètres Calculs"):
        config = st.session_state.get('pnl_config', {})

        config['calculate_accrued'] = st.checkbox(
            "Calculer Accrued PnL",
            value=config.get('calculate_accrued', True),
            help="PnL d'intérêts courus"
        )

        config['calculate_mtm'] = st.checkbox(
            "Calculer MTM PnL",
            value=config.get('calculate_mtm', True),
            help="PnL de valorisation mark-to-market"
        )

        config['calculate_rate'] = st.checkbox(
            "Calculer Rate PnL",
            value=config.get('calculate_rate', True),
            help="PnL de mouvement de taux"
        )

        config['calculate_liquidity'] = st.checkbox(
            "Calculer Liquidity PnL",
            value=config.get('calculate_liquidity', True),
            help="PnL d'ajustement de liquidité"
        )

        ois_override = st.number_input(
            "OIS Rate Override (test)",
            value=0.0,
            step=0.001,
            format="%.4f",
            help="Laisser 0 pour calcul automatique"
        )

        config['ois_rate_override'] = ois_override if ois_override > 0 else None
        st.session_state.pnl_config = config


def _render_cache_monitoring():
    \
    st.markdown("---")
    st.subheader("⚡ Cache & Performance")


    cache_stats = cache_manager.get_cache_info()


    if cache_stats['total_requests'] > 0:
        hit_rate = cache_stats['hit_rate']
        if hit_rate > 80:
            color, icon = '#35b779', '🚀'
        elif hit_rate > 50:
            color, icon = '#ffa726', '⚡'
        else:
            color, icon = '#ff6b6b', '🐌'

        st.markdown(f"""
        <div style="
            background: {color}20;
            border-left: 4px solid {color};
            padding: 0.5rem;
            margin-bottom: 0.5rem;
            border-radius: 4px;
        ">
            <div style="color: {color}; font-weight: bold; font-size: 0.9rem;">
                {icon} Cache Hit Rate: {hit_rate:.0f}%
            </div>
            <div style="color: {color}; font-size: 0.8rem;">
                {cache_stats['hits']} hits / {cache_stats['total_requests']} requêtes
            </div>
        </div>
        """, unsafe_allow_html=True)


        if cache_stats['time_saved_seconds'] > 0:
            time_saved = cache_stats['time_saved_seconds']
            st.markdown(f"""
            <div style="
                background: #35b77920;
                border-left: 4px solid #35b779;
                padding: 0.5rem;
                margin-bottom: 0.5rem;
                border-radius: 4px;
            ">
                <div style="color: #35b779; font-weight: bold; font-size: 0.9rem;">
                    ⏱️ Temps économisé: {time_saved:.1f}s
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: #ccc20;
            border-left: 4px solid #ccc;
            padding: 0.5rem;
            margin-bottom: 0.5rem;
            border-radius: 4px;
        ">
            <div style="color: #666; font-weight: bold; font-size: 0.9rem;">
                💤 Cache inactif
            </div>
        </div>
        """, unsafe_allow_html=True)


    with st.expander("🛠️ Actions Cache"):
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Vider Cache", help="Supprime tout le cache"):
                clear_all_caches()
                st.success("Cache vidé !")
                st.rerun()

        with col2:
            if st.button("Stats Détaillées", help="Affiche stats complètes"):
                st.json(get_cache_status())


def _render_real_time_monitoring():
    \
    st.markdown("---")
    st.subheader("Monitoring")

    df_pnl = st.session_state.get('df_pnl_enhanced')

    if df_pnl is None or df_pnl.empty:
        st.info("⏳ PnL en attente")
        return


    if 'risk_limits' not in st.session_state:
        st.session_state.risk_limits = {
            'max_notional_per_pair': 100_000_000,
            'max_tenor_concentration': 0.3,
            'var_limit': 5_000_000,
            'max_deals_per_trader': 50
        }

    rl = st.session_state.risk_limits


    _render_compact_utilization_card(df_pnl, rl)
    _render_compact_urgent_deals_card(df_pnl)
    _render_compact_concentration_card(df_pnl, rl)
    _render_compact_risk_score_card(df_pnl, rl)


def _render_compact_utilization_card(df_pnl, rl):
    \
    total_notional = df_pnl['amount'].sum() if 'amount' in df_pnl.columns else 0
    global_limit = rl['max_notional_per_pair'] * 5
    utilization = (total_notional / global_limit * 100) if global_limit > 0 else 0

    if utilization > 80:
        color, icon = '#ff6b6b', 'CRITICAL'
    elif utilization > 60:
        color, icon = '#ffa726', 'WARNING'
    else:
        color, icon = '#35b779', 'OK'

    st.markdown(f"""
    <div style="
        background: {color}20;
        border-left: 4px solid {color};
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
    ">
        <div style="color: {color}; font-weight: bold; font-size: 0.9rem;">
            {icon} Utilisation: {utilization:.0f}%
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_compact_urgent_deals_card(df_pnl):
    \
    urgent_count = 0

    if 'maturity_date' in df_pnl.columns:
        try:
            df_temp = df_pnl.copy()
            df_temp['days_to_maturity'] = (pd.to_datetime(df_temp['maturity_date']) - pd.Timestamp.now()).dt.days
            urgent_count = len(df_temp[df_temp['days_to_maturity'] <= 7])
        except:
            pass

    if urgent_count > 5:
        color, icon = '#ff6b6b', 'CRITICAL'
    elif urgent_count > 2:
        color, icon = '#ffa726', 'WARNING'
    else:
        color, icon = '#35b779', 'OK'

    st.markdown(f"""
    <div style="
        background: {color}20;
        border-left: 4px solid {color};
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
    ">
        <div style="color: {color}; font-weight: bold; font-size: 0.9rem;">
            {icon} Échéances ≤7j: {urgent_count}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_compact_concentration_card(df_pnl, rl):
    \
    max_concentration = 0

    if 'base_currency' in df_pnl.columns and 'amount' in df_pnl.columns:
        total_notional = df_pnl['amount'].sum()
        if total_notional > 0:
            ccy_expo = df_pnl.groupby('base_currency')['amount'].sum()
            max_concentration = (ccy_expo.max() / total_notional * 100)

    if max_concentration > rl['max_tenor_concentration'] * 100:
        color, icon = '#ff6b6b', 'CRITICAL'
    elif max_concentration > rl['max_tenor_concentration'] * 80:
        color, icon = '#ffa726', 'WARNING'
    else:
        color, icon = '#35b779', 'OK'

    st.markdown(f"""
    <div style="
        background: {color}20;
        border-left: 4px solid {color};
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
    ">
        <div style="color: {color}; font-weight: bold; font-size: 0.9rem;">
            {icon} Concentration: {max_concentration:.0f}%
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_compact_risk_score_card(df_pnl, rl):
    \
    risk_score = _calculate_compact_risk_score(df_pnl, rl)

    if risk_score >= 70:
        color, icon = '#ff6b6b', 'CRITICAL'
    elif risk_score >= 40:
        color, icon = '#ffa726', 'WARNING'
    else:
        color, icon = '#35b779', 'OK'

    st.markdown(f"""
    <div style="
        background: {color}20;
        border-left: 4px solid {color};
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
    ">
        <div style="color: {color}; font-weight: bold; font-size: 0.9rem;">
            {icon} Score Risque: {risk_score}/100
        </div>
    </div>
    """, unsafe_allow_html=True)


def _calculate_compact_risk_score(df_pnl, rl) -> int:
    \
    risk_score = 0


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
            df_temp = df_pnl.copy()
            df_temp['days_to_maturity'] = (pd.to_datetime(df_temp['maturity_date']) - pd.Timestamp.now()).dt.days
            urgent_count = len(df_temp[df_temp['days_to_maturity'] <= 7])

            if urgent_count > 5:
                risk_score += 30
            elif urgent_count > 2:
                risk_score += 15
        except:
            pass


    if 'base_currency' in df_pnl.columns and 'amount' in df_pnl.columns:
        total_notional = df_pnl['amount'].sum()
        if total_notional > 0:
            ccy_expo = df_pnl.groupby('base_currency')['amount'].sum()
            max_concentration = (ccy_expo.max() / total_notional)

            if max_concentration > rl['max_tenor_concentration']:
                risk_score += 30
            elif max_concentration > rl['max_tenor_concentration'] * 0.8:
                risk_score += 15

    return min(risk_score, 100)


def _render_debug_section():
    \
    st.markdown("---")
    if st.checkbox("🐛 Mode Debug"):

        st.session_state.debug_mode = True

        st.markdown("**Logs récents:**")
        recent_logs = get_recent_logs(5)
        for log in recent_logs:
            st.caption(f"[{log.get('level', 'INFO')}] {str(log.get('message', ''))[:30]}...")


        cache_stats = cache_manager.get_cache_info()
        if cache_stats['total_requests'] > 0:
            st.caption(f"Cache: {cache_stats['hits']}/{cache_stats['total_requests']} hits")
    else:
        st.session_state.debug_mode = False


def get_portfolio_summary() -> dict:
    \
    deals = st.session_state.get('generic_deals', [])

    if not deals:
        return {
            'total_deals': 0,
            'total_notional': 0,
            'products': {},
            'currencies': {}
        }


    total_notional = sum(deal.amount for deal in deals)


    products = {}
    for deal in deals:
        products[deal.product] = products.get(deal.product, 0) + 1


    currencies = {}
    for deal in deals:
        base_ccy = getattr(deal, 'base_currency', deal.pair_currency.split('/')[0])
        currencies[base_ccy] = currencies.get(base_ccy, 0) + deal.amount

    return {
        'total_deals': len(deals),
        'total_notional': total_notional,
        'products': products,
        'currencies': currencies
    }