import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Grants Initiative-specific keywords
open_keywords = [
    "apply now", "open", "submit the form", "application form"
]

def get_user_agent():
    try:
        from fake_useragent import UserAgent
        ua = UserAgent()
        return ua.random
    except Exception as e:
        logger.warning(f"⚠️ UserAgent fallback: {e}")
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

def is_grant_open(text):
    text = text.lower()
    return any(keyword in text for keyword in open_keywords)

def scrape_global_grants_initiative(url="https://www.globalgrantsinitiative.org/application"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"🔍 Scraping Global Grants Initiative: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        text = BeautifulSoup(res.text, 'html.parser').get_text(separator=' ')
        status = 'open' if is_grant_open(text) else 'closed'

        logger.info(f"✅ Global Grants Initiative Status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"❌ Error scraping Global Grants Initiative: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# def main():
#     result = scrape_global_grants_initiative()
#     print("=== Global Grants Initiative Scraper Result ===")
#     print(result)

# if __name__ == "__main__":
#     main()
