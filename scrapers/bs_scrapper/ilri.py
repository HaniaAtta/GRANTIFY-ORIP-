import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

# Wordbanks
open_keywords = [
    "call for proposals", "tender", "request for proposals",
    "apply for funding", "grant", "bid", "deadline"
]
closed_keywords = [
    "applications closed", "deadline passed",
    "submission closed", "no longer accepting"
]

def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0"

def is_open(text):
    t = text.lower()
    if any(kw in t for kw in closed_keywords):
        return False
    return any(kw in t for kw in open_keywords)

def scrape_ilri(url="https://www.ilri.org"):
    today = datetime.now().date()
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Filter out context like news, research, careers
        false_ctx = ['news', 'research', 'careers', 'publications', 'subscribe']
        if any(ctx in text.lower() for ctx in false_ctx):
            logger.info("Non-grant context detected. Marking as closed.")
            status = 'closed'
        else:
            status = 'open' if is_open(text) else 'closed'

        # Date-based check for future deadlines or tender windows
        for tag in soup.find_all(['p','li','div','span','h2','h3']):
            txt = tag.get_text().strip()
            for fmt in ("%d %B %Y","%B %d, %Y"):
                try:
                    dt = datetime.strptime(txt, fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    continue

        logger.info(f"ILRI status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping ILRI: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_ilri())