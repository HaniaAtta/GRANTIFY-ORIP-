import logging
import re
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Grant-specific open keywords
open_keywords = [
    "deadline", "apply now", "open until", "currently accepting",
    "funding opportunity", "submission deadline", "open call"
]

# === Grant Status Logic ===
def is_grant_open(text):
    text = text.lower()

    if not any(keyword in text for keyword in open_keywords):
        return False

    # Try to find various date formats
    date_patterns = re.findall(
        r'(\d{1,2} \w+ \d{4}|\w+ \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\w+ \d{4})',
        text
    )

    date_formats = [
        "%d %B %Y", "%B %d, %Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y",
        "%B %Y", "%b %d, %Y", "%d %b %Y", "%b %Y"
    ]

    for date_str in date_patterns:
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                if "%d" not in fmt:
                    dt = dt.replace(day=1)  # approximate if day is missing
                if dt >= datetime.utcnow():
                    return True
            except Exception:
                continue

    return True  # fallback: open keyword present, but no past deadline found

# === Scraper ===
def scrape_hu_maarif(url="https://hu.maarifschool.org/page/the-turkish-maarif-foundation"):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = None
    try:
        logger.info(f"🌐 Visiting Wellcome Grants Page: {url}")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        # Wait for a specific element or fallback to sleep
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main, h2, .paragraph, .wysiwyg"))
            )
        except Exception:
            logger.warning("⚠ Timeout waiting for content, using sleep fallback.")
            time.sleep(5)

        html = driver.page_source
        text = BeautifulSoup(html, 'html.parser').get_text(separator=' ')

        # DEBUG: Save HTML (optional)
        # with open("/tmp/wellcome_debug.html", "w", encoding="utf-8") as f:
        #     f.write(html)

        status = 'open' if is_grant_open(text) else 'closed'
        logger.info(f"✅ Wellcome Grant Status: {status}")
        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"❌ Error scraping Wellcome: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

    finally:
        if driver:
            driver.quit()

# === CLI Runner ===
# def main():
#     result = scrape_wellcome()
#     print("=== Wellcome Grants Scraper Result ===")
#     print(result)

# if _name_ == "_main_":
#     main()
