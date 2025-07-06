import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

# === Logger Setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

# === Keyword Lists ===
open_keywords = [
    "call for proposals", "apply now", "funding available",
    "grant", "scholarship", "deadline", "submit application"
]
closed_keywords = [
    "applications closed", "deadline passed",
    "submission closed", "no longer accepting"
]

# === User-Agent ===
def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# === Grant Status Checker ===
def is_open(text):
    t = text.lower()
    if any(kw in t for kw in closed_keywords):
        return False
    return any(kw in t for kw in open_keywords)

# === Scraper Function ===
def scrape_centralasia(url="https://centralasiainstitute.org"):
    today = datetime.utcnow().date()
    headers = {'User-Agent': get_user_agent()}

    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True).lower()

        # Filter out donation/planned-giving-only pages
        false_context = ['donate', 'legacy', 'planned giving', 'donor advised']
        if any(ctx in text for ctx in false_context):
            logger.info("Detected donation/planned-giving content. Marking as closed.")
            status = 'closed'
        else:
            status = 'open' if is_open(text) else 'closed'

        # Look for future dates to determine openness
        for tag in soup.find_all(['p', 'li', 'div', 'span', 'h2', 'h3']):
            txt = tag.get_text()
            for fmt in ("%d %B %Y", "%B %d, %Y"):
                try:
                    dt = datetime.strptime(txt.strip(), fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    continue

        logger.info(f"Central Asia Institute status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping Central Asia Institute: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# === Optional test run
# if __name__ == "__main__":
#     print(scrape_centralasia())
