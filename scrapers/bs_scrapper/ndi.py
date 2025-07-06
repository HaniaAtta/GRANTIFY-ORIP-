import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

open_keywords = [
    "request for proposals", "apply for a grant", "ERA fund",
    "call for proposals", "grant opportunities", "apply now", "funding"
]
closed_keywords = [
    "applications closed", "deadline passed", "no longer accepting",
    "submission closed"
]

def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

def is_open(text):
    t = text.lower()
    if any(kw in t for kw in closed_keywords):
        return False
    return any(kw in t for kw in open_keywords)

def scrape_ndi(url="https://www.ndi.org"):
    today = datetime.now().date()
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Filter out non-grant context (news, jobs, about)
        false_context = ['careers', 'about', 'news', 'blog', 'program development']
        if any(ctx in text.lower() for ctx in false_context):
         logger.info("Non-grant context detected. Marking as closed.")
         return {'url': url, 'status': 'closed'}

        status = 'open' if is_open(text) else 'closed'


        # Date-based check in PDFs/links is beyond scope, but scan visible dates
        for tag in soup.find_all(['p', 'li', 'div', 'h2', 'h3']): 
            txt = tag.get_text()
            for fmt in ("%d %B %Y", "%B %d, %Y"):
                try:
                    dt = datetime.strptime(txt.strip(), fmt).date()
                    if dt >= today:
                        status = 'open'
                except:
                    pass

        logger.info(f"NDI status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"Error scraping NDI: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     print(scrape_ndi())