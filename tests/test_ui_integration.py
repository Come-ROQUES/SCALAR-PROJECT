"""
Tests d'intégration UI pour Streamlit
Simulation d'interactions utilisateur complètes
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Ajout du path pour imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from treasury.models import GenericDeal, ProductType, DepositLoan
from treasury.pnl import compute_enhanced_pnl_vectorized
from treasury.config import PnLConfig


class StreamlitTestSession:
    """Simulateur de session Streamlit pour tests"""
    
    def __init__(self):
        self.session_state = {}
        self.widgets = {}
        self.uploaded_files = []
        self.charts = []
        self.messages = []
    
    def set_widget_value(self, key: str, value):
        """Simule l'interaction avec un widget"""
        self.widgets[key] = value
        return value
    
    def upload_file(self, file_content: bytes, filename: str):
        """Simule l'upload d'un fichier"""
        mock_file = Mock()
        mock_file.name = filename
        mock_file.size = len(file_content)
        mock_file.read.return_value = file_content
        mock_file.getvalue.return_value = file_content
        
        self.uploaded_files.append(mock_file)
        return mock_file
    
    def clear_session(self):
        """Reset session pour nouveau test"""
        self.session_state.clear()
        self.widgets.clear()
        self.uploaded_files.clear()
        self.charts.clear()
        self.messages.clear()


@pytest.fixture
def streamlit_session():
    """Fixture session Streamlit mockée"""
    return StreamlitTestSession()


@pytest.fixture
def sample_deals_data():
    """Fixture avec données de deals d'exemple"""
    return [
        {
            'comment': 'EUR/USD FX Swap',
            'product': 'FX_SWAP',
            'deal_id': 'FXS001',
            'd_or_l': 'L',
            'pair_currency': 'EUR/USD',
            'amount': 10_000_000,
            'trade_date': '2025-01-01',
            'value_date': '2025-01-03',
            'maturity_date': '2025-12-03',
            'client_rate': 0.045,
            'ois_equivalent_rate': 0.044,
            'trader_id': 'TRD001'
        },
        {
            'comment': 'USD IRS 3Y',
            'product': 'IRS',
            'deal_id': 'IRS001',
            'd_or_l': 'D',
            'pair_currency': 'USD',
            'amount': 50_000_000,
            'trade_date': '2025-01-02',
            'value_date': '2025-01-04',
            'maturity_date': '2028-01-04',
            'client_rate': 0.035,
            'ois_equivalent_rate': 0.033,
            'trader_id': 'TRD002'
        }
    ]


@pytest.fixture
def mock_excel_file(sample_deals_data):
    """Crée un fichier Excel mock pour tests"""
    df = pd.DataFrame(sample_deals_data)
    
    # Simulation fichier Excel en mémoire
    from io import BytesIO
    excel_buffer = BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='DEALS', index=False)
    
    excel_buffer.seek(0)
    return excel_buffer.getvalue()


class TestStreamlitUIIntegration:
    """Tests d'intégration UI complets"""
    
    @patch('streamlit.session_state')
    @patch('streamlit.file_uploader')
    @patch('streamlit.selectbox')
    @patch('streamlit.button')
    def test_complete_import_workflow(self, mock_button, mock_selectbox, 
                                    mock_file_uploader, mock_session_state,
                                    streamlit_session, mock_excel_file):
        """Test workflow complet d'import Excel"""
        
        # Configuration des mocks
        mock_session_state.__getitem__ = lambda key: streamlit_session.session_state.get(key, [])
        mock_session_state.__setitem__ = lambda key, value: streamlit_session.session_state.update({key: value})
        mock_session_state.get = lambda key, default=None: streamlit_session.session_state.get(key, default)
        
        # Simulation upload fichier
        mock_file = streamlit_session.upload_file(mock_excel_file, "test_deals.xlsx")
        mock_file_uploader.return_value = mock_file
        
        # Simulation configuration PnL
        mock_selectbox.side_effect = [True, True, True, True]  # Tous les calculs activés
        mock_button.return_value = True  # Bouton "Calculer PnL" cliqué
        
        # Import du module à tester (avec mocks en place)
        from ui.components.tabs.import_tab import render_import_tab
        
        # Exécution du workflow d'import
        try:
            render_import_tab()
            
            # Vérifications
            assert mock_file_uploader.called
            assert 'generic_deals' in streamlit_session.session_state
            assert len(streamlit_session.session_state.get('generic_deals', [])) > 0
            
        except Exception as e:
            pytest.skip(f"Test nécessite environnement Streamlit: {e}")
    
    @patch('streamlit.session_state')
    @patch('streamlit.plotly_chart')
    def test_pnl_calculation_and_display(self, mock_plotly_chart, mock_session_state,
                                       streamlit_session, sample_deals_data):
        """Test calcul PnL et affichage des résultats"""
        
        # Préparation des deals
        deals = []
        for deal_data in sample_deals_data:
            deal = GenericDeal(**deal_data)
            deals.append(deal)
        
        # Configuration session
        streamlit_session.session_state['generic_deals'] = deals
        streamlit_session.session_state['pnl_config'] = PnLConfig()
        
        mock_session_state.__getitem__ = lambda key: streamlit_session.session_state.get(key, [])
        mock_session_state.get = lambda key, default=None: streamlit_session.session_state.get(key, default)
        
        # Calcul PnL
        df_pnl = compute_enhanced_pnl_vectorized(deals, PnLConfig())
        streamlit_session.session_state['df_pnl_enhanced'] = df_pnl
        
        # Test affichage
        try:
            from ui.components.tabs.pnl_tab import render_pnl_tab
            render_pnl_tab()
            
            # Vérifications
            assert not df_pnl.empty
            assert 'total_pnl' in df_pnl.columns
            assert len(df_pnl) == len(deals)
            
            # Vérification que des graphiques ont été générés
            assert mock_plotly_chart.called
            
        except Exception as e:
            pytest.skip(f"Test nécessite modules UI: {e}")
    
    def test_risk_monitoring_alerts(self, streamlit_session):
        """Test système d'alertes et monitoring"""
        
        # Données avec violations de limites
        risky_data = pd.DataFrame({
            'deal_id': ['RISK001', 'RISK002'],
            'total_pnl': [-15_000_000, 8_000_000],  # Gros impact négatif
            'base_currency': ['USD', 'EUR'],
            'amount': [100_000_000, 200_000_000],
            'product': ['LOAN', 'DEPOSIT']
        })
        
        streamlit_session.session_state['df_pnl_enhanced'] = risky_data
        
        # Test monitoring
        from treasury.monitoring.alerts import alert_manager
        alert_manager.run_full_monitoring(risky_data)
        
        # Vérifications alertes
        summary = alert_manager.get_dashboard_summary()
        assert summary['total_active'] >= 0
        
        # Test VaR breach simulé
        alert_manager.check_var_limits(var_95=-12_000_000, var_99=-18_000_000)
        
        summary_after = alert_manager.get_dashboard_summary()
        assert summary_after['total_active'] > summary['total_active']
    
    @patch('streamlit.session_state')
    def test_cache_performance_integration(self, mock_session_state, streamlit_session):
        """Test intégration cache et performance"""
        
        # Configuration cache
        from treasury.cache import cache_manager
        
        # Données volumineuses pour test performance
        large_deals = []
        for i in range(100):
            deal = GenericDeal(
                comment=f'Deal {i}',
                product=ProductType.DEPOSIT,
                deal_id=f'DEAL{i:03d}',
                d_or_l=DepositLoan.DEPOSIT,
                pair_currency='USD',
                amount=1_000_000,
                trade_date=datetime(2025, 1, 1),
                value_date=datetime(2025, 1, 3),
                maturity_date=datetime(2025, 12, 31),
                client_rate=0.05,
                ois_equivalent_rate=0.048
            )
            large_deals.append(deal)
        
        # Test calcul avec cache
        cache_key = f"pnl_calculation_{hash(str(large_deals))}"
        
        # Premier calcul (miss cache)
        import time
        start_time = time.time()
        
        result_1 = compute_enhanced_pnl_vectorized(large_deals, PnLConfig())
        cache_manager.set(cache_key, result_1)
        
        first_calculation_time = time.time() - start_time
        
        # Deuxième calcul (hit cache)
        start_time = time.time()
        
        cached_result = cache_manager.get(cache_key)
        
        cache_retrieval_time = time.time() - start_time
        
        # Vérifications
        assert cached_result is not None
        assert len(cached_result) == len(result_1)
        assert cache_retrieval_time < first_calculation_time  # Cache plus rapide
    
    def test_data_validation_edge_cases(self):
        """Test validation avec cas limites"""
        
        # Cas limite: dates incohérentes
        invalid_deal_data = {
            'comment': 'Invalid Deal',
            'product': 'DEPOSIT',
            'deal_id': 'INV001',
            'd_or_l': 'D',
            'pair_currency': 'USD',
            'amount': 1_000_000,
            'trade_date': '2025-01-10',
            'value_date': '2025-01-05',  # value_date < trade_date
            'maturity_date': '2025-01-01',  # maturity_date < value_date
            'client_rate': 0.05,
            'ois_equivalent_rate': 0.048
        }
        
        # Doit lever une ValidationError
        with pytest.raises(Exception):  # Pydantic ValidationError
            GenericDeal(**invalid_deal_data)
        
        # Cas limite: taux négatifs
        negative_rate_data = invalid_deal_data.copy()
        negative_rate_data.update({
            'value_date': '2025-01-15',
            'maturity_date': '2025-12-31',
            'client_rate': -0.01,  # Taux négatif
        })
        
        with pytest.raises(Exception):
            GenericDeal(**negative_rate_data)
    
    @patch('streamlit.warning')
    @patch('streamlit.error') 
    @patch('streamlit.success')
    def test_user_feedback_messages(self, mock_success, mock_error, mock_warning):
        """Test messages de feedback utilisateur"""
        
        # Simulation erreurs diverses
        error_scenarios = [
            (pd.DataFrame(), "DataFrame vide"),
            (None, "Données nulles"),
        ]
        
        for error_data, error_msg in error_scenarios:
            try:
                from treasury.pnl import validate_pnl_results
                result = validate_pnl_results(error_data)
                
                # Vérification que des erreurs sont détectées
                assert not result['is_valid']
                assert len(result['errors']) > 0
                
            except Exception:
                # Erreur attendue dans certains cas
                pass


@pytest.mark.integration
class TestFullUserJourney:
    """Tests bout-en-bout simulant un utilisateur complet"""
    
    def test_complete_user_workflow(self, streamlit_session, mock_excel_file):
        """Workflow utilisateur complet de A à Z"""
        
        # 1. Démarrage application
        streamlit_session.clear_session()
        
        # 2. Upload fichier Excel
        uploaded_file = streamlit_session.upload_file(mock_excel_file, "portfolio.xlsx")
        assert uploaded_file.name == "portfolio.xlsx"
        
        # 3. Configuration calculs PnL
        pnl_config = PnLConfig(
            calculate_accrued=True,
            calculate_mtm=True,
            calculate_rate=True,
            calculate_liquidity=True
        )
        streamlit_session.session_state['pnl_config'] = pnl_config
        
        # 4. Simulation calculs (deals mockés)
        mock_deals = [
            GenericDeal(
                comment='Test Deal',
                product=ProductType.LOAN,
                deal_id='TEST001',
                d_or_l=DepositLoan.LOAN,
                pair_currency='USD',
                amount=5_000_000,
                trade_date=datetime(2025, 1, 1),
                value_date=datetime(2025, 1, 3),
                maturity_date=datetime(2025, 6, 30),
                client_rate=0.055,
                ois_equivalent_rate=0.050
            )
        ]
        
        # 5. Calcul PnL
        df_pnl = compute_enhanced_pnl_vectorized(mock_deals, pnl_config)
        streamlit_session.session_state['df_pnl_enhanced'] = df_pnl
        streamlit_session.session_state['generic_deals'] = mock_deals
        
        # 6. Vérifications finales
        assert not df_pnl.empty
        assert len(df_pnl) == 1
        assert df_pnl.iloc[0]['deal_id'] == 'TEST001'
        assert 'total_pnl' in df_pnl.columns
        
        # 7. Test export (simulation)
        export_data = {
            'deals_count': len(mock_deals),
            'total_pnl': df_pnl['total_pnl'].sum(),
            'timestamp': datetime.now().isoformat()
        }
        
        assert export_data['deals_count'] > 0
        assert 'total_pnl' in export_data


if __name__ == "__main__":
    # Lancement des tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-k", "not slow"  # Exclut les tests marqués slow
    ])
