# tests/conftest.py
import pytest
import pandas as pd
from datetime import datetime, date
from decimal import Decimal
import sys
import os

# Ajouter src au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Imports Treasury (avec gestion d'erreur)
try:
    from treasury.models import GenericDeal, ProductType, DepositLoan
except ImportError as e:
    print(f"Erreur import models: {e}")
    print("Vérifiez que src/treasury/models.py existe")


@pytest.fixture
def sample_deal():
    """Deal de test simple"""
    return GenericDeal(
        comment="Test Deal",
        product=ProductType.DEPOSIT,
        deal_id="TEST001",
        d_or_l=DepositLoan.DEPOSIT,
        pair_currency="USD",
        amount=10_000_000,  # 10M
        trade_date=date(2025, 8, 1),
        value_date=date(2025, 8, 3),
        maturity_date=date(2025, 12, 3),
        client_rate=0.045,
        ois_equivalent_rate=0.044,
        trader_id="TRADER_01"
    )


@pytest.fixture
def sample_pnl_config():
    """Configuration PnL de test"""
    return {
        'calculate_accrued': True,
        'calculate_mtm': True,
        'calculate_rate': True,
        'calculate_liquidity': True,
        'ois_rate_override': None
    }