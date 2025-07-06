import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

# === Logging setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Keyword List ===
open_keywords = [
    'request for proposals', 'rfp open', 'active rfp', 'now accepting proposals',
    'currently available opportunities', 'collaborative research opportunities',
    'funding is available', 'opportunity available', 'solicitation open',
    'open request', 'partnership opportunities', 'submit your proposal',
    'accepting concept notes', 'grant application open', 'call for collaboration',
    'project funding available', 'currently accepting', 'research call open',
    'invitation to apply', 'invitation to bid', 'inviting applications',
    'expression of interest open', 'business opportunity available',
    'funding window open', 'partner with usp', 'submit concept note'
]

# === User-Agent ===
def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# === Status Checker ===
def is_grant_open(text):
    text = text.lower()
    has_open_keyword = any(keyword.lower() in text for keyword in open_keywords)

    if not has_open_keyword:
        return False

    # Optional: date logic (you can comment this out if not needed)
    date_match = re.search(r'(\d{1,2} \w+ \d{4})', text)
    if date_match:
        try:
            found_date = datetime.strptime(date_match.group(1), "%d %B %Y")
            if found_date < datetime.utcnow():
                return False
        except ValueError:
            pass

    return True

# === Main Scraper ===
def scrape_usp(url="https://www.usp.org"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping USP: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        text = BeautifulSoup(res.text, 'html.parser').get_text(separator=" ")
        status = "open" if is_grant_open(text) else "closed"
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# === Run Directly (Optional Test)
# if __name__ == "__main__":
#     result = scrape_usp()
#     print(result)
