import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ICIMOD-specific keywords
open_keywords = [
    "open now",
    "apply now",
    "apply here", 'funding opportunity', 'call for applications', 'open call',
    'environmental grant', 'spring water grant', 'currently open',
    'accepting proposals', 'application deadline', 'climate funding'
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

    # Check for keywords
    has_open_keyword = any(keyword in text for keyword in open_keywords)
    if not has_open_keyword:
        return False

    # Try to extract a date like "20 June 2024"
    date_match = re.search(r'(\d{1,2} \w+ \d{4})', text)
    if date_match:
        try:
            found_date = datetime.strptime(date_match.group(1), "%d %B %Y")
            if found_date < datetime.utcnow():
                logger.info(f"🕒 Date found is in the past: {found_date}")
                return False
        except ValueError:
            logger.warning("⚠️ Could not parse date from string")

    return True

def scrape_icimod(url="https://www.icimod.org/film-grants-on-water-springs-2024/"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"🔍 Scraping ICIMOD: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        text = BeautifulSoup(res.text, 'html.parser').get_text(separator=' ')
        status = 'open' if is_grant_open(text) else 'closed'

        logger.info(f"✅ ICIMOD Status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"❌ Error scraping ICIMOD: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# def main():
#     result = scrape_icimod()
#     print("=== ICIMOD Scraper Result ===")
#     print(result)

# if __name__ == "__main__":
#     main()
