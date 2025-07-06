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
    "call for proposals", "apply now", "funding available",
    "grant", "scholarship", "deadline", "submit application"
]
closed_keywords = [
    "applications closed", "deadline passed",
    "submission closed", "no longer accepting"
]

def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

def is_open(text):
    t = text.lower()
    if any(kw in t for kw in closed_keywords):
        return False
    return any(kw in t for kw in open_keywords)

def scrape_worlded(url="https://worlded.org"):
    today = datetime.now().date()
    headers = {'User-Agent': get_user_agent()}

    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Filter out non-grant context
        false_context = ['research','publications','press','blog','about','learning']
        if any(ctx in text.lower() for ctx in false_context):
            logger.info("Non-grant context detected. Marking as closed.")
            status = 'closed'
        else:
            status = 'open' if is_open(text) else 'closed'

        # Date-based check
        for tag in soup.find_all(['p','li','div','span','h2','h3']):
            txt = tag.get_text()
            for fmt in ("%d %B %Y","%B %d, %Y"):
                try:
                    dt = datetime.strptime(txt.strip(), fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    continue

        logger.info(f"WorldEd status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping WorldEd: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_worlded())