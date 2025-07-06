import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

# === Logger Setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

# === Keyword Banks ===
open_keywords = [
    "apply now", "call for applications", "deadline", "grant",
    "funding available", "submit application", "call for proposals"
]
closed_keywords = [
    "closed", "deadline passed", "submission closed", "no longer accepting",
    "applications closed"
]

# === User-Agent ===
def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# === Status Checker ===
def is_open(text):
    t = text.lower()
    if any(kw in t for kw in closed_keywords):
        return False
    return any(kw in t for kw in open_keywords)

# === Main Scraper ===
def scrape_orphansinneed(url="https://www.orphansinneed.org.uk"):
    today = datetime.utcnow().date()
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Primary status detection
        status = 'open' if is_open(text) else 'closed'

        # Date-based fallback detection
        for tag in soup.find_all(['p', 'li', 'div', 'span', 'h2', 'h3']):
            txt = tag.get_text()
            for fmt in ('%d %B %Y', '%B %d, %Y'):
                try:
                    dt = datetime.strptime(txt.strip(), fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    continue

        logger.info(f"OrphansInNeed status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# === Optional test run
# if __name__ == "__main__":
#     print(scrape_orphansinneed())
