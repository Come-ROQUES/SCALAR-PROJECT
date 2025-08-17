"""
Utilitaires pour la gestion des dates
Extrait du monolithe app.py
"""

import pandas as pd
from typing import Union
from datetime import datetime
from ..logging_config import logger

# Date de valorisation globale - utilisée dans tous les calculs
VAL_DATE = pd.Timestamp.utcnow().tz_localize(None).normalize()


def to_naive_ts(x: Union[str, pd.Timestamp, datetime]) -> pd.Timestamp:
    """
    Convertit en Timestamp tz-naive avec gestion d'erreurs robuste
    
    Args:
        x: Date sous forme string, Timestamp ou datetime
        
    Returns:
        pd.Timestamp: Timestamp timezone-naive
    """
    try:
        t = pd.to_datetime(x, errors="coerce")
        if isinstance(t, pd.Timestamp) and t.tz is not None:
            return t.tz_localize(None)
        return t
    except Exception as e:
        logger.warning(f"Erreur conversion date {x}: {e}")
        return pd.NaT


def to_naive_series(s: pd.Series) -> pd.Series:
    """
    Convertit une série en tz-naive avec gestion d'erreurs
    
    Args:
        s: Série pandas contenant des dates
        
    Returns:
        pd.Series: Série avec dates timezone-naive
    """
    try:
        s = pd.to_datetime(s, errors="coerce")
        if hasattr(s.dt, 'tz') and s.dt.tz is not None:
            s = s.dt.tz_localize(None)
        return s
    except Exception as e:
        logger.warning(f"Erreur conversion série dates: {e}")
        return s


def get_years_between(start_date: pd.Timestamp, end_date: pd.Timestamp) -> float:
    """
    Calcule le nombre d'années entre deux dates (convention 365j/an)
    
    Args:
        start_date: Date de début
        end_date: Date de fin
        
    Returns:
        float: Nombre d'années (peut être fractionnaire)
    """
    if pd.isna(start_date) or pd.isna(end_date):
        return 0.0
    
    days_diff = (end_date - start_date).days
    return max(0.0, days_diff / 365.0)


def get_days_to_maturity(maturity_date: pd.Timestamp, 
                        val_date: pd.Timestamp = None) -> int:
    """
    Calcule le nombre de jours jusqu'à l'échéance
    
    Args:
        maturity_date: Date d'échéance
        val_date: Date de valorisation (défaut: VAL_DATE global)
        
    Returns:
        int: Nombre de jours (peut être négatif si échu)
    """
    if val_date is None:
        val_date = VAL_DATE
        
    if pd.isna(maturity_date):
        return 0
    
    return (maturity_date - val_date).days


def classify_tenor(time_to_maturity_years: float) -> str:
    """
    Classifie la maturité en buckets standardisés
    
    Args:
        time_to_maturity_years: Durée jusqu'à maturité en années
        
    Returns:
        str: Bucket de tenor ("1M", "3M", "6M", "12M", "2Y", etc.)
    """
    if pd.isna(time_to_maturity_years) or time_to_maturity_years <= 0:
        return "Expired"
    
    years = time_to_maturity_years
    
    if years <= 1/12:  # <= 1 mois
        return "1M"
    elif years <= 0.25:  # <= 3 mois
        return "3M"
    elif years <= 0.5:   # <= 6 mois
        return "6M"
    elif years <= 1:     # <= 12 mois
        return "12M"
    elif years <= 2:     # <= 2 ans
        return "2Y"
    elif years <= 5:     # <= 5 ans
        return "5Y"
    elif years <= 10:    # <= 10 ans
        return "10Y"
    else:
        return f"{int(years)}Y"


def is_business_day(date: pd.Timestamp, 
                   holidays: list = None) -> bool:
    """
    Vérifie si une date est un jour ouvré
    
    Args:
        date: Date à vérifier
        holidays: Liste optionnelle de jours fériés
        
    Returns:
        bool: True si jour ouvré
    """
    if pd.isna(date):
        return False
    
    # Weekend check
    if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Holiday check (simple - à adapter selon vos besoins)
    if holidays and date.normalize() in holidays:
        return False
    
    return True


def add_business_days(start_date: pd.Timestamp, 
                     business_days: int,
                     holidays: list = None) -> pd.Timestamp:
    """
    Ajoute un nombre de jours ouvrés à une date
    
    Args:
        start_date: Date de départ
        business_days: Nombre de jours ouvrés à ajouter
        holidays: Liste optionnelle de jours fériés
        
    Returns:
        pd.Timestamp: Date résultante
    """
    if pd.isna(start_date):
        return pd.NaT
    
    current_date = start_date
    days_added = 0
    
    while days_added < business_days:
        current_date += pd.Timedelta(days=1)
        if is_business_day(current_date, holidays):
            days_added += 1
    
    return current_date


def get_accrual_period_fraction(start_date: pd.Timestamp,
                               end_date: pd.Timestamp,
                               day_count_convention: str = "ACT/365") -> float:
    """
    Calcule la fraction d'année selon une convention de décompte
    
    Args:
        start_date: Date de début de la période
        end_date: Date de fin de la période  
        day_count_convention: Convention ("ACT/365", "ACT/360", "30/360", etc.)
        
    Returns:
        float: Fraction d'année
    """
    if pd.isna(start_date) or pd.isna(end_date):
        return 0.0
    
    if end_date <= start_date:
        return 0.0
    
    days = (end_date - start_date).days
    
    if day_count_convention == "ACT/365":
        return days / 365.0
    elif day_count_convention == "ACT/360":
        return days / 360.0
    elif day_count_convention == "30/360":
        # Simplification - implémentation complète 30/360 plus complexe
        return days / 360.0
    else:
        logger.warning(f"Convention inconnue {day_count_convention}, utilisation ACT/365")
        return days / 365.0


def get_val_date() -> pd.Timestamp:
    """Retourne la date de valorisation actuelle"""
    return VAL_DATE


def set_val_date(new_val_date: Union[str, pd.Timestamp, datetime]) -> None:
    """
    Définit une nouvelle date de valorisation globale
    Utile pour les tests ou la valorisation historique
    """
    global VAL_DATE
    VAL_DATE = to_naive_ts(new_val_date)
    logger.info(f"Date de valorisation mise à jour: {VAL_DATE}")