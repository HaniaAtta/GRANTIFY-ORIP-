import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

# === Logging Setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

# === Wordbanks ===
open_keywords = [
    "apply now", "call for applications", "grant",
    "funding available", "deadline", "submission deadline",
    "open for registration"
]
closed_keywords = [
    "applications closed", "now closed",
    "deadline passed", "submission closed", "no longer accepting"
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
def scrape_actionforhumanity(url="https://actionforhumanity.org"):
    today = datetime.utcnow().date()
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        full_text = soup.get_text(separator=' ', strip=True)

        status = 'open' if is_open(full_text) else 'closed'

        # Date-based fallback
        for tag in soup.find_all(['p', 'li', 'div', 'span', 'h2', 'h3']):
            t = tag.get_text()
            for fmt in ('%d %B %Y', '%B %d, %Y'):
                try:
                    dt = datetime.strptime(t.strip(), fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    continue

        logger.info(f"Action for Humanity status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# === Optional test run
# if __name__ == "__main__":
#     print(scrape_actionforhumanity())
