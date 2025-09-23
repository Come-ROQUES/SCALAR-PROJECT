
\
\
\
\

import streamlit as st
import pandas as pd
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple
from functools import wraps
from datetime import datetime, date, timedelta
from io import StringIO


class CacheManager:
\

    def __init__(self):
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_time_saved': 0.0
        }

    def get_cache_info(self) -> Dict[str, Any]:
        \
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'time_saved_seconds': self.cache_stats['total_time_saved'],
            **self.cache_stats
        }

    def clear_cache(self, cache_type: str = 'all'):
        \
        if cache_type == 'all':
            st.cache_data.clear()
            if hasattr(st, 'cache_resource'):
                st.cache_resource.clear()


        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_time_saved': 0.0
        }



cache_manager = CacheManager()


def serialize_deals_for_cache(deals: List) -> str:
    \
    deals_data = []
    for deal in deals:
        deal_dict = {
            'comment': deal.comment,
            'product': deal.product.value if hasattr(deal.product, 'value') else str(deal.product),
            'deal_id': deal.deal_id,
            'd_or_l': deal.d_or_l.value if hasattr(deal.d_or_l, 'value') else str(deal.d_or_l),
            'pair_currency': deal.pair_currency,
            'amount': float(deal.amount),

            'trade_date': deal.trade_date.strftime('%Y-%m-%d') if hasattr(deal.trade_date, 'strftime') else str(deal.trade_date),
            'value_date': deal.value_date.strftime('%Y-%m-%d') if hasattr(deal.value_date, 'strftime') else str(deal.value_date),
            'maturity_date': deal.maturity_date.strftime('%Y-%m-%d') if hasattr(deal.maturity_date, 'strftime') else str(deal.maturity_date),
            'client_rate': float(deal.client_rate),
            'ois_equivalent_rate': float(deal.ois_equivalent_rate),
            'trader_id': deal.trader_id
        }
        deals_data.append(deal_dict)

    return json.dumps(deals_data, sort_keys=True)


def _parse_date_flexible(date_str: str) -> date:
    \
    if isinstance(date_str, date):
        return date_str


    date_str = str(date_str).strip()


    formats_to_try = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
    ]

    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.date()
        except ValueError:
            continue


    try:

        if 'T' in date_str:
            date_str = date_str.split('T')[0]
        return date.fromisoformat(date_str)
    except ValueError:

        try:
            parts = date_str.split('-')
            if len(parts) >= 3:
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                return date(year, month, day)
        except:
            pass

    raise ValueError(f"Cannot parse date: {date_str}")


@st.cache_data(ttl=3600, show_spinner=True)
def compute_enhanced_pnl_vectorized_cached(deals_json: str, config_json: str) -> str:
\
\
\
\

    from treasury.pnl import compute_enhanced_pnl_vectorized
    from treasury.models import GenericDeal, ProductType, DepositLoan


    deals_data = json.loads(deals_json)
    config = json.loads(config_json)


    deals = []
    for deal_data in deals_data:
        try:

            if isinstance(deal_data['product'], str):
                product = ProductType(deal_data['product'])
            else:
                product = deal_data['product']

            if isinstance(deal_data['d_or_l'], str):
                d_or_l = DepositLoan(deal_data['d_or_l'])
            else:
                d_or_l = deal_data['d_or_l']


            trade_date = _parse_date_flexible(deal_data['trade_date'])
            value_date = _parse_date_flexible(deal_data['value_date'])
            maturity_date = _parse_date_flexible(deal_data['maturity_date'])

            deal = GenericDeal(
                comment=deal_data['comment'],
                product=product,
                deal_id=deal_data['deal_id'],
                d_or_l=d_or_l,
                pair_currency=deal_data['pair_currency'],
                amount=deal_data['amount'],
                trade_date=trade_date,
                value_date=value_date,
                maturity_date=maturity_date,
                client_rate=deal_data['client_rate'],
                ois_equivalent_rate=deal_data['ois_equivalent_rate'],
                trader_id=deal_data.get('trader_id')
            )
            deals.append(deal)
        except Exception as e:
            print(f"Erreur reconstruction deal {deal_data.get('deal_id', 'UNKNOWN')}: {e}")
            continue


    if not deals:
        print("WARNING: Aucun deal valide après reconstruction depuis cache")
        return pd.DataFrame().to_json(orient='records')


    df_pnl = compute_enhanced_pnl_vectorized(deals, config)


    return df_pnl.to_json(orient='records', date_format='iso')


def compute_pnl_with_cache(deals: List, config: Dict[str, Any]) -> pd.DataFrame:
    \
\
\
\
    start_time = time.time()


    if not deals:
        print("WARNING: Aucun deal fourni pour calcul PnL")
        return pd.DataFrame()

    try:

        deals_json = serialize_deals_for_cache(deals)
        config_json = json.dumps(config, sort_keys=True)


        result_json = compute_enhanced_pnl_vectorized_cached(deals_json, config_json)


        if result_json.strip() == '[]' or not result_json.strip():

            raise ValueError("Résultat cache vide")

        df_pnl = pd.read_json(StringIO(result_json), orient='records')


        date_columns = ['trade_date', 'value_date', 'maturity_date']
        for col in date_columns:
            if col in df_pnl.columns:
                df_pnl[col] = pd.to_datetime(df_pnl[col]).dt.date

        execution_time = time.time() - start_time
        cache_manager.cache_stats['hits'] += 1


        if st.session_state.get('debug_mode', False):
            st.sidebar.success(f"PnL calculé en {execution_time:.2f}s (cache: ACTIF)")

        return df_pnl

    except Exception as e:

        print(f"Cache failed, using direct calculation: {e}")
        from treasury.pnl import compute_enhanced_pnl_vectorized

        cache_manager.cache_stats['misses'] += 1
        df_pnl = compute_enhanced_pnl_vectorized(deals, config)
        execution_time = time.time() - start_time

        if st.session_state.get('debug_mode', False):
            st.sidebar.warning(f"🐌 PnL calculé en {execution_time:.2f}s (sans cache: {str(e)[:50]})")

        return df_pnl


def get_cache_status() -> Dict[str, Any]:
    \
    return {
        'streamlit_cache_stats': {
            'data_cache_entries': len([k for k in st.session_state.keys() if 'cache' in k.lower()]),
            'session_size_mb': len(str(st.session_state)) / 1024 / 1024
        },
        'custom_cache_stats': cache_manager.get_cache_info(),
        'last_updated': datetime.now().isoformat()
    }


def clear_all_caches():
\

    st.cache_data.clear()


    cache_manager.clear_cache()


    keys_to_remove = [key for key in st.session_state.keys() if key.startswith('cache_')]
    for key in keys_to_remove:
        del st.session_state[key]


def test_cache_performance():
\

    from treasury.models import GenericDeal, ProductType, DepositLoan


    test_deal = GenericDeal(
        comment="Cache Test",
        product=ProductType.DEPOSIT,
        deal_id="CACHE001",
        d_or_l=DepositLoan.DEPOSIT,
        pair_currency="USD",
        amount=10_000_000,
        trade_date=date(2025, 8, 1),
        value_date=date(2025, 8, 3),
        maturity_date=date(2025, 12, 3),
        client_rate=0.045,
        ois_equivalent_rate=0.044
    )

    deals_json = serialize_deals_for_cache([test_deal])
    config_json = json.dumps({'calculate_accrued': True, 'calculate_mtm': True})


    start_time = time.time()
    result1 = compute_enhanced_pnl_vectorized_cached(deals_json, config_json)
    time1 = time.time() - start_time


    start_time = time.time()
    result2 = compute_enhanced_pnl_vectorized_cached(deals_json, config_json)
    time2 = time.time() - start_time


    speed_improvement = time1 / time2 if time2 > 0 else float('inf')

    return {
        'first_call_time': time1,
        'cached_call_time': time2,
        'speed_improvement': speed_improvement,
        'cache_working': speed_improvement > 2,
        'results_identical': result1 == result2
    }
