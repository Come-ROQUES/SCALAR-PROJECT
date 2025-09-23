
import pandas as pd
import numpy as np
from typing import Dict, List, Union, Any, Optional

from .utils.dates import VAL_DATE, to_naive_series, classify_tenor, get_years_between
from .logging_config import logger


def convert_generic_to_analytics_format(df_pnl: pd.DataFrame) -> pd.DataFrame:

    try:
        if df_pnl.empty:
            logger.warning("DataFrame PnL vide pour conversion analytics")
            return pd.DataFrame()

        analytics_rows = []

        for _, row in df_pnl.iterrows():

            if pd.notna(row.get('time_to_maturity_years')):
                tenor = classify_tenor(row['time_to_maturity_years'])
            else:
                tenor = "Unknown"


            pair_currency = row.get('pair_currency', '')
            if '/' in pair_currency:
                devise_base = pair_currency.split('/')[0]
                devise_quote = pair_currency.split('/')[1]
            else:
                devise_base = pair_currency
                devise_quote = 'USD'

            analytics_row = {
                'deal_id': row.get('deal_id', ''),
                'paire': pair_currency,
                'notional': row.get('amount', 0),
                'date_ouverture': row.get('trade_date'),
                'date_echeance': row.get('maturity_date'),
                'tenor': tenor,
                'type': row.get('product', ''),
                'trader_id': row.get('trader_id') or 'Unknown',
                'instrument': row.get('product', ''),
                'devise_base': devise_base,
                'devise_quote': devise_quote,
                'pnl_total': row.get('total_pnl', 0),
                'pnl_accrued': row.get('accrued_pnl', 0),
                'pnl_mtm': row.get('mtm_pnl', 0),
                'client_rate': row.get('client_rate', 0),
                'ois_rate': row.get('ois_rate_now', 0)
            }

            analytics_rows.append(analytics_row)

        df_analytics = pd.DataFrame(analytics_rows)


        if not df_analytics.empty:

            df_analytics['date_echeance'] = to_naive_series(df_analytics['date_echeance'])
            df_analytics['date_ouverture'] = to_naive_series(df_analytics['date_ouverture'])


            df_analytics['days_to_maturity'] = (df_analytics['date_echeance'] - VAL_DATE).dt.days


            df_analytics['notional_m'] = df_analytics['notional'] / 1_000_000
            df_analytics['pnl_total_m'] = df_analytics['pnl_total'] / 1_000_000


            df_analytics['is_urgent'] = df_analytics['days_to_maturity'] <= 7
            df_analytics['is_expired'] = df_analytics['days_to_maturity'] < 0


            df_analytics['size_category'] = pd.cut(
                df_analytics['notional_m'],
                bins=[0, 10, 50, 100, 500, float('inf')],
                labels=['Small', 'Medium', 'Large', 'XLarge', 'Jumbo']
            )

        logger.info(f"Conversion analytics: {len(df_pnl)} -> {len(df_analytics)} lignes")
        return df_analytics

    except Exception as e:
        logger.error(f"Erreur conversion Generic→Analytics: {e}")
        return pd.DataFrame()


def calculate_portfolio_concentrations(df_analytics: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    concentrations = {}

    try:
        if df_analytics.empty:
            return concentrations

        total_notional = df_analytics['notional'].sum()

        if total_notional == 0:
            logger.warning("Notionnel total nul pour calcul concentrations")
            return concentrations


        conc_devise = df_analytics.groupby('devise_base').agg({
            'notional': 'sum',
            'deal_id': 'count',
            'pnl_total': 'sum'
        }).reset_index()

        conc_devise['concentration_pct'] = conc_devise['notional'] / total_notional * 100
        conc_devise = conc_devise.sort_values('concentration_pct', ascending=False)
        concentrations['devise'] = conc_devise


        conc_produit = df_analytics.groupby('instrument').agg({
            'notional': 'sum',
            'deal_id': 'count',
            'pnl_total': 'sum'
        }).reset_index()

        conc_produit['concentration_pct'] = conc_produit['notional'] / total_notional * 100
        conc_produit = conc_produit.sort_values('concentration_pct', ascending=False)
        concentrations['produit'] = conc_produit


        conc_tenor = df_analytics.groupby('tenor').agg({
            'notional': 'sum',
            'deal_id': 'count',
            'pnl_total': 'sum'
        }).reset_index()

        conc_tenor['concentration_pct'] = conc_tenor['notional'] / total_notional * 100
        conc_tenor = conc_tenor.sort_values('concentration_pct', ascending=False)
        concentrations['tenor'] = conc_tenor


        if 'trader_id' in df_analytics.columns:
            conc_trader = df_analytics.groupby('trader_id').agg({
                'notional': 'sum',
                'deal_id': 'count',
                'pnl_total': 'sum'
            }).reset_index()

            conc_trader['concentration_pct'] = conc_trader['notional'] / total_notional * 100
            conc_trader = conc_trader.sort_values('concentration_pct', ascending=False)
            concentrations['trader'] = conc_trader

        logger.info(f"Concentrations calculées: {list(concentrations.keys())}")

    except Exception as e:
        logger.error(f"Erreur calcul concentrations: {e}")

    return concentrations


def calculate_time_profile(df_analytics: pd.DataFrame) -> pd.DataFrame:
    try:
        if df_analytics.empty:
            return pd.DataFrame()


        time_buckets = [
            (0, 7, '0-7j'),
            (8, 30, '1M'),
            (31, 90, '3M'),
            (91, 180, '6M'),
            (181, 365, '1Y'),
            (366, 730, '2Y'),
            (731, 1825, '5Y'),
            (1826, float('inf'), '5Y+')
        ]

        profile_data = []

        for min_days, max_days, bucket_name in time_buckets:
            if max_days == float('inf'):
                mask = df_analytics['days_to_maturity'] >= min_days
            else:
                mask = (df_analytics['days_to_maturity'] >= min_days) & (df_analytics['days_to_maturity'] <= max_days)

            subset = df_analytics[mask]

            if not subset.empty:
                profile_data.append({
                    'bucket': bucket_name,
                    'min_days': min_days,
                    'max_days': max_days if max_days != float('inf') else 9999,
                    'deal_count': len(subset),
                    'notional': subset['notional'].sum(),
                    'notional_m': subset['notional'].sum() / 1_000_000,
                    'pnl_total': subset['pnl_total'].sum(),
                    'avg_rate': subset['client_rate'].mean(),
                    'instruments': list(subset['instrument'].unique())
                })

        df_profile = pd.DataFrame(profile_data)

        if not df_profile.empty:
            total_notional = df_profile['notional'].sum()
            df_profile['concentration_pct'] = df_profile['notional'] / total_notional * 100 if total_notional > 0 else 0

        logger.info(f"Profil temporel calculé: {len(df_profile)} buckets")
        return df_profile

    except Exception as e:
        logger.error(f"Erreur calcul profil temporel: {e}")
        return pd.DataFrame()


def calculate_pnl_attribution(df_analytics: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    \
\
\
\
\
\
\
\
\
    attributions = {}

    try:
        if df_analytics.empty or 'pnl_total' not in df_analytics.columns:
            return attributions


        attr_devise = df_analytics.groupby('devise_base').agg({
            'pnl_total': ['sum', 'mean', 'count'],
            'notional': 'sum'
        }).round(0)

        attr_devise.columns = ['pnl_total', 'pnl_moyenne', 'deal_count', 'notional']
        attr_devise['pnl_total_m'] = attr_devise['pnl_total'] / 1_000_000
        attr_devise['pnl_bps'] = (attr_devise['pnl_total'] / attr_devise['notional'] * 10_000).fillna(0)
        attributions['devise'] = attr_devise.reset_index()


        attr_produit = df_analytics.groupby('instrument').agg({
            'pnl_total': ['sum', 'mean', 'count'],
            'notional': 'sum'
        }).round(0)

        attr_produit.columns = ['pnl_total', 'pnl_moyenne', 'deal_count', 'notional']
        attr_produit['pnl_total_m'] = attr_produit['pnl_total'] / 1_000_000
        attr_produit['pnl_bps'] = (attr_produit['pnl_total'] / attr_produit['notional'] * 10_000).fillna(0)
        attributions['produit'] = attr_produit.reset_index()


        attr_tenor = df_analytics.groupby('tenor').agg({
            'pnl_total': ['sum', 'mean', 'count'],
            'notional': 'sum'
        }).round(0)

        attr_tenor.columns = ['pnl_total', 'pnl_moyenne', 'deal_count', 'notional']
        attr_tenor['pnl_total_m'] = attr_tenor['pnl_total'] / 1_000_000
        attr_tenor['pnl_bps'] = (attr_tenor['pnl_total'] / attr_tenor['notional'] * 10_000).fillna(0)
        attributions['tenor'] = attr_tenor.reset_index()

        logger.info(f"Attribution PnL calculée: {list(attributions.keys())}")

    except Exception as e:
        logger.error(f"Erreur attribution PnL: {e}")

    return attributions


def calculate_performance_metrics(df_analytics: pd.DataFrame) -> Dict[str, float]:
    \
\
\
\
\
\
\
\
\
    metrics = {}

    try:
        if df_analytics.empty:
            return metrics


        total_notional = df_analytics['notional'].sum()
        total_pnl = df_analytics['pnl_total'].sum() if 'pnl_total' in df_analytics.columns else 0
        deal_count = len(df_analytics)

        metrics['total_notional_usd'] = total_notional
        metrics['total_notional_m'] = total_notional / 1_000_000
        metrics['total_pnl_usd'] = total_pnl
        metrics['total_pnl_m'] = total_pnl / 1_000_000
        metrics['deal_count'] = deal_count


        if total_notional > 0:
            metrics['roi_pct'] = total_pnl / total_notional * 100
            metrics['pnl_bps'] = total_pnl / total_notional * 10_000
        else:
            metrics['roi_pct'] = 0
            metrics['pnl_bps'] = 0


        if deal_count > 0:
            metrics['avg_pnl_per_deal'] = total_pnl / deal_count
            metrics['avg_notional_per_deal'] = total_notional / deal_count
        else:
            metrics['avg_pnl_per_deal'] = 0
            metrics['avg_notional_per_deal'] = 0


        if 'pnl_total' in df_analytics.columns and len(df_analytics) > 1:
            pnl_std = df_analytics['pnl_total'].std()
            pnl_mean = df_analytics['pnl_total'].mean()

            metrics['pnl_volatility'] = pnl_std
            metrics['pnl_volatility_m'] = pnl_std / 1_000_000


            if pnl_mean != 0:
                metrics['pnl_cv'] = pnl_std / abs(pnl_mean)
            else:
                metrics['pnl_cv'] = 0


            if pnl_std > 0:
                metrics['sharpe_ratio'] = pnl_mean / pnl_std
            else:
                metrics['sharpe_ratio'] = 0


        if 'devise_base' in df_analytics.columns:
            devise_concentrations = df_analytics.groupby('devise_base')['notional'].sum()
            max_concentration = devise_concentrations.max() / total_notional if total_notional > 0 else 0
            metrics['max_currency_concentration'] = max_concentration


        if 'days_to_maturity' in df_analytics.columns:
            urgent_deals = len(df_analytics[df_analytics['days_to_maturity'] <= 7])
            metrics['urgent_deals_count'] = urgent_deals
            metrics['urgent_deals_pct'] = urgent_deals / deal_count * 100 if deal_count > 0 else 0


        if 'days_to_maturity' in df_analytics.columns and total_notional > 0:
            weighted_maturity = (df_analytics['days_to_maturity'] * df_analytics['notional']).sum() / total_notional
            metrics['avg_maturity_days'] = weighted_maturity
            metrics['avg_maturity_years'] = weighted_maturity / 365

        logger.info(f"Métriques performance calculées: {len(metrics)} indicateurs")

    except Exception as e:
        logger.error(f"Erreur calcul métriques performance: {e}")

    return metrics


def create_summary_report(df_analytics: pd.DataFrame) -> Dict[str, any]:
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
        report = {
            'generated_at': pd.Timestamp.now(),
            'data_as_of': VAL_DATE,
            'portfolio_metrics': calculate_performance_metrics(df_analytics),
            'concentrations': calculate_portfolio_concentrations(df_analytics),
            'time_profile': calculate_time_profile(df_analytics),
            'pnl_attribution': calculate_pnl_attribution(df_analytics)
        }


        metrics = report['portfolio_metrics']

        executive_summary = {
            'total_deals': int(metrics.get('deal_count', 0)),
            'total_notional_m': round(metrics.get('total_notional_m', 0), 1),
            'total_pnl_m': round(metrics.get('total_pnl_m', 0), 2),
            'roi_bps': round(metrics.get('pnl_bps', 0), 1),
            'urgent_deals': int(metrics.get('urgent_deals_count', 0)),
            'max_concentration': round(metrics.get('max_currency_concentration', 0) * 100, 1)
        }

        report['executive_summary'] = executive_summary


        alerts = []

        if executive_summary['urgent_deals'] > 5:
            alerts.append({
                'level': 'warning',
                'message': f"{executive_summary['urgent_deals']} deals expirent dans 7 jours",
                'recommendation': "Préparer le renouvellement ou la clôture"
            })

        if executive_summary['max_concentration'] > 40:
            alerts.append({
                'level': 'warning',
                'message': f"Concentration max: {executive_summary['max_concentration']:.1f}%",
                'recommendation': "Diversifier l'exposition par devise"
            })

        if abs(executive_summary['total_pnl_m']) > 10:
            level = 'info' if executive_summary['total_pnl_m'] > 0 else 'warning'
            alerts.append({
                'level': level,
                'message': f"PnL significatif: {executive_summary['total_pnl_m']:+.1f}M",
                'recommendation': "Analyser les sources de PnL"
            })

        report['alerts'] = alerts

        logger.info(f"Rapport synthèse généré: {len(alerts)} alertes")
        return report

    except Exception as e:
        logger.error(f"Erreur génération rapport: {e}")
        return {}


def export_analytics_to_excel(df_analytics: pd.DataFrame, filename_prefix: str = "analytics") -> bytes:
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
        import io

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            workbook = writer.book


            money_format = workbook.add_format({'num_format': '#,##0'})
            percent_format = workbook.add_format({'num_format': '0.00%'})
            header_format = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white'})


            df_analytics.to_excel(writer, sheet_name="Portfolio_Details", index=False)


            concentrations = calculate_portfolio_concentrations(df_analytics)
            for dim, df_conc in concentrations.items():
                sheet_name = f"Concentration_{dim.title()}"
                df_conc.to_excel(writer, sheet_name=sheet_name, index=False)


            attributions = calculate_pnl_attribution(df_analytics)
            for dim, df_attr in attributions.items():
                sheet_name = f"Attribution_{dim.title()}"
                df_attr.to_excel(writer, sheet_name=sheet_name, index=False)


            time_profile = calculate_time_profile(df_analytics)
            if not time_profile.empty:
                time_profile.to_excel(writer, sheet_name="Profil_Temporel", index=False)


            metrics = calculate_performance_metrics(df_analytics)
            metrics_df = pd.DataFrame([
                {'Métrique': k, 'Valeur': v} for k, v in metrics.items()
            ])
            metrics_df.to_excel(writer, sheet_name="Métriques_Performance", index=False)


            report = create_summary_report(df_analytics)
            if 'executive_summary' in report:
                summary_df = pd.DataFrame([
                    {'Indicateur': k, 'Valeur': v} for k, v in report['executive_summary'].items()
                ])
                summary_df.to_excel(writer, sheet_name="Résumé_Exécutif", index=False)


            if 'alerts' in report and report['alerts']:
                alerts_df = pd.DataFrame(report['alerts'])
                alerts_df.to_excel(writer, sheet_name="Alertes", index=False)

        logger.info(f"Export analytics Excel généré")
        return output.getvalue()

    except Exception as e:
        logger.error(f"Erreur export analytics Excel: {e}")
        raise


def validate_analytics_data(df_analytics: pd.DataFrame) -> Dict[str, any]:
    \
\
\
\
\
\
\
\
\
    validation = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'data_quality_score': 100
    }

    try:
        if df_analytics.empty:
            validation['errors'].append("DataFrame analytics vide")
            validation['is_valid'] = False
            validation['data_quality_score'] = 0
            return validation

        required_columns = ['deal_id', 'notional', 'tenor', 'instrument', 'devise_base']
        missing_columns = [col for col in required_columns if col not in df_analytics.columns]

        if missing_columns:
            validation['errors'].append(f"Colonnes manquantes: {missing_columns}")
            validation['is_valid'] = False
            validation['data_quality_score'] -= 20


        null_counts = df_analytics.isnull().sum()
        high_null_columns = null_counts[null_counts > len(df_analytics) * 0.1].index.tolist()

        if high_null_columns:
            validation['warnings'].append(f"Colonnes avec >10% valeurs manquantes: {high_null_columns}")
            validation['data_quality_score'] -= 10


        if 'notional' in df_analytics.columns:
            negative_notionals = len(df_analytics[df_analytics['notional'] <= 0])
            if negative_notionals > 0:
                validation['warnings'].append(f"{negative_notionals} notionnels négatifs ou nuls")
                validation['data_quality_score'] -= 5


            q99 = df_analytics['notional'].quantile(0.99)
            if q99 > 1_000_000_000:
                validation['warnings'].append(f"Notionnels très élevés détectés (max: {q99:,.0f})")
                validation['data_quality_score'] -= 5


        if 'days_to_maturity' in df_analytics.columns:
            expired_deals = len(df_analytics[df_analytics['days_to_maturity'] < 0])
            if expired_deals > 0:
                validation['warnings'].append(f"{expired_deals} deals expirés")


        validation['data_quality_score'] = max(0, validation['data_quality_score'])

        logger.info(f"Validation analytics: score {validation['data_quality_score']}/100")

    except Exception as e:
        validation['errors'].append(f"Erreur validation: {e}")
        validation['is_valid'] = False
        validation['data_quality_score'] = 0
        logger.error(f"Erreur validation analytics: {e}")

    return validation