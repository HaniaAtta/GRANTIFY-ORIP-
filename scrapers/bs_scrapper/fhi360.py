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
    "call for proposals", "request for proposals", "solicitation",
    "rfp", "tender", "funding opportunity", "proposal", "bid"
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
    lower = text.lower()
    if any(kw in lower for kw in closed_keywords):
        return False
    return any(kw in lower for kw in open_keywords)

def scrape_fhi360(url="https://www.fhi360.org/partner-us-business-opportunities/"):
    today = datetime.now().date()
    headers = {'User-Agent': get_user_agent()}

    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=20)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Detect procurement/business opportunities context
        if "solicitations for goods and services" in text.lower() or "requests for proposals" in text.lower():
            status = 'open'
        else:
            status = 'open' if is_open(text) else 'closed'

        # Date‑based check for future deadlines
        for tag in soup.find_all(['p', 'li', 'div', 'span', 'h2', 'h3']):
            txt = tag.get_text(strip=True)
            for fmt in ("%d %B %Y", "%B %d, %Y"):
                try:
                    dt = datetime.strptime(txt, fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    pass

        logger.info(f"FHI360 status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping FHI 360: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_fhi360())