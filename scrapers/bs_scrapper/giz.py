import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GIZ-specific open keywords
open_keywords = [
    "call for proposals",
    "apply for funding",
    "request proposals"
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

    # Match both types of dates: "20 June 2024" or "29.05.2025."
    date_patterns = re.findall(r'(\d{1,2} \w+ \d{4})|(\d{2}\.\d{2}\.\d{4})', text)

    if not date_patterns:
        logger.warning("⚠️ No date found, assuming open")
        return True

    for match in date_patterns:
        date_str = match[0] if match[0] else match[1]
        formats = ["%d %B %Y", "%d.%m.%Y"]
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str.strip("."), fmt)
                if parsed_date >= datetime.utcnow():
                    return True  # Still valid
            except ValueError:
                continue

    logger.info("📅 All deadlines have passed.")
    return False

def scrape_giz(url="https://www.giz.de/en/worldwide/205555.html"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"🔍 Scraping GIZ: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        text = BeautifulSoup(res.text, 'html.parser').get_text(separator=' ')
        status = 'open' if is_grant_open(text) else 'closed'

        logger.info(f"✅ GIZ Status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"❌ Error scraping GIZ: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# def main():
#     result = scrape_giz()
#     print("=== GIZ Scraper Result ===")
#     print(result)

# if __name__ == "__main__":
#     main()
