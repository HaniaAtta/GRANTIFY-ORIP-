# import logging
# import requests
# from bs4 import BeautifulSoup
# from fake_useragent import UserAgent
# import re
# from datetime import datetime

# # === Logging setup ===
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # === Keyword List ===
# open_keywords = [
#    "Submit a project proposal", "open now","apply now"
# ]

# # === User-Agent ===
# def get_user_agent():
#     try:
#         ua = UserAgent()
#         return ua.random
#     except:
#         return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# # === Status Checker ===
# def is_grant_open(text):
#     text = text.lower()
#     has_open_keyword = any(keyword.lower() in text for keyword in open_keywords)

#     if not has_open_keyword:
#         return False

#     # Optional: check for recent date (not outdated)
#     date_match = re.search(r'(\d{1,2} \w+ \d{4})', text)
#     if date_match:
#         try:
#             found_date = datetime.strptime(date_match.group(1), "%d %B %Y")
#             if found_date < datetime.utcnow():
#                 return False  # Too old
#         except ValueError:
#             pass  # Ignore if unparseable

#     return True

# # === Main Scraper ===
# def scrape_iki_small_grants(url="https://iki-small-grants.de/application/"):
#     headers = {'User-Agent': get_user_agent()}
#     try:
#         logger.info(f"Scraping IKI Small Grants: {url}")
#         res = requests.get(url, headers=headers, timeout=10)
#         res.raise_for_status()

#         text = BeautifulSoup(res.text, 'html.parser').get_text(separator=" ")
#         status = "open" if is_grant_open(text) else "closed"
#         return {'url': url, 'status': status}
#     except Exception as e:
#         logger.error(f"Error scraping {url}: {str(e)}")
#         return {'url': url, 'status': 'error', 'error': str(e)}

# # === Run Directly ===
# # if __name__ == "__main__":
# #     result = scrape_iki_small_grants()
# #     print(result)



# import requests
# from bs4 import BeautifulSoup
# from app.ai.classifier import classify_grant

# def scrape_iki_small_grants():
#     """
#     Scrapes IKI Small Grants application page and classifies with AI.
#     """
#     results = []
#     landing_page = "https://iki-small-grants.de/application/"

#     try:
#         response = requests.get(landing_page, timeout=10)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, "html.parser")

#         text = soup.get_text(" ", strip=True)

#         # 🔥 Pass page text to AI classifier
#         ai_result = classify_grant(landing_page, text)

#         results.append({
#             "url": landing_page,
#             "status": ai_result["status"],
#             "landing_page": landing_page,
#             "categories": ai_result.get("categories", ["Other"]),
#             "source": "AI"   # 👈 mark it clearly
#         })

#     except Exception as e:
#         print(f"❌ Error scraping IKI Small Grants: {e}")
#         results.append({
#             "url": landing_page,
#             "status": "error",
#             "error": str(e),
#             "landing_page": landing_page,
#             "categories": ["Other"],
#             "source": "rule_based"
#         })

#     return results
def scrape_iki_small_grants():
    """
    Crawl IKI Small Grants website and detect if applications are open.
    Stops once an application-related page is found.
    Always attaches hardcoded regions as fallback.
    Appends eligibility info to status.
    """
    base_url = "https://iki-small-grants.de/application/"
    visited = set()
    to_visit = [base_url]
    results = []

    try:
        while to_visit:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(" ", strip=True)

            # ✅ Region/eligibility filter
            region_status = get_region_status(text)

            # ✅ Check for any keyword in text
            if any(keyword in text.lower() for keyword in KEYWORDS):
                ai_result = classify_grant(url, text)

                # Use AI categories if available, fallback to HARDCODED_REGIONS
                categories = ai_result.get("categories") or HARDCODED_REGIONS

                results.append({
                    "url": url,
                    "status": f"{ai_result['status']} - {region_status}",
                    "landing_page": url,
                    "categories": categories,
                    "source": "AI+keywords"
                })
                return results  # Stop at first match

            # ✅ Enqueue internal links
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    if full_url not in visited:
                        to_visit.append(full_url)

        # ❌ No application page found, fallback to base page
        fallback_text = requests.get(base_url, timeout=10).text
        region_status = get_region_status(fallback_text)
        ai_result = classify_grant(base_url, fallback_text)

        categories = ai_result.get("categories") or HARDCODED_REGIONS

        results.append({
            "url": base_url,
            "status": f"{ai_result['status']} - {region_status}",
            "landing_page": base_url,
            "categories": categories,
            "source": "AI-fallback"
        })

    except Exception as e:
        print(f"❌ Error scraping IKI Small Grants: {e}")
        results.append({
            "url": base_url,
            "status": f"error - Not Eligible",
            "error": str(e),
            "landing_page": base_url,
            "categories": HARDCODED_REGIONS,
            "source": "rule_based"
        })

    return results
