# tests/test_pnl.py
import pytest
import pandas as pd

def test_pnl_calculation_basic(sample_deal, sample_pnl_config):
    """Test calcul PnL basique"""
    try:
        from treasury.pnl import compute_enhanced_pnl_vectorized
        
        deals = [sample_deal]
        df_pnl = compute_enhanced_pnl_vectorized(deals, sample_pnl_config)
        
        # Vérifications basiques
        assert not df_pnl.empty, "DataFrame PnL ne doit pas être vide"
        assert len(df_pnl) == 1, "Doit avoir 1 ligne pour 1 deal"
        assert 'total_pnl' in df_pnl.columns, "Colonne total_pnl manquante"
        
        print(f"✅ PnL calculé: {df_pnl['total_pnl'].iloc[0]:,.0f}")
        
    except ImportError as e:
        pytest.skip(f"Module PnL non disponible: {e}")
    except Exception as e:
        assert False, f"Erreur calcul PnL: {e}"


def test_pnl_imports():
    """Test imports modules PnL"""
    try:
        from treasury.pnl import compute_enhanced_pnl_vectorized, get_pnl_summary
        print("✅ Imports PnL OK")
        assert True
    except ImportError as e:
        assert False, f"Import PnL échoué: {e}"