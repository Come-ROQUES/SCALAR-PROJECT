"""
Gestion du session state Streamlit pour le Treasury Dashboard
"""

import pandas as pd
import streamlit as st
from typing import Dict, Any, List
import logging

from .config import DEFAULT_SESSION_STATE

# Logger simple pour éviter la dépendance circulaire
logger = logging.getLogger(__name__)


def init_session_state():
    """
    Initialise le session state avec les valeurs par défaut
    """
    try:
        for key, default_value in DEFAULT_SESSION_STATE.items():
            if key not in st.session_state:
                if isinstance(default_value, dict):
                    st.session_state[key] = default_value.copy()
                elif key == 'df_pnl_enhanced':
                    st.session_state[key] = pd.DataFrame()
                else:
                    st.session_state[key] = default_value
            elif isinstance(default_value, dict):
                # Vérifier que toutes les sous-clés existent
                for sub_key, sub_default in default_value.items():
                    if sub_key not in st.session_state[key]:
                        st.session_state[key][sub_key] = sub_default
        
        logger.info("Session state initialisé")
        
    except Exception as e:
        logger.error(f"Erreur initialisation session state: {e}")


def reset_session_state():
    """
    Remet à zéro le session state
    """
    try:
        for key in DEFAULT_SESSION_STATE.keys():
            if key in st.session_state:
                del st.session_state[key]
        
        init_session_state()
        logger.info("Session state reset")
        
    except Exception as e:
        logger.error(f"Erreur reset session state: {e}")


def get_session_info() -> Dict[str, Any]:
    """
    Retourne des informations sur l'état de la session
    
    Returns:
        Dict: Informations de session
    """
    try:
        info = {
            'deals_count': len(st.session_state.get('generic_deals', [])),
            'has_pnl_data': not st.session_state.get('df_pnl_enhanced', pd.DataFrame()).empty,
            'pnl_config': st.session_state.get('pnl_config', {}),
            'risk_limits': st.session_state.get('risk_limits', {}),
            'session_keys': list(st.session_state.keys())
        }
        
        if info['has_pnl_data']:
            df_pnl = st.session_state.get('df_pnl_enhanced')
            info['pnl_shape'] = df_pnl.shape
            if 'total_pnl' in df_pnl.columns:
                info['total_pnl_usd'] = df_pnl['total_pnl'].sum()
        
        return info
        
    except Exception as e:
        logger.error(f"Erreur récupération session info: {e}")
        return {}


def validate_session_state() -> Dict[str, Any]:
    """
    Valide l'état du session state
    
    Returns:
        Dict: Résultats de validation
    """
    validation = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Vérification clés requises
        for key in DEFAULT_SESSION_STATE.keys():
            if key not in st.session_state:
                validation['errors'].append(f"Clé manquante: {key}")
                validation['is_valid'] = False
        
        # Vérification types
        if 'generic_deals' in st.session_state:
            if not isinstance(st.session_state['generic_deals'], list):
                validation['errors'].append("generic_deals doit être une liste")
                validation['is_valid'] = False
        
        if 'df_pnl_enhanced' in st.session_state:
            if not isinstance(st.session_state['df_pnl_enhanced'], pd.DataFrame):
                validation['errors'].append("df_pnl_enhanced doit être un DataFrame")
                validation['is_valid'] = False
        
        # Vérifications cohérence
        deals_count = len(st.session_state.get('generic_deals', []))
        df_pnl = st.session_state.get('df_pnl_enhanced', pd.DataFrame())
        
        if deals_count > 0 and not df_pnl.empty:
            if len(df_pnl) != deals_count:
                validation['warnings'].append(
                    f"Incohérence: {deals_count} deals vs {len(df_pnl)} lignes PnL"
                )
        
        logger.info(f"Validation session: {validation['is_valid']}")
        
    except Exception as e:
        validation['errors'].append(f"Erreur validation: {e}")
        validation['is_valid'] = False
        logger.error(f"Erreur validation session state: {e}")
    
    return validation


def clear_pnl_data():
    """
    Efface uniquement les données PnL (garde les deals)
    """
    try:
        if 'df_pnl_enhanced' in st.session_state:
            st.session_state.df_pnl_enhanced = pd.DataFrame()
        
        logger.info("Données PnL effacées")
        
    except Exception as e:
        logger.error(f"Erreur effacement PnL: {e}")


def clear_all_data():
    """
    Efface toutes les données (deals + PnL)
    """
    try:
        if 'generic_deals' in st.session_state:
            st.session_state.generic_deals = []
        
        clear_pnl_data()
        logger.info("Toutes les données effacées")
        
    except Exception as e:
        logger.error(f"Erreur effacement données: {e}")


def backup_session_data() -> Dict[str, Any]:
    """
    Crée une sauvegarde des données de session
    
    Returns:
        Dict: Données sauvegardées
    """
    try:
        backup = {
            'deals': st.session_state.get('generic_deals', []),
            'pnl_config': st.session_state.get('pnl_config', {}),
            'risk_limits': st.session_state.get('risk_limits', {}),
            'timestamp': pd.Timestamp.now()
        }
        
        # Sérialisation des deals pour sauvegarde
        if backup['deals']:
            backup['deals_serialized'] = [deal.dict() for deal in backup['deals']]
        
        logger.info(f"Sauvegarde créée: {len(backup.get('deals', []))} deals")
        return backup
        
    except Exception as e:
        logger.error(f"Erreur sauvegarde session: {e}")
        return {}


def restore_session_data(backup: Dict[str, Any]):
    """
    Restaure les données depuis une sauvegarde
    
    Args:
        backup: Données de sauvegarde
    """
    try:
        from .models import GenericDeal
        
        if 'deals_serialized' in backup:
            deals = [GenericDeal(**deal_dict) for deal_dict in backup['deals_serialized']]
            st.session_state.generic_deals = deals
        
        if 'pnl_config' in backup:
            st.session_state.pnl_config.update(backup['pnl_config'])
        
        if 'risk_limits' in backup:
            st.session_state.risk_limits.update(backup['risk_limits'])
        
        # Effacer PnL car il faut recalculer
        clear_pnl_data()
        
        logger.info(f"Session restaurée: {len(st.session_state.generic_deals)} deals")
        
    except Exception as e:
        logger.error(f"Erreur restauration session: {e}")


class SessionManager:
    """
    Gestionnaire avancé du session state
    """
    
    def __init__(self):
        self.logger = logger
    
    def ensure_initialized(self):
        """S'assure que le session state est initialisé"""
        if not hasattr(st.session_state, '_treasury_initialized'):
            init_session_state()
            st.session_state._treasury_initialized = True
    
    def get_deals(self):
        """Récupère les deals de façon sécurisée"""
        self.ensure_initialized()
        return st.session_state.get('generic_deals', [])
    
    def set_deals(self, deals):
        """Définit les deals et efface le PnL"""
        self.ensure_initialized()
        st.session_state.generic_deals = deals
        clear_pnl_data()
        self.logger.info(f"Deals mis à jour: {len(deals)}")
    
    def get_pnl_data(self):
        """Récupère les données PnL de façon sécurisée"""
        self.ensure_initialized()
        return st.session_state.get('df_pnl_enhanced', pd.DataFrame())
    
    def set_pnl_data(self, df_pnl):
        """Définit les données PnL"""
        self.ensure_initialized()
        st.session_state.df_pnl_enhanced = df_pnl
        self.logger.info(f"PnL mis à jour: {df_pnl.shape}")
    
    def get_config(self):
        """Récupère la configuration PnL"""
        self.ensure_initialized()
        return st.session_state.get('pnl_config', {})
    
    def update_config(self, **kwargs):
        """Met à jour la configuration PnL"""
        self.ensure_initialized()
        config = st.session_state.get('pnl_config', {})
        config.update(kwargs)
        st.session_state.pnl_config = config
        
        # Marquer PnL comme obsolète
        if hasattr(st.session_state, '_pnl_needs_recalc'):
            st.session_state._pnl_needs_recalc = True
    
    def needs_pnl_recalc(self):
        """Vérifie si le PnL doit être recalculé"""
        return (
            st.session_state.get('_pnl_needs_recalc', False) or
            self.get_pnl_data().empty and len(self.get_deals()) > 0
        )
    
    def mark_pnl_calculated(self):
        """Marque le PnL comme à jour"""
        st.session_state._pnl_needs_recalc = False
    
    def get_summary_stats(self):
        """Retourne des statistiques résumées"""
        deals = self.get_deals()
        df_pnl = self.get_pnl_data()
        
        stats = {
            'deals_count': len(deals),
            'has_pnl': not df_pnl.empty,
            'pnl_needs_recalc': self.needs_pnl_recalc()
        }
        
        if deals:
            from collections import Counter
            product_counts = Counter(deal.product for deal in deals)
            stats['products'] = dict(product_counts)
        
        if not df_pnl.empty and 'total_pnl' in df_pnl.columns:
            stats['total_pnl_usd'] = df_pnl['total_pnl'].sum()
            stats['total_pnl_m'] = stats['total_pnl_usd'] / 1_000_000
        
        return stats


# Instance globale
session_manager = SessionManager()