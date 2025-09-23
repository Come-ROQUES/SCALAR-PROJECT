\
\
\
\

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import json
from treasury.config import UIConfig


def render_footer():
    \
    st.markdown("---")

    _render_status_metrics()
    _render_footer_actions()

    footer_html = UIConfig.get_footer_html(st.session_state.get('ui_theme', 'liquid_glass'))
    st.markdown(
        f"""
        <div class="glass-card" style="color: var(--text-primary) !important;">
            {footer_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def _render_status_metrics():
    \
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.caption(f"🕐 MAJ: {datetime.now().strftime('%H:%M:%S')}")

    with col2:
        deal_count = len(st.session_state.get('generic_deals', []))
        st.caption(f"Deals: {deal_count}")

    with col3:
        _render_pnl_status()

    with col4:
        _render_refresh_button()


def _render_pnl_status():
    \
    df_pnl = st.session_state.get('df_pnl_enhanced')

    if df_pnl is not None and not df_pnl.empty and 'total_pnl' in df_pnl.columns:
        total_pnl = df_pnl['total_pnl'].sum() / 1_000_000
        st.caption(f"PnL: ${total_pnl:+.1f}M")
    else:
        st.caption("PnL: En attente")


def _render_refresh_button():
    \
    if st.button("Refresh", type="secondary"):

        current_theme = st.session_state.get('ui_theme', 'liquid_glass')
        from treasury.config import UIConfig
        theme_css = UIConfig.get_theme_css(current_theme)
        st.markdown(theme_css, unsafe_allow_html=True)
        st.rerun()


def _render_footer_actions():
    \
    with st.expander("Actions Système"):
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Vider Session", help="Supprime toutes les données en session"):
                _clear_session_data()

        with col2:
            if st.button("Statut Détaillé", help="Affiche le statut détaillé de l'application"):
                _show_detailed_status()

        with col3:
            if st.button("💾 Export Session", help="Exporte l'état de la session"):
                _export_session_state()


def _clear_session_data():
    \
    keys_to_clear = [
        'generic_deals',
        'df_pnl_enhanced',
        'pnl_config',
        'risk_limits'
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    st.success("SUCCESS Session vidée avec succès")
    st.rerun()


def _show_detailed_status():
    \
    status_info = _get_application_status()

    st.markdown("### Statut Détaillé de l'Application")


    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Données:**")
        st.write(f"• Deals en mémoire: {status_info['deals_count']}")
        st.write(f"• PnL calculé: {'OK' if status_info['pnl_available'] else 'ERROR'}")
        st.write(f"• Configuration PnL: {'OK' if status_info['config_valid'] else 'ERROR'}")

    with col2:
        st.markdown("**💾 Session:**")
        st.write(f"• Taille session: {status_info['session_size']} KB")
        st.write(f"• Dernière activité: {status_info['last_activity']}")
        st.write(f"• Modules chargés: {status_info['modules_loaded']}")


    if st.checkbox("Détails Techniques"):
        st.json(status_info['technical_details'])


def _export_session_state():
    \
    session_data = _prepare_session_export()


    session_json = json.dumps(session_data, indent=2, default=str)

    st.download_button(
        label="📥 Télécharger État Session",
        data=session_json,
        file_name=f"treasury_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


def _get_application_status() -> Dict[str, Any]:
    \
    deals = st.session_state.get('generic_deals', [])
    df_pnl = st.session_state.get('df_pnl_enhanced')
    config = st.session_state.get('pnl_config', {})


    session_size = _estimate_session_size()


    modules_status = _check_modules_status()

    return {
        'deals_count': len(deals),
        'pnl_available': df_pnl is not None and not df_pnl.empty,
        'config_valid': bool(config),
        'session_size': session_size,
        'last_activity': datetime.now().strftime('%H:%M:%S'),
        'modules_loaded': f"{len(modules_status['loaded'])}/{len(modules_status['total'])}",
        'technical_details': {
            'session_keys': list(st.session_state.keys()),
            'pnl_columns': list(df_pnl.columns) if df_pnl is not None else [],
            'config_params': list(config.keys()) if config else [],
            'modules_status': modules_status
        }
    }


def _estimate_session_size() -> int:
    \
    import sys

    total_size = 0

    for key, value in st.session_state.items():
        try:
            if isinstance(value, pd.DataFrame):
                total_size += value.memory_usage(deep=True).sum()
            elif isinstance(value, list):
                total_size += sys.getsizeof(value)
                for item in value[:10]:
                    total_size += sys.getsizeof(item)
            else:
                total_size += sys.getsizeof(value)
        except:
            pass

    return total_size // 1024


def _check_modules_status() -> Dict[str, Any]:
    \
    required_modules = [
        'treasury.config',
        'treasury.session',
        'treasury.models',
        'treasury.pnl',
        'treasury.io.excel',
        'treasury.visuals',
        'treasury.risk',
        'treasury.analytics'
    ]

    loaded_modules = []
    failed_modules = []

    for module in required_modules:
        try:
            __import__(module)
            loaded_modules.append(module)
        except ImportError:
            failed_modules.append(module)

    return {
        'total': required_modules,
        'loaded': loaded_modules,
        'failed': failed_modules
    }


def _prepare_session_export() -> Dict[str, Any]:
    \
    export_data = {
        'export_info': {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'description': 'Treasury Dashboard Session Export'
        },
        'deals_summary': {
            'count': len(st.session_state.get('generic_deals', [])),
            'products': _get_products_summary(),
            'currencies': _get_currencies_summary()
        },
        'pnl_summary': _get_pnl_export_summary(),
        'configuration': {
            'pnl_config': st.session_state.get('pnl_config', {}),
            'risk_limits': st.session_state.get('risk_limits', {})
        }
    }

    return export_data


def _get_products_summary() -> Dict[str, int]:
    \
    deals = st.session_state.get('generic_deals', [])
    products = {}

    for deal in deals:
        product = str(deal.product)
        products[product] = products.get(product, 0) + 1

    return products


def _get_currencies_summary() -> Dict[str, int]:
    \
    deals = st.session_state.get('generic_deals', [])
    currencies = {}

    for deal in deals:
        currency = deal.pair_currency
        currencies[currency] = currencies.get(currency, 0) + 1

    return currencies


def _get_pnl_export_summary() -> Dict[str, Any]:
    \
    df_pnl = st.session_state.get('df_pnl_enhanced')

    if df_pnl is None or df_pnl.empty:
        return {'available': False}

    summary = {
        'available': True,
        'total_deals': len(df_pnl),
        'columns': list(df_pnl.columns)
    }


    pnl_columns = ['accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl', 'total_pnl']
    available_pnl_cols = [col for col in pnl_columns if col in df_pnl.columns]

    if available_pnl_cols:
        summary['pnl_statistics'] = {}
        for col in available_pnl_cols:
            summary['pnl_statistics'][col] = {
                'total': float(df_pnl[col].sum()),
                'mean': float(df_pnl[col].mean()),
                'std': float(df_pnl[col].std()) if len(df_pnl) > 1 else 0,
                'min': float(df_pnl[col].min()),
                'max': float(df_pnl[col].max())
            }

    return summary


def render_system_health_indicator():
    \
    health_status = _check_system_health()


    if health_status['score'] >= 80:
        color = '#26de81'
        icon = 'OK'
        status_text = 'EXCELLENT'
    elif health_status['score'] >= 60:
        color = '#ffa726'
        icon = 'WARNING'
        status_text = 'ATTENTION'
    else:
        color = '#ff6b6b'
        icon = 'CRITICAL'
        status_text = 'CRITIQUE'


    st.markdown(f"""
    <div style="
        background: {color}20;
        border: 1px solid {color};
        border-radius: 8px;
        padding: 0.5rem;
        text-align: center;
        margin-top: 1rem;
    ">
        <span style="color: {color}; font-weight: bold;">
            {icon} Système: {status_text} ({health_status['score']}/100)
        </span>
    </div>
    """, unsafe_allow_html=True)


def _check_system_health() -> Dict[str, Any]:
    \
    health_score = 100
    issues = []


    deals = st.session_state.get('generic_deals', [])
    if not deals:
        health_score -= 30
        issues.append("Aucun deal chargé")


    df_pnl = st.session_state.get('df_pnl_enhanced')
    if df_pnl is None or df_pnl.empty:
        health_score -= 20
        issues.append("PnL non calculé")


    config = st.session_state.get('pnl_config', {})
    if not config:
        health_score -= 15
        issues.append("Configuration PnL manquante")


    risk_limits = st.session_state.get('risk_limits', {})
    if not risk_limits:
        health_score -= 10
        issues.append("Limites de risque non configurées")


    modules_status = _check_modules_status()
    if modules_status['failed']:
        health_score -= len(modules_status['failed']) * 5
        issues.extend([f"Module manquant: {mod}" for mod in modules_status['failed']])

    return {
        'score': max(0, health_score),
        'issues': issues,
        'status': 'healthy' if health_score >= 80 else 'warning' if health_score >= 60 else 'critical'
    }