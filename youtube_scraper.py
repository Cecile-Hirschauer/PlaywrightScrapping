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
            
            # Activer les journaux de la console du navigateur pour le débogage (optionnel)
            context.on("console", lambda msg: log.debug(f"CONSOLE: {msg.text}"))
            
            # Ouvrir une nouvelle page
            page = context.new_page()
            
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
            
            # Attendre les résultats et cliquer sur la première vidéo
            click_first_video(page)
            
            # Interagir avec la page vidéo
            description = interact_with_video_page(page)
            
            # Capturer les commentaires
            comments = capture_comments(page)
            
            # Enregistrer les résultats dans un fichier texte
            save_results(description, comments)
            
            # Pause pour montrer le résultat
            log.info("Script terminé avec succès")
            page.wait_for_timeout(5000)
            
            # Fermeture propre du navigateur
            context.close()
            browser.close()
            
        except Exception as e:
            log.error(f"Erreur générale: {e}")
            
            # Capture d'écran en cas d'erreur pour déboguer
            try:
                if 'page' in locals():
                    page.screenshot(path="error_screenshot.png")
                    log.info("Capture d'écran d'erreur enregistrée dans 'error_screenshot.png'")
            except Exception as screenshot_error:
                log.error(f"Erreur lors de la capture d'écran: {screenshot_error}")
        finally:
            try:
                if 'context' in locals():
                    context.close()
                if 'browser' in locals():
                    browser.close()
            except Exception as close_error:
                log.error(f"Erreur lors de la fermeture du navigateur: {close_error}")

def handle_consent_dialogs(page):
    """Gère les différentes boîtes de dialogue de consentement qui peuvent apparaître"""
    try:
        # Plusieurs variantes de boutons de consentement (avec échappement approprié des apostrophes)
        consent_buttons = [
            "button:has-text('Accepter tout')",
            "button:has-text(\"J'accepte\")",  # Utilisation de guillemets doubles à l'extérieur
            "button:has-text('Agree')",
            "button:has-text('Accept')",
            "button:has-text('Accept all')",
            "button:has-text('I agree')",
            "[aria-label='Accept all']",
            "[aria-label='Accepter tout']"
        ]
        
        for button in consent_buttons:
            try:
                if page.is_visible(button, timeout=1000):
                    log.info(f"Bouton de consentement trouvé: {button}")
                    page.click(button)
                    page.wait_for_timeout(1000)
                    return True
            except Exception as button_error:
                continue
                
        log.info("Aucune boîte de dialogue de consentement détectée")
        return False
        
    except Exception as e:
        log.warning(f"Erreur lors de la gestion des dialogues de consentement: {e}")
        return False

def perform_search(page, search_term):
    """Effectue une recherche sur YouTube"""
    try:
        log.info(f"Recherche de: '{search_term}'")
        
        # Trouver le champ de recherche (plusieurs variantes possibles)
        search_selectors = ["input#search", "input[name='search_query']", "[placeholder='Rechercher']"]
        
        search_input = None
        for selector in search_selectors:
            if page.is_visible(selector, timeout=1000):
                search_input = selector
                break
                
        if not search_input:
            raise Exception("Champ de recherche introuvable")
            
        # Cliquer d'abord sur le champ de recherche pour être sûr qu'il a le focus
        page.click(search_input)
        page.wait_for_timeout(500)
        
        # Effacer le champ et saisir le terme de recherche
        page.fill(search_input, "")
        page.type(search_input, search_term, delay=100)
        page.wait_for_timeout(500)
        
        # Presser Entrée au lieu de chercher le bouton de recherche
        page.press(search_input, "Enter")
        
        # Attendre que la page de résultats se charge
        log.info("Attente des résultats de recherche...")
        page.wait_for_load_state("networkidle", timeout=10000)
        page.wait_for_selector("ytd-video-renderer, ytd-compact-video-renderer", timeout=10000)
        log.info("Résultats de recherche chargés")
        
    except Exception as e:
        log.error(f"Erreur lors de la recherche: {e}")
        raise e

def click_first_video(page):
    """Clique sur la première vidéo des résultats de recherche"""
    try:
        log.info("Recherche de vidéos dans les résultats...")
        
        # Attendre que les résultats soient réellement chargés
        page.wait_for_timeout(2000)
        
        # Plusieurs sélecteurs possibles pour les titres de vidéos
        video_selectors = [
            "ytd-video-renderer h3 a#video-title",
            "ytd-video-renderer h3 a",
            "#contents ytd-video-renderer a#video-title"
        ]
        
        video_found = False
        for selector in video_selectors:
            if page.is_visible(selector, timeout=1000):
                # Obtenir le texte du titre pour le log
                title_element = page.query_selector(selector)
                title_text = title_element.text_content().strip() if title_element else "Titre inconnu"
                log.info(f"Première vidéo trouvée: {title_text}")
                
                # Cliquer sur la vidéo
                page.click(selector)
                video_found = True
                break
                
        if not video_found:
            raise Exception("Aucune vidéo trouvée dans les résultats")
        
        # Attendre que la page vidéo se charge
        log.info("Attente du chargement de la page vidéo...")
        page.wait_for_load_state("networkidle", timeout=15000)
        page.wait_for_selector("video", timeout=15000)
        log.info("Page vidéo chargée")
        
    except Exception as e:
        log.error(f"Erreur lors du clic sur la vidéo: {e}")
        raise e

def interact_with_video_page(page):
    """Interagit avec les éléments de la page vidéo et retourne la description"""
    try:
        # Attendre que les éléments de la vidéo soient chargés
        log.info("Attente que la vidéo se charge complètement...")
        page.wait_for_timeout(3000)
        
        # Tenter d'étendre la description
        try:
            expand_selectors = [
                "#expand",
                "tp-yt-paper-button#expand",
                "#expand-button",
                "#more",
                "#description-inline-expander button"
            ]
            
            for selector in expand_selectors:
                if page.is_visible(selector, timeout=1000):
                    log.info(f"Bouton d'expansion trouvé: {selector}")
                    page.click(selector)
                    page.wait_for_timeout(1000)
                    break
        except Exception as e:
            log.warning(f"Impossible d'étendre la description: {e}")
        
        # Capturer le texte de la description
        description_text = ""
        try:
            description_selectors = [
                "#description-inline-expander",
                "#description",
                "#description-text"
            ]
            
            for selector in description_selectors:
                if page.is_visible(selector, timeout=1000):
                    description_text = page.text_content(selector).strip()
                    log.info(f"Description trouvée ({len(description_text)} caractères)")
                    log.debug(f"Début de la description: {description_text[:100]}...")
                    break
        except Exception as e:
            log.warning(f"Impossible de récupérer la description: {e}")
            
        return description_text
        
    except Exception as e:
        log.error(f"Erreur lors de l'interaction avec la page vidéo: {e}")
        return ""

def capture_comments(page):
    """Fait défiler pour charger et capturer les commentaires"""
    try:
        log.info("Défilement pour charger les commentaires...")
        
        # Faire défiler jusqu'à la section des commentaires
        page.evaluate("""
            window.scrollTo({
                top: document.querySelector('#comments') ? document.querySelector('#comments').offsetTop : 1000,
                behavior: 'smooth'
            });
        """)
        
        # Attendre que la section des commentaires se charge
        page.wait_for_timeout(2000)
        
        # Faire défiler plusieurs fois pour charger plus de commentaires
        for i in range(5):
            page.evaluate("window.scrollBy(0, 500)")
            page.wait_for_timeout(1000)
            log.info(f"Défilement {i+1}/5 effectué")
        
        log.info("Fin du défilement atteinte")
        
        # Attendre que les commentaires se chargent
        page.wait_for_timeout(2000)
        
        # Tenter de récupérer les commentaires
        comments = []
        
        try:
            # Essayer d'abord de récupérer le texte des commentaires
            comment_text_elements = page.query_selector_all("#content-text")
            
            if comment_text_elements and len(comment_text_elements) > 0:
                log.info(f"{len(comment_text_elements)} textes de commentaires trouvés")
                
                # Récupérer également les auteurs des commentaires
                author_elements = page.query_selector_all("#author-text")
                
                # Associer les auteurs et les textes
                for i in range(min(len(comment_text_elements), len(author_elements) if author_elements else 0)):
                    author = author_elements[i].text_content().strip() if i < len(author_elements) else "Auteur inconnu"
                    comment = comment_text_elements[i].text_content().strip()
                    
                    # Nettoyer le texte du commentaire (supprimer les espaces multiples)
                    comment = re.sub(r'\s+', ' ', comment)
                    
                    comments.append({
                        "author": author,
                        "text": comment
                    })
            
            # Si aucun commentaire n'a été trouvé, essayer une autre méthode
            if not comments:
                comment_elements = page.query_selector_all("ytd-comment-thread-renderer")
                
                if comment_elements and len(comment_elements) > 0:
                    log.info(f"{len(comment_elements)} commentaires trouvés avec le sélecteur: ytd-comment-thread-renderer")
                    
                    for i, comment_el in enumerate(comment_elements[:20]):  # Limiter à 20 commentaires
                        try:
                            # Essayer de récupérer l'auteur et le texte du commentaire de cette manière
                            author_el = comment_el.query_selector("#author-text")
                            text_el = comment_el.query_selector("#content-text")
                            
                            author = author_el.text_content().strip() if author_el else "Auteur inconnu"
                            comment = text_el.text_content().strip() if text_el else "Texte non trouvé"
                            
                            # Nettoyer le texte du commentaire
                            comment = re.sub(r'\s+', ' ', comment)
                            
                            comments.append({
                                "author": author,
                                "text": comment
                            })
                        except Exception as comment_error:
                            log.warning(f"Erreur lors de l'extraction du commentaire {i}: {comment_error}")
        
        except Exception as e:
            log.warning(f"Erreur lors de l'extraction des commentaires: {e}")
        
        log.info(f"Total de {len(comments)} commentaires extraits")
        
        # Afficher quelques commentaires comme exemple
        for i, comment in enumerate(comments[:5]):
            log.info(f"Commentaire {i+1}: {comment['author']} - {comment['text'][:100]}...")
            
        return comments
            
    except Exception as e:
        log.error(f"Erreur lors de la capture des commentaires: {e}")
        return []

def save_results(description, comments):
    """Enregistre les résultats dans un fichier texte"""
    try:
        with open("youtube_results.txt", "w", encoding="utf-8") as f:
            f.write("=== DESCRIPTION DE LA VIDÉO ===\n\n")
            f.write(description)
            f.write("\n\n=== COMMENTAIRES ===\n\n")
            
            for i, comment in enumerate(comments):
                f.write(f"{i+1}. {comment['author']}:\n{comment['text']}\n\n")
                
        log.info("Résultats enregistrés dans youtube_results.txt")
    except Exception as e:
        log.error(f"Erreur lors de l'enregistrement des résultats: {e}")

if __name__ == "__main__":
    scrape_youtube()