\
\
\
\

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any


from treasury.pnl import get_pnl_summary

try:
    from treasury.logging_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def render_performance_tab():
    \
    st.subheader("Analyse de Performance")

    df_pnl = st.session_state.get('df_pnl_enhanced')
    deals = st.session_state.get('generic_deals', [])

    if not deals:
        st.info("Importez d'abord des deals pour l'analyse de performance")
        return

    if df_pnl is None or df_pnl.empty:
        st.info("Calculez d'abord les PnL pour l'analyse de performance")
        return

    _render_performance_kpis(df_pnl)
    _render_performance_by_product(df_pnl)
    _render_performance_analysis(df_pnl)


def _render_performance_kpis(df_pnl: pd.DataFrame):
    \
    st.markdown("### KPIs de Performance")

    summary = get_pnl_summary(df_pnl)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_pnl_m = summary.get('total_pnl_m', 0)
        st.metric("PnL Total", f"${total_pnl_m:+.2f}M")

    with col2:
        deal_count = summary.get('deal_count', 0)
        avg_pnl = (total_pnl_m * 1000 / deal_count) if deal_count > 0 else 0
        st.metric("PnL Moyen/Deal", f"${avg_pnl:+.0f}k")

    with col3:
        if 'amount' in df_pnl.columns:
            total_notional = df_pnl['amount'].sum() / 1_000_000
            pnl_ratio = (total_pnl_m / total_notional * 100) if total_notional > 0 else 0
            st.metric("Ratio PnL/Notionnel", f"{pnl_ratio:+.3f}%")
        else:
            st.metric("Ratio PnL/Notionnel", "N/A")

    with col4:
        if 'total_pnl' in df_pnl.columns:
            positive_deals = len(df_pnl[df_pnl['total_pnl'] > 0])
            win_rate = (positive_deals / deal_count * 100) if deal_count > 0 else 0
            st.metric("Taux de Succès", f"{win_rate:.1f}%")
        else:
            st.metric("Taux de Succès", "N/A")


def _render_performance_by_product(df_pnl: pd.DataFrame):
    \
    st.markdown("### Performance par Produit")

    if 'product' in df_pnl.columns and 'total_pnl' in df_pnl.columns:
        perf_by_product = df_pnl.groupby('product').agg({
            'total_pnl': ['sum', 'mean', 'count'],
            'amount': 'sum' if 'amount' in df_pnl.columns else lambda x: 0
        }).round(2)

        perf_by_product.columns = ['PnL_Total', 'PnL_Moyen', 'Nb_Deals', 'Notionnel']
        perf_by_product['PnL_Total_M'] = perf_by_product['PnL_Total'] / 1_000_000
        perf_by_product['Notionnel_M'] = perf_by_product['Notionnel'] / 1_000_000

        st.dataframe(perf_by_product[['PnL_Total_M', 'PnL_Moyen', 'Nb_Deals', 'Notionnel_M']],
                    use_container_width=True)


        _create_performance_chart(perf_by_product)


def _create_performance_chart(perf_data):
    \
    fig_product = go.Figure()
    fig_product.add_trace(go.Bar(
        x=perf_data.index,
        y=perf_data['PnL_Total_M'],
        name='PnL Total (M)',
        marker_color='#440154',
        text=[f"{val:+.1f}M" for val in perf_data['PnL_Total_M']],
        textposition='auto'
    ))
    fig_product.update_layout(
        title='PnL Total par Produit',
        xaxis_title='Produit',
        yaxis_title='PnL (M USD)',
        template='plotly_dark',
        height=400
    )
    st.plotly_chart(fig_product, use_container_width=True)


def _render_performance_analysis(df_pnl: pd.DataFrame):
    \
    st.markdown("### 🔍 Analyse Avancée")

    if 'total_pnl' not in df_pnl.columns:
        st.warning("Colonne 'total_pnl' manquante pour l'analyse")
        return


    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Distribution des PnL**")
        pnl_stats = _calculate_pnl_statistics(df_pnl['total_pnl'])
        for stat, value in pnl_stats.items():
            if isinstance(value, (int, float)):
                st.metric(stat.replace('_', ' ').title(), f"{value:,.0f}")

    with col2:
        st.markdown("**Top/Bottom Performers**")
        _render_top_bottom_performers(df_pnl)


    if 'trader_id' in df_pnl.columns:
        _render_trader_performance(df_pnl)


    if 'trade_date' in df_pnl.columns:
        _render_temporal_analysis(df_pnl)


def _render_top_bottom_performers(df_pnl: pd.DataFrame):
    \
    if 'deal_id' in df_pnl.columns:
        top_deals = df_pnl.nlargest(3, 'total_pnl')[['deal_id', 'total_pnl']]
        bottom_deals = df_pnl.nsmallest(3, 'total_pnl')[['deal_id', 'total_pnl']]

        st.write("🏆 Top 3:")
        for _, row in top_deals.iterrows():
            st.write(f"• {row['deal_id']}: ${row['total_pnl']:,.0f}")

        st.write("📉 Bottom 3:")
        for _, row in bottom_deals.iterrows():
            st.write(f"• {row['deal_id']}: ${row['total_pnl']:,.0f}")
    else:
        st.write("Colonnes deal_id manquante pour l'analyse des performers")


def _render_trader_performance(df_pnl: pd.DataFrame):
    \
    st.markdown("---")
    st.markdown("### 👥 Performance par Trader")

    trader_perf = df_pnl.groupby('trader_id').agg({
        'total_pnl': ['sum', 'mean', 'count', 'std'],
        'amount': 'sum' if 'amount' in df_pnl.columns else lambda x: 0
    }).round(2)

    trader_perf.columns = ['PnL_Total', 'PnL_Moyen', 'Nb_Deals', 'PnL_StdDev', 'Volume_Total']
    trader_perf['PnL_Total_M'] = trader_perf['PnL_Total'] / 1_000_000


    trader_perf['Sharpe_Ratio'] = trader_perf.apply(
        lambda row: row['PnL_Moyen'] / row['PnL_StdDev']
        if row['PnL_StdDev'] > 0 and not pd.isna(row['PnL_StdDev'])
        else 0,
        axis=1
    )


    trader_perf = trader_perf.sort_values('PnL_Total', ascending=False)

    st.dataframe(trader_perf[['PnL_Total_M', 'PnL_Moyen', 'Nb_Deals', 'Sharpe_Ratio']],
                use_container_width=True)


    _create_trader_performance_chart(trader_perf)


def _create_trader_performance_chart(trader_perf):
    \
    fig_trader = go.Figure()



    sharpe_ratios = trader_perf['Sharpe_Ratio'].fillna(0)

    abs_sharpe = np.abs(sharpe_ratios)
    max_sharpe = abs_sharpe.max() if abs_sharpe.max() > 0 else 1
    marker_sizes = 5 + (abs_sharpe / max_sharpe) * 35


    x_values = trader_perf['Nb_Deals'].fillna(0)
    y_values = trader_perf['PnL_Total_M'].fillna(0)
    color_values = trader_perf['PnL_Total_M'].fillna(0)


    fig_trader.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='markers+text',
        text=trader_perf.index,
        textposition="top center",
        marker=dict(
            size=marker_sizes,
            color=color_values,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="PnL Total (M)"),
            sizemin=5,
            line=dict(width=1, color='white')
        ),
        hovertemplate='<b>%{text}</b><br>Deals: %{x}<br>PnL: %{y:.1f}M<br>Sharpe: %{customdata:.2f}<extra></extra>',
        customdata=sharpe_ratios
    ))

    fig_trader.update_layout(
        title='Performance Traders: PnL vs Volume (taille = |Sharpe Ratio|)',
        xaxis_title='Nombre de Deals',
        yaxis_title='PnL Total (M USD)',
        template='plotly_dark',
        height=500
    )

    st.plotly_chart(fig_trader, use_container_width=True)


def _render_temporal_analysis(df_pnl: pd.DataFrame):
    \
    st.markdown("---")
    st.markdown("### 📅 Analyse Temporelle")

    try:

        df_temp = df_pnl.copy()
        df_temp['trade_date'] = pd.to_datetime(df_temp['trade_date'])
        df_temp['month_year'] = df_temp['trade_date'].dt.to_period('M')


        monthly_perf = df_temp.groupby('month_year').agg({
            'total_pnl': ['sum', 'count', 'mean'],
            'amount': 'sum' if 'amount' in df_temp.columns else lambda x: 0
        }).round(2)

        monthly_perf.columns = ['PnL_Total', 'Nb_Deals', 'PnL_Moyen', 'Volume']
        monthly_perf['PnL_Total_M'] = monthly_perf['PnL_Total'] / 1_000_000


        fig_temporal = go.Figure()

        fig_temporal.add_trace(go.Bar(
            x=[str(period) for period in monthly_perf.index],
            y=monthly_perf['PnL_Total_M'],
            name='PnL Mensuel',
            marker_color='#31688e',
            text=[f"{val:+.1f}M" for val in monthly_perf['PnL_Total_M']],
            textposition='auto'
        ))

        fig_temporal.update_layout(
            title='Évolution du PnL par Mois',
            xaxis_title='Période',
            yaxis_title='PnL (M USD)',
            template='plotly_dark',
            height=400
        )

        st.plotly_chart(fig_temporal, use_container_width=True)


        st.dataframe(monthly_perf[['PnL_Total_M', 'Nb_Deals', 'PnL_Moyen']],
                    use_container_width=True)

    except Exception as e:
        st.warning(f"Erreur analyse temporelle: {e}")


def _calculate_pnl_statistics(pnl_series) -> Dict[str, float]:
    \
    return {
        'mean': pnl_series.mean(),
        'median': pnl_series.median(),
        'std': pnl_series.std(),
        'min': pnl_series.min(),
        'max': pnl_series.max(),
        'skewness': pnl_series.skew() if hasattr(pnl_series, 'skew') else 0,
        'positive_ratio': (pnl_series > 0).mean()
    }