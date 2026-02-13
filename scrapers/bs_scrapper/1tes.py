# # test_scraper.py
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from app.ai.classifier import classify_grant
# import random

# # User agents
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
# ]

# LINK_KEYWORDS = ["apply", "application", "submit", "opportunity","grants"]

# def get_user_agent():
#     return random.choice(USER_AGENTS)

# def scrape_fundsforngos(base_url="https://www.fundsforngos.org/"):
#     results = []
#     visited = set()
#     to_visit = [base_url]
#     domain = urlparse(base_url).netloc

#     headers = {
#         "User-Agent": get_user_agent(),
#         "Accept-Language": "en-US,en;q=0.9",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#         "Referer": base_url
#     }

#     try:
#         while to_visit:
#             url = to_visit.pop(0)
#             if url in visited:
#                 continue
#             visited.add(url)

#             # Fetch the page
#             res = requests.get(url, headers=headers, timeout=15)
#             res.raise_for_status()
#             soup = BeautifulSoup(res.text, "html.parser")
#             text = soup.get_text(" ", strip=True)

#             # Step 1: Look for links with keywords
#             for link in soup.find_all("a", href=True):
#                 href = link["href"]
#                 link_text = link.get_text(" ", strip=True).lower()
#                 if any(k in href.lower() or k in link_text for k in LINK_KEYWORDS):
#                     landing_page = urljoin(url, href)
#                     try:
#                         landing_resp = requests.get(landing_page, headers=headers, timeout=15)
#                         landing_resp.raise_for_status()
#                         landing_text = landing_resp.text
#                         ai_result = classify_grant(landing_page, landing_text)
#                         results.append({
#                             "url": landing_page,
#                             "status": ai_result.get("status", "unknown"),
#                             "landing_page": landing_page,
#                             "categories": ai_result.get("categories", ["Other"]),
#                             "regions": ai_result.get("regions", []),
#                             "source": "AI-link"
#                         })
#                         return results
#                     except requests.exceptions.RequestException as e:
#                         # 403 or other fetch issues → fallback to base page AI
#                         ai_result = classify_grant(url, text)
#                         results.append({
#                             "url": landing_page,
#                             "status": ai_result.get("status", "unknown"),
#                             "landing_page": landing_page,
#                             "categories": ai_result.get("categories", ["Other"]),
#                             "regions": ai_result.get("regions", []),
#                             "source": f"AI-base-fallback due to: {e}"
#                         })
#                         return results

#             # Step 2: AI classification on current page if no landing link found
#             ai_result = classify_grant(url, text)
#             results.append({
#                 "url": url,
#                 "status": ai_result.get("status", "unknown"),
#                 "landing_page": url,
#                 "categories": ai_result.get("categories", ["Other"]),
#                 "regions": ai_result.get("regions", []),
#                 "source": "AI-base"
#             })
#             return results

#     except Exception as e:
#         results.append({
#             "url": base_url,
#             "status": "error",
#             "error": str(e),
#             "landing_page": base_url,
#             "categories": ["Other"],
#             "regions": [],
#             "source": "error"
#         })
#     return results

# if __name__ == "__main__":
#     print(scrape_fundsforngos())



# test_scraper_selenium.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from urllib.parse import urljoin, urlparse
from app.ai.classifier import classify_grant
import random
import time
# User agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

LINK_KEYWORDS = ["apply", "application", "submit", "opportunity"]

def scrape_fundsforngos(base_url="https://www.fundsforngos.org/"):
    results = []
    visited = set()
    to_visit = [base_url]
    domain = urlparse(base_url).netloc

    # Selenium setup
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    driver = webdriver.Chrome(service=Service(), options=chrome_options)

    try:
        while to_visit:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)

            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                time.sleep(1)  # Give some extra time for JS
                text = driver.find_element(By.TAG_NAME, "body").text

                # Look for landing links
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    link_text = link.text.lower()
                    if href and any(k in href.lower() or k in link_text for k in LINK_KEYWORDS):
                        landing_page = urljoin(url, href)
                        try:
                            driver.get(landing_page)
                            WebDriverWait(driver, 10).until(
                                lambda d: d.execute_script('return document.readyState') == 'complete'
                            )
                            landing_text = driver.find_element(By.TAG_NAME, "body").text
                            ai_result = classify_grant(landing_page, landing_text)
                            results.append({
                                "url": landing_page,
                                "status": ai_result.get("status", "unknown"),
                                "landing_page": landing_page,
                                "categories": ai_result.get("categories", ["Other"]),
                                "regions": ai_result.get("regions", []),
                                "source": "AI-link"
                            })
                            return results
                        except TimeoutException:
                            ai_result = classify_grant(url, text)
                            results.append({
                                "url": landing_page,
                                "status": ai_result.get("status", "unknown"),
                                "landing_page": landing_page,
                                "categories": ai_result.get("categories", ["Other"]),
                                "regions": ai_result.get("regions", []),
                                "source": f"AI-base-fallback due to timeout"
                            })
                            return results

                # AI classification on current page if no landing link found
                ai_result = classify_grant(url, text)
                results.append({
                    "url": url,
                    "status": ai_result.get("status", "unknown"),
                    "landing_page": url,
                    "categories": ai_result.get("categories", ["Other"]),
                    "regions": ai_result.get("regions", []),
                    "source": "AI-base"
                })
                return results

            except Exception as e:
                results.append({
                    "url": url,
                    "status": "error",
                    "error": str(e),
                    "landing_page": url,
                    "categories": ["Other"],
                    "regions": [],
                    "source": "error"
                })

    finally:
        driver.quit()

    return results


# # Example usage
# if __name__ == "__main__":
#     print(scrape_fundsforngos())
