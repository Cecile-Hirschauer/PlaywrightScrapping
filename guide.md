# Guide complet de scraping YouTube avec Playwright

## 1. Introduction

### Qu'est-ce que le scraping web ?

Le scraping web est une technique permettant d'extraire automatiquement des données à partir de sites web. C'est comme si vous naviguiez sur un site, lisiez son contenu et copiiez certaines informations, mais effectué par un programme informatique.

### Qu'est-ce que Playwright ?

Playwright est une bibliothèque d'automatisation de navigateur développée par Microsoft. Elle permet de contrôler programmatiquement Chrome, Firefox ou Safari pour interagir avec des pages web comme le ferait un utilisateur humain.

Contrairement à des outils plus simples comme `requests` ou `BeautifulSoup`, Playwright peut :

- Exécuter du JavaScript
- Interagir avec des éléments dynamiques
- Remplir des formulaires
- Cliquer sur des boutons
- Faire défiler la page
- Attendre que des éléments apparaissent

### Qu'est-ce qu'AgentQL ?

AgentQL est une extension pour Playwright qui simplifie la sélection et l'interaction avec les éléments de la page. Au lieu d'écrire des sélecteurs CSS complexes, AgentQL permet de définir une structure de requête qui sera utilisée pour extraire des éléments de la page.

## 2. Installation et configuration

### Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de packages Python)

### Installation des dépendances

```bash
pip install playwright
pip install agentql
python -m playwright install chromium
```

La dernière commande télécharge et installe les navigateurs nécessaires à Playwright.

## 3. Structure du script

Notre script de scraping YouTube est organisé en fonctions modulaires, chacune responsable d'une tâche spécifique:

1. `scrape_youtube()` - Fonction principale qui coordonne tout le processus
2. `handle_consent_dialogs()` - Gère les fenêtres de consentement de cookies
3. `perform_search()` - Effectue une recherche sur YouTube
4. `click_first_video()` - Clique sur la première vidéo des résultats
5. `interact_with_video_page()` - Interagit avec la page vidéo et récupère la description
6. `capture_comments()` - Charge et capture les commentaires
7. `save_results()` - Enregistre les résultats dans un fichier

## 4. Explication détaillée du code

### Imports et configuration initiale

```python
import logging
import time
import re
from playwright.sync_api import sync_playwright, TimeoutError

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

URL = "https://www.youtube.com/"
SEARCH_TERM = "learn javascript full course"
```

- `logging` permet de générer des messages d'information et d'erreur
- `time` est utilisé pour créer des délais entre les actions
- `re` (regular expressions) aide à nettoyer les données extraites
- `sync_playwright` est l'API synchrone de Playwright
- `TimeoutError` est utilisé pour gérer les erreurs de délai d'attente

### Fonction principale

```python
def scrape_youtube():
    with sync_playwright() as playwright:
        try:
            browser_type = playwright.chromium
            browser = browser_type.launch(
                headless=False,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )

            # Créer un contexte avec des dimensions réalistes
            context = browser.new_context(
                viewport={'width': 1366, 'height': 768},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )

            # Ouvrir une nouvelle page
            page = context.new_page()

            # ... reste du code ...

        except Exception as e:
            log.error(f"Erreur générale: {e}")
            # ... gestion des erreurs ...

        finally:
            # ... nettoyage ...
```

Explication:

- `with sync_playwright() as playwright:` - Initialise Playwright et s'assure qu'il sera correctement fermé
- `browser_type = playwright.chromium` - Sélectionne Chromium comme navigateur
- `browser = browser_type.launch(...)` - Lance le navigateur avec des options spécifiques:
  - `headless=False` - Affiche le navigateur (pratique pour déboguer)
  - `args=[...]` - Arguments supplémentaires pour le navigateur
- `context = browser.new_context(...)` - Crée un contexte de navigation (comme une session)
  - `viewport` - Définit la taille de la fenêtre
  - `user_agent` - Définit un user-agent réaliste pour éviter la détection de bot
- `page = context.new_page()` - Ouvre un nouvel onglet
- Les blocs `try/except/finally` permettent de gérer les erreurs et d'assurer le nettoyage

### Navigation et recherche

```python
# Accéder à YouTube
log.info("Accès à YouTube...")
page.goto(URL, wait_until="domcontentloaded")

# Attendre que la page soit réellement prête
page.wait_for_selector('input#search, input[name="search_query"]', state="visible", timeout=10000)
log.info("Page YouTube chargée")

# Gérer les boîtes de dialogue de consentement
handle_consent_dialogs(page)

# Recherche
perform_search(page, SEARCH_TERM)
```

Explication:

- `page.goto(URL, wait_until="domcontentloaded")` - Navigue vers YouTube et attend que le DOM soit chargé
- `page.wait_for_selector(...)` - Attend qu'un élément spécifique soit visible, ce qui indique que la page est prête
- `handle_consent_dialogs(page)` - Vérifie et gère les fenêtres de consentement de cookies
- `perform_search(page, SEARCH_TERM)` - Effectue la recherche sur YouTube

### Gestion des consentements

```python
def handle_consent_dialogs(page):
    """Gère les différentes boîtes de dialogue de consentement qui peuvent apparaître"""
    try:
        # Plusieurs variantes de boutons de consentement
        consent_buttons = [
            "button:has-text('Accepter tout')",
            "button:has-text(\"J'accepte\")",
            # ... autres boutons ...
        ]

        for button in consent_buttons:
```
