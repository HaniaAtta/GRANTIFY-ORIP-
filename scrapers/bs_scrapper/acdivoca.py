import logging, requests, re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

# === Logging Setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session = requests.Session()

# === Constants ===
file_kw = [".pdf", ".doc", ".docx"]
open_terms = ["rfp", "request for proposal", "expression of interest"]
year_pattern = re.compile(r"(20[2-3]\d)")

# === User-Agent ===
def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0"

# === Main Scraper Function ===
def scrape_acdivoca(url="https://www.acdivoca.org"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scanning site for PDF links: {url}")
        res = session.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        links = [a.get("href") for a in soup.find_all("a", href=True)]
        pdf_links = [link for link in links if any(link.lower().endswith(ext) for ext in file_kw)]

        recent_rfps = []
        for link in pdf_links:
            low = link.lower()
            if any(term in low for term in open_terms):
                m = year_pattern.search(link)
                year = int(m.group(1)) if m else None
                if year and year >= datetime.now().year:
                    recent_rfps.append(link)

        status = 'open' if recent_rfps else 'closed'
        logger.info(f"Found {len(recent_rfps)} recent RFP/EoI PDFs: marking as {status}")
        return {'url': url, 'status': status, 'found_links': recent_rfps}
    except Exception as e:
        logger.error(f"Error scanning ACDI/VOCA PDFs: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# === Example Usage ===
# if __name__ == "__main__":
#     print(scrape_acdivoca())
