import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

# 🎯 Wordbanks
open_keywords = [
    "call for proposals", "grant", "funding",
    "request for proposals", "apply for funding",
    "tender", "deadline"
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
    txt = text.lower()
    if any(kw in txt for kw in closed_keywords):
        return False
    return any(kw in txt for kw in open_keywords)

def scrape_mercycorps(url="https://www.mercycorps.org"):
    today = datetime.now().date()
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        full_text = soup.get_text(separator=' ', strip=True)

        # Filter out non-grant context (careers, news, donations)
        false_ctx = ['careers', 'news', 'donate', 'internship', 'job', 'volunteer']
        if any(ctx in full_text.lower() for ctx in false_ctx):
            logger.info("Non-grant content detected. Marking as closed.")
            return {'url': url, 'status': 'closed'}

        status = 'open' if is_open(full_text) else 'closed'

        # Date-based override
        for tag in soup.find_all(['p', 'li', 'div', 'span', 'h2', 'h3']):
            text = tag.get_text().strip()
            for fmt in ("%d %B %Y", "%B %d, %Y"):
                try:
                    dt = datetime.strptime(text, fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    pass

        logger.info(f"MercyCorps status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping Mercy Corps: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     result = scrape_mercycorps()
#     print(result)