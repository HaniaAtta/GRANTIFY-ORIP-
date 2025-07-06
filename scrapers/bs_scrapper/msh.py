import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup session
session = requests.Session()

# Generate random user-agent
def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# Check if the page text suggests an open opportunity
def is_grant_open(text, keywords):
    text = text.lower()

    has_open_keyword = any(keyword in text for keyword in keywords)
    if not has_open_keyword:
        return False

    # Optionally check for a valid future date
    date_match = re.search(r'(\d{1,2} \w+ \d{4})', text)
    if date_match:
        try:
            found_date = datetime.strptime(date_match.group(1), "%d %B %Y")
            if found_date < datetime.utcnow():
                return False
        except ValueError:
            pass

    return True

# Scraper for MSH (Management Sciences for Health)
def scrape_msh(url="https://msh.org/partner-with-us/"):
    custom_keywords = [
        "submit via email",
        "send your proposal to",
        "submit your application to",
        "email your application to",
        "applications should be sent to",
        "proposals must be emailed to",
        "submissions via email",
        "submit proposals at",
        "submit to",
        "please email your response to",
        "contact our team at"
    ]

    headers = {'User-Agent': get_user_agent()}
    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ')
        is_open = is_grant_open(text, custom_keywords)
        logger.info(f"[✓] Scraped: {url} | Status: {'open' if is_open else 'closed'}")
        return {'url': url, 'status': 'open' if is_open else 'closed'}
    except Exception as e:
        logger.error(f"[✗] Failed to scrape {url}: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# Main entry point
# def main():
#     result = scrape_msh()
#     print("Result:", result)

# if __name__ == "__main__":
#     main()
