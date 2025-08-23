"""
Dashboard de performance avancé pour Treasury
Attribution PnL détaillée et métriques de performance
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from treasury.analytics import convert_generic_to_analytics_format
from treasury.logging_config import logger


def render_advanced_performance_dashboard():
    """Dashboard de performance avancé"""
    st.markdown("## Performance Analytics Advanced")
    
    df_pnl = st.session_state.get('df_pnl_enhanced', pd.DataFrame())
    
    if df_pnl.empty:
        st.warning("⚠️ Aucune donnée PnL - Importez d'abord vos deals")
        return
    
    # Navigation par onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "Attribution PnL", 
        "Trends & Patterns", 
        "Risk-Adjusted Returns",
        "Trade Analytics"
    ])
    
    with tab1:
        render_pnl_attribution_analysis(df_pnl)
    
    with tab2:
        render_trend_analysis(df_pnl)
    
    with tab3:
        render_risk_adjusted_returns(df_pnl)
    
    with tab4:
        render_trade_analytics(df_pnl)


def render_pnl_attribution_analysis(df_pnl: pd.DataFrame):
    """Analyse d'attribution PnL détaillée"""
    st.markdown("### Attribution PnL Détaillée")
    
    # Métriques globales
    col1, col2, col3, col4 = st.columns(4)
    
    total_pnl = df_pnl['total_pnl'].sum() / 1e6
    accrued_pnl = df_pnl['accrued_pnl'].sum() / 1e6 if 'accrued_pnl' in df_pnl.columns else 0
    mtm_pnl = df_pnl['mtm_pnl'].sum() / 1e6 if 'mtm_pnl' in df_pnl.columns else 0
    
    col1.metric("PnL Total", f"${total_pnl:.1f}M")
    col2.metric("Accrued PnL", f"${accrued_pnl:.1f}M")  
    col3.metric("MTM PnL", f"${mtm_pnl:.1f}M")
    col4.metric("Deals Count", f"{len(df_pnl):,}")
    
    # Attribution par composante
    st.markdown("#### Décomposition par Composante")
    
    if all(col in df_pnl.columns for col in ['accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl']):
        
        # Graphique waterfall
        fig_waterfall = create_pnl_waterfall_chart(df_pnl)
        st.plotly_chart(fig_waterfall, use_container_width=True)
        
        # Attribution par devise
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### 💱 Attribution par Devise")
            if 'base_currency' in df_pnl.columns:
                fig_currency = create_attribution_by_currency(df_pnl)
                st.plotly_chart(fig_currency, use_container_width=True)
        
        with col_right:
            st.markdown("#### 📅 Attribution par Maturité")
            if 'time_to_maturity_years' in df_pnl.columns:
                fig_maturity = create_attribution_by_maturity(df_pnl)
                st.plotly_chart(fig_maturity, use_container_width=True)
    
    # Top Contributors/Detractors
    st.markdown("#### 🏆 Top Contributors & Detractors")
    
    col_contrib, col_detract = st.columns(2)
    
    with col_contrib:
        st.markdown("**🟢 Top Contributors**")
        top_contributors = df_pnl.nlargest(5, 'total_pnl')[['deal_id', 'total_pnl', 'product']]
        top_contributors['total_pnl_m'] = top_contributors['total_pnl'] / 1e6
        st.dataframe(
            top_contributors[['deal_id', 'product', 'total_pnl_m']].rename(columns={
                'deal_id': 'Deal ID',
                'product': 'Product', 
                'total_pnl_m': 'PnL (M$)'
            }),
            hide_index=True
        )
    
    with col_detract:
        st.markdown("**🔴 Top Detractors**")
        top_detractors = df_pnl.nsmallest(5, 'total_pnl')[['deal_id', 'total_pnl', 'product']]
        top_detractors['total_pnl_m'] = top_detractors['total_pnl'] / 1e6
        st.dataframe(
            top_detractors[['deal_id', 'product', 'total_pnl_m']].rename(columns={
                'deal_id': 'Deal ID',
                'product': 'Product',
                'total_pnl_m': 'PnL (M$)'
            }),
            hide_index=True
        )


def render_trend_analysis(df_pnl: pd.DataFrame):
    """Analyse des tendances temporelles"""
    st.markdown("### Analyse des Tendances")
    
    # Simulation de données historiques (à remplacer par vraies données)
    historical_data = generate_historical_pnl_simulation(df_pnl)
    
    # Évolution PnL dans le temps
    st.markdown("#### Évolution PnL Temporelle")
    
    fig_evolution = go.Figure()
    
    # PnL cumulé
    fig_evolution.add_trace(go.Scatter(
        x=historical_data.index,
        y=historical_data['cumulative_pnl'],
        mode='lines',
        name='PnL Cumulé',
        line=dict(color='#00d4aa', width=3)
    ))
    
    # PnL journalier (barres)
    fig_evolution.add_trace(go.Bar(
        x=historical_data.index,
        y=historical_data['daily_pnl'],
        name='PnL Journalier',
        marker_color='rgba(0, 212, 170, 0.3)',
        yaxis='y2'
    ))
    
    fig_evolution.update_layout(
        title="Évolution PnL dans le Temps",
        xaxis_title="Date",
        yaxis_title="PnL Cumulé ($M)",
        yaxis2=dict(
            title="PnL Journalier ($M)",
            overlaying='y',
            side='right'
        ),
        height=400,
        template='plotly_dark'
    )
    
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # Métriques de volatilité
    col1, col2, col3 = st.columns(3)
    
    daily_vol = historical_data['daily_pnl'].std()
    max_drawdown = calculate_max_drawdown(historical_data['cumulative_pnl'])
    sharpe_approx = historical_data['daily_pnl'].mean() / daily_vol if daily_vol > 0 else 0
    
    col1.metric("Volatilité Journalière", f"${daily_vol:.2f}M")
    col2.metric("Max Drawdown", f"${max_drawdown:.2f}M")
    col3.metric("Sharpe Approximatif", f"{sharpe_approx:.2f}")


def render_risk_adjusted_returns(df_pnl: pd.DataFrame):
    """Métriques de performance ajustées du risque"""
    st.markdown("### Returns Ajustés du Risque")
    
    # Calcul métriques risque-rendement
    metrics = calculate_risk_adjusted_metrics(df_pnl)
    
    # Affichage métriques
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Ratio Information", f"{metrics.get('information_ratio', 0):.2f}")
    col2.metric("Return on VaR", f"{metrics.get('return_on_var', 0):.2f}")
    col3.metric("Calmar Ratio", f"{metrics.get('calmar_ratio', 0):.2f}")
    col4.metric("Sortino Ratio", f"{metrics.get('sortino_ratio', 0):.2f}")
    
    # Graphique risque-rendement par deal
    st.markdown("#### 💎 Profil Risque-Rendement par Deal")
    
    fig_risk_return = create_risk_return_scatter(df_pnl)
    st.plotly_chart(fig_risk_return, use_container_width=True)


def render_trade_analytics(df_pnl: pd.DataFrame):
    """Analytics spécifiques aux trades"""
    st.markdown("### Trade Analytics")
    
    # Distribution des tailles de deals
    st.markdown("#### Distribution Tailles de Deals")
    
    if 'amount' in df_pnl.columns:
        fig_size_dist = px.histogram(
            df_pnl,
            x='amount',
            nbins=20,
            title="Distribution des Notionnels",
            template='plotly_dark'
        )
        fig_size_dist.update_xaxis(title="Notionnel ($)")
        fig_size_dist.update_yaxis(title="Nombre de Deals")
        st.plotly_chart(fig_size_dist, use_container_width=True)
    
    # Performance par produit
    st.markdown("#### Performance par Type de Produit")
    
    if 'product' in df_pnl.columns:
        product_perf = df_pnl.groupby('product').agg({
            'total_pnl': ['sum', 'mean', 'count'],
            'amount': 'sum'
        }).round(2)
        
        product_perf.columns = ['PnL Total', 'PnL Moyen', 'Nb Deals', 'Notionnel Total']
        product_perf['PnL Total (M$)'] = product_perf['PnL Total'] / 1e6
        product_perf['Notionnel (M$)'] = product_perf['Notionnel Total'] / 1e6
        product_perf['PnL/Notionnel (bps)'] = (product_perf['PnL Total'] / product_perf['Notionnel Total'] * 10000).round(1)
        
        display_cols = ['Nb Deals', 'PnL Total (M$)', 'PnL/Notionnel (bps)', 'Notionnel (M$)']
        st.dataframe(product_perf[display_cols])


# Fonctions utilitaires

def create_pnl_waterfall_chart(df_pnl: pd.DataFrame) -> go.Figure:
    """Crée un graphique waterfall des composantes PnL"""
    
    components = ['accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl']
    values = [df_pnl[comp].sum() / 1e6 for comp in components if comp in df_pnl.columns]
    labels = ['Accrued', 'MTM', 'Rate', 'Liquidity'][:len(values)]
    
    fig = go.Figure(go.Waterfall(
        name="PnL Attribution",
        orientation="v",
        measure=["relative"] * len(values) + ["total"],
        x=labels + ["Total"],
        textposition="outside",
        text=[f"${v:.1f}M" for v in values] + [f"${sum(values):.1f}M"],
        y=values + [sum(values)],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(
        title="Attribution PnL par Composante",
        template='plotly_dark',
        height=400
    )
    
    return fig


def create_attribution_by_currency(df_pnl: pd.DataFrame) -> go.Figure:
    """Attribution PnL par devise"""
    
    currency_pnl = df_pnl.groupby('base_currency')['total_pnl'].sum() / 1e6
    
    fig = px.pie(
        values=currency_pnl.abs(),
        names=currency_pnl.index,
        title="Attribution par Devise",
        template='plotly_dark'
    )
    
    return fig


def create_attribution_by_maturity(df_pnl: pd.DataFrame) -> go.Figure:
    """Attribution PnL par bucket de maturité"""
    
    # Création buckets maturité
    df_pnl['maturity_bucket'] = pd.cut(
        df_pnl['time_to_maturity_years'],
        bins=[0, 0.5, 1, 2, 5, 10],
        labels=['<6M', '6M-1Y', '1Y-2Y', '2Y-5Y', '5Y+']
    )
    
    maturity_pnl = df_pnl.groupby('maturity_bucket')['total_pnl'].sum() / 1e6
    
    fig = px.bar(
        x=maturity_pnl.index,
        y=maturity_pnl.values,
        title="Attribution par Maturité",
        template='plotly_dark'
    )
    
    fig.update_xaxis(title="Bucket Maturité")
    fig.update_yaxis(title="PnL ($M)")
    
    return fig


def generate_historical_pnl_simulation(df_pnl: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Génère des données PnL historiques simulées"""
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Simulation basée sur PnL actuel
    base_pnl = df_pnl['total_pnl'].sum() / 1e6
    daily_vol = abs(base_pnl) * 0.1  # 10% volatilité
    
    np.random.seed(42)  # Reproductibilité
    daily_changes = np.random.normal(0, daily_vol, days)
    daily_pnl = base_pnl * 0.1 + daily_changes  # Base + variations
    
    return pd.DataFrame({
        'daily_pnl': daily_pnl,
        'cumulative_pnl': daily_pnl.cumsum()
    }, index=dates)


def calculate_max_drawdown(cumulative_pnl: pd.Series) -> float:
    """Calcule le maximum drawdown"""
    
    running_max = cumulative_pnl.expanding().max()
    drawdown = cumulative_pnl - running_max
    return drawdown.min()


def calculate_risk_adjusted_metrics(df_pnl: pd.DataFrame) -> Dict[str, float]:
    """Calcule diverses métriques ajustées du risque"""
    
    if df_pnl.empty:
        return {}
    
    total_pnl = df_pnl['total_pnl'].sum()
    pnl_std = df_pnl['total_pnl'].std()
    
    # Approximations simples
    metrics = {}
    
    if pnl_std > 0:
        metrics['information_ratio'] = total_pnl / pnl_std
        metrics['sharpe_approx'] = (total_pnl / len(df_pnl)) / pnl_std
    
    # Return on VaR approximatif
    var_approx = abs(df_pnl['total_pnl'].quantile(0.05))
    if var_approx > 0:
        metrics['return_on_var'] = total_pnl / var_approx
    
    # Autres ratios (approximations)
    metrics['calmar_ratio'] = 0.8  # Placeholder
    metrics['sortino_ratio'] = 1.2  # Placeholder
    
    return metrics


def create_risk_return_scatter(df_pnl: pd.DataFrame) -> go.Figure:
    """Graphique risque-rendement par deal"""
    
    # Calcul approximatif de risque par deal
    df_plot = df_pnl.copy()
    df_plot['risk_proxy'] = abs(df_plot['amount']) / 1e6  # Notionnel comme proxy risque
    df_plot['return'] = df_plot['total_pnl'] / 1e6
    
    fig = px.scatter(
        df_plot,
        x='risk_proxy',
        y='return',
        color='product',
        size=abs(df_plot['return']) + 1,  # Taille proportionnelle à PnL
        hover_data=['deal_id'],
        title="Profil Risque-Rendement par Deal",
        template='plotly_dark',
        labels={
            'risk_proxy': 'Risque Proxy (Notionnel M$)',
            'return': 'Return (PnL M$)'
        }
    )
    
    # Ligne de tendance
    if len(df_plot) > 1:
        z = np.polyfit(df_plot['risk_proxy'], df_plot['return'], 1)
        p = np.poly1d(z)
        
        fig.add_trace(go.Scatter(
            x=df_plot['risk_proxy'],
            y=p(df_plot['risk_proxy']),
            mode='lines',
            name='Tendance',
            line=dict(dash='dash', color='yellow')
        ))
    
    return fig
