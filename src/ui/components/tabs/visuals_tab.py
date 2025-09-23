\
\
\
\

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

try:
    from treasury.logging_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def render_visuals_tab():
    \
    st.subheader("📊 Analyses Visuelles pour Trading")

    df_pnl = st.session_state.get('df_pnl_enhanced')

    if df_pnl is None or df_pnl.empty:
        st.info("Calculez d'abord les PnL pour afficher les graphiques")
        return


    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💰 PnL par Produit & Devise")
        fig1 = create_pnl_by_product_chart(df_pnl)
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("### ⏰ Profil de Maturité")
        fig3 = create_maturity_profile_chart(df_pnl)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown("### 🎯 Performance par Trader")
        fig2 = create_trader_performance_chart(df_pnl)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### ⚖️ Risque vs Rendement")
        fig4 = create_risk_return_scatter(df_pnl)
        st.plotly_chart(fig4, use_container_width=True)


def create_pnl_by_product_chart(df_pnl: pd.DataFrame) -> go.Figure:
    \
\
\
\
    try:
        if df_pnl.empty:
            return _create_empty_chart("Aucune donnée PnL")


        if 'base_currency' not in df_pnl.columns and 'pair_currency' in df_pnl.columns:
            df_pnl['base_currency'] = df_pnl['pair_currency'].str.split('/').str[0]


        agg_data = df_pnl.groupby(['product', 'base_currency']).agg({
            'total_pnl': 'sum',
            'amount': 'sum',
            'deal_id': 'count'
        }).reset_index()

        agg_data['pnl_m'] = agg_data['total_pnl'] / 1_000_000
        agg_data['amount_m'] = agg_data['amount'] / 1_000_000


        fig = px.bar(
            agg_data,
            x='product',
            y='pnl_m',
            color='base_currency',
            title="PnL Total par Produit et Devise",
            labels={
                'pnl_m': 'PnL (M USD)',
                'product': 'Produit',
                'base_currency': 'Devise de Base'
            },
            hover_data={
                'deal_id': True,
                'amount_m': ':.1f'
            }
        )


        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)

        fig.update_layout(
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig

    except Exception as e:
        logger.error(f"Erreur graphique PnL par produit: {e}")
        return _create_error_chart(f"Erreur: {e}")


def create_trader_performance_chart(df_pnl: pd.DataFrame) -> go.Figure:
    \
\
\
\
    try:
        if df_pnl.empty or 'trader_id' not in df_pnl.columns:
            return _create_empty_chart("Données trader manquantes")


        trader_stats = df_pnl.groupby('trader_id').agg({
            'total_pnl': 'sum',
            'amount': 'sum',
            'deal_id': 'count'
        }).reset_index()


        trader_stats = trader_stats[trader_stats['deal_id'] >= 2]

        if trader_stats.empty:
            return _create_empty_chart("Pas assez de deals par trader")

        trader_stats['pnl_m'] = trader_stats['total_pnl'] / 1_000_000
        trader_stats['volume_m'] = trader_stats['amount'] / 1_000_000
        trader_stats['pnl_bps'] = (trader_stats['total_pnl'] / trader_stats['amount'] * 10_000).fillna(0)


        fig = px.scatter(
            trader_stats,
            x='volume_m',
            y='pnl_m',
            size='deal_id',
            color='pnl_bps',
            hover_name='trader_id',
            title="Performance Traders: Volume vs PnL",
            labels={
                'volume_m': 'Volume Total (M USD)',
                'pnl_m': 'PnL Total (M USD)',
                'deal_id': 'Nombre de Deals',
                'pnl_bps': 'PnL (bps)'
            },
            color_continuous_scale='RdYlGn',
            size_max=15
        )


        if len(trader_stats) > 1:
            median_volume = trader_stats['volume_m'].median()
            median_pnl = trader_stats['pnl_m'].median()

            fig.add_vline(x=median_volume, line_dash="dot", line_color="gray", opacity=0.5)
            fig.add_hline(y=median_pnl, line_dash="dot", line_color="gray", opacity=0.5)

        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)

        fig.update_layout(height=350)

        return fig

    except Exception as e:
        logger.error(f"Erreur graphique trader performance: {e}")
        return _create_error_chart(f"Erreur: {e}")


def create_maturity_profile_chart(df_pnl: pd.DataFrame) -> go.Figure:
    \
\
\
\
    try:
        if df_pnl.empty or 'maturity_date' not in df_pnl.columns:
            return _create_empty_chart("Données de maturité manquantes")


        df_temp = df_pnl.copy()
        today = pd.Timestamp.now().normalize()
        df_temp['days_to_maturity'] = (pd.to_datetime(df_temp['maturity_date']) - today).dt.days
        df_temp = df_temp[df_temp['days_to_maturity'] >= 0]

        if df_temp.empty:
            return _create_empty_chart("Aucune position active")


        bins = [0, 7, 14, 30, 60, 90, 180, 365, 999999]
        labels = ['0-7j', '8-14j', '15-30j', '31-60j', '61-90j', '91-180j', '180j-1Y', '1Y+']

        df_temp['maturity_bucket'] = pd.cut(
            df_temp['days_to_maturity'],
            bins=bins,
            labels=labels,
            right=False
        )


        maturity_agg = df_temp.groupby('maturity_bucket').agg({
            'amount': 'sum',
            'total_pnl': 'sum',
            'deal_id': 'count'
        }).reset_index()

        maturity_agg['amount_m'] = maturity_agg['amount'] / 1_000_000
        maturity_agg['pnl_m'] = maturity_agg['total_pnl'] / 1_000_000


        colors = ['#ff6b6b' if pnl < 0 else '#26de81' if pnl > 0 else '#95a5a6'
                 for pnl in maturity_agg['pnl_m']]

        fig = go.Figure()


        fig.add_trace(go.Bar(
            x=maturity_agg['maturity_bucket'],
            y=maturity_agg['amount_m'],
            marker_color=colors,
            name='Volume',
            text=[f"{v:.0f}M<br>{d} deals" for v, d in zip(maturity_agg['amount_m'], maturity_agg['deal_id'])],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Volume: %{y:.1f}M USD<br>PnL: %{customdata:+.2f}M USD<extra></extra>',
            customdata=maturity_agg['pnl_m']
        ))

        fig.update_layout(
            title="Profil de Maturité du Portefeuille",
            xaxis_title="Échéance",
            yaxis_title="Volume (M USD)",
            height=350,
            showlegend=False
        )

        return fig

    except Exception as e:
        logger.error(f"Erreur graphique maturité: {e}")
        return _create_error_chart(f"Erreur: {e}")


def create_risk_return_scatter(df_pnl: pd.DataFrame) -> go.Figure:
    \
\
\
\
    try:
        if df_pnl.empty:
            return _create_empty_chart("Aucune donnée PnL")

        df_temp = df_pnl.copy()


        if 'time_to_maturity_years' in df_temp.columns:

            vol_by_product = {
                'FX_SWAP': 0.12,
                'IRS': 0.08,
                'DEPOSIT': 0.05,
                'LOAN': 0.06
            }

            df_temp['volatility'] = df_temp['product'].map(vol_by_product).fillna(0.10)
            df_temp['risk_estimate'] = (
                df_temp['amount'] *
                df_temp['volatility'] *
                np.sqrt(df_temp['time_to_maturity_years'].fillna(0.5))
            ) / 1_000_000
        else:

            df_temp['risk_estimate'] = df_temp['amount'] * 0.10 / 1_000_000

        df_temp['return_estimate'] = df_temp['total_pnl'] / 1_000_000


        df_temp = df_temp[
            (df_temp['risk_estimate'] <= df_temp['risk_estimate'].quantile(0.95)) &
            (df_temp['return_estimate'] >= df_temp['return_estimate'].quantile(0.05)) &
            (df_temp['return_estimate'] <= df_temp['return_estimate'].quantile(0.95))
        ]

        if df_temp.empty:
            return _create_empty_chart("Pas de données après filtrage")


        fig = px.scatter(
            df_temp,
            x='risk_estimate',
            y='return_estimate',
            color='product',
            size='amount',
            hover_data=['deal_id', 'trader_id', 'client_rate'],
            title="Profil Risque-Rendement par Deal",
            labels={
                'risk_estimate': 'Risque Estimé (M USD)',
                'return_estimate': 'Rendement PnL (M USD)',
                'product': 'Produit'
            }
        )


        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)
        fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.7)


        if len(df_temp) > 5:

            max_risk = df_temp['risk_estimate'].max()
            optimal_return = max_risk * 0.5

            fig.add_trace(go.Scatter(
                x=[0, max_risk],
                y=[0, optimal_return],
                mode='lines',
                name='Ratio Optimal (approx)',
                line=dict(dash='dot', color='orange', width=2),
                hoverinfo='skip'
            ))

        fig.update_layout(height=350)

        return fig

    except Exception as e:
        logger.error(f"Erreur graphique risque-rendement: {e}")
        return _create_error_chart(f"Erreur: {e}")


def _create_empty_chart(message: str) -> go.Figure:
    \
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font_size=14,
        font_color="gray"
    )
    fig.update_layout(
        height=350,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig


def _create_error_chart(error_msg: str) -> go.Figure:
    \
    fig = go.Figure()
    fig.add_annotation(
        text=error_msg,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font_size=12,
        font_color="red"
    )
    fig.update_layout(
        height=350,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig


