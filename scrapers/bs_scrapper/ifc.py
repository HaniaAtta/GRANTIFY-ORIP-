import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG)  # Use DEBUG to see text preview
logger = logging.getLogger(__name__)
session = requests.Session()

# ✅ Improved open keywords for World Bank/IFC context
open_keywords = [
    "request for proposals", "rfp", "tender", "expression of interest",
    "funding opportunity", "solicitation", "view the notice", "active",
    "now accepting", "open until", "deadline", "respond by", "response due"
]

closed_keywords = [
    "applications closed", "no longer accepting", "deadline passed", "submission closed"
]

def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0"

def is_open(text):
    t = text.lower()
    if any(word in t for word in closed_keywords):
        return False
    return any(word in t for word in open_keywords)

def scrape_ifc(url="https://ifc.org"):
    headers = {'User-Agent': get_user_agent()}
    today = datetime.now().date()

    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=20)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        logger.debug(f"Text preview:\n{text[:1000]}")  # 👀 See scraped content

        status = 'open' if is_open(text) else 'closed'

        # 📅 Check if any future date is listed
        for tag in soup.find_all(['p', 'li', 'span', 'div', 'h2', 'h3']):
            txt = tag.get_text(strip=True)
            for fmt in ("%B %d, %Y", "%d %B %Y"):
                try:
                    dt = datetime.strptime(txt, fmt).date()
                    if dt >= today:
                        logger.debug(f"Future deadline found: {dt}")
                        status = 'open'
                except:
                    continue

        logger.info(f"IFC status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"Error scraping IFC: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# ✅ Run
# if __name__ == "__main__":
#     print(scrape_ifc())