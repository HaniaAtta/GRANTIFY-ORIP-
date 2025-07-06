import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

open_keywords = [
    "request for proposal", "request for quotation", "tender", "expression of interest",
    "rfp", "rfq", "call for proposals", "open for submission", "deadline to submit", 
    "submit your proposal", "view the solicitation", "opportunities", "active"
]
closed_keywords = ["submission closed", "applications closed", "no longer accepting"]

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

def scrape_dtglobal(url="https://dt-global.com/proposals/"):
    today = datetime.now().date()
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=20)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        text = soup.get_text(separator=' ', strip=True).lower()
        logger.debug(f"Extracted text preview:\n{text[:500]}")  # debug first chunk

        status = 'open' if is_open(text) else 'closed'

        # Look for deadline dates on the page
        for tag in soup.find_all(['p', 'li', 'div', 'span','h2','h3']):
            txt = tag.get_text(strip=True)
            for fmt in ("%B %d, %Y", "%d %B %Y"):
                try:
                    dt = datetime.strptime(txt, fmt).date()
                    if dt >= today:
                        logger.info(f"Detected future deadline: {dt}")
                        status = 'open'
                except:
                    continue

        logger.info(f"DT Global status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping DT Global: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_dtglobal())