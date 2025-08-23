"""
Onglet PnL pour Treasury Dashboard
Module UI séparé pour les calculs et affichage PnL avec cache optimisé
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Imports Treasury - éviter import circulaire
try:
    from treasury.cache import compute_pnl_with_cache
except ImportError:
    from treasury.pnl import compute_enhanced_pnl_vectorized
    from treasury.models import PnLConfig
    
    def compute_pnl_with_cache(deals, config_dict=None):
        """Fallback si cache non disponible"""
        if config_dict is None:
            config_dict = {}
        config = PnLConfig(**config_dict)
        return compute_enhanced_pnl_vectorized(deals, config)

try:
    from treasury.logging_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def render_pnl_tab():
    """Onglet de calcul et affichage PnL avec cache intelligent"""
    st.subheader("Calculs PnL Modulaires")
    
    deals = st.session_state.get('generic_deals', [])
    
    if not deals:
        st.info("Importez d'abord des deals dans l'onglet 'Import'")
        return
    
    _render_pnl_controls()
    _render_pnl_calculations()


def _render_pnl_controls():
    """Contrôles pour les calculs PnL"""
    st.markdown("**🎛️ Contrôles**")
    
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    
    with col_ctrl1:
        if st.button("Recalculer PnL", type="primary", use_container_width=True):
            _recalculate_pnl()
    
    with col_ctrl2:
        if st.button("🧪 Test Choc +50bp", use_container_width=True):
            _run_stress_test()
    
    with col_ctrl3:
        if st.button("Reset Config", use_container_width=True):
            _reset_pnl_config()
    
    st.markdown("---")


def _recalculate_pnl():
    """Recalcule le PnL avec la configuration actuelle"""
    deals = st.session_state.get('generic_deals', [])
    
    if not deals:
        st.error("Aucun deal importé")
        return
    
    with st.spinner("Calcul en cours..."):
        start_time = time.time()
        
        # Configuration par défaut si pas définie
        config_dict = st.session_state.get('pnl_config', {
            'calculate_accrued': True,
            'calculate_mtm': True,
            'calculate_rate': True,
            'calculate_liquidity': True,
            'ois_rate_override': None
        })
        
        df_pnl = compute_pnl_with_cache(deals, config_dict)
        st.session_state.df_pnl_enhanced = df_pnl
        calc_time = time.time() - start_time
        st.success(f"PnL recalculé en {calc_time:.1f}s")
        st.rerun()  # Forcer le refresh de l'interface


def _run_stress_test():
    """Lance un test de stress avec choc de taux"""
    deals = st.session_state.get('generic_deals', [])
    
    if not deals:
        st.error("Aucun deal importé")
        return
        
    config_dict = st.session_state.get('pnl_config', {
        'calculate_accrued': True,
        'calculate_mtm': True,
        'calculate_rate': True,
        'calculate_liquidity': True,
        'ois_rate_override': None
    }).copy()
    
    config_dict['ois_rate_override'] = 0.055
    
    with st.spinner("Test en cours..."):
        df_test = compute_pnl_with_cache(deals, config_dict)
        st.session_state.df_pnl_enhanced = df_test
        st.info("Test: OIS = 5.5%")
        st.rerun()


def _reset_pnl_config():
    """Remet la configuration PnL à zéro"""
    st.session_state.pnl_config = {
        'calculate_accrued': True,
        'calculate_mtm': True,
        'calculate_rate': True,
        'calculate_liquidity': True,
        'ois_rate_override': None
    }
    st.info("Configuration remise à zéro")
    st.rerun()


def _render_pnl_calculations():
    """Affichage des calculs et résultats PnL"""
    deals = st.session_state.get('generic_deals', [])
    
    if not deals:
        st.info("Aucun deal importé. Allez dans l'onglet Import pour charger des données.")
        return
    
    # Calcul initial si nécessaire
    if st.session_state.get('df_pnl_enhanced') is None or st.session_state.df_pnl_enhanced.empty:
        with st.spinner("Calcul PnL initial..."):
            config_dict = st.session_state.get('pnl_config', {
                'calculate_accrued': True,
                'calculate_mtm': True,
                'calculate_rate': True,
                'calculate_liquidity': True,
                'ois_rate_override': None
            })
            
            df_pnl = compute_pnl_with_cache(deals, config_dict)
            st.session_state.df_pnl_enhanced = df_pnl
    
    df_pnl = st.session_state.df_pnl_enhanced
    
    if not df_pnl.empty:
        _validate_and_display_pnl(df_pnl)
        _render_pnl_metrics(df_pnl)
        _render_pnl_charts(df_pnl)
        _render_pnl_actions(df_pnl)
        _render_pnl_details(df_pnl)


def _validate_and_display_pnl(df_pnl: pd.DataFrame):
    """Valide et affiche les erreurs/warnings PnL"""
    # Import local pour éviter circularité
    from treasury.pnl import validate_pnl_results
    
    validation = validate_pnl_results(df_pnl)
    
    if not validation['is_valid']:
        for error in validation['errors']:
            st.error(f"❌ {error}")
    
    for warning in validation['warnings']:
        st.warning(f"⚠️ {warning}")


def _render_pnl_metrics(df_pnl: pd.DataFrame):
    """Affiche les métriques principales PnL"""
    # Import local pour éviter circularité
    from treasury.pnl import get_pnl_summary
    
    summary = get_pnl_summary(df_pnl)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Accrued (M)", f"{summary.get('accrued_pnl_m', 0):+.2f}")
    col2.metric("MTM (M)", f"{summary.get('mtm_pnl_m', 0):+.2f}")
    col3.metric("Rate (M)", f"{summary.get('rate_pnl_m', 0):+.2f}")
    col4.metric("Liquidity (M)", f"{summary.get('liquidity_pnl_m', 0):+.2f}")
    col5.metric("TOTAL (M)", f"{summary.get('total_pnl_m', 0):+.2f}")


def _render_pnl_charts(df_pnl: pd.DataFrame):
    """Affiche les graphiques PnL"""
    st.markdown("### Visualisations PnL")
    
    try:
        # Import local pour éviter circularité
        from treasury.visuals import create_pnl_breakdown_chart, create_pnl_waterfall_enhanced
        
        # Graphique breakdown
        fig_breakdown = create_pnl_breakdown_chart(df_pnl)
        st.plotly_chart(fig_breakdown, use_container_width=True)
        
        # Graphique waterfall
        fig_waterfall = create_pnl_waterfall_enhanced(df_pnl)
        st.plotly_chart(fig_waterfall, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erreur lors de la création des graphiques: {e}")
        logger.error(f"Erreur graphiques PnL: {e}")


def _render_pnl_actions(df_pnl: pd.DataFrame):
    """Boutons d'action pour le PnL"""
    st.markdown("---")
    st.markdown("### Actions et Détails")
    
    # Import local pour éviter circularité
    from treasury.pnl import get_pnl_summary
    summary = get_pnl_summary(df_pnl)
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("💾 Export Excel", use_container_width=True):
            _export_pnl_to_excel(df_pnl)
    
    with col_action2:
        st.metric("Deals", summary.get('deal_count', 0))
    
    with col_action3:
        st.metric("PnL/Deal (k)", f"{summary.get('avg_pnl_per_deal', 0)*1000:.0f}")


def _export_pnl_to_excel(df_pnl: pd.DataFrame):
    """Exporte le PnL vers Excel"""
    try:
        # Import local pour éviter circularité
        from treasury.io.excel import export_pnl_to_excel
        
        excel_data = export_pnl_to_excel(df_pnl)
        st.download_button(
            "📥 Télécharger Excel PnL",
            data=excel_data,
            file_name=f"pnl_export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Erreur export Excel: {e}")


def _render_pnl_details(df_pnl: pd.DataFrame):
    """Table détaillée des résultats PnL"""
    with st.expander("Détail par Deal"):
        # Colonnes d'affichage
        display_cols = [
            'deal_id', 'product', 'amount', 'time_to_maturity_years',
            'accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl', 'total_pnl'
        ]
        available_cols = [col for col in display_cols if col in df_pnl.columns]
        
        # Formatage pour affichage
        df_display = df_pnl[available_cols].copy()
        for col in ['accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl', 'total_pnl']:
            if col in df_display.columns:
                df_display[col] = (df_display[col] / 1000).round(1)  # En milliers
        
        st.dataframe(df_display, use_container_width=True, height=400)


def get_pnl_attribution(df_pnl: pd.DataFrame) -> Dict[str, Any]:
    """Calcule l'attribution PnL par différentes dimensions"""
    attribution = {}
    
    if df_pnl.empty:
        return attribution
    
    # Attribution par produit
    if 'product' in df_pnl.columns and 'total_pnl' in df_pnl.columns:
        attribution['by_product'] = df_pnl.groupby('product')['total_pnl'].sum().to_dict()
    
    # Attribution par devise
    if 'pair_currency' in df_pnl.columns and 'total_pnl' in df_pnl.columns:
        attribution['by_currency'] = df_pnl.groupby('pair_currency')['total_pnl'].sum().to_dict()
    
    # Attribution par trader
    if 'trader_id' in df_pnl.columns and 'total_pnl' in df_pnl.columns:
        attribution['by_trader'] = df_pnl.groupby('trader_id')['total_pnl'].sum().to_dict()
    
    # Attribution par composante
    pnl_components = ['accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl']
    available_components = [col for col in pnl_components if col in df_pnl.columns]
    
    if available_components:
        attribution['by_component'] = {
            comp: df_pnl[comp].sum() for comp in available_components
        }
    
    return attribution


def calculate_pnl_statistics(df_pnl: pd.DataFrame) -> Dict[str, float]:
    """Calcule des statistiques avancées sur le PnL"""
    if df_pnl.empty or 'total_pnl' not in df_pnl.columns:
        return {}
    
    pnl_values = df_pnl['total_pnl']
    
    return {
        'mean': pnl_values.mean(),
        'median': pnl_values.median(),
        'std': pnl_values.std(),
        'min': pnl_values.min(),
        'max': pnl_values.max(),
        'skewness': pnl_values.skew(),
        'kurtosis': pnl_values.kurtosis(),
        'positive_count': (pnl_values > 0).sum(),
        'negative_count': (pnl_values < 0).sum(),
        'win_rate': (pnl_values > 0).mean()
    }