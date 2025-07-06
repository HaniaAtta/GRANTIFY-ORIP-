import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

# === Logging setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === German/English Keywords ===
open_keywords = [
    'bewerbungsfrist', 'jetzt bewerben', 'stipendien', 'bewerbung bis', 
    'call for applications', 'apply now', 'application deadline', 
    'stipendium', 'stipendienprogramm', 'förderung'
]

closed_keywords = [
    'bewerbungsfrist abgelaufen', 'nicht mehr möglich', 'bewerbung geschlossen',
    'achtung frist verpasst', 'ende der bewerbungsfrist', 'deadline passed'
]

german_months = [
    'januar','februar','märz','april','mai','juni','juli',
    'august','september','oktober','november','dezember'
]

# === User-Agent ===
def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# === Status Checker ===
def is_grant_open(text):
    text = text.lower()
    if any(kw in text for kw in closed_keywords):
        return False
    if any(kw in text for kw in open_keywords):
        return True

    # Fallback: Look for German-style dates like "bis 31. August 2025"
    if 'bis' in text:
        if any(month in text for month in german_months):
            return True

    return False

# === Main Scraper ===
def scrape_boell(url="https://www.boell.de/en/foundation/scholarships"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping Boell Foundation: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        status = "open" if is_grant_open(text) else "closed"
        logger.info(f"Detected status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# === Optional Test Run
# if __name__ == "__main__":
#     print(scrape_boell())
