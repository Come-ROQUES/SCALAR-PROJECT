"""
Configuration de logging pour Streamlit
Version simplifiée pour éviter les dépendances circulaires
"""

import logging
from datetime import datetime
from typing import List, Dict, Any

# Configuration seulement si Streamlit est disponible
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class StreamlitLogHandler(logging.Handler):
    """
    Handler custom qui stocke les logs dans le session state Streamlit
    pour affichage temps réel dans l'interface
    """
    
    def emit(self, record):
        """Émet un log vers le session state Streamlit"""
        if not STREAMLIT_AVAILABLE:
            return
            
        # S'assurer que app_logs existe dans session state
        if 'app_logs' not in st.session_state:
            st.session_state.app_logs = []
        
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.name,
        }
        
        # Maintenir une taille maximum de logs
        logs = st.session_state.app_logs
        if len(logs) >= 100:
            logs.pop(0)  # Supprimer le plus ancien
        
        logs.append(log_entry)


def setup_logger(name: str = "treasury") -> logging.Logger:
    """
    Configure et retourne un logger pour le module Treasury
    
    Args:
        name: Nom du logger
        
    Returns:
        logging.Logger: Logger configuré
    """
    logger = logging.getLogger(name)
    
    # Éviter la duplication de handlers
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Handler console pour développement
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler Streamlit si disponible
    if STREAMLIT_AVAILABLE:
        st_handler = StreamlitLogHandler()
        logger.addHandler(st_handler)
    
    return logger


def get_recent_logs(max_logs: int = 10) -> List[Dict[str, Any]]:
    """
    Récupère les logs récents du session state
    
    Args:
        max_logs: Nombre maximum de logs à retourner
        
    Returns:
        List[Dict]: Liste des logs récents
    """
    if not STREAMLIT_AVAILABLE:
        return []
        
    if 'app_logs' not in st.session_state:
        return []
    
    logs = st.session_state.app_logs
    return logs[-max_logs:] if len(logs) > max_logs else logs


def clear_logs():
    """Efface tous les logs du session state"""
    if STREAMLIT_AVAILABLE and 'app_logs' in st.session_state:
        st.session_state.app_logs = []


def log_performance(func_name: str, execution_time: float, deals_count: int = None):
    """
    Log spécialisé pour les métriques de performance
    
    Args:
        func_name: Nom de la fonction
        execution_time: Temps d'exécution en secondes
        deals_count: Nombre de deals traités (optionnel)
    """
    logger = get_logger()
    
    if deals_count:
        logger.info(f"⚡ {func_name}: {execution_time:.3f}s pour {deals_count} deals "
                   f"({deals_count/execution_time:.0f} deals/sec)")
    else:
        logger.info(f"⚡ {func_name}: {execution_time:.3f}s")


def log_calculation_summary(module: str, deals_processed: int, errors: int, warnings: int):
    """
    Log de résumé pour les calculs
    
    Args:
        module: Nom du module (ex: "PnL", "Risk", etc.)
        deals_processed: Nombre de deals traités
        errors: Nombre d'erreurs
        warnings: Nombre de warnings
    """
    logger = get_logger()
    
    status = "✅" if errors == 0 else "⚠️" if errors < deals_processed else "❌"
    
    logger.info(f"{status} {module}: {deals_processed} deals, "
               f"{errors} erreurs, {warnings} warnings")


def log_data_quality(data_source: str, total_rows: int, valid_rows: int, 
                    invalid_rows: int):
    """
    Log pour la qualité des données importées
    
    Args:
        data_source: Source des données (ex: "Excel Import")
        total_rows: Nombre total de lignes
        valid_rows: Nombre de lignes valides
        invalid_rows: Nombre de lignes invalides
    """
    logger = get_logger()
    
    quality_pct = (valid_rows / total_rows * 100) if total_rows > 0 else 0
    status = "✅" if quality_pct >= 95 else "⚠️" if quality_pct >= 80 else "❌"
    
    logger.info(f"{status} {data_source}: {quality_pct:.1f}% qualité "
               f"({valid_rows}/{total_rows} valides)")


# Instance globale du logger
logger = setup_logger()


def get_logger() -> logging.Logger:
    """Retourne l'instance globale du logger"""
    return logger