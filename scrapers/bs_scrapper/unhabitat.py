import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime
from dateutil import parser

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

# ✅ Expanded wordbank for detecting open status
open_keywords = [
    "call for proposals", "expression of interest", "funding opportunity", "solicitation",
    "submit proposal", "submission deadline", "apply by", "open call",
    "currently accepting", "implementation projects", "deadline for submission"
]

# ❌ False-positive words like HR or newsletter
false_context = ["donate", "volunteer", "press release", "newsletter", "career", "job"]

def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0"

def is_open(text):
    t = text.lower()
    if any(ctx in t for ctx in false_context):
        logger.info("Detected non-grant context. Marking as closed.")
        return False
    return any(kw in t for kw in open_keywords)

def scrape_unhabitat(url="https://unhabitat.org/join-us/calls"):
    headers = {'User-Agent': get_user_agent()}
    today = datetime.now().date()

    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        status = 'open' if is_open(text) else 'closed'

        # 🔍 Check for dates in content
        for tag in soup.find_all(['p', 'li', 'span', 'div']):
            txt = tag.get_text(strip=True)
            try:
                dt = parser.parse(txt, fuzzy=True).date()
                if dt >= today:
                    logger.info(f"Found future date: {dt}")
                    status = 'open'
                    break
            except:
                continue

        logger.info(f"UN-Habitat status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping UN-Habitat: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_unhabitat())