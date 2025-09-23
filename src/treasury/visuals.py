\
\
\
\

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, Dict, List, Union, Any

from .analytics import convert_generic_to_analytics_format
from .logging_config import logger


def create_pnl_breakdown_chart(df_pnl: pd.DataFrame) -> go.Figure:
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
        if df_pnl.empty:
            fig.add_annotation(
                text="Aucune donnée PnL disponible",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font_size=16
            )
            return fig


        pnl_columns = ['accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl']
        available_columns = [col for col in pnl_columns if col in df_pnl.columns]

        if not available_columns:
            fig.add_annotation(
                text="Colonnes PnL non trouvées",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font_size=16
            )
            return fig


        agg_dict = {col: 'sum' for col in available_columns}
        pnl_by_product = df_pnl.groupby('product').agg(agg_dict).reset_index()


        for col in available_columns:
            pnl_by_product[f'{col}_m'] = pnl_by_product[col] / 1_000_000


        colors = {
            'accrued_pnl_m': '#4ecdc4',
            'mtm_pnl_m': '#45b7d1',
            'rate_pnl_m': '#96ceb4',
            'liquidity_pnl_m': '#ffeaa7'
        }

        names = {
            'accrued_pnl_m': 'Accrued PnL',
            'mtm_pnl_m': 'MTM PnL',
            'rate_pnl_m': 'Rate PnL',
            'liquidity_pnl_m': 'Liquidity PnL'
        }


        for col in available_columns:
            col_m = f'{col}_m'
            if col_m in pnl_by_product.columns:
                fig.add_trace(go.Bar(
                    name=names.get(col_m, col),
                    x=pnl_by_product['product'],
                    y=pnl_by_product[col_m],
                    marker_color=colors.get(col_m, '#cccccc'),
                    hovertemplate=f'<b>%{{x}}</b><br>{names.get(col_m, col)}: %{{y:.2f}}M USD<extra></extra>'
                ))

        fig.update_layout(
            title='Décomposition PnL par Type et Produit (M USD)',
            xaxis_title='Produit',
            yaxis_title='PnL (M USD)',
            barmode='stack',
            height=400,
            hovermode='x unified',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug("Graphique PnL breakdown créé")

    except Exception as e:
        logger.error(f"Erreur création graphique PnL breakdown: {e}")
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font_size=14, font_color="red"
        )

    return fig


def create_pnl_waterfall_enhanced(df_pnl: pd.DataFrame) -> go.Figure:
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
        if df_pnl.empty:
            fig.add_annotation(
                text="Aucune donnée PnL pour waterfall",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font_size=16
            )
            return fig


        components = {}
        pnl_columns = ['accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl']

        for col in pnl_columns:
            if col in df_pnl.columns:
                components[col.replace('_pnl', '').title()] = df_pnl[col].sum() / 1_000_000

        if not components:
            fig.add_annotation(
                text="Aucune composante PnL trouvée",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font_size=16
            )
            return fig

        categories = list(components.keys())
        values = list(components.values())
        total_value = sum(values)


        fig.add_trace(go.Waterfall(
            name="PnL Breakdown",
            orientation="v",
            measure=["relative"] * len(categories) + ["total"],
            x=categories + ["Total PnL"],
            y=values + [total_value],
            textposition="outside",
            text=[f"{v:+.2f}M" for v in values] + [f"{total_value:+.2f}M"],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#26de81"}},
            decreasing={"marker": {"color": "#ff6b6b"}},
            totals={"marker": {"color": "#45b7d1"}}
        ))

        fig.update_layout(
            title='Waterfall PnL Enhanced - Décomposition Complète',
            yaxis_title='PnL (M USD)',
            height=500,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug("Graphique waterfall créé")

    except Exception as e:
        logger.error(f"Erreur waterfall: {e}")
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font_size=14, font_color="red"
        )

    return fig


def create_3d_risk_surface() -> go.Figure:
\
\
\

    import streamlit as st

    try:
        df_pnl = st.session_state.get('df_pnl_enhanced', pd.DataFrame())
        df = convert_generic_to_analytics_format(df_pnl)

        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Aucune position pour surface 3D",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig


        tenors = sorted(df['tenor'].dropna().unique().tolist())
        pairs = sorted(df['paire'].dropna().unique().tolist())


        if len(tenors) < 2 or len(pairs) < 2:
            agg_data = df.groupby('paire')['notional'].sum() / 1_000_000
            fig = px.bar(
                x=agg_data.index,
                y=agg_data.values,
                title='Exposition par Paire (Vue 2D)',
                labels={'x': 'Paire', 'y': 'Notionnel (M USD)'}
            )
            return fig


        df['tenor'] = pd.Categorical(df['tenor'], categories=tenors, ordered=True)


        g = (df.groupby(['paire', 'tenor'])['notional']
             .sum().div(1_000_000).rename('notional_m').reset_index())


        g['vol'] = 0.18
        g['var_m'] = g['notional_m'] * g['vol'] * 2.33


        Z = g.pivot(index='paire', columns='tenor', values='var_m').fillna(0.0)


        x_indices = np.arange(len(Z.columns))
        y_indices = np.arange(len(Z.index))
        X, Y = np.meshgrid(x_indices, y_indices)


        hover_text = []
        for i, pair in enumerate(Z.index):
            row = []
            for j, tenor in enumerate(Z.columns):
                var_val = Z.iloc[i, j]
                hover_str = f"Paire: {pair}<br>Tenor: {tenor}<br>VaR: {var_val:.2f}M USD"
                row.append(hover_str)
            hover_text.append(row)


        fig = go.Figure(data=[go.Surface(
            z=Z.values,
            x=X,
            y=Y,
            colorscale='Viridis',
            opacity=0.85,
            text=hover_text,
            hovertemplate='%{text}<extra></extra>',
            showscale=True,
            colorbar=dict(title="VaR (M USD)")
        )])

        fig.update_layout(
            title='Surface 3D VaR par Paire × Tenor',
            scene=dict(
                xaxis=dict(
                    title='Tenor',
                    tickmode='array',
                    tickvals=x_indices,
                    ticktext=Z.columns.tolist(),
                    titlefont=dict(color='white'),
                    tickfont=dict(color='white')
                ),
                yaxis=dict(
                    title='Paire',
                    tickmode='array',
                    tickvals=y_indices,
                    ticktext=Z.index.tolist(),
                    titlefont=dict(color='white'),
                    tickfont=dict(color='white')
                ),
                zaxis_title='VaR (M USD)'
            ),
            height=600,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug("Surface 3D créée")
        return fig

    except Exception as e:
        logger.error(f"Erreur surface 3D: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig


def create_3d_portfolio_composition() -> go.Figure:
    \
\
\
    import streamlit as st

    try:
        df_pnl = st.session_state.get('df_pnl_enhanced', pd.DataFrame())
        df = convert_generic_to_analytics_format(df_pnl)

        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Aucune position Enhanced",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font_size=16
            )
            return fig


        comp = (df.groupby(['paire', 'type', 'tenor'])['notional'].sum().reset_index())
        if comp.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Pas de données pour composition 3D",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font_size=16
            )
            return fig

        comp['notional_m'] = comp['notional'] / 1_000_000
        size_series = np.clip(comp['notional_m'] / 10.0, 3, 30)

        fig = go.Figure()


        colors = {
            'FX_SWAP': '#ff6b6b',
            'IRS': '#4ecdc4',
            'DEPOSIT': '#45b7d1',
            'LOAN': '#ffeaa7'
        }

        for instrument_type in comp['type'].unique():
            data = comp[comp['type'] == instrument_type]
            if data.empty:
                continue

            fig.add_trace(go.Scatter3d(
                x=data['paire'],
                y=data['tenor'],
                z=data['notional_m'],
                mode='markers',
                marker=dict(
                    size=size_series.loc[data.index],
                    opacity=0.9,
                    line=dict(width=1, color='white'),
                    color=colors.get(instrument_type, '#cccccc')
                ),
                name=f"{instrument_type} ({len(data)} deals)",
                hovertemplate=(
                    '<b>%{x}</b><br>'
                    'Tenor: %{y}<br>'
                    'Notionnel: %{z:.1f}M USD<br>'
                    'Type: ' + instrument_type +
                    '<extra></extra>'
                )
            ))

        fig.update_layout(
            title='Composition 3D Enhanced (Tous Produits)',
            scene=dict(
                xaxis_title='Paire',
                yaxis_title='Tenor',
                zaxis_title='Notionnel (M USD)'
            ),
            height=600,
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug("Composition 3D créée")
        return fig

    except Exception as e:
        logger.error(f"Erreur composition 3D: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig


def create_time_decay_analysis() -> go.Figure:
    \
\
\
    import streamlit as st
    from .utils.dates import VAL_DATE, to_naive_series

    try:
        df_pnl = st.session_state.get('df_pnl_enhanced', pd.DataFrame())
        df = convert_generic_to_analytics_format(df_pnl)

        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Aucune position Enhanced",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font_size=16
            )
            return fig


        df['date_echeance'] = to_naive_series(df['date_echeance'])
        days_to = (df['date_echeance'] - VAL_DATE).dt.days
        df['days_to_maturity'] = days_to.clip(lower=0)


        bins = [0, 7, 14, 30, 60, 90, 180, 365, 999999]
        labels = ['0-7j', '8-14j', '15-30j', '31-60j', '61-90j', '91-180j', '180j-1Y', '1Y+']
        df['maturity_bucket'] = pd.cut(df['days_to_maturity'], bins=bins, labels=labels, right=False)


        td = (df.groupby(['maturity_bucket', 'paire', 'instrument'])['notional'].sum().reset_index())
        td['notional_m'] = td['notional'] / 1_000_000


        fig = px.bar(
            td,
            x='maturity_bucket',
            y='notional_m',
            color='paire',
            pattern_shape='instrument',
            title='⏰ Profil de Maturité Enhanced (Tous Produits)',
            labels={
                'maturity_bucket': "Plage d'échéance",
                'notional_m': 'Notionnel (M USD)',
                'paire': 'Paire'
            },
            height=500
        )

        fig.update_layout(
            xaxis_title="Jours jusqu'à Échéance",
            yaxis_title="Notionnel (M USD)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug("Analyse time decay créée")
        return fig

    except Exception as e:
        logger.error(f"Erreur time decay: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig


def create_liquidity_heatmap() -> go.Figure:
    \
\
\
\
\
\
    import streamlit as st

    try:
        df_pnl = st.session_state.get('df_pnl_enhanced', pd.DataFrame())
        df = convert_generic_to_analytics_format(df_pnl)

        fig = go.Figure()

        if df.empty:
            fig.add_annotation(
                text="Aucune position pour heatmap",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig

        pairs = df['paire'].unique().tolist()
        tenors = sorted(df['tenor'].dropna().unique().tolist())

        if not tenors:
            fig.add_annotation(
                text="Pas de tenors valides",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig


        liquidity_matrix = []
        hover_matrix = []

        for pair in pairs:
            row = []
            hover_row = []

            for tenor in tenors:
                selection = df[(df['paire'] == pair) & (df['tenor'] == tenor)]

                if selection.empty:
                    row.append(0)
                    hover_row.append(f"{pair}/{tenor}: Aucune position")
                else:
                    total_m = selection['notional'].sum() / 1_000_000
                    deal_count = len(selection)
                    instruments = ", ".join(selection['instrument'].unique())


                    liquidity_score = min(100, (total_m / 10) + (deal_count * 5))

                    row.append(liquidity_score)
                    hover_row.append(
                        f"{pair}/{tenor}<br>"
                        f"Volume: {total_m:.1f}M USD<br>"
                        f"Deals: {deal_count}<br>"
                        f"Instruments: {instruments}<br>"
                        f"Score Liquidité: {liquidity_score:.1f}"
                    )

            liquidity_matrix.append(row)
            hover_matrix.append(hover_row)


        fig.add_trace(go.Heatmap(
            z=liquidity_matrix,
            x=tenors,
            y=pairs,
            colorscale='Viridis',
            text=hover_matrix,
            hovertemplate='%{text}<extra></extra>',
            colorbar=dict(title="Score Liquidité")
        ))

        fig.update_layout(
            title='💧 Heatmap Liquidité par Paire × Tenor',
            xaxis_title='Tenor',
            yaxis_title='Paire',
            height=430,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug("Heatmap liquidité créée")
        return fig

    except Exception as e:
        logger.error(f"Erreur heatmap liquidité: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig


def create_correlation_heatmap() -> go.Figure:
    \
\
\
\
\
\
    import streamlit as st

    try:
        df_pnl = st.session_state.get('df_pnl_enhanced', pd.DataFrame())

        fig = go.Figure()

        if df_pnl.empty:
            fig.add_annotation(
                text="Aucune donnée PnL pour corrélation",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig


        pnl_cols = [col for col in ['accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl']
                   if col in df_pnl.columns]

        if len(pnl_cols) < 2:
            fig.add_annotation(
                text="Pas assez de types PnL pour corrélation",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig


        corr_matrix = df_pnl[pnl_cols].corr()


        labels = [col.replace('_pnl', '').title() for col in corr_matrix.columns]


        fig.add_trace(go.Heatmap(
            z=corr_matrix.values,
            x=labels,
            y=labels,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.round(2).values,
            texttemplate='%{text}',
            textfont={"size": 12},
            hovertemplate='%{x} vs %{y}<br>Corrélation: %{z:.3f}<extra></extra>',
            colorbar=dict(title="Corrélation")
        ))

        fig.update_layout(
            title='🔗 Matrice de Corrélation des PnL',
            height=400,
            xaxis_title='Type PnL',
            yaxis_title='Type PnL',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug("Heatmap corrélation créée")
        return fig

    except Exception as e:
        logger.error(f"Erreur heatmap corrélation: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig


def create_portfolio_composition_pie(df_pnl: pd.DataFrame, dimension: str = 'product') -> go.Figure:
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
        if df_pnl.empty or dimension not in df_pnl.columns:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Données manquantes pour dimension: {dimension}",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig


        composition = df_pnl.groupby(dimension).agg({
            'amount': 'sum',
            'deal_id': 'count',
            'total_pnl': 'sum'
        }).reset_index()

        composition['amount_m'] = composition['amount'] / 1_000_000
        composition['pnl_m'] = composition['total_pnl'] / 1_000_000


        fig = go.Figure(data=[go.Pie(
            labels=composition[dimension],
            values=composition['amount_m'],
            hole=0.3,
            textinfo='label+percent',
            hovertemplate=(
                '<b>%{label}</b><br>'
                'Notionnel: %{value:.1f}M USD<br>'
                'Deals: %{customdata[0]}<br>'
                'PnL: %{customdata[1]:+.2f}M USD<br>'
                '<extra></extra>'
            ),
            customdata=list(zip(composition['deal_id'], composition['pnl_m']))
        )])

        fig.update_layout(
            title=f'🥧 Composition Portefeuille par {dimension.title()}',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug(f"Graphique composition {dimension} créé")
        return fig

    except Exception as e:
        logger.error(f"Erreur graphique composition: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig


def create_maturity_profile_chart(df_pnl: pd.DataFrame) -> go.Figure:
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
        if df_pnl.empty or 'maturity_date' not in df_pnl.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="Données d'échéances manquantes",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig

        from .utils.dates import VAL_DATE


        df_temp = df_pnl.copy()
        df_temp['days_to_maturity'] = (pd.to_datetime(df_temp['maturity_date']) - VAL_DATE).dt.days


        bins = [0, 7, 14, 30, 60, 90, 180, 365, 999999]
        labels = ['0-7j', '8-14j', '15-30j', '31-60j', '61-90j', '91-180j', '180j-1Y', '1Y+']

        df_temp['maturity_bucket'] = pd.cut(
            df_temp['days_to_maturity'],
            bins=bins,
            labels=labels,
            right=False
        )


        maturity_profile = df_temp.groupby(['maturity_bucket', 'product']).agg({
            'amount': 'sum',
            'deal_id': 'count'
        }).reset_index()

        maturity_profile['amount_m'] = maturity_profile['amount'] / 1_000_000


        fig = px.bar(
            maturity_profile,
            x='maturity_bucket',
            y='amount_m',
            color='product',
            title='⏰ Profil de Maturité du Portefeuille',
            labels={
                'maturity_bucket': "Plage d'échéance",
                'amount_m': 'Notionnel (M USD)',
                'product': 'Produit'
            },
            height=500
        )

        fig.update_layout(
            xaxis_title="Jours jusqu'à échéance",
            yaxis_title="Notionnel (M USD)",
            barmode='stack',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug("Graphique profil maturité créé")
        return fig

    except Exception as e:
        logger.error(f"Erreur profil maturité: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig


def create_pnl_trend_chart(df_pnl: pd.DataFrame, groupby_column: str = 'trade_date') -> go.Figure:
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
        if df_pnl.empty or groupby_column not in df_pnl.columns:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Colonne {groupby_column} manquante",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig


        df_temp = df_pnl.copy()
        df_temp[groupby_column] = pd.to_datetime(df_temp[groupby_column])

        trend_data = df_temp.groupby([df_temp[groupby_column].dt.date, 'product']).agg({
            'total_pnl': 'sum',
            'amount': 'sum'
        }).reset_index()

        trend_data['total_pnl_m'] = trend_data['total_pnl'] / 1_000_000
        trend_data['amount_m'] = trend_data['amount'] / 1_000_000


        fig = px.line(
            trend_data,
            x=groupby_column,
            y='total_pnl_m',
            color='product',
            title='Évolution PnL par Date de Trade',
            labels={
                groupby_column: 'Date',
                'total_pnl_m': 'PnL Total (M USD)',
                'product': 'Produit'
            }
        )

        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

        fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))

        logger.debug("Graphique tendance PnL créé")
        return fig

    except Exception as e:
        logger.error(f"Erreur tendance PnL: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig


def create_trader_performance_chart(df_pnl: pd.DataFrame) -> go.Figure:
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
        if df_pnl.empty or 'trader_id' not in df_pnl.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="Données trader manquantes",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig


        trader_perf = df_pnl.groupby('trader_id').agg({
            'total_pnl': 'sum',
            'amount': 'sum',
            'deal_id': 'count'
        }).reset_index()


        trader_perf = trader_perf[trader_perf['deal_id'] >= 2]

        if trader_perf.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Pas assez de données trader",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig

        trader_perf['pnl_m'] = trader_perf['total_pnl'] / 1_000_000
        trader_perf['amount_m'] = trader_perf['amount'] / 1_000_000
        trader_perf['pnl_bps'] = (trader_perf['total_pnl'] / trader_perf['amount'] * 10_000).fillna(0)


        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=trader_perf['amount_m'],
            y=trader_perf['pnl_m'],
            mode='markers+text',
            text=trader_perf['trader_id'],
            textposition='top center',
            marker=dict(
                size=trader_perf['deal_id'] * 3,
                color=trader_perf['pnl_bps'],
                colorscale='RdYlGn',
                colorbar=dict(title="PnL (bps)"),
                line=dict(width=2, color='white')
            ),
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Volume: %{x:.1f}M USD<br>'
                'PnL: %{y:+.2f}M USD<br>'
                'Deals: %{customdata[0]}<br>'
                'PnL: %{customdata[1]:+.1f} bps<br>'
                '<extra></extra>'
            ),
            customdata=list(zip(trader_perf['deal_id'], trader_perf['pnl_bps']))
        ))

        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

        fig.update_layout(
            title='👥 Performance par Trader',
            xaxis_title='Volume Trading (M USD)',
            yaxis_title='PnL Total (M USD)',
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug("Graphique performance trader créé")
        return fig

    except Exception as e:
        logger.error(f"Erreur performance trader: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig


def create_risk_return_scatter(df_pnl: pd.DataFrame) -> go.Figure:
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
        if df_pnl.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Aucune donnée pour scatter",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig


        df_temp = df_pnl.copy()

        if 'time_to_maturity_years' in df_temp.columns:

            df_temp['risk_estimate'] = (
                df_temp['amount'] *
                df_temp['time_to_maturity_years'].fillna(0) *
                0.15
            ) / 1_000_000
        else:
            df_temp['risk_estimate'] = df_temp['amount'] * 0.10 / 1_000_000

        df_temp['return_estimate'] = df_temp['total_pnl'] / 1_000_000


        fig = px.scatter(
            df_temp,
            x='risk_estimate',
            y='return_estimate',
            color='product',
            size='amount',
            hover_data=['deal_id', 'client_rate'],
            title='Profil Risque-Rendement par Deal',
            labels={
                'risk_estimate': 'Risque Estimé (M USD)',
                'return_estimate': 'Rendement (PnL M USD)',
                'product': 'Produit'
            }
        )


        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)


        if len(df_temp) > 5:
            x_range = np.linspace(df_temp['risk_estimate'].min(), df_temp['risk_estimate'].max(), 50)
            efficient_frontier = x_range * 0.3

            fig.add_trace(go.Scatter(
                x=x_range,
                y=efficient_frontier,
                mode='lines',
                name='Frontière Efficiente (approx)',
                line=dict(dash='dot', color='orange'),
                hoverinfo='skip'
            ))

        fig.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))

        logger.debug("Scatter risque-rendement créé")
        return fig

    except Exception as e:
        logger.error(f"Erreur scatter risque-rendement: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig


def create_scenario_analysis() -> go.Figure:
    \
\
\
    import streamlit as st

    try:
        df_pnl = st.session_state.get('df_pnl_enhanced', pd.DataFrame())

        if df_pnl.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Aucune donnée PnL pour analyse scénarios",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig


        scenarios = {
            'Récession': {'rate_shift': -0.02, 'fx_vol': 1.5, 'credit_spread': 0.01},
            'Inflation': {'rate_shift': 0.025, 'fx_vol': 1.2, 'credit_spread': 0.005},
            'Stagflation': {'rate_shift': 0.01, 'fx_vol': 1.8, 'credit_spread': 0.015},
            'Reprise': {'rate_shift': 0.015, 'fx_vol': 0.8, 'credit_spread': -0.002},
            'Crise Bancaire': {'rate_shift': -0.015, 'fx_vol': 2.0, 'credit_spread': 0.02}
        }

        results = []
        for scenario_name, params in scenarios.items():
            total_impact = 0


            if 'mtm_pnl' in df_pnl.columns and 'amount' in df_pnl.columns:
                mtm_impact = df_pnl['amount'].sum() * params['rate_shift'] * 0.3
                total_impact += mtm_impact


            if 'rate_pnl' in df_pnl.columns and 'amount' in df_pnl.columns:
                rate_impact = df_pnl['amount'].sum() * params['rate_shift'] * 0.2
                total_impact += rate_impact


            if 'liquidity_pnl' in df_pnl.columns and 'amount' in df_pnl.columns:
                liq_impact = df_pnl['amount'].sum() * params['credit_spread'] * 0.1
                total_impact += liq_impact

            results.append({
                'Scénario': scenario_name,
                'Impact': total_impact / 1_000_000,
                'Rate Shift': f"{params['rate_shift']*100:+.1f}%",
                'FX Vol': f"{params['fx_vol']:.1f}x",
                'Credit Spread': f"{params['credit_spread']*10000:+.0f}bp"
            })

        df_results = pd.DataFrame(results)


        fig = go.Figure(data=[go.Bar(
            x=df_results['Scénario'],
            y=df_results['Impact'],
            marker_color=['#ff6b6b' if x < 0 else '#26de81' for x in df_results['Impact']],
            text=[f"{x:+.1f}M" for x in df_results['Impact']],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Impact: %{y:+.1f}M USD<extra></extra>'
        )])

        fig.update_layout(
            title='🌍 Analyse de Scénarios Macroéconomiques',
            yaxis_title='Impact P&L (M USD)',
            height=400,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug("Analyse scénarios créée")
        return fig

    except Exception as e:
        logger.error(f"Erreur analyse scénarios: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig


def create_var_breakdown() -> go.Figure:
    \
\
\
    import streamlit as st
    from .risk import run_monte_carlo_simulation
    from .analytics import convert_generic_to_analytics_format

    try:
        df_pnl = st.session_state.get('df_pnl_enhanced', pd.DataFrame())

        if df_pnl.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Aucun résultat VaR",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig


        df_analytics = convert_generic_to_analytics_format(df_pnl)
        sim_results = run_monte_carlo_simulation(df_analytics, n_simulations=10000, seed=123)

        if not sim_results:
            fig = go.Figure()
            fig.add_annotation(
                text="Impossible de calculer VaR breakdown",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig


        components = {}

        if 'fx_component' in sim_results:
            fx_pnl = np.array(sim_results['fx_component'])
            components['FX VaR 95%'] = np.percentile(fx_pnl, 5) / 1_000_000
            components['FX VaR 99%'] = np.percentile(fx_pnl, 1) / 1_000_000

        if 'rate_component' in sim_results:
            rate_pnl = np.array(sim_results['rate_component'])
            components['Rate VaR 95%'] = np.percentile(rate_pnl, 5) / 1_000_000
            components['Rate VaR 99%'] = np.percentile(rate_pnl, 1) / 1_000_000


        components['Total VaR 95%'] = sim_results.get('var_95', 0) / 1_000_000
        components['Total VaR 99%'] = sim_results.get('var_99', 0) / 1_000_000

        if not components:
            fig = go.Figure()
            fig.add_annotation(
                text="Pas de composantes VaR disponibles",
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font_size=16
            )
            return fig

        categories = list(components.keys())
        values = list(components.values())


        colors = ['#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#ff6b6b', '#e17055']

        fig = go.Figure(data=[go.Bar(
            x=categories,
            y=values,
            marker_color=colors[:len(categories)],
            text=[f"{v:+.1f}M" for v in values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>VaR: %{y:+.1f}M USD<extra></extra>'
        )])

        fig.update_layout(
            title='Décomposition VaR par Composante',
            yaxis_title='VaR (M USD)',
            height=400,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        logger.debug("VaR breakdown créé")
        return fig

    except Exception as e:
        logger.error(f"Erreur VaR breakdown: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur: {str(e)}",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False, font_size=14, font_color="red"
        )
        return fig