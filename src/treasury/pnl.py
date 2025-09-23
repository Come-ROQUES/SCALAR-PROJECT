\
\
\
\

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Union
from datetime import datetime
import time

from .models import GenericDeal, DealPnL, PnLConfig, MarketData
from .market import get_ois_rate_now, MOCK_MARKET_DATA
from .utils.dates import VAL_DATE, get_years_between, get_days_to_maturity


try:
    from .logging_config import logger, log_performance, log_calculation_summary
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    def log_performance(func_name: str, execution_time: float, deals_count: int = None):
        logger.info(f"⚡ {func_name}: {execution_time:.3f}s")
    def log_calculation_summary(module: str, deals_processed: int, errors: int, warnings: int):
        logger.info(f"{module}: {deals_processed} deals, {errors} erreurs")
from .logging_config import logger, log_performance, log_calculation_summary


def calculate_accrued_pnl(deal: GenericDeal,
                         ois_rate_now: float,
                         val_date: pd.Timestamp = VAL_DATE) -> float:
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
\
    try:

        if not hasattr(deal, 'value_date') or not deal.value_date:
            logger.warning(f"Value date manquante pour deal {deal.deal_id}")
            return 0.0

        if deal.value_date > val_date:
            return 0.0


        if not isinstance(deal.client_rate, (int, float)) or np.isnan(deal.client_rate):
            logger.warning(f"Client rate invalide pour deal {deal.deal_id}")
            return 0.0

        if not isinstance(deal.ois_equivalent_rate, (int, float)) or np.isnan(deal.ois_equivalent_rate):
            logger.warning(f"OIS equivalent rate invalide pour deal {deal.deal_id}")
            return 0.0


        years_accrued = get_years_between(deal.value_date, val_date)
        if years_accrued <= 0:
            return 0.0


        rate_diff = deal.client_rate - deal.ois_equivalent_rate


        sign = 1.0 if deal.d_or_l == "L" else -1.0


        accrued_pnl = sign * rate_diff * deal.amount * years_accrued


        if not isinstance(accrued_pnl, (int, float)) or np.isnan(accrued_pnl):
            logger.warning(f"Accrued PnL invalide pour deal {deal.deal_id}")
            return 0.0

        logger.debug(f"Accrued {deal.deal_id}: {rate_diff:.4f} × {deal.amount:,.0f} "
                    f"× {years_accrued:.3f} = {accrued_pnl:,.0f}")

        return accrued_pnl

    except Exception as e:
        logger.error(f"Erreur calcul accrued PnL pour deal {getattr(deal, 'deal_id', 'UNKNOWN')}: {e}")
        return 0.0


def calculate_mtm_pnl(deal: GenericDeal,
                      ois_rate_now: float,
                      val_date: pd.Timestamp = VAL_DATE) -> float:
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
\
    try:
        if deal.maturity_date <= val_date:
            return 0.0


        if not isinstance(ois_rate_now, (int, float)) or np.isnan(ois_rate_now):
            logger.warning(f"OIS rate now invalide pour deal {deal.deal_id}")
            return 0.0

        if not isinstance(deal.ois_equivalent_rate, (int, float)) or np.isnan(deal.ois_equivalent_rate):
            logger.warning(f"OIS equivalent rate invalide pour deal {deal.deal_id}")
            return 0.0


        time_to_maturity = get_years_between(val_date, deal.maturity_date)
        if time_to_maturity <= 0:
            return 0.0


        duration_approx = time_to_maturity * 0.8


        rate_change = ois_rate_now - deal.ois_equivalent_rate


        sign = 1.0 if deal.d_or_l == "L" else -1.0


        mtm_pnl = -sign * rate_change * deal.amount * duration_approx


        if not isinstance(mtm_pnl, (int, float)) or np.isnan(mtm_pnl):
            logger.warning(f"MTM PnL invalide pour deal {deal.deal_id}")
            return 0.0

        logger.debug(f"MTM {deal.deal_id}: -{sign} × {rate_change:.4f} × {deal.amount:,.0f} "
                    f"× {duration_approx:.3f} = {mtm_pnl:,.0f}")

        return mtm_pnl

    except Exception as e:
        logger.error(f"Erreur calcul MTM PnL pour deal {getattr(deal, 'deal_id', 'UNKNOWN')}: {e}")
        return 0.0


def calculate_rate_pnl(deal: GenericDeal,
                       ois_rate_now: float,
                       val_date: pd.Timestamp = VAL_DATE) -> float:
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
\
    try:
        if deal.maturity_date <= val_date:
            return 0.0


        if not isinstance(ois_rate_now, (int, float)) or np.isnan(ois_rate_now):
            logger.warning(f"OIS rate now invalide pour deal {deal.deal_id}")
            return 0.0

        if not isinstance(deal.ois_equivalent_rate, (int, float)) or np.isnan(deal.ois_equivalent_rate):
            logger.warning(f"OIS equivalent rate invalide pour deal {deal.deal_id}")
            return 0.0


        curve_shift = ois_rate_now - deal.ois_equivalent_rate
        time_to_maturity = get_years_between(val_date, deal.maturity_date)

        if time_to_maturity <= 0:
            return 0.0


        rate_sensitivity = 0.5
        sign = 1.0 if deal.d_or_l == "L" else -1.0


        rate_pnl = sign * curve_shift * deal.amount * time_to_maturity * rate_sensitivity


        if not isinstance(rate_pnl, (int, float)) or np.isnan(rate_pnl):
            logger.warning(f"Rate PnL invalide pour deal {deal.deal_id}")
            return 0.0

        logger.debug(f"Rate {deal.deal_id}: {sign} × {curve_shift:.4f} × {deal.amount:,.0f} "
                    f"× {time_to_maturity:.3f} × {rate_sensitivity} = {rate_pnl:,.0f}")

        return rate_pnl

    except Exception as e:
        logger.error(f"Erreur calcul rate PnL pour deal {getattr(deal, 'deal_id', 'UNKNOWN')}: {e}")
        return 0.0


def calculate_liquidity_pnl(deal: GenericDeal,
                           ois_rate_now: float,
                           val_date: pd.Timestamp = VAL_DATE) -> float:
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
\
    try:
        if deal.maturity_date <= val_date:
            return 0.0


        if not isinstance(deal.amount, (int, float)) or deal.amount <= 0:
            logger.warning(f"Montant invalide pour deal {deal.deal_id}")
            return 0.0


        size_factor = min(deal.amount / 100_000_000, 1.0)
        time_to_maturity = get_years_between(val_date, deal.maturity_date)

        if time_to_maturity <= 0:
            return 0.0

        maturity_factor = min(time_to_maturity, 1.0)


        liquidity_spread = size_factor * maturity_factor * 0.001


        sign = 1.0 if deal.d_or_l == "L" else -1.0
        liq_pnl = -sign * liquidity_spread * deal.amount


        if not isinstance(liq_pnl, (int, float)) or np.isnan(liq_pnl):
            logger.warning(f"Liquidity PnL invalide pour deal {deal.deal_id}")
            return 0.0

        logger.debug(f"Liquidity {deal.deal_id}: -{sign} × {liquidity_spread:.4f} "
                    f"× {deal.amount:,.0f} = {liq_pnl:,.0f}")

        return liq_pnl

    except Exception as e:
        logger.error(f"Erreur calcul liquidity PnL pour deal {getattr(deal, 'deal_id', 'UNKNOWN')}: {e}")
        return 0.0


def calculate_deal_pnl(deal: GenericDeal,
                      config: PnLConfig,
                      market_data: MarketData = MOCK_MARKET_DATA,
                      val_date: pd.Timestamp = VAL_DATE) -> DealPnL:
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
\
\
    try:

        if not hasattr(deal, 'deal_id') or not deal.deal_id:
            raise ValueError("Deal ID manquant")

        if not hasattr(deal, 'pair_currency') or not deal.pair_currency:
            raise ValueError("Devise manquante")

        if not hasattr(deal, 'amount') or deal.amount <= 0:
            raise ValueError("Montant invalide")

        if not hasattr(deal, 'maturity_date') or not deal.maturity_date:
            raise ValueError("Date de maturité manquante")


        if '/' in deal.pair_currency:
            base_ccy = deal.pair_currency.split('/')[0]
        else:
            base_ccy = deal.pair_currency


        if deal.maturity_date <= val_date:
            logger.debug(f"Deal {deal.deal_id} expiré, PnL = 0")
            return DealPnL(
                deal_id=deal.deal_id,
                accrued_pnl=0.0,
                mtm_pnl=0.0,
                rate_pnl=0.0,
                liquidity_pnl=0.0,
                total_pnl=0.0,
                ois_rate_used=0.0,
                calculation_timestamp=datetime.now()
            )


        time_to_maturity = get_years_between(val_date, deal.maturity_date)


        try:
            if config.ois_rate_override is not None:
                ois_rate_now = float(config.ois_rate_override)
            else:
                ois_rate_now = get_ois_rate_now(base_ccy, time_to_maturity, market_data)


            if not isinstance(ois_rate_now, (int, float)) or np.isnan(ois_rate_now):
                logger.warning(f"Taux OIS invalide pour {deal.deal_id}, utilisation de 0.02")
                ois_rate_now = 0.02

        except Exception as rate_error:
            logger.warning(f"Erreur récupération taux OIS pour {deal.deal_id}: {rate_error}, utilisation de 0.02")
            ois_rate_now = 0.02


        accrued_pnl = 0.0
        if config.calculate_accrued:
            try:
                accrued_pnl = calculate_accrued_pnl(deal, ois_rate_now, val_date)
                if not isinstance(accrued_pnl, (int, float)) or np.isnan(accrued_pnl):
                    accrued_pnl = 0.0
            except Exception as e:
                logger.warning(f"Erreur calcul accrued PnL pour {deal.deal_id}: {e}")
                accrued_pnl = 0.0

        mtm_pnl = 0.0
        if config.calculate_mtm:
            try:
                mtm_pnl = calculate_mtm_pnl(deal, ois_rate_now, val_date)
                if not isinstance(mtm_pnl, (int, float)) or np.isnan(mtm_pnl):
                    mtm_pnl = 0.0
            except Exception as e:
                logger.warning(f"Erreur calcul MTM PnL pour {deal.deal_id}: {e}")
                mtm_pnl = 0.0

        rate_pnl = 0.0
        if config.calculate_rate:
            try:
                rate_pnl = calculate_rate_pnl(deal, ois_rate_now, val_date)
                if not isinstance(rate_pnl, (int, float)) or np.isnan(rate_pnl):
                    rate_pnl = 0.0
            except Exception as e:
                logger.warning(f"Erreur calcul rate PnL pour {deal.deal_id}: {e}")
                rate_pnl = 0.0

        liquidity_pnl = 0.0
        if config.calculate_liquidity:
            try:
                liquidity_pnl = calculate_liquidity_pnl(deal, ois_rate_now, val_date)
                if not isinstance(liquidity_pnl, (int, float)) or np.isnan(liquidity_pnl):
                    liquidity_pnl = 0.0
            except Exception as e:
                logger.warning(f"Erreur calcul liquidity PnL pour {deal.deal_id}: {e}")
                liquidity_pnl = 0.0


        total_pnl = accrued_pnl + mtm_pnl + rate_pnl + liquidity_pnl


        if not isinstance(total_pnl, (int, float)) or np.isnan(total_pnl):
            logger.warning(f"Total PnL invalide pour {deal.deal_id}, remise à zéro")
            total_pnl = 0.0

        return DealPnL(
            deal_id=deal.deal_id,
            accrued_pnl=accrued_pnl,
            mtm_pnl=mtm_pnl,
            rate_pnl=rate_pnl,
            liquidity_pnl=liquidity_pnl,
            total_pnl=total_pnl,
            ois_rate_used=ois_rate_now,
            calculation_timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Erreur critique calcul PnL deal {getattr(deal, 'deal_id', 'UNKNOWN')}: {e}")

        return DealPnL(
            deal_id=getattr(deal, 'deal_id', 'ERROR'),
            accrued_pnl=0.0,
            mtm_pnl=0.0,
            rate_pnl=0.0,
            liquidity_pnl=0.0,
            total_pnl=0.0,
            ois_rate_used=0.0,
            calculation_timestamp=datetime.now()
        )


def compute_enhanced_pnl_vectorized(deals: List[GenericDeal],
                                   config: PnLConfig,
                                   market_data: MarketData = MOCK_MARKET_DATA) -> pd.DataFrame:
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
\
    start_time = time.time()

    if not deals:
        logger.warning("Aucun deal fourni pour calcul PnL")
        return pd.DataFrame()

    logger.info(f"Début calcul PnL Enhanced pour {len(deals)} deals avec config: {config}")

    results = []
    errors = 0
    warnings = 0

    for deal in deals:
        try:
            deal_pnl = calculate_deal_pnl(deal, config, market_data)


            if np.isnan(deal_pnl.total_pnl):
                errors += 1


            result_row = {
                'deal_id': deal.deal_id,
                'comment': deal.comment,
                'product': deal.product,
                'd_or_l': deal.d_or_l,
                'pair_currency': deal.pair_currency,
                'amount': deal.amount,
                'trade_date': deal.trade_date,
                'value_date': deal.value_date,
                'maturity_date': deal.maturity_date,
                'client_rate': deal.client_rate,
                'ois_equivalent_rate': deal.ois_equivalent_rate,
                'ois_rate_now': deal_pnl.ois_rate_used,
                'time_to_maturity_years': get_years_between(VAL_DATE, deal.maturity_date),
                'accrued_pnl': deal_pnl.accrued_pnl,
                'mtm_pnl': deal_pnl.mtm_pnl,
                'rate_pnl': deal_pnl.rate_pnl,
                'liquidity_pnl': deal_pnl.liquidity_pnl,
                'total_pnl': deal_pnl.total_pnl,
                'trader_id': deal.trader_id,
                'base_currency': deal.pair_currency.split('/')[0] if '/' in deal.pair_currency else deal.pair_currency,
                'calculation_timestamp': deal_pnl.calculation_timestamp
            }

            results.append(result_row)

        except Exception as e:
            errors += 1
            logger.error(f"Erreur calcul deal {deal.deal_id}: {e}")


            error_row = {
                'deal_id': getattr(deal, 'deal_id', 'ERROR'),
                'comment': getattr(deal, 'comment', ''),
                'product': getattr(deal, 'product', ''),
                'total_pnl': 0.0,
                'accrued_pnl': 0.0,
                'mtm_pnl': 0.0,
                'rate_pnl': 0.0,
                'liquidity_pnl': 0.0,
                'error': str(e)
            }
            results.append(error_row)


    result_df = pd.DataFrame(results)


    execution_time = time.time() - start_time
    log_performance("compute_enhanced_pnl_vectorized", execution_time, len(deals))
    log_calculation_summary("PnL", len(deals), errors, warnings)

    logger.info(f"Calcul PnL terminé: {len(result_df)} résultats, "
               f"{errors} erreurs en {execution_time:.2f}s")

    return result_df


def get_pnl_summary(df_pnl: pd.DataFrame) -> Dict[str, float]:
    \
\
\
\
\
\
\
\
\
    if df_pnl.empty:
        return {}

    summary = {}

    for pnl_type in ['accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl', 'total_pnl']:
        if pnl_type in df_pnl.columns:
            total = df_pnl[pnl_type].sum()
            summary[f'{pnl_type}_m'] = total / 1_000_000


    summary['deal_count'] = len(df_pnl)
    summary['avg_pnl_per_deal'] = summary.get('total_pnl_m', 0) / len(df_pnl) if len(df_pnl) > 0 else 0

    if 'amount' in df_pnl.columns:
        total_notional = df_pnl['amount'].sum()
        summary['total_notional_m'] = total_notional / 1_000_000
        summary['pnl_bps'] = (summary.get('total_pnl_m', 0) * 1_000_000 / total_notional * 10_000) if total_notional > 0 else 0

    return summary


def validate_pnl_results(df_pnl: pd.DataFrame) -> Dict[str, any]:
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
        'warnings': []
    }

    if df_pnl.empty:
        validation['errors'].append("DataFrame PnL vide")
        validation['is_valid'] = False
        return validation


    nan_counts = df_pnl.isna().sum()
    for col, nan_count in nan_counts.items():
        if nan_count > 0 and col.endswith('_pnl'):
            validation['warnings'].append(f"{nan_count} valeurs NaN dans {col}")


    for pnl_col in ['accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl', 'total_pnl']:
        if pnl_col in df_pnl.columns:
            values = df_pnl[pnl_col].dropna()
            if len(values) > 0:
                q99 = values.quantile(0.99)
                q01 = values.quantile(0.01)


                if abs(q99) > 100_000_000:
                    validation['warnings'].append(f"{pnl_col}: valeur extrême détectée ({q99:,.0f})")
                if abs(q01) > 100_000_000:
                    validation['warnings'].append(f"{pnl_col}: valeur extrême détectée ({q01:,.0f})")


    if all(col in df_pnl.columns for col in ['accrued_pnl', 'mtm_pnl', 'rate_pnl', 'liquidity_pnl', 'total_pnl']):
        calculated_total = (df_pnl['accrued_pnl'] + df_pnl['mtm_pnl'] +
                           df_pnl['rate_pnl'] + df_pnl['liquidity_pnl'])

        diff = abs(calculated_total - df_pnl['total_pnl']).max()
        if diff > 0.01:
            validation['warnings'].append(f"Incohérence total PnL (max diff: {diff:.2f})")

    return validation