__version__ = "0.1.0"
__author__ = "Treasury Team"

from .config import settings
from .models import GenericDeal, ProductType, DepositLoan, MarketData, PnLConfig
from .session import session_manager, init_session_state
from .logging_config import logger

from .pnl import compute_enhanced_pnl_vectorized, get_pnl_summary
from .market import get_ois_rate_now, MOCK_MARKET_DATA
from .analytics import convert_generic_to_analytics_format, calculate_performance_metrics
from .io.excel import build_template_generic, read_generic_deals_with_validation

__all__ = [
    'settings',
    'GenericDeal',
    'ProductType',
    'DepositLoan',
    'MarketData',
    'PnLConfig',
    'session_manager',
    'init_session_state',
    'logger',
    'compute_enhanced_pnl_vectorized',
    'get_pnl_summary',
    'get_ois_rate_now',
    'MOCK_MARKET_DATA',
    'convert_generic_to_analytics_format',
    'calculate_performance_metrics',
    'build_template_generic',
    'read_generic_deals_with_validation',
]


def get_version():
    return __version__


def health_check():
    try:
        from . import models, pnl, market, analytics, visuals, risk, io
        test_deal = GenericDeal(
            comment="Test Deal",
            product=ProductType.DEPOSIT,
            deal_id="TEST001",
            d_or_l=DepositLoan.DEPOSIT,
            pair_currency="USD",
            amount=1000000,
            trade_date="2025-01-01",
            value_date="2025-01-01",
            maturity_date="2025-12-31",
            client_rate=0.05,
            ois_equivalent_rate=0.048
        )
        df_test = compute_enhanced_pnl_vectorized([test_deal])
        return {
            'status': 'healthy',
            'version': __version__,
            'modules_loaded': True,
            'calculation_test': not df_test.empty
        }
    except Exception as e:
        return {
            'status': 'error',
            'version': __version__,
            'error': str(e)
        }


def create_sample_portfolio():
    from datetime import datetime, timedelta

    base_date = datetime.now()

    sample_deals = [
        GenericDeal(
            comment="EUR/USD FX Swap 6M",
            product=ProductType.FX_SWAP,
            deal_id="FXS001",
            d_or_l=DepositLoan.LOAN,
            pair_currency="EUR/USD",
            amount=25_000_000,
            trade_date=base_date - timedelta(days=30),
            value_date=base_date - timedelta(days=28),
            maturity_date=base_date + timedelta(days=150),
            client_rate=0.045,
            ois_equivalent_rate=0.043,
            trader_id="TRD001"
        ),
        GenericDeal(
            comment="USD IRS 3Y",
            product=ProductType.IRS,
            deal_id="IRS001",
            d_or_l=DepositLoan.DEPOSIT,
            pair_currency="USD",
            amount=100_000_000,
            trade_date=base_date - timedelta(days=60),
            value_date=base_date - timedelta(days=58),
            maturity_date=base_date + timedelta(days=1095),
            client_rate=0.042,
            ois_equivalent_rate=0.041,
            trader_id="TRD002"
        ),
        GenericDeal(
            comment="GBP Deposit 3M",
            product=ProductType.DEPOSIT,
            deal_id="DEP001",
            d_or_l=DepositLoan.DEPOSIT,
            pair_currency="GBP",
            amount=15_000_000,
            trade_date=base_date - timedelta(days=15),
            value_date=base_date - timedelta(days=13),
            maturity_date=base_date + timedelta(days=75),
            client_rate=0.038,
            ois_equivalent_rate=0.037,
            trader_id="TRD001"
        ),
        GenericDeal(
            comment="CHF Loan 1Y",
            product=ProductType.LOAN,
            deal_id="LOA001",
            d_or_l=DepositLoan.LOAN,
            pair_currency="CHF",
            amount=30_000_000,
            trade_date=base_date - timedelta(days=45),
            value_date=base_date - timedelta(days=43),
            maturity_date=base_date + timedelta(days=320),
            client_rate=0.025,
            ois_equivalent_rate=0.024,
            trader_id="TRD003"
        )
    ]

    logger.info(f"Portefeuille d'exemple créé: {len(sample_deals)} deals")
    return sample_deals


def configure_package(
    debug_mode: bool = False,
    custom_market_data: MarketData = None,
    max_file_size_mb: int = None
):
    global MOCK_MARKET_DATA

    if debug_mode:
        logger.setLevel("DEBUG")
        logger.info("Mode debug activé")

    if custom_market_data:
        from . import market
        market.MOCK_MARKET_DATA = custom_market_data
        logger.info("Données de marché personnalisées configurées")

    if max_file_size_mb:
        from . import config
        config.settings.MAX_FILE_SIZE_MB = max_file_size_mb
        logger.info(f"Taille max fichier: {max_file_size_mb}MB")


logger.info(f"Treasury Dashboard v{__version__} - Modules chargés")