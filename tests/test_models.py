
import pytest
from datetime import date

def test_sample_deal_creation(sample_deal):
    \
    assert sample_deal.deal_id == "TEST001"
    assert sample_deal.amount == 10_000_000
    assert sample_deal.trader_id == "TRADER_01"


def test_imports_treasury():
    \
    try:
        from treasury.models import GenericDeal, ProductType, DepositLoan
        from treasury.config import settings
        print("✅ Imports Treasury OK")
        assert True
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        assert False, f"Import Treasury échoué: {e}"


def test_deal_basic_properties(sample_deal):
\

    assert sample_deal.value_date >= sample_deal.trade_date
    assert sample_deal.maturity_date > sample_deal.value_date


    assert sample_deal.amount > 0