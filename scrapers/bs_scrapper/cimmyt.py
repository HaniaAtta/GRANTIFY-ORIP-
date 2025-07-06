import logging, requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

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
    lower = text.lower()
    if any(kw in lower for kw in closed_keywords):
        return False
    return any(kw in lower for kw in open_keywords)

def scrape_cimmyt(url="https://www.cimmyt.org"):
    today = datetime.now().date()
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        r = session.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        text = BeautifulSoup(r.text, 'html.parser').get_text(separator=' ', strip=True)

        # Early exit if site is mostly news/research
        for ctx in ['news', 'research', 'publications', 'careers']:
            if ctx in text.lower():
                logger.info("Non-grant context detected—returning closed.")
                return {'url': url, 'status': 'closed'}

        status = 'open' if is_open(text) else 'closed'

        # date-based override if found future dates
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup.find_all(['p','li','div','span','h2','h3']):
            t = tag.get_text(strip=True)
            for fmt in ("%d %B %Y","%B %d, %Y"):
                try:
                    if datetime.strptime(t, fmt).date() >= today:
                        status = 'open'
                except: pass

        logger.info(f"CIMMYT status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(e)
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__=="__main__":
#     print(scrape_cimmyt())