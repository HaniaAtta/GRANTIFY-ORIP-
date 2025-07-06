import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

# Integrated wordbanks
open_keywords = [
    "apply now", "deadline", "call for applications",
    "grant", "funding available", "submit application"
]
closed_keywords = [
    "closed", "not accepting", "no longer accepting",
    "submission closed", "deadline passed"
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

def scrape_kort(url="https://kort.org.uk"):
    today = datetime.now().date()
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        status = 'open' if is_open(text) else 'closed'

        # Look for future dates indicating planned calls
        for tag in soup.find_all(['p', 'li', 'div', 'span', 'h2', 'h3']):
            txt = tag.get_text()
            for fmt in ('%d %B %Y', '%B %d, %Y'):
                try:
                    dt = datetime.strptime(txt.strip(), fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    pass

        logger.info(f"KORT status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"Error scraping KORT: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_kort())