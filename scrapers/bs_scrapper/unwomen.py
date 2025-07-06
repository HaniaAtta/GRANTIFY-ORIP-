import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

# Wordbanks
open_keywords = [
    "call for proposals", "request for proposals", "funding opportunity",
    "tenders", "procurement", "submit your proposal", "rfp", "rfq",
    "currently open", "open call", "deadline to submit", "view opportunities", "opportunities"
]
closed_keywords = [
    "applications closed", "no longer accepting", "submission closed", "window closed"
]
false_context = ["careers", "volunteer", "donate", "internship"]

def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0"

def is_open(text, soup):
    t = text.lower()

    # ✅ Extra: Detect external platform like UNGM
    if "ungm.org" in t or any("ungm.org" in a.get("href", "") for a in soup.find_all("a")):
        logger.info("Detected UNGM procurement link. Marking as open.")
        return True

    if any(kw in t for kw in closed_keywords):
        return False
    return any(kw in t for kw in open_keywords)

def scrape_unwomen(url="https://www.unwomen.org/en/about-us/procurement"):
    headers = {'User-Agent': get_user_agent()}
    today = datetime.now().date()

    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # ✅ First check if clearly open
        if is_open(text, soup):
            status = 'open'
        # ❌ Then check for HR-only page (false hits)
        elif any(ctx in text.lower() for ctx in false_context):
            logger.info("Detected non-grant content (careers, donate, etc). Marking as closed.")
            status = 'closed'
        else:
            status = 'closed'

        # 🔍 Date check for confidence
        for tag in soup.find_all(['p', 'li', 'div', 'span']):
            txt = tag.get_text(strip=True)
            for fmt in ("%B %d, %Y", "%d %B %Y"):
                try:
                    dt = datetime.strptime(txt, fmt).date()
                    if dt >= today:
                        logger.info(f"Future deadline found: {dt}")
                        status = 'open'
                except:
                    continue

        logger.info(f"UN Women status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping UN Women: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}


# if __name__ == "__main__":
#     print(scrape_unwomen())