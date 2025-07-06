import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prepare Center–specific open keywords
open_keywords = [
    "call for applications",
    "small research grants program",
    "grant cycles",
    "current grant cycles",
    "submit proposal",
    "apply now",
    "research grants",
    "funding opportunity"
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
    has_open_keyword = any(keyword in text for keyword in open_keywords)

    if not has_open_keyword:
        return False

    # Look for date like "20 June 2024"
    date_match = re.search(r'(\d{1,2} \w+ \d{4})', text)
    if date_match:
        try:
            found_date = datetime.strptime(date_match.group(1), "%d %B %Y")
            if found_date < datetime.utcnow():
                logger.info(f"🕒 Found past date: {found_date}")
                return False
        except ValueError:
            logger.warning("⚠️ Invalid date format found")

    return True

def scrape_prepare_center(url="https://preparecenter.org/activity/gdpc-research-activities/gdpc-small-research-grants-program/"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"🔍 Scraping Prepare Center: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        text = BeautifulSoup(res.text, 'html.parser').get_text(separator=' ')
        status = 'open' if is_grant_open(text) else 'closed'

        logger.info(f"✅ Prepare Center Status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"❌ Error scraping Prepare Center: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# def main():
#     result = scrape_prepare_center()
#     print("=== Prepare Center Scraper Result ===")
#     print(result)

# if __name__ == "__main__":
#     main()
