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
    "grant", "funding", "call for proposals",
    "apply now", "deadline", "apply for funding",
    "request for proposals"
]
closed_keywords = [
    "applications closed", "closed", "deadline passed",
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

def scrape_solidaritycenter(url="https://www.solidaritycenter.org"):
    today = datetime.now().date()
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Filter out context-heavy false positives (e.g., news, statements, jobs)
        false_context = ['statement', 'donate', 'contact us', 'jobs', 'internship', 'take action']
        if any(kw in text.lower() for kw in false_context):
            logger.info("Non-grant context detected. Marking as closed.")
            status = 'closed'
        else:
            status = 'open' if is_open(text) else 'closed'

        # Search for future dates (none expected)
        for tag in soup.find_all(['p', 'li', 'div', 'span', 'h2', 'h3']):
            txt = tag.get_text()
            for fmt in ('%d %B %Y', '%B %d, %Y'):
                try:
                    dt = datetime.strptime(txt.strip(), fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    pass

        logger.info(f"SolidarityCenter status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping Solidarity Center: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_solidaritycenter())