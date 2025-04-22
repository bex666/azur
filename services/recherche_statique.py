import os
import random
import time
from datetime import datetime
from services.location import get_current_location
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import urllib.request
import sys

TAB_HISTORY = {}
LINKS_OPENED = 0
START_TIME = datetime.now()

try:
    import winsound
    def beep(): winsound.Beep(1000, 400)
except ImportError:
    def beep(): print("\a", end='')

def simulate_human_typing(element, text):
    ActionChains(element.parent).move_to_element(element).click().perform()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.25))
        if random.random() < 0.1:
            element.send_keys(Keys.BACKSPACE)
            time.sleep(0.1)
        if random.random() < 0.05:
            element.send_keys(Keys.ARROW_LEFT)
            time.sleep(0.1)
            element.send_keys(Keys.DELETE)

def wait_and_accept_cookies(driver):
    try:
        buttons = driver.find_elements(By.XPATH, "//button")
        for b in buttons:
            if 'accepter' in b.text.lower() or 'accept' in b.text.lower():
                b.click()
                print("✅ Cookies acceptés")
                break
    except Exception:
        pass

def detect_captcha(driver):
    try:
        if "sorry/index" in driver.current_url or "captcha" in driver.page_source.lower():
            print("⚠️ CAPTCHA détecté !")
            beep()
            return True
    except Exception:
        pass
    return False

def download_pdf(url):
    try:
        file_name = url.split("/")[-1]
        output_path = os.path.join("/mnt/data", file_name)
        urllib.request.urlretrieve(url, output_path)
        print(f"📥 PDF téléchargé : {file_name}")
    except Exception as e:
        print(f"⚠️ Erreur lors du téléchargement PDF : {e}")

def scroll_randomly(driver):
    for _ in range(random.randint(3, 6)):
        y = random.randint(200, 800) * random.choice([1, -1])
        driver.execute_script(f"window.scrollBy(0, {y});")
        time.sleep(random.uniform(1.0, 2.5))

def hover_random_links(driver):
    links = driver.find_elements(By.TAG_NAME, "a")
    if links:
        for _ in range(random.randint(3, 6)):
            link = random.choice(links)
            try:
                ActionChains(driver).move_to_element(link).pause(random.uniform(0.3, 0.8)).perform()
            except:
                continue

def explore_site(driver, depth=2):
    for _ in range(depth):
        scroll_randomly(driver)
        hover_random_links(driver)
        links = [a for a in driver.find_elements(By.TAG_NAME, "a") if a.get_attribute("href")]
        internal_links = [a for a in links if driver.current_url.split("/")[2] in a.get_attribute("href")]
        if internal_links:
            next_link = random.choice(internal_links)
            href = next_link.get_attribute("href")
            try:
                print(f"🧭 Navigation interne vers : {href}")
                driver.get(href)
                time.sleep(random.uniform(4, 7))
            except:
                continue

def main():
    global LINKS_OPENED
    loc = get_current_location()

    print("\n🔍 Recherche statique simulée")
    print("=" * 40)
    print(f"🌍 Ville actuelle      : {loc.get('city', '-')}")
    print(f"📍 Pays                : {loc.get('country', '-')}")
    print(f"🧭 Coordonnées         : {loc.get('lat', '-')} / {loc.get('lon', '-')}")

    keywords_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'mot_cles.txt'))
    try:
        with open(keywords_path, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ Fichier de mots-clés introuvable.")
        return

    if not keywords:
        print("⚠️ Aucun mot-clé trouvé.")
        return

    random.shuffle(keywords)
    options = uc.ChromeOptions()
    options.add_argument("--user-data-dir=./config/chrome_user_data")
    options.add_argument("--profile-directory=Default")
    driver = uc.Chrome(options=options)

    try:
        for keyword in keywords:
            print("\n🔄 Appuyez sur Ctrl+C pour arrêter proprement la session.")
            print(f"\n🧪 Mot-clé : '{keyword}'")
            driver.get("https://www.google.com")
            time.sleep(random.uniform(2, 4))
            wait_and_accept_cookies(driver)

            search_box = driver.find_element(By.NAME, "q")
            simulate_human_typing(search_box, keyword)
            time.sleep(random.uniform(1, 2))
            search_box.send_keys(Keys.RETURN)
            time.sleep(random.uniform(3, 5))

            if detect_captcha(driver):
                input("⚠️ CAPTCHA détecté. Résolvez-le manuellement puis appuyez sur Entrée...")

            results = driver.find_elements(By.XPATH, "//a[@href and not(contains(@href, '/search?'))]")
            real_links = [a for a in results if 'google.' not in a.get_attribute("href") and a.get_attribute("href")]

            if real_links:
                chosen = random.choice(real_links[:5])
                url = chosen.get_attribute("href")
                print(f"🔗 Visite : {url}")
                driver.get(url)
                LINKS_OPENED += 1
                time.sleep(random.uniform(5, 8))
                explore_site(driver)
            else:
                print("⚠️ Aucun lien externe pertinent trouvé.")

            pause = random.uniform(15, 30)
            print(f"⏸️ Pause inactive de {pause:.1f} secondes...")
            time.sleep(pause)

    except KeyboardInterrupt:
        print("\n🛑 Interruption utilisateur détectée.")

    except Exception as e:
        print(f"❌ Erreur pendant la simulation : {e}")

    finally:
        end_time = datetime.now()
        duration = end_time - START_TIME
        print("\n📊 Fin de session")
        print(f"⏱️ Durée totale : {str(duration).split('.')[0]}")
        print(f"🔗 Nombre total de liens ouverts : {LINKS_OPENED}")
        driver.quit()
