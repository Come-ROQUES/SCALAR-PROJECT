\
\
\
\

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
import json

from ..logging_config import logger


class AlertLevel(str, Enum):
    \
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    FATAL = "fatal"


class AlertType(str, Enum):
    \
    VAR_BREACH = "var_breach"
    CONCENTRATION = "concentration"
    MTM_SHOCK = "mtm_shock"
    LIQUIDITY = "liquidity"
    OPERATIONAL = "operational"
    DATA_QUALITY = "data_quality"


@dataclass
class Alert:
    \
    alert_id: str
    alert_type: AlertType
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    deal_ids: List[str] = field(default_factory=list)
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    is_active: bool = True
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        \
        return {
            'alert_id': self.alert_id,
            'alert_type': self.alert_type.value,
            'level': self.level.value,
            'title': self.title,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'deal_ids': self.deal_ids,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'is_active': self.is_active,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }


class AlertManager:
\

    def __init__(self):
        self.active_alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        self.notification_handlers: List[Callable] = []


        self.thresholds = {
            'var_95_limit': 5_000_000,
            'var_99_limit': 10_000_000,
            'concentration_limit': 0.30,
            'mtm_shock_limit': 2_000_000,
            'data_quality_min': 0.95
        }


        self._load_from_session()

    def add_notification_handler(self, handler: Callable[[Alert], None]):
        \
        self.notification_handlers.append(handler)

    def create_alert(self,
                    alert_type: AlertType,
                    level: AlertLevel,
                    title: str,
                    message: str,
                    **kwargs) -> Alert:
\

        alert_id = f"{alert_type.value}_{int(datetime.now().timestamp())}"

        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            level=level,
            title=title,
            message=message,
            **kwargs
        )


        recent_similar = [
            a for a in self.active_alerts
            if (a.alert_type == alert_type and
                a.title == title and
                (datetime.now() - a.timestamp) < timedelta(minutes=5))
        ]

        if not recent_similar:
            self.active_alerts.append(alert)
            self._notify_handlers(alert)
            self._save_to_session()
            logger.warning(f"ALERTE {level.value.upper()}: {title}")

        return alert

    def acknowledge_alert(self, alert_id: str, user: str = "system"):
        \
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged_by = user
                alert.acknowledged_at = datetime.now()
                alert.is_active = False


                self.alert_history.append(alert)
                self.active_alerts.remove(alert)
                self._save_to_session()
                break

    def check_var_limits(self, var_95: float, var_99: float):
        \
        if abs(var_95) > self.thresholds['var_95_limit']:
            self.create_alert(
                AlertType.VAR_BREACH,
                AlertLevel.WARNING if abs(var_95) < self.thresholds['var_95_limit'] * 1.2 else AlertLevel.CRITICAL,
                "Dépassement VaR 95%",
                f"VaR 95% = ${var_95/1e6:.1f}M (limite: ${self.thresholds['var_95_limit']/1e6:.1f}M)",
                current_value=var_95,
                threshold_value=self.thresholds['var_95_limit']
            )

        if abs(var_99) > self.thresholds['var_99_limit']:
            self.create_alert(
                AlertType.VAR_BREACH,
                AlertLevel.CRITICAL,
                "Dépassement VaR 99%",
                f"VaR 99% = ${var_99/1e6:.1f}M (limite: ${self.thresholds['var_99_limit']/1e6:.1f}M)",
                current_value=var_99,
                threshold_value=self.thresholds['var_99_limit']
            )

    def check_concentration_risk(self, df_pnl: pd.DataFrame):
        \
        if df_pnl.empty:
            return


        if 'base_currency' in df_pnl.columns and 'amount' in df_pnl.columns:
            total_notional = df_pnl['amount'].sum()
            currency_exposure = df_pnl.groupby('base_currency')['amount'].sum()

            for currency, exposure in currency_exposure.items():
                concentration = exposure / total_notional
                if concentration > self.thresholds['concentration_limit']:
                    self.create_alert(
                        AlertType.CONCENTRATION,
                        AlertLevel.WARNING,
                        f"Concentration {currency} élevée",
                        f"Exposition {currency}: {concentration:.1%} (limite: {self.thresholds['concentration_limit']:.1%})",
                        current_value=concentration,
                        threshold_value=self.thresholds['concentration_limit']
                    )

    def check_data_quality(self, df_pnl: pd.DataFrame):
        \
        if df_pnl.empty:
            self.create_alert(
                AlertType.DATA_QUALITY,
                AlertLevel.CRITICAL,
                "Aucune donnée PnL",
                "Dataset PnL vide - calculs impossibles"
            )
            return


        total_rows = len(df_pnl)
        valid_rows = len(df_pnl.dropna(subset=['total_pnl']))
        quality_ratio = valid_rows / total_rows if total_rows > 0 else 0

        if quality_ratio < self.thresholds['data_quality_min']:
            self.create_alert(
                AlertType.DATA_QUALITY,
                AlertLevel.WARNING,
                "Qualité données dégradée",
                f"Seulement {quality_ratio:.1%} des données sont valides (minimum: {self.thresholds['data_quality_min']:.1%})",
                current_value=quality_ratio,
                threshold_value=self.thresholds['data_quality_min']
            )

    def check_mtm_shocks(self, df_pnl: pd.DataFrame):
        \
        if df_pnl.empty or 'mtm_pnl' not in df_pnl.columns:
            return

        total_mtm = df_pnl['mtm_pnl'].sum()
        if abs(total_mtm) > self.thresholds['mtm_shock_limit']:
            level = AlertLevel.WARNING if abs(total_mtm) < self.thresholds['mtm_shock_limit'] * 2 else AlertLevel.CRITICAL

            self.create_alert(
                AlertType.MTM_SHOCK,
                level,
                "Choc MTM détecté",
                f"Impact MTM total: ${total_mtm/1e6:.1f}M (seuil: ${self.thresholds['mtm_shock_limit']/1e6:.1f}M)",
                current_value=total_mtm,
                threshold_value=self.thresholds['mtm_shock_limit']
            )

    def run_full_monitoring(self, df_pnl: pd.DataFrame, var_results: Dict = None):
        \
        logger.info("Lancement monitoring complet...")


        self.check_data_quality(df_pnl)


        self.check_concentration_risk(df_pnl)


        self.check_mtm_shocks(df_pnl)


        if var_results:
            var_95 = var_results.get('var_95', 0)
            var_99 = var_results.get('var_99', 0)
            self.check_var_limits(var_95, var_99)

        logger.info(f"Monitoring terminé - {len(self.active_alerts)} alertes actives")

    def get_dashboard_summary(self) -> Dict:
        \
        active_by_level = {}
        for level in AlertLevel:
            active_by_level[level.value] = len([
                a for a in self.active_alerts if a.level == level
            ])

        return {
            'total_active': len(self.active_alerts),
            'by_level': active_by_level,
            'last_check': datetime.now(),
            'critical_count': active_by_level.get('critical', 0),
            'warning_count': active_by_level.get('warning', 0)
        }

    def _notify_handlers(self, alert: Alert):
        \
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Erreur notification handler: {e}")

    def _save_to_session(self):
        \
        if 'st' in globals():
            st.session_state['alert_manager_data'] = {
                'active_alerts': [a.to_dict() for a in self.active_alerts],
                'alert_history': [a.to_dict() for a in self.alert_history[-50:]],
                'thresholds': self.thresholds
            }

    def _load_from_session(self):
        \
        if 'st' in globals() and 'alert_manager_data' in st.session_state:
            data = st.session_state['alert_manager_data']


            if 'thresholds' in data:
                self.thresholds.update(data['thresholds'])



alert_manager = AlertManager()



def streamlit_notification_handler(alert: Alert):
    \
    if 'st' in globals():
        icon_map = {
            AlertLevel.INFO: "INFO",
            AlertLevel.WARNING: "WARNING",
            AlertLevel.CRITICAL: "CRITICAL",
            AlertLevel.FATAL: "FATAL"
        }

        icon = icon_map.get(alert.level, "ALERT")

        if alert.level in [AlertLevel.CRITICAL, AlertLevel.FATAL]:
            st.error(f"{icon} **{alert.title}**: {alert.message}")
        elif alert.level == AlertLevel.WARNING:
            st.warning(f"{icon} **{alert.title}**: {alert.message}")
        else:
            st.info(f"{icon} **{alert.title}**: {alert.message}")


def email_notification_handler(alert: Alert):
\

    if alert.level in [AlertLevel.CRITICAL, AlertLevel.FATAL]:
        logger.info(f"📧 Email notification needed for: {alert.title}")



alert_manager.add_notification_handler(streamlit_notification_handler)
