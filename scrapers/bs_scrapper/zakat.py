import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

open_keywords = [
    "scholarship", "apply now", "community service scholarship",
    "apply", "eligibility", "deadline"
]
closed_keywords = [
    "applications closed", "deadline passed", "no longer accepting",
    "submission closed"
]

false_context = [
    "donate", "volunteer", "zakat calculator", "our work",
    "annual report", "career", "contact us"
]

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

def scrape_zakat(url="https://www.zakat.org/get-involved/scholarships"):
    today = datetime.now().date()
    headers = {'User-Agent': get_user_agent()}
    
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Fix: Do not mark closed just because "donate" appears
        false_hits = sum(ctx in text.lower() for ctx in false_context)
        if false_hits >= 3 and not is_open(text):
            logger.info("Mostly non-grant context detected. Marking as closed.")
            return {'url': url, 'status': 'closed'}

        status = 'open' if is_open(text) else 'closed'

        # Look for date mentions
        for tag in soup.find_all(['p','li','div','span','h2','h3']):
            txt = tag.get_text().strip()
            for fmt in ("%B %d, %Y", "%d %B %Y"):
                try:
                    dt = datetime.strptime(txt, fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    continue

        logger.info(f"Zakat status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping Zakat: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     result = scrape_zakat()
#     print(result)