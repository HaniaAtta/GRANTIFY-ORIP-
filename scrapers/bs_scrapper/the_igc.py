import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The IGC-specific keywords
open_keywords = [
    "call for papers",
    "call for proposals",
    "open until",
    "open from",
    "apply now",
    "submission deadline"
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

def scrape_the_igc(url="https://www.theigc.org/researchers/funding"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"🔍 Scraping The IGC: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        text = BeautifulSoup(res.text, 'html.parser').get_text(separator=' ')
        status = 'open' if is_grant_open(text) else 'closed'

        logger.info(f"✅ The IGC Status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"❌ Error scraping The IGC: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# def main():
#     result = scrape_the_igc()
#     print("=== The IGC Scraper Result ===")
#     print(result)

# if __name__ == "__main__":
#     main()
