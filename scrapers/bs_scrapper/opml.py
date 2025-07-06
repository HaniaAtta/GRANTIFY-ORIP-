import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OPML-specific open keywords
open_keywords = [
    'policy research', 'advisory services',
    'consultancy opportunity', 'call for proposals',
    'apply now', 'now open'
]

def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception as e:
        logger.warning(f"⚠️ UserAgent fallback: {e}")
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

def is_grant_open(text):
    text = text.lower()
    return any(keyword in text for keyword in open_keywords)

def scrape_opml(url="https://opml.co.uk"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"🔍 Scraping OPML: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        text = BeautifulSoup(res.text, 'html.parser').get_text(separator=' ')
        status = 'open' if is_grant_open(text) else 'closed'

        logger.info(f"✅ OPML Status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"❌ Error scraping OPML: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# def main():
#     result = scrape_opml()
#     print("=== OPML Scraper Result ===")
#     print(result)

# if __name__ == "__main__":
#     main()
