import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# === Logging setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Keyword Lists ===
open_keywords = [
    'application deadline', 'applications are now open',
    'deadline', 'call for applications', 'apply now',
    'stipendien', 'stipendium', 'bewerbung bis', 'bewerbung jetzt'
]

closed_keywords = [
    'applications closed', 'deadline passed',
    'bewerbung geschlossen', 'nicht mehr möglich',
    'keine bewerbung', 'frist verpasst'
]

# === Status Checker ===
def is_grant_open(text):
    text = text.lower()
    if any(kw in text for kw in closed_keywords):
        return False
    return any(kw in text for kw in open_keywords)

# === Scraper ===
def scrape_kas(url="https://www.kas.de/en/web/begabtenfoerderung-und-kultur"):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    today = datetime.utcnow().date()

    try:
        logger.info(f"Scraping KAS using Selenium: {url}")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        text = soup.get_text(separator=' ', strip=True)
        status = 'open' if is_grant_open(text) else 'closed'

        # Optional date check: scan visible text for "Application deadline July 15, 2025"
        for tag in soup.find_all(['p', 'li', 'div', 'h2', 'h3']):
            txt = tag.get_text()
            if 'application deadline' in txt.lower() or 'deadline' in txt.lower():
                try:
                    parts = txt.strip().split()
                    dt = datetime.strptime(' '.join(parts[-3:]), '%B %d, %Y').date()
                    if dt >= today:
                        status = 'open'
                except:
                    pass

        logger.info(f"KAS detected status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        try:
            driver.quit()
        except:
            pass
        return {'url': url, 'status': 'error', 'error': str(e)}

# === Optional test run
# if __name__ == "__main__":
#     print(scrape_kas())
