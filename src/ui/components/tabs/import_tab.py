"""
Onglet Import pour Treasury Dashboard
Module UI séparé pour l'import des données
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from typing import List, Dict, Any

# Imports Treasury
from treasury.config import settings
from treasury.io.excel import ExcelProcessor, build_template_generic
from treasury.models import GenericDeal

try:
    from treasury.logging_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def render_import_tab():
    """Onglet d'import des données"""
    st.subheader("Import Excel Format Générique")
    
    _render_template_section()
    _render_format_info()
    _render_upload_form()


def _render_template_section():
    """Section téléchargement template au-dessus de l'import"""
    st.markdown("### 📥 Template Excel")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        **Téléchargez le template Excel** pour importer vos deals avec la bonne structure.
        Le template contient les colonnes requises et des exemples de données.
        """)
    
    with col2:
        # Template download
        template_data = build_template_generic()
        st.download_button(
            label="Télécharger Template",
            data=template_data,
            file_name=f"treasury_template_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Template avec structure complète et documentation",
            type="primary",
            use_container_width=True
        )
    
    st.markdown("---")


def _render_format_info():
    """Information sur le format attendu"""
    with st.expander("Format Attendu - Cliquez pour voir les détails"):
        st.markdown("""
        **Structure requise :**  
        - **Feuille** : `DEALS`
        - **Colonnes obligatoires** :
          - `comment` : Description du deal
          - `product` : Type de produit (DEPOSIT, LOAN, FX_SWAP, etc.)
          - `deal_id` : Identifiant unique du deal
          - `d_or_l` : DEPOSIT ou LOAN
          - `pair_currency` : Paire de devises (ex: EUR/USD)
          - `amount` : Montant notionnel
          - `trade_date` : Date de trade (YYYY-MM-DD)
          - `value_date` : Date de valeur
          - `maturity_date` : Date d'échéance  
          - `client_rate` : Taux client (décimal)
          - `ois_equivalent_rate` : Taux OIS équivalent
          - `trader_id` : Identifiant du trader (optionnel)
        
        **Conseils :**
        - Utilisez le template pour éviter les erreurs de format
        - Les dates doivent être au format YYYY-MM-DD
        - Les taux sont en décimal (0.05 pour 5%)
        """)


def _render_upload_form():
    """Formulaire d'upload et traitement"""
    st.markdown("### 📤 Import de Fichier")
    
    processor = ExcelProcessor()
    
    with st.form("upload_form"):
        uploaded_file = st.file_uploader(
            "Sélectionner fichier Excel",
            type=["xlsx", "xls"],
            help=f"Taille max: {settings.MAX_FILE_SIZE_MB}MB"
        )
        
        # Options de traitement
        st.markdown("**Options de traitement :**")
        col1, col2 = st.columns(2)
        with col1:
            auto_clean = st.checkbox("🧹 Nettoyage automatique", value=True, 
                                   help="Supprime les lignes vides et corrige les formats")
        with col2:
            auto_generate_ids = st.checkbox("🆔 Générer IDs manquants", value=True,
                                          help="Génère automatiquement les deal_id manquants")
        
        # Bouton submit obligatoire
        submitted = st.form_submit_button("Importer & Valider", type="primary")
        
        # Traitement seulement si formulaire soumis ET fichier présent
        if submitted:
            if uploaded_file is not None:
                _process_uploaded_file(processor, uploaded_file, auto_clean, auto_generate_ids)
            else:
                st.warning("Veuillez sélectionner un fichier Excel à importer")


def _process_uploaded_file(processor: ExcelProcessor, uploaded_file, auto_clean: bool, auto_generate_ids: bool):
    """Traite le fichier uploadé"""
    with st.spinner("Traitement en cours..."):
        start_time = time.time()
        
        try:
            deals, warnings, metadata = processor.process_file(
                uploaded_file, 
                auto_clean=auto_clean,
                auto_generate_ids=auto_generate_ids
            )
            
            processing_time = time.time() - start_time
            
            # Sauvegarde en session
            st.session_state.generic_deals = deals
            
            # Affichage résultats
            _display_import_results(deals, warnings, metadata, processing_time)
            
        except Exception as e:
            st.error(f"ERROR Erreur lors du traitement: {e}")
            logger.error(f"Erreur import: {e}")


def _display_import_results(deals: List[GenericDeal], warnings: List[str], metadata: Dict[str, Any], processing_time: float):
    """Affiche les résultats de l'import"""
    if deals:
        st.success(f"SUCCESS {len(deals)} deals importés avec succès en {processing_time:.1f}s")
        
        # Preview des données
        _display_deals_preview(deals)
        
        # Métadonnées
        _display_import_metadata(metadata)
        
        # Auto-calcul PnL pour faciliter l'usage
        with st.spinner("Calcul PnL automatique..."):
            try:
                # Import des modules PnL
                from treasury.pnl import compute_enhanced_pnl_vectorized
                from treasury.models import PnLConfig
                
                # Configuration par défaut
                config = PnLConfig()
                
                # Calcul PnL
                df_pnl = compute_enhanced_pnl_vectorized(deals, config)
                st.session_state.df_pnl_enhanced = df_pnl
                
                if not df_pnl.empty:
                    total_pnl = df_pnl['total_pnl'].sum() / 1_000_000  # En millions
                    st.info(f"PnL calculé automatiquement: {total_pnl:+.2f}M USD")
                    
            except Exception as e:
                logger.warning(f"Erreur calcul PnL automatique: {e}")
                st.warning("Calcul PnL automatique échoué. Utilisez l'onglet PnL pour calculer manuellement.")
    else:
        st.error("ERROR Aucun deal valide importé")
    
    # Warnings
    _display_import_warnings(warnings)


def _display_deals_preview(deals: List[GenericDeal]):
    """Affiche un aperçu des deals importés"""
    deals_display = pd.DataFrame([{
        'deal_id': d.deal_id,
        'product': d.product,
        'pair_currency': d.pair_currency,
        'amount_M': d.amount / 1_000_000,
        'maturity': d.maturity_date.date(),
        'client_rate': f"{d.client_rate:.2%}"
    } for d in deals[:100]])  # Limite affichage à 100
    
    st.dataframe(deals_display, use_container_width=True, height=300)


def _display_import_metadata(metadata: Dict[str, Any]):
    """Affiche les métadonnées de l'import"""
    with st.expander("Métadonnées Import"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Lignes originales", metadata.get('original_rows', 0))
        col2.metric("Deals valides", metadata.get('valid_deals', 0))
        col3.metric("Erreurs", metadata.get('invalid_deals', 0))


def _display_import_warnings(warnings: List[str]):
    """Affiche les warnings de l'import"""
    if warnings:
        with st.expander(f"Warnings ({len(warnings)})"):
            for warning in warnings[:20]:  # Limite affichage à 20
                st.warning(warning)
            if len(warnings) > 20:
                st.info(f"... et {len(warnings) - 20} autres warnings")


def validate_import_data(deals: List[GenericDeal]) -> Dict[str, Any]:
    """Valide les données importées et retourne un rapport"""
    validation_report = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'statistics': {}
    }
    
    if not deals:
        validation_report['is_valid'] = False
        validation_report['errors'].append("Aucun deal importé")
        return validation_report
    
    # Statistiques de base
    validation_report['statistics'] = {
        'total_deals': len(deals),
        'total_notional': sum(deal.amount for deal in deals),
        'products': list(set(deal.product for deal in deals)),
        'currencies': list(set(deal.pair_currency for deal in deals))
    }
    
    # Validations métier
    _validate_deal_ids(deals, validation_report)
    _validate_amounts(deals, validation_report)
    _validate_dates(deals, validation_report)
    _validate_rates(deals, validation_report)
    
    return validation_report


def _validate_deal_ids(deals: List[GenericDeal], report: Dict[str, Any]):
    """Valide l'unicité des deal IDs"""
    deal_ids = [deal.deal_id for deal in deals]
    duplicates = [id for id in set(deal_ids) if deal_ids.count(id) > 1]
    
    if duplicates:
        report['warnings'].append(f"Deal IDs dupliqués: {', '.join(duplicates)}")


def _validate_amounts(deals: List[GenericDeal], report: Dict[str, Any]):
    """Valide les montants"""
    for deal in deals:
        if deal.amount <= 0:
            report['errors'].append(f"Deal {deal.deal_id}: montant invalide ({deal.amount})")
        elif deal.amount > 1_000_000_000:  # 1B limit
            report['warnings'].append(f"Deal {deal.deal_id}: montant très élevé ({deal.amount:,.0f})")


def _validate_dates(deals: List[GenericDeal], report: Dict[str, Any]):
    """Valide la cohérence des dates"""
    for deal in deals:
        if deal.value_date < deal.trade_date:
            report['errors'].append(f"Deal {deal.deal_id}: value_date < trade_date")
        
        if deal.maturity_date < deal.value_date:
            report['errors'].append(f"Deal {deal.deal_id}: maturity_date < value_date")


def _validate_rates(deals: List[GenericDeal], report: Dict[str, Any]):
    """Valide les taux"""
    for deal in deals:
        if deal.client_rate < -0.1 or deal.client_rate > 1.0:  # -10% à 100%
            report['warnings'].append(f"Deal {deal.deal_id}: taux client inhabituel ({deal.client_rate:.2%})")
        
        if deal.ois_equivalent_rate < -0.1 or deal.ois_equivalent_rate > 1.0:
            report['warnings'].append(f"Deal {deal.deal_id}: taux OIS inhabituel ({deal.ois_equivalent_rate:.2%})")