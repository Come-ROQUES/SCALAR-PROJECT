\
\
\
\

import logging
from datetime import datetime
from typing import List, Dict, Any


try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class StreamlitLogHandler(logging.Handler):
\
\
\
\

    def emit(self, record):
        \
        if not STREAMLIT_AVAILABLE:
            return


        if 'app_logs' not in st.session_state:
            st.session_state.app_logs = []

        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.name,
        }


        logs = st.session_state.app_logs
        if len(logs) >= 100:
            logs.pop(0)

        logs.append(log_entry)


def setup_logger(name: str = "treasury") -> logging.Logger:
    \
\
\
\
\
\
\
\
\
    logger = logging.getLogger(name)


    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)


    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


    if STREAMLIT_AVAILABLE:
        st_handler = StreamlitLogHandler()
        logger.addHandler(st_handler)

    return logger


def get_recent_logs(max_logs: int = 10) -> List[Dict[str, Any]]:
    \
\
\
\
\
\
\
\
\
    if not STREAMLIT_AVAILABLE:
        return []

    if 'app_logs' not in st.session_state:
        return []

    logs = st.session_state.app_logs
    return logs[-max_logs:] if len(logs) > max_logs else logs


def clear_logs():
    \
    if STREAMLIT_AVAILABLE and 'app_logs' in st.session_state:
        st.session_state.app_logs = []


def log_performance(func_name: str, execution_time: float, deals_count: int = None):
    \
\
\
\
\
\
\
\
    logger = get_logger()

    if deals_count:
        logger.info(f"⚡ {func_name}: {execution_time:.3f}s pour {deals_count} deals "
                   f"({deals_count/execution_time:.0f} deals/sec)")
    else:
        logger.info(f"⚡ {func_name}: {execution_time:.3f}s")


def log_calculation_summary(module: str, deals_processed: int, errors: int, warnings: int):
    \
\
\
\
\
\
\
\
\
    logger = get_logger()

    status = "OK" if errors == 0 else "WARNING" if errors < deals_processed else "ERROR"

    logger.info(f"{status} {module}: {deals_processed} deals, "
               f"{errors} erreurs, {warnings} warnings")


def log_data_quality(data_source: str, total_rows: int, valid_rows: int,
                    invalid_rows: int):
    \
\
\
\
\
\
\
\
\
    logger = get_logger()

    quality_pct = (valid_rows / total_rows * 100) if total_rows > 0 else 0
    status = "OK" if quality_pct >= 95 else "WARNING" if quality_pct >= 80 else "ERROR"

    logger.info(f"{status} {data_source}: {quality_pct:.1f}% qualité "
               f"({valid_rows}/{total_rows} valides)")



logger = setup_logger()


def get_logger() -> logging.Logger:
    \
    return logger