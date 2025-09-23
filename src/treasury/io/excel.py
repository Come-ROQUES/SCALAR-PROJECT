\
\
\
\

import io
import pandas as pd
from typing import Tuple, List, Dict, Any, Union, Optional
from datetime import datetime

from ..config import settings, ALLOWED_EXTENSIONS
from ..models import GenericDeal
from ..utils.dates import to_naive_ts
from ..logging_config import logger, log_data_quality


def validate_file_security(file) -> None:
\
\
\
\
\
\
\
\
\

    if file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"Fichier trop volumineux (max {settings.MAX_FILE_SIZE_MB}MB)")


    if not any(file.name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise ValueError(f"Extension non autorisée. Autorisées: {ALLOWED_EXTENSIONS}")

    logger.info(f"Fichier validé: {file.name} ({file.size:,} bytes)")



@pd.api.extensions.register_dataframe_accessor("_treas")
class _TreasuryAccessor:
\

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def to_excel_bytes(self, sheet_name: str = "DEALS") -> bytes:
        \
\
\
\
\
\
\
\
\
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            self._obj.to_excel(writer, sheet_name=sheet_name, index=False)
        return output.getvalue()


def build_template_generic() -> bytes:
    \
\
\
\
\
\
    try:

        sample_data = {
            'comment': [
                'EUR/USD FX Swap Q4', 'USD IRS 3Y Fixed', 'GBP Deposit 6M', 'CHF Loan 1Y',
                'JPY/USD FX Forward', 'EUR IRS 5Y Receiver', 'CAD Deposit 3M', 'AUD Loan 2Y',
                'USD/CHF FX Swap H1', 'GBP IRS 2Y Payer', 'EUR Deposit 1Y', 'USD Loan 6M',
                'GBP/USD FX Forward', 'CHF IRS 7Y Fixed', 'JPY Deposit 9M', 'CAD Loan 18M',
                'EUR/GBP Cross Currency', 'AUD IRS 4Y Receiver', 'USD Deposit 2M', 'SEK Loan 3Y'
            ],
            'product': [
                'FX_SWAP', 'IRS', 'DEPOSIT', 'LOAN',
                'FX_SWAP', 'IRS', 'DEPOSIT', 'LOAN',
                'FX_SWAP', 'IRS', 'DEPOSIT', 'LOAN',
                'FX_SWAP', 'IRS', 'DEPOSIT', 'LOAN',
                'FX_SWAP', 'IRS', 'DEPOSIT', 'LOAN'
            ],
            'deal_id': [
                'FXS001', 'IRS001', 'DEP001', 'LOA001',
                'FXS002', 'IRS002', 'DEP002', 'LOA002',
                'FXS003', 'IRS003', 'DEP003', 'LOA003',
                'FXS004', 'IRS004', 'DEP004', 'LOA004',
                'FXS005', 'IRS005', 'DEP005', 'LOA005'
            ],
            'd_or_l': [
                'L', 'D', 'D', 'L',
                'L', 'D', 'D', 'L',
                'L', 'D', 'D', 'L',
                'L', 'D', 'D', 'L',
                'L', 'D', 'D', 'L'
            ],
            'pair_currency': [
                'EUR/USD', 'USD', 'GBP', 'CHF',
                'JPY/USD', 'EUR', 'CAD', 'AUD',
                'USD/CHF', 'GBP', 'EUR', 'USD',
                'GBP/USD', 'CHF', 'JPY', 'CAD',
                'EUR/GBP', 'AUD', 'USD', 'SEK'
            ],
            'amount': [
                10_000_000, 50_000_000, 25_000_000, 15_000_000,
                8_000_000, 75_000_000, 30_000_000, 20_000_000,
                12_000_000, 40_000_000, 35_000_000, 18_000_000,
                15_000_000, 60_000_000, 22_000_000, 25_000_000,
                18_000_000, 45_000_000, 28_000_000, 32_000_000
            ],
            'trade_date': [
                '2025-08-01', '2025-08-01', '2025-08-01', '2025-08-01',
                '2025-08-02', '2025-08-02', '2025-08-02', '2025-08-02',
                '2025-08-05', '2025-08-05', '2025-08-05', '2025-08-05',
                '2025-08-06', '2025-08-06', '2025-08-06', '2025-08-06',
                '2025-08-07', '2025-08-07', '2025-08-07', '2025-08-07'
            ],
            'value_date': [
                '2025-08-03', '2025-08-03', '2025-08-03', '2025-08-03',
                '2025-08-04', '2025-08-04', '2025-08-04', '2025-08-04',
                '2025-08-07', '2025-08-07', '2025-08-07', '2025-08-07',
                '2025-08-08', '2025-08-08', '2025-08-08', '2025-08-08',
                '2025-08-09', '2025-08-09', '2025-08-09', '2025-08-09'
            ],
            'maturity_date': [
                '2025-12-03', '2028-08-03', '2026-02-03', '2026-08-03',
                '2026-01-04', '2030-08-04', '2025-11-04', '2027-08-04',
                '2026-02-07', '2027-08-07', '2026-08-07', '2026-02-07',
                '2026-03-08', '2032-08-08', '2026-05-08', '2027-02-08',
                '2026-04-09', '2029-08-09', '2025-10-09', '2028-08-09'
            ],
            'client_rate': [
                0.0450, 0.0425, 0.0380, 0.0400,
                0.0465, 0.0410, 0.0355, 0.0415,
                0.0475, 0.0435, 0.0385, 0.0405,
                0.0455, 0.0420, 0.0370, 0.0410,
                0.0480, 0.0440, 0.0375, 0.0425
            ],
            'ois_equivalent_rate': [
                0.0440, 0.0420, 0.0375, 0.0395,
                0.0460, 0.0405, 0.0350, 0.0410,
                0.0470, 0.0430, 0.0380, 0.0400,
                0.0450, 0.0415, 0.0365, 0.0405,
                0.0475, 0.0435, 0.0370, 0.0420
            ],
            'trader_id': [
                'TRD001', 'TRD002', 'TRD001', 'TRD003',
                'TRD004', 'TRD002', 'TRD005', 'TRD003',
                'TRD001', 'TRD006', 'TRD002', 'TRD004',
                'TRD007', 'TRD003', 'TRD008', 'TRD005',
                'TRD009', 'TRD001', 'TRD010', 'TRD006'
            ]
        }

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

            df_sample = pd.DataFrame(sample_data)
            df_sample.to_excel(writer, sheet_name="DEALS", index=False)


            documentation = pd.DataFrame({
                "Colonne": list(sample_data.keys()),
                "Type": [
                    "Text", "Enum", "Text", "Enum", "Text", "Number",
                    "Date", "Date", "Date", "Decimal", "Decimal", "Text"
                ],
                "Description": [
                    "Nom/description du deal",
                    "FX_SWAP, IRS, DEPOSIT, LOAN",
                    "ID unique du deal",
                    "D (Deposit) ou L (Loan)",
                    "Paire devises (EUR/USD) ou devise unique (USD)",
                    "Montant en devise de base",
                    "Date de négociation (YYYY-MM-DD)",
                    "Date de valeur (YYYY-MM-DD)",
                    "Date de maturité (YYYY-MM-DD)",
                    "Taux client (décimal, ex: 0.045 = 4.5%)",
                    "Taux OIS équivalent (décimal)",
                    "ID trader (optionnel)"
                ],
                "Exemple": [
                    'EUR/USD FX Swap', 'FX_SWAP', 'FXS001', 'L', 'EUR/USD', '10000000',
                    '2025-08-01', '2025-08-03', '2025-12-03', '0.045', '0.044', 'TRD001'
                ],
                "Obligatoire": [
                    'Oui', 'Oui', 'Oui', 'Oui', 'Oui', 'Oui',
                    'Oui', 'Oui', 'Oui', 'Oui', 'Oui', 'Non'
                ]
            })

            documentation.to_excel(writer, sheet_name="DOCUMENTATION", index=False)


            validation_data = pd.DataFrame({
                "Products_Valides": ["FX_SWAP", "IRS", "DEPOSIT", "LOAN"],
                "D_or_L_Valides": ["D", "L", "", ""],
                "Devises_Exemples": ["USD", "EUR", "GBP", "JPY"],
                "Paires_Exemples": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF"]
            })

            validation_data.to_excel(writer, sheet_name="VALIDATION", index=False)

        logger.info("Template générique créé avec succès")
        return output.getvalue()

    except Exception as e:
        logger.error(f"Erreur création template: {e}")
        raise


def read_generic_deals_with_validation(file) -> Tuple[List[GenericDeal], List[str]]:
    \
\
\
\
\
\
\
\
\
    warnings_list: List[str] = []
    deals: List[GenericDeal] = []

    try:

        validate_file_security(file)


        xl = pd.ExcelFile(file)
        logger.info(f"Feuilles disponibles: {xl.sheet_names}")


        if "DEALS" not in xl.sheet_names:
            warnings_list.append("Feuille 'DEALS' absente. Feuilles trouvées: " + ", ".join(xl.sheet_names))
            return deals, warnings_list


        df_deals = xl.parse("DEALS")
        logger.info(f"Lecture DEALS: {len(df_deals)} lignes, {len(df_deals.columns)} colonnes")


        if len(df_deals) > settings.MAX_ROWS_PER_SHEET:
            warnings_list.append(f"DEALS tronqué à {settings.MAX_ROWS_PER_SHEET} lignes (total: {len(df_deals)})")
            df_deals = df_deals.head(settings.MAX_ROWS_PER_SHEET)


        required_columns = [
            'comment', 'product', 'deal_id', 'd_or_l', 'pair_currency',
            'amount', 'trade_date', 'value_date', 'maturity_date',
            'client_rate', 'ois_equivalent_rate'
        ]

        missing_columns = [col for col in required_columns if col not in df_deals.columns]
        if missing_columns:
            warnings_list.append(f"Colonnes manquantes: {missing_columns}")


        logger.info(f"Colonnes trouvées: {df_deals.columns.tolist()}")


        df_deals = df_deals.dropna(how='all')

        valid_deals = 0
        invalid_deals = 0


        for idx, row in df_deals.iterrows():
            try:
                row_dict = row.to_dict()


                for date_col in ['trade_date', 'value_date', 'maturity_date']:
                    if date_col in row_dict and pd.notna(row_dict[date_col]):
                        row_dict[date_col] = to_naive_ts(row_dict[date_col])
                    else:
                        raise ValueError(f"Date {date_col} manquante ou invalide")


                if 'trader_id' in row_dict and pd.isna(row_dict['trader_id']):
                    row_dict['trader_id'] = None


                for numeric_col in ['amount', 'client_rate', 'ois_equivalent_rate']:
                    if numeric_col in row_dict:
                        if pd.isna(row_dict[numeric_col]):
                            raise ValueError(f"Valeur manquante pour {numeric_col}")
                        try:
                            row_dict[numeric_col] = float(row_dict[numeric_col])
                        except (ValueError, TypeError):
                            raise ValueError(f"Valeur non numérique pour {numeric_col}: {row_dict[numeric_col]}")


                deal = GenericDeal(**row_dict)
                deals.append(deal)
                valid_deals += 1

            except Exception as e:
                invalid_deals += 1
                error_msg = f"Deal ligne {idx+2}: {str(e)}"
                warnings_list.append(error_msg)
                logger.warning(f"Échec validation deal ligne {idx+2}: {e}")


                if len(warnings_list) > 20:
                    warnings_list.append(f"... et {invalid_deals - 20} autres erreurs")
                    break


        total_rows = len(df_deals)
        log_data_quality("Excel Import", total_rows, valid_deals, invalid_deals)

        if valid_deals == 0:
            warnings_list.append("Aucun deal valide trouvé dans le fichier")

    except Exception as e:
        error_msg = f"Erreur lecture fichier: {str(e)}"
        warnings_list.append(error_msg)
        logger.error(error_msg)

    logger.info(f"Import terminé: {len(deals)} deals validés, {len(warnings_list)} warnings")
    return deals, warnings_list


def export_pnl_to_excel(df_pnl: pd.DataFrame, filename_prefix: str = "pnl_export") -> bytes:
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
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            workbook = writer.book


            money_format = workbook.add_format({'num_format': '#,##0', 'align': 'right'})
            percent_format = workbook.add_format({'num_format': '0.00%', 'align': 'right'})
            date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'align': 'center'})


            df_export = df_pnl.copy()


            pnl_columns = [col for col in df_export.columns if col.endswith('_pnl')]
            for col in pnl_columns:
                if col in df_export.columns:
                    df_export[col] = df_export[col].round(0)

            df_export.to_excel(writer, sheet_name="PnL_Details", index=False)


            worksheet = writer.sheets["PnL_Details"]


            column_widths = {
                'deal_id': 12, 'comment': 25, 'product': 12, 'pair_currency': 12,
                'amount': 15, 'client_rate': 10, 'ois_equivalent_rate': 10,
                'accrued_pnl': 15, 'mtm_pnl': 15, 'rate_pnl': 15,
                'liquidity_pnl': 15, 'total_pnl': 15
            }

            for col_idx, (col_name, width) in enumerate(column_widths.items()):
                if col_name in df_export.columns:
                    worksheet.set_column(col_idx, col_idx, width)


            for col_idx, col_name in enumerate(df_export.columns):
                if col_name in ['amount'] + pnl_columns:
                    worksheet.set_column(col_idx, col_idx, None, money_format)
                elif col_name in ['client_rate', 'ois_equivalent_rate', 'ois_rate_now']:
                    worksheet.set_column(col_idx, col_idx, None, percent_format)
                elif 'date' in col_name.lower():
                    worksheet.set_column(col_idx, col_idx, None, date_format)


            if not df_pnl.empty:
                summary_data = []


                if 'product' in df_pnl.columns:
                    product_summary = df_pnl.groupby('product').agg({
                        'deal_id': 'count',
                        'amount': 'sum',
                        'total_pnl': 'sum'
                    }).round(0)
                    product_summary.columns = ['Nb_Deals', 'Notionnel_Total', 'PnL_Total']
                    product_summary.to_excel(writer, sheet_name="Resume_Produits")


                if 'trader_id' in df_pnl.columns:
                    trader_summary = df_pnl.groupby('trader_id').agg({
                        'deal_id': 'count',
                        'amount': 'sum',
                        'total_pnl': 'sum'
                    }).round(0)
                    trader_summary.columns = ['Nb_Deals', 'Notionnel_Total', 'PnL_Total']
                    trader_summary.to_excel(writer, sheet_name="Resume_Traders")


                global_metrics = {
                    'Metric': ['Total_Deals', 'Total_Notionnel', 'PnL_Total', 'PnL_Moyen_Deal'],
                    'Value': [
                        len(df_pnl),
                        df_pnl['amount'].sum() if 'amount' in df_pnl.columns else 0,
                        df_pnl['total_pnl'].sum() if 'total_pnl' in df_pnl.columns else 0,
                        df_pnl['total_pnl'].mean() if 'total_pnl' in df_pnl.columns else 0
                    ]
                }

                pd.DataFrame(global_metrics).to_excel(writer, sheet_name="Metriques_Globales", index=False)

        logger.info(f"Export Excel PnL créé: {len(df_pnl)} lignes")
        return output.getvalue()

    except Exception as e:
        logger.error(f"Erreur export Excel PnL: {e}")
        raise


def validate_excel_structure(file) -> Dict[str, any]:
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
        'warnings': [],
        'sheet_info': {},
        'column_info': {}
    }

    try:
        validate_file_security(file)

        xl = pd.ExcelFile(file)
        validation['sheet_info'] = {
            'sheet_names': xl.sheet_names,
            'sheet_count': len(xl.sheet_names)
        }


        if "DEALS" not in xl.sheet_names:
            validation['errors'].append("Feuille 'DEALS' requise manquante")
            validation['is_valid'] = False
        else:

            df_header = xl.parse("DEALS", nrows=0)
            columns = df_header.columns.tolist()

            validation['column_info'] = {
                'found_columns': columns,
                'column_count': len(columns)
            }


            required_columns = [
                'comment', 'product', 'deal_id', 'd_or_l', 'pair_currency',
                'amount', 'trade_date', 'value_date', 'maturity_date',
                'client_rate', 'ois_equivalent_rate'
            ]

            missing_columns = [col for col in required_columns if col not in columns]
            extra_columns = [col for col in columns if col not in required_columns + ['trader_id']]

            if missing_columns:
                validation['errors'].append(f"Colonnes requises manquantes: {missing_columns}")
                validation['is_valid'] = False

            if extra_columns:
                validation['warnings'].append(f"Colonnes non reconnues (ignorées): {extra_columns}")


            try:
                df_count = xl.parse("DEALS")
                row_count = len(df_count)
                validation['column_info']['row_count'] = row_count

                if row_count > settings.MAX_ROWS_PER_SHEET:
                    validation['warnings'].append(f"Fichier volumineux: {row_count} lignes "
                                                f"(max {settings.MAX_ROWS_PER_SHEET})")

                if row_count == 0:
                    validation['errors'].append("Feuille DEALS vide")
                    validation['is_valid'] = False

            except Exception as e:
                validation['warnings'].append(f"Impossible de compter les lignes: {e}")

        logger.info(f"Validation structure Excel: {validation['is_valid']}")

    except Exception as e:
        validation['errors'].append(f"Erreur validation structure: {e}")
        validation['is_valid'] = False
        logger.error(f"Erreur validation Excel: {e}")

    return validation


def read_excel_preview(file, max_rows: int = 10) -> pd.DataFrame:
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
        validate_file_security(file)
        xl = pd.ExcelFile(file)

        if "DEALS" in xl.sheet_names:
            df_preview = xl.parse("DEALS", nrows=max_rows)
            logger.info(f"Preview Excel: {len(df_preview)} lignes, {len(df_preview.columns)} colonnes")
            return df_preview
        else:
            logger.warning("Feuille DEALS non trouvée pour preview")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Erreur preview Excel: {e}")
        return pd.DataFrame()


def clean_excel_data(df: pd.DataFrame) -> pd.DataFrame:
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
        df_clean = df.copy()


        df_clean = df_clean.dropna(how='all')


        string_columns = ['comment', 'deal_id', 'pair_currency', 'trader_id']
        for col in string_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()

                df_clean[col] = df_clean[col].replace('nan', pd.NA)


        enum_columns = ['product', 'd_or_l']
        for col in enum_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip().str.upper()


        if 'amount' in df_clean.columns:
            df_clean = df_clean[df_clean['amount'] > 0]


        rate_columns = ['client_rate', 'ois_equivalent_rate']
        for col in rate_columns:
            if col in df_clean.columns:

                mask = df_clean[col] > 1
                df_clean.loc[mask, col] = df_clean.loc[mask, col] / 100


                df_clean = df_clean[(df_clean[col] >= 0) & (df_clean[col] <= 1)]

        logger.info(f"Nettoyage Excel: {len(df)} -> {len(df_clean)} lignes")
        return df_clean

    except Exception as e:
        logger.error(f"Erreur nettoyage Excel: {e}")
        return df


def generate_deal_id_if_missing(df: pd.DataFrame) -> pd.DataFrame:
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
        df_result = df.copy()

        if 'deal_id' in df_result.columns:

            missing_mask = df_result['deal_id'].isna() | (df_result['deal_id'] == '')
            missing_count = missing_mask.sum()

            if missing_count > 0:
                logger.warning(f"Génération automatique de {missing_count} deal_id manquants")


                timestamp = datetime.now().strftime('%Y%m%d')

                for idx, is_missing in enumerate(missing_mask):
                    if is_missing:
                        auto_id = f"AUTO_{timestamp}_{idx+1:03d}"
                        df_result.loc[missing_mask.index[idx], 'deal_id'] = auto_id

        return df_result

    except Exception as e:
        logger.error(f"Erreur génération deal_id: {e}")
        return df


def export_validation_report(validation_results: List[str],
                           success_count: int,
                           error_count: int) -> bytes:
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
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

            summary_data = {
                'Métrique': ['Deals valides', 'Erreurs', 'Taux de succès'],
                'Valeur': [success_count, error_count,
                          f"{success_count/(success_count+error_count)*100:.1f}%" if (success_count+error_count) > 0 else "0%"]
            }

            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Résumé", index=False)


            if validation_results:
                errors_df = pd.DataFrame({
                    'Ligne': range(1, len(validation_results) + 1),
                    'Message': validation_results
                })
                errors_df.to_excel(writer, sheet_name="Détail_Erreurs", index=False)

        logger.info(f"Rapport validation généré: {success_count} succès, {error_count} erreurs")
        return output.getvalue()

    except Exception as e:
        logger.error(f"Erreur génération rapport: {e}")
        raise


class ExcelProcessor:
\
\
\

    def __init__(self):
        self.logger = logger

    def process_file(self, file, auto_clean: bool = True,
                    auto_generate_ids: bool = True) -> Tuple[List[GenericDeal], List[str], Dict]:
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
        metadata = {
            'processed_at': datetime.now(),
            'filename': file.name,
            'filesize': file.size,
            'auto_clean': auto_clean,
            'auto_generate_ids': auto_generate_ids
        }

        try:

            structure_validation = validate_excel_structure(file)
            if not structure_validation['is_valid']:
                return [], structure_validation['errors'], metadata


            xl = pd.ExcelFile(file)
            df = xl.parse("DEALS")

            metadata['original_rows'] = len(df)
            metadata['original_columns'] = len(df.columns)


            if auto_clean:
                df = clean_excel_data(df)
                metadata['cleaned_rows'] = len(df)


            if auto_generate_ids:
                df = generate_deal_id_if_missing(df)


            if len(df) > settings.MAX_ROWS_PER_SHEET:
                df = df.head(settings.MAX_ROWS_PER_SHEET)
                metadata['truncated_to'] = settings.MAX_ROWS_PER_SHEET


            deals = []
            warnings = []

            for idx, row in df.iterrows():
                try:
                    row_dict = row.to_dict()


                    for date_col in ['trade_date', 'value_date', 'maturity_date']:
                        if date_col in row_dict:
                            row_dict[date_col] = to_naive_ts(row_dict[date_col])


                    if 'trader_id' in row_dict and pd.isna(row_dict['trader_id']):
                        row_dict['trader_id'] = None

                    deal = GenericDeal(**row_dict)
                    deals.append(deal)

                except Exception as e:
                    warnings.append(f"Ligne {idx+2}: {str(e)}")

            metadata['valid_deals'] = len(deals)
            metadata['invalid_deals'] = len(warnings)

            self.logger.info(f"Traitement Excel terminé: {len(deals)} deals valides")

            return deals, warnings, metadata

        except Exception as e:
            error_msg = f"Erreur traitement Excel: {e}"
            self.logger.error(error_msg)
            return [], [error_msg], metadata