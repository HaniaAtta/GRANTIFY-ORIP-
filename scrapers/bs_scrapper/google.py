import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Google.org-specific grant keywords
open_keywords = [
    "open call",
    "apply now",
    "funding opportunity",
    "call for proposals",
    "applications are open",
    "accepting applications",
    "submit your application",
    "now accepting proposals",
    "inviting applications",
    "grant opportunity",
    "nonprofits can apply",
    "eligible organizations",
    "generative ai accelerator",
    "ai opportunity fund",
    "impact challenge"
]

def get_user_agent():
    try:
        from fake_useragent import UserAgent
        return UserAgent().random
    except Exception as e:
        logger.warning(f"⚠️ UserAgent fallback: {e}")
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

def is_grant_open(text):
    text = text.lower()
    return any(keyword in text for keyword in open_keywords)

def scrape_google(url="https://www.google.org/"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"🔍 Scraping Google.org: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        text = BeautifulSoup(res.text, 'html.parser').get_text(separator=' ')
        status = 'open' if is_grant_open(text) else 'closed'

        logger.info(f"✅ Google.org Status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"❌ Error scraping Google.org: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# def main():
#     result = scrape_google()
#     print("=== Google.org Scraper Result ===")
#     print(result)

# if __name__ == "__main__":
#     main()
