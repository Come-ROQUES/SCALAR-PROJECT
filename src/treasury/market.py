\
\
\
\

from typing import Dict, Optional, Union, List
from .models import MarketData
from .logging_config import logger



MOCK_MARKET_DATA = MarketData(
    ois_curves={
        "USD": {0.25: 0.052, 0.5: 0.051, 1.0: 0.050, 2.0: 0.047, 5.0: 0.043, 10.0: 0.040},
        "EUR": {0.25: 0.036, 0.5: 0.034, 1.0: 0.033, 2.0: 0.031, 5.0: 0.028, 10.0: 0.026},
        "JPY": {0.25: 0.003, 0.5: 0.004, 1.0: 0.005, 2.0: 0.007, 5.0: 0.009, 10.0: 0.010},
        "GBP": {0.25: 0.049, 0.5: 0.048, 1.0: 0.047, 2.0: 0.044, 5.0: 0.041, 10.0: 0.038},
        "CHF": {0.25: 0.018, 0.5: 0.017, 1.0: 0.016, 2.0: 0.015, 5.0: 0.013, 10.0: 0.012},
    },
    fx_spots={
        "EUR/USD": 1.0850, "USD/JPY": 148.50, "GBP/USD": 1.2650, "USD/CHF": 0.8750,
        "AUD/USD": 0.6580, "USD/CAD": 1.3520, "EUR/GBP": 0.8580, "EUR/JPY": 161.20
    },
    float_indices={
        "EURIBOR_3M": 0.033, "SOFR_3M": 0.052, "CHF_SARON_3M": 0.016,
        "JPY_TONA_3M": 0.005, "GBP_SONIA_3M": 0.047,
    }
)


def get_ois_rate_now(currency: str,
                     maturity_years: float,
                     market_data: MarketData = MOCK_MARKET_DATA) -> float:
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
\
\
    try:
        curve = market_data.ois_curves.get(currency, {1.0: 0.05})

        if not curve:
            logger.warning(f"Courbe OIS non trouvée pour {currency}, utilisation 5% par défaut")
            return 0.05


        sorted_points = sorted(curve.items())


        if maturity_years <= sorted_points[0][0]:
            rate = sorted_points[0][1]
            logger.debug(f"OIS {currency} {maturity_years}Y: extrapolation flat = {rate:.4f}")
            return rate


        if maturity_years >= sorted_points[-1][0]:
            rate = sorted_points[-1][1]
            logger.debug(f"OIS {currency} {maturity_years}Y: extrapolation flat = {rate:.4f}")
            return rate


        for (t0, r0), (t1, r1) in zip(sorted_points[:-1], sorted_points[1:]):
            if t0 <= maturity_years <= t1:
                weight = (maturity_years - t0) / (t1 - t0)
                interpolated_rate = r0 + weight * (r1 - r0)
                logger.debug(f"OIS {currency} {maturity_years}Y: interpolation "
                           f"entre {t0}Y({r0:.4f}) et {t1}Y({r1:.4f}) = {interpolated_rate:.4f}")
                return interpolated_rate


        logger.warning(f"Erreur interpolation OIS {currency} {maturity_years}Y")
        return sorted_points[-1][1]

    except Exception as e:
        logger.error(f"Erreur calcul OIS {currency} {maturity_years}Y: {e}")
        return 0.05


def get_fx_spot(pair: str, market_data: MarketData = MOCK_MARKET_DATA) -> float:
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
        if pair in market_data.fx_spots:
            return market_data.fx_spots[pair]


        if '/' in pair:
            base, quote = pair.split('/')
            inverted_pair = f"{quote}/{base}"
            if inverted_pair in market_data.fx_spots:
                inverted_rate = market_data.fx_spots[inverted_pair]
                return 1.0 / inverted_rate if inverted_rate != 0 else 1.0

        logger.warning(f"Paire FX {pair} non trouvée, utilisation 1.0 par défaut")
        return 1.0

    except Exception as e:
        logger.error(f"Erreur récupération FX {pair}: {e}")
        return 1.0


def get_float_index_rate(index: str, market_data: MarketData = MOCK_MARKET_DATA) -> float:
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
        if index in market_data.float_indices:
            return market_data.float_indices[index]

        logger.warning(f"Indice {index} non trouvé, utilisation 3% par défaut")
        return 0.03

    except Exception as e:
        logger.error(f"Erreur récupération indice {index}: {e}")
        return 0.03


def build_curve_from_instruments(currency: str,
                                instruments: Dict[str, float],
                                curve_type: str = "OIS") -> Dict[float, float]:
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

    curve = {}

    tenor_to_years = {
        "1M": 1/12, "3M": 0.25, "6M": 0.5, "9M": 0.75,
        "1Y": 1.0, "18M": 1.5, "2Y": 2.0, "3Y": 3.0,
        "4Y": 4.0, "5Y": 5.0, "7Y": 7.0, "10Y": 10.0,
        "15Y": 15.0, "20Y": 20.0, "30Y": 30.0
    }

    try:
        for tenor, rate in instruments.items():
            if tenor in tenor_to_years:
                years = tenor_to_years[tenor]
                curve[years] = rate
            else:
                logger.warning(f"Tenor {tenor} non reconnu pour courbe {currency} {curve_type}")

        logger.info(f"Courbe {curve_type} {currency} construite: {len(curve)} points")
        return curve

    except Exception as e:
        logger.error(f"Erreur construction courbe {currency} {curve_type}: {e}")
        return {1.0: 0.05}


def refresh_market_data() -> MarketData:
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

        logger.info("Rafraîchissement données de marché (mock)")


        import random

        updated_curves = {}
        for currency, curve in MOCK_MARKET_DATA.ois_curves.items():
            updated_curve = {}
            shock = random.uniform(-0.0005, 0.0005)

            for tenor, rate in curve.items():
                updated_curve[tenor] = max(0.0, rate + shock)

            updated_curves[currency] = updated_curve


        updated_fx = {}
        for pair, rate in MOCK_MARKET_DATA.fx_spots.items():
            shock = random.uniform(-0.001, 0.001)
            updated_fx[pair] = max(0.01, rate * (1 + shock))

        return MarketData(
            ois_curves=updated_curves,
            fx_spots=updated_fx,
            float_indices=MOCK_MARKET_DATA.float_indices.copy()
        )

    except Exception as e:
        logger.error(f"Erreur rafraîchissement market data: {e}")
        return MOCK_MARKET_DATA


def validate_market_data(market_data: MarketData) -> Dict[str, any]:
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

    try:

        for currency, curve in market_data.ois_curves.items():
            if not curve:
                validation['errors'].append(f"Courbe OIS {currency} vide")
                validation['is_valid'] = False
                continue


            tenors = sorted(curve.keys())
            rates = [curve[t] for t in tenors]


            negative_rates = [r for r in rates if r < 0]
            if negative_rates:
                validation['warnings'].append(f"Taux négatifs dans courbe {currency}: {len(negative_rates)} points")


            extreme_rates = [r for r in rates if r < -0.02 or r > 0.20]
            if extreme_rates:
                validation['warnings'].append(f"Taux extrêmes dans courbe {currency}: {extreme_rates}")


        for pair, rate in market_data.fx_spots.items():
            if rate <= 0:
                validation['errors'].append(f"Taux FX {pair} négatif ou nul: {rate}")
                validation['is_valid'] = False

            if rate > 1000 or rate < 0.001:
                validation['warnings'].append(f"Taux FX {pair} extrême: {rate}")


        for index, rate in market_data.float_indices.items():
            if rate < -0.05 or rate > 0.25:
                validation['warnings'].append(f"Indice {index} extrême: {rate:.4f}")

        logger.info(f"Validation market data: {len(validation['errors'])} erreurs, "
                   f"{len(validation['warnings'])} warnings")

    except Exception as e:
        validation['errors'].append(f"Erreur validation: {e}")
        validation['is_valid'] = False
        logger.error(f"Erreur validation market data: {e}")

    return validation


def get_currency_from_pair(pair_currency: str) -> str:
    \
\
\
\
\
\
\
\
\
    if '/' in pair_currency:
        return pair_currency.split('/')[0]
    return pair_currency


def interpolate_curve(curve: Dict[float, float], target_maturity: float) -> float:
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
    if not curve:
        return 0.05

    sorted_points = sorted(curve.items())


    if target_maturity <= sorted_points[0][0]:
        return sorted_points[0][1]

    if target_maturity >= sorted_points[-1][0]:
        return sorted_points[-1][1]


    for (t0, r0), (t1, r1) in zip(sorted_points[:-1], sorted_points[1:]):
        if t0 <= target_maturity <= t1:
            weight = (target_maturity - t0) / (t1 - t0)
            return r0 + weight * (r1 - r0)

    return sorted_points[-1][1]


class MarketDataProvider:
\
\
\
\
\
\
\
\
\

    def __init__(self, name: str):
        self.name = name
        self.logger = logger

    def get_ois_curve(self, currency: str) -> Dict[float, float]:
        \
        raise NotImplementedError

    def get_fx_rates(self) -> Dict[str, float]:
        \
        raise NotImplementedError

    def get_float_indices(self) -> Dict[str, float]:
        \
        raise NotImplementedError

    def refresh(self) -> MarketData:
        \
        try:
            return MarketData(
                ois_curves={ccy: self.get_ois_curve(ccy) for ccy in ["USD", "EUR", "GBP", "JPY", "CHF"]},
                fx_spots=self.get_fx_rates(),
                float_indices=self.get_float_indices()
            )
        except Exception as e:
            self.logger.error(f"Erreur refresh {self.name}: {e}")
            return MOCK_MARKET_DATA


class MockMarketDataProvider(MarketDataProvider):
\

    def __init__(self):
        super().__init__("Mock Provider")

    def get_ois_curve(self, currency: str) -> Dict[float, float]:
        return MOCK_MARKET_DATA.ois_curves.get(currency, {1.0: 0.05})

    def get_fx_rates(self) -> Dict[str, float]:
        return MOCK_MARKET_DATA.fx_spots.copy()

    def get_float_indices(self) -> Dict[str, float]:
        return MOCK_MARKET_DATA.float_indices.copy()

    def refresh(self) -> MarketData:
        \
        return refresh_market_data()



default_provider = MockMarketDataProvider()