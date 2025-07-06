import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

open_keywords = [
    "call for proposals", "request for proposals", "grant",
    "small grants", "solicitation", "rfp",
    "business opportunity", "funding opportunity", "bid"
]
closed_keywords = [
    "applications closed", "deadline passed",
    "no longer accepting", "submission closed"
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

def scrape_unops(url="https://www.unops.org/business-opportunities"):
    today = datetime.now().date()
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        # global retry built-in
        res = session.get(url, headers=headers, timeout=20)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Main logic: detect 'call for proposals' etc.
        status = 'open' if is_open(text) else 'closed'

        # If page mentions tender/grants and also future date, it's certainly open
        for tag in soup.find_all(['p','li','div','span','h2','h3']):
            txt = tag.get_text(strip=True)
            for fmt in ("%d %B %Y","%B %d, %Y"):
                try:
                    dt = datetime.strptime(txt, fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    continue

        logger.info(f"UNOPS status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping UNOPS: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_unops())