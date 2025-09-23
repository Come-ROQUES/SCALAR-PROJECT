\
\
\
\

from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime


class ProductType(str, Enum):
    \
    FX_SWAP = "FX_SWAP"
    IRS = "IRS"
    DEPOSIT = "DEPOSIT"
    LOAN = "LOAN"


class DepositLoan(str, Enum):
    \
    DEPOSIT = "D"
    LOAN = "L"


class GenericDeal(BaseModel):
    \
\
\
\
    comment: str = Field(..., min_length=1, description="Nom/description du deal")
    product: ProductType = Field(..., description="Type de produit")
    deal_id: str = Field(..., min_length=1, description="ID unique du deal")
    d_or_l: DepositLoan = Field(..., description="Deposit (D) ou Loan (L)")
    pair_currency: str = Field(..., min_length=3, description="Paire devises ou devise unique")
    amount: float = Field(..., gt=0, description="Montant")
    trade_date: datetime = Field(..., description="Date de trade")
    value_date: datetime = Field(..., description="Date de valeur")
    maturity_date: datetime = Field(..., description="Date de maturité")
    client_rate: float = Field(..., ge=0, le=1, description="Taux client (décimal)")
    ois_equivalent_rate: float = Field(..., ge=0, le=1, description="Taux OIS équivalent (décimal)")
    trader_id: Optional[str] = Field(None, description="ID du trader")

    @validator('maturity_date')
    def maturity_after_value(cls, v, values):
        \
        if 'value_date' in values and v <= values['value_date']:
            raise ValueError("maturity_date doit être postérieure à value_date")
        return v

    @validator('value_date')
    def value_after_trade(cls, v, values):
        \
        if 'trade_date' in values and v < values['trade_date']:
            raise ValueError("value_date doit être >= trade_date")
        return v

    class Config:
        use_enum_values = True


@dataclass
class MarketData:
    \
\
\
\
    ois_curves: Dict[str, Dict[float, float]]
    fx_spots: Dict[str, float]
    float_indices: Dict[str, float]


@dataclass
class DealPnL:
    \
    deal_id: str
    accrued_pnl: float
    mtm_pnl: float
    rate_pnl: float
    liquidity_pnl: float
    total_pnl: float
    ois_rate_used: float
    calculation_timestamp: datetime

    @property
    def total_pnl_m(self) -> float:
        \
        return self.total_pnl / 1_000_000


@dataclass
class RiskMetrics:
    \
    var_95: float
    var_99: float
    expected_shortfall: float
    total_notional: float
    currency_exposures: Dict[str, float]
    tenor_concentrations: Dict[str, float]

    def var_95_m(self) -> float:
        \
        return self.var_95 / 1_000_000

    def var_99_m(self) -> float:
        \
        return self.var_99 / 1_000_000


@dataclass
class PnLConfig:
    \
    calculate_accrued: bool = True
    calculate_mtm: bool = True
    calculate_rate: bool = True
    calculate_liquidity: bool = True
    ois_rate_override: Optional[float] = None

    def __post_init__(self):
        \
        if self.ois_rate_override is not None:
            if not (0 <= self.ois_rate_override <= 1):
                raise ValueError("ois_rate_override doit être entre 0 et 1")


@dataclass
class RiskLimits:
    \
    max_notional_per_pair: float = 500_000_000
    max_tenor_concentration: float = 0.40
    var_limit: float = 1_000_000
    max_deals_urgent: int = 5

    def validate_portfolio(self, portfolio_stats: Dict) -> Dict[str, bool]:
        \
        violations = {}


        if 'max_concentration' in portfolio_stats:
            violations['concentration'] = portfolio_stats['max_concentration'] > self.max_tenor_concentration

        if 'var_estimate' in portfolio_stats:
            violations['var'] = portfolio_stats['var_estimate'] > self.var_limit

        return violations