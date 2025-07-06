import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

# Wordbanks
open_keywords = [
    "request for proposals", "call for proposals", "apply now",
    "accepting applications", "grant opportunity", "funding available",
    "rfq", "rfp", "tender", "expression of interest",
    "procurement opportunities", "vendor opportunities", "solicitations", "proposal deadline"
]
false_context = ["careers", "volunteer", "donate", "newsroom", "media", "blog"]

def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0"

def is_open(text):
    t = text.lower()
    return any(word in t for word in open_keywords)

def scrape_nature(url="https://www.nature.org"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        if any(ctx in text.lower() for ctx in false_context):
            logger.info("Detected HR/news context. Marking as closed.")
            return {'url': url, 'status': 'closed'}

        status = 'open' if is_open(text) else 'closed'
        logger.info(f"Nature.org status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping nature.org: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_nature())