import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

open_keywords = [
    "request for proposals", "call for proposals", "rfq", "rfp", "expression of interest",
    "funding opportunity", "procurement opportunity", "now accepting applications",
    "apply by", "deadline", "grant opportunity", "submit your proposal",
    "open for submission", "solicitations"
]
false_context = ["careers", "jobs", "donate", "news", "volunteer", "press release"]

def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0"

def is_open(text):
    t = text.lower()
    if any(term in t for term in false_context):
        logger.info("Detected non-funding content. Marking as closed.")
        return False
    return any(term in t for term in open_keywords)

def scrape_di(url="https://democracyinternational.com"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        status = 'open' if is_open(text) else 'closed'
        logger.info(f"Democracy International status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"Error scraping DI: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_di())