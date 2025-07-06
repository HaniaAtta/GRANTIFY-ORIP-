import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

# === Logging setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Keyword Lists ===
open_keywords = [
    'sponsored registration', 'scholarships open', 'applications open',
    'submissions open', 'submit application', 'apply by', 'deadline',
    'submission deadline', 'abstract submission', 'call for proposals',
    'inviting applications', 'accepting applications', 'grant funding support'
]

closed_keywords = [
    'applications closed', 'now closed', 'deadline passed',
    'submission closed', 'no longer accepting', 'submissions are closed'
]

# === User-Agent ===
def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# === Status Checker ===
def is_grant_open(text):
    text = text.lower()
    if any(keyword in text for keyword in closed_keywords):
        return False
    if any(keyword in text for keyword in open_keywords):
        return True

    # Optional: Fallback check based on future dates
    date_matches = re.findall(r'(\d{1,2} \w+ \d{4}|\w+ \d{1,2}, \d{4})', text)
    for date_str in date_matches:
        for fmt in ['%d %B %Y', '%B %d, %Y']:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt).date()
                if parsed_date >= datetime.utcnow().date():
                    return True
            except:
                continue
    return False

# === Main Scraper ===
def scrape_theunion(url="https://theunion.org"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping The Union: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        status = "open" if is_grant_open(text) else "closed"
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# === Run Directly (Optional Testing)
# if __name__ == "__main__":
#     print(scrape_theunion())
