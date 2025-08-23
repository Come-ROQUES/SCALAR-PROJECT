
# SCALAR - Advanced Treasury Dashboard

## Version 2.2 

**Dernières améliorations (Août 2025):**
- **Architecture simplifiée** : Nettoyage des dépendances (-75% de complexité)
- **CI/CD optimisé** : Pipeline simplifié (390 → 50 lignes)
- **Performance** : Code plus focalisé et maintenable

---

## Vue d'Ensemble

**Nom du Projet** : SCALAR
**Type** : Application Streamlit modulaire pour gestion de portefeuille treasury  
**Version Actuelle** : 2.2   
**Dernière MAJ** : 2025-08-23  
**Développeur Principal** : Côme ROQUES  

### Objectif
Application web moderne pour l'analyse de PnL, gestion des risques et monitoring temps réel de portefeuilles de trading treasury avec import Excel générique, visualisations avancées et système de cache intelligent pour performances optimales.

---

## Architecture Technique Complète

### Structure des Dossiers (Nettoyée V2.2)
```
SCALAR-PROJECT/
├── src/
│   ├── treasury/                    # Core business logic
│   │   ├── config.py               # Configuration & UI theming
│   │   ├── session.py              # State management  
│   │   ├── models.py               # Data models & validation
│   │   ├── cache.py                # Intelligent caching system
│   │   ├── pnl.py                  # P&L calculations
│   │   ├── market.py               # Market data providers
│   │   ├── risk.py                 # Risk analytics & VaR
│   │   ├── analytics.py            # Performance analytics
│   │   ├── visuals.py              # Chart generation
│   │   ├── logging_config.py       # Logging configuration
│   │   ├── assets.py               # Asset management
│   │   ├── cache/
│   │   │   └── redis_cache.py      # Redis integration
│   │   ├── monitoring/
│   │   │   └── alerts.py           # Risk monitoring
│   │   ├── utils/
│   │   │   └── dates.py            # Date utilities
│   │   └── io/
│   │       └── excel.py            # Excel import/export
│   │
│   └── ui/                         # User interface
│       ├── app.py                  # Main application
│       └── components/
│           ├── sidebar.py          # Sidebar controls
│           ├── footer.py           # Status footer
│           └── tabs/
│               ├── import_tab.py   # Data import
│               ├── pnl_tab.py      # P&L analysis
│               ├── visuals_tab.py  # 3D visualizations
│               ├── performance_tab.py # Performance tracking
│               ├── var_tab.py      # VaR calculations
│               └── risk_tab.py     # Risk management
│
├── tests/                          # Unit tests
├── static/                         # Static assets
├── .github/workflows/              # CI/CD pipeline
├── requirements.txt                # Core dependencies
└── README.md                       # Documentation
```

## Installation & Lancement

### Prérequis
- Python 3.11+ 
- Git

### Installation Rapide
```bash
# 1. Cloner le repository
git clone https://github.com/Come-ROQUES/SCALAR-PROJECT.git
cd SCALAR-PROJECT

# 2. Installer les dépendances (core seulement)
pip install -r requirements.txt

# 3. Lancer l'application
cd src && streamlit run ui/app.py
```

### Alternative avec environnement virtuel
```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer et lancer
pip install -r requirements.txt
cd src && streamlit run ui/app.py
```

L'application sera accessible sur `http://localhost:8501`

---
│               ├── var_tab.py      
│               ├── performance_tab.py
│               └── risk_tab.py     
│
├── tests/                         
│   ├── __init__.py
│   ├── conftest.py                 
│   ├── test_models.py              
│   ├── test_pnl.py                 
│   ├── test_risk.py               
│   └── test_cache.py               
│
├── pytest.ini                     
├── PROJECT_CONTEXT.md             
└── run_app.py                      
```

### Points d'Entrée
```bash
# Méthode recommandée (depuis SCALAR-PROJECT/)
cd src && streamlit run ui/app.py

# Alternative avec PYTHONPATH
export PYTHONPATH=$PWD/src && streamlit run src/ui/app.py

<<<<<<< HEAD
# Vérification : depuis SCALAR-PROJECT/
pwd  # doit être: /Users/comeroques/Projects/IDOITFORFUN/SCALAR-PROJECT
```

=======
>>>>>>> 225442aa6c2a64264d68e5cb82a1dfb835ec1971
---

## NOUVEAUTÉ V2.1 : Système de Cache Intelligent

### Architecture Cache
```python
# Nouveau module: src/treasury/cache.py
├── CacheManager                    # Gestionnaire stats & monitoring
├── compute_pnl_with_cache()       # Wrapper cache PnL principal
├── compute_enhanced_pnl_vectorized_cached()  # Version cachée Streamlit
├── serialize_deals_for_cache()    # Sérialisation optimisée
├── get_cache_status()             # Monitoring cache
└── test_cache_performance()       # Tests performance
```

### Performances Obtenues
- **PnL Calculs** : 2-10x plus rapide avec cache
- **Cache Hit Rate** : 80%+ typique
- **Temps économisé** : Plusieurs secondes par session
- **Memory footprint** : Optimisé JSON serialization

### Utilisation Cache
```python
# AVANT (sans cache)
df_pnl = compute_enhanced_pnl_vectorized(deals, config)

# APRÈS (avec cache automatique)
from treasury.cache import compute_pnl_with_cache
df_pnl = compute_pnl_with_cache(deals, config)
```

---

## Design System & UI

### Thème Viridis Moderne (Inchangé)
```python
VIRIDIS_COLORS = {
    'primary': '#440154',      # Violet foncé
    'secondary': '#31688e',    # Bleu-vert foncé  
    'accent': '#35b779',       # Vert
    'light': '#fde725',        # Jaune-vert clair
    'dark': '#0d1421',         # Presque noir
    'surface': '#1a1d29',      # Gris très foncé
    'text_primary': '#ffffff', # Blanc
    'success': '#35b779',
    'warning': '#fde725', 
    'error': '#ff6b6b'
}
```

### Sidebar Enrichie V2.1
```
Status Portfolio
├── Badges des deals par type
Configuration PnL  
├── Paramètres de calcul
Cache & Performance (NOUVEAU)
├── Cache Hit Rate: XX%
├── Temps économisé: X.Xs
├── Actions Cache (Vider/Stats)
Monitoring
├── STATUS-Utilisation: XX%
├── STATUS-Échéances ≤7j: X
├── STATUS-Concentration: XX%
├── STATUS-Score Risque: XX/100
Mode Debug
├── Logs récents
└── Stats cache détaillées
```

---

## Fonctionnalités Métier (Mises à Jour)

### 1. **Import de Données** (`import_tab.py`) 
- **Template Excel** intégré en haut de page
- **Validation avancée** avec gestion erreurs robuste
- **Nettoyage automatique** des fichiers
- **Génération d'IDs** manquants
- **Interface modernisée** avec expandeur format

### 2. **Calculs PnL** (`pnl_tab.py`) **+ Cache**
- **Cache intelligent** : Calculs 2-10x plus rapides
- **4 composantes** : Accrued, MTM, Rate, Liquidity PnL
- **Configuration modulaire** via sidebar
- **Stress tests** rapides (+50bp)
- **Graphiques interactifs** : Breakdown + Waterfall
- **Feedback performance** temps réel en mode debug

**Performance PnL V2.1 :**
```
Premier calcul : ~2-5s (cache miss)
Calculs suivants : ~0.1-0.5s (cache hit)  
Amélioration : 5-20x plus rapide
```

### 3. **Gestion des Risques** (`risk_tab.py`) 
- **Configuration limites** : Notionnel/Paire, Concentration, VaR
- **Détection violations** automatique
- **5 scénarios prédéfinis** :
  1. Crise Systémique : FX -15%, Taux +200bp, Crédit +200bp
  2. Resserrement Fed : FX -5%, Taux +150bp, Crédit +50bp
  3. Crise Émergente : FX -8%, Taux +50bp, Crédit +150bp
  4. Volatilité Extrême : FX -12%, Taux +100bp, Crédit +100bp
  5. Carry Trade Unwind : FX -6%, Taux -100bp, Crédit +50bp

### 4. **Monitoring Temps Réel** (`sidebar.py`) **+ Cache Stats**
- **4 indicateurs risque** toujours visibles
- **Monitoring cache** avec hit rate et temps économisé
- **Actions cache** : Vider, Stats détaillées
- **Mode debug** intégré avec logs

---

## Infrastructure de Tests (NOUVELLE)

### Tests Opérationnels
```bash
# Tests Risk Management (8/8 )
pytest tests/test_risk.py -v

# Tests Cache Performance  
pytest tests/test_cache.py -v

# Tous les tests
pytest tests/ -v

# Tests sans les lents
pytest tests/ -m "not slow" -v
```

### Couverture Tests V2.1
- **test_risk.py** : 8 tests (concentration, Monte Carlo, limites)
- **test_models.py** : Validation Pydantic, imports Treasury
- **test_pnl.py** : Calculs PnL basiques
- **test_cache.py** : Performance cache, sérialisation
- **pytest.ini** : Configuration markers (slow, integration, unit)

### Résultats Tests Actuels
```
======================== 8 passed, 0 failed ========================
Cache améliore vitesse de 5.2x
Risk imports OK
Concentration max: 83.3%
Impact FX: -3.0M, Rate: +2.1M, Credit: +0.1M
```

---

## Configuration Technique V2.1

### Session State Structure (Mise à Jour)
```python
st.session_state = {
    'generic_deals': List[GenericDeal],           # Deals importés
    'df_pnl_enhanced': pd.DataFrame,              # Résultats PnL
    'pnl_config': {                               # Config calculs
        'calculate_accrued': True,
        'calculate_mtm': True, 
        'calculate_rate': True,
        'calculate_liquidity': True,
        'ois_rate_override': None
    },
    'risk_limits': {                              # Limites de risque
        'max_notional_per_pair': 100_000_000,
        'max_tenor_concentration': 0.3,
        'var_limit': 5_000_000,
        'max_deals_per_trader': 50
    },
    'debug_mode': False,                          # NOUVEAU - Mode debug
    'cache_*': {},                                # NOUVEAU - Données cache
    'ui_theme': 'viridis_modern'
}
```

### Cache Configuration
```python
# Cache TTL (Time To Live)
├── PnL Calculations: 1 heure (3600s)
├── Market Data: 15 minutes (900s)  
├── Risk Analysis: 30 minutes (1800s)
└── Portfolio Analytics: 30 minutes (1800s)

# Cache Strategies
├── Streamlit @st.cache_data: Calculs lourds
├── Session State: Cache léger temporaire
└── Custom CacheManager: Stats & monitoring
```

---

## Issues Résolues V2.1

### Problèmes Pytest 
```bash
# ERROR ERREUR: pytest.mark.slow unknown marker
# SOLUTION: pytest.ini avec markers configuration

[tool:pytest]
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Performance Plotly 
```python
# ERROR ERREUR: sizemax property invalid
# SOLUTION: Manual size normalization
abs_values = np.abs(values)
max_val = abs_values.max() if abs_values.max() > 0 else 1
sizes = 5 + (abs_values / max_val) * 35  # Entre 5-40px
```

### Imports Relatifs 
```python
# ERROR ERREUR: attempted relative import with no known parent package
# SOLUTION: Absolute imports + path management
from ui.components.sidebar import render_sidebar  # Not: from .components
```

### Cache Performance 
```python
# ERROR PROBLÈME: Calculs PnL lents (2-5s)
# SOLUTION: Cache intelligent avec JSON serialization
# Résultat: 5-20x amélioration performance
```

---

## Workflow Utilisateur V2.1

### 1. **Import & Setup**
```
Onglet Import → Template Download → Remplir Excel → Upload → Validation
```

### 2. **Calcul PnL Optimisé** 
```
Sidebar Config → Onglet PnL → Recalculer → Cache Hit → Résultats Instantanés
```

### 3. **Monitoring Continu**
```
Sidebar Cache: Hit Rate 85% → Monitoring: Score Risque 25/100 → Alertes: OK
```

### 4. **Analyse & Tests**
```
Performance → VaR → Risk → Stress Tests → Scénarios → Impact Visualization
```

---

## Roadmap V2.2+ (Prochaines Phases)

### Phase 1.3 - Tests & Validation (En Cours)
- [ ] **Tests d'intégration UI** : Streamlit components
- [ ] **Validation données** renforcée edge cases
- [ ] **Performance monitoring** avancé

### Phase 2 - Fonctionnalités Métier
- [ ] **Bloomberg/Reuters API** intégration
- [ ] **Modèles pricing** avancés (day-count, calendriers)
- [ ] **Attribution PnL** décomposée (carry, roll, vol)

### Phase 3 - Infrastructure Scaling  
- [ ] **PostgreSQL** persistance données
- [ ] **FastAPI** backend séparé
- [ ] **Docker** containerisation

### Phase 4 - UX/AI Avancé
- [ ] **Machine Learning** prédiction risques
- [ ] **PDF Reports** automatisés
- [ ] **Mobile responsiveness**

---

## Améliorations Performance V2.1

### Cache Hit Rates Observés
```
Typical Performance:
├── Cache Hit Rate: 80-95%
├── PnL Calculation: 5-20x faster
├── UI Responsiveness: Immediate (<0.5s)
└── Memory Usage: +15% (acceptable trade-off)
```

### Optimisations Techniques
- **JSON Serialization** pour cache Streamlit
- **Lazy loading** imports lourds
- **Date conversion** optimisée
- **Error handling** robuste avec fallbacks

---

## Points Critiques pour Développeurs

### 1. **Utilisation Cache (IMPORTANT)**
```python
# ERROR NE PAS FAIRE:
df_pnl = compute_enhanced_pnl_vectorized(deals, config)

# TOUJOURS FAIRE:
from treasury.cache import compute_pnl_with_cache
df_pnl = compute_pnl_with_cache(deals, config)
```

### 2. **Mode Debug**
```python
# Activer mode debug pour monitoring cache
st.session_state.debug_mode = True
# Sidebar affichera temps d'exécution + cache status
```

### 3. **Tests Avant Deploy**
```bash
# Vérification complète avant déploiement
pytest tests/ -v                    # Tous les tests
pytest tests/test_cache.py -v       # Cache spécifiquement  
pytest tests/test_risk.py -v        # Risk management
```

---

## Debug & Troubleshooting V2.1

### Problèmes Cache
```bash
# Cache ne fonctionne pas
→ Vérifier imports: from treasury.cache import compute_pnl_with_cache
→ Mode debug activé: Sidebar montre cache status
→ Clear cache: Bouton "Vider Cache" dans sidebar

# Performance dégradée
→ Cache hit rate < 50%: Vérifier données consistent
→ Memory issues: Clear cache régulièrement
→ Serialization errors: Vérifier structure deals
```

### Tests Echec
```bash
# pytest tests failed
→ cd SCALAR-PROJECT (vérifier position)
→ PYTHONPATH=$PWD/src (si nécessaire)
→ pytest tests/test_simple.py -v (test minimal)
```

### UI Issues
```bash
# Sidebar cache vide
→ Aucun calcul PnL effectué yet
→ Importer deals + calculer PnL une fois
→ Cache stats apparaîtront après

# Performance monitoring
→ Mode debug ON dans sidebar
→ Temps calcul affiché
→ Cache hit/miss visible
```

---

## Informations Projet V2.1

**Développeur** : Côme ROQUES  
**Projet** : SCALAR-PROJECT  
**Path** : `/Users/comeroques/Projects/IDOITFORFUN/SCALAR-PROJECT`  
**Version** : Treasury Dashboard v2.1 - Cache Intelligent  
**Status** : Production Ready avec Tests  

### Dépendances V2.1
```
streamlit >= 1.28.0
pandas >= 2.0.0  
plotly >= 5.15.0
pydantic >= 2.0.0
numpy >= 1.24.0
openpyxl >= 3.1.0
pytest >= 7.0.0          # NOUVEAU
pytest-cov >= 4.0.0      # NOUVEAU
```

### Performance Benchmarks
```
Environment: MacBook Pro M1
Typical Dataset: 50-200 deals
Cache Performance:
  ├── First calculation: 2.1s
  ├── Cached calculation: 0.2s  
  ├── Improvement: 10.5x
  └── Hit rate: 87%
```
---


<<<<<<< HEAD
**Dernière mise à jour** : 2025-08-17 - Cache intelligent intégré, tests opérationnels, performance optimisée
=======
**Dernière mise à jour** : 2025-08-17 - Cache intelligent intégré, tests opérationnels, performance optimisée
>>>>>>> 225442aa6c2a64264d68e5cb82a1dfb835ec1971
