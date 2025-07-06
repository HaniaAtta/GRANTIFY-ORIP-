import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Being Initiative-specific open keywords
open_keywords = [
    "request for proposals",
    "funding opportunities",
    "apply by",
    "submit your application",
    "application deadline"
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
    
    if not any(keyword in text for keyword in open_keywords):
        return False

    # 🔍 Match formats like "24 June 2025" or "June 24, 2025"
    date_patterns = re.findall(r'(\d{1,2} \w+ \d{4})|(\w+ \d{1,2}, \d{4})', text)

    if not date_patterns:
        logger.warning("⚠️ No deadline date found, assuming open")
        return True

    for match in date_patterns:
        date_str = match[0] if match[0] else match[1]
        for fmt in ("%d %B %Y", "%B %d, %Y"):
            try:
                deadline = datetime.strptime(date_str, fmt)
                if deadline >= datetime.utcnow():
                    return True
            except ValueError:
                continue

    logger.info("📅 All deadlines have passed.")
    return False

def scrape_being_initiative(url="https://being-initiative.org/news/applications-now-open-funding-youth-mental-health-innovations/"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"🔍 Scraping Being Initiative: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        text = BeautifulSoup(res.text, 'html.parser').get_text(separator=' ')
        status = 'open' if is_grant_open(text) else 'closed'

        logger.info(f"✅ Being Initiative Status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"❌ Error scraping Being Initiative: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# def main():
#     result = scrape_being_initiative()
#     print("=== Being Initiative Scraper Result ===")
#     print(result)

# if __name__ == "__main__":
#     main()
