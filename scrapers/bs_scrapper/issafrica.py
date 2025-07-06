import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

open_keywords = [
    "call for proposals", "request for proposals", "tenders",
    "funding opportunity", "grants", "open call", "submit your proposal",
    "rfq", "rfp", "deadline to submit"
]

closed_keywords = ["applications closed", "no longer accepting", "submission closed"]
non_grant_context = ["careers", "newsletter", "volunteer", "donate"]

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

def scrape_issafrica(url="https://issafrica.org"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        if any(word in text.lower() for word in non_grant_context):
            logger.info("Detected non-grant content. Marking as closed.")
            return {'url': url, 'status': 'closed'}

        status = 'open' if is_open(text) else 'closed'
        logger.info(f"ISS Africa status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping ISS Africa: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_issafrica())