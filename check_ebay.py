import os
import smtplib
import requests

# 🔑 Secrets from GitHub
EBAY_API_KEY = os.getenv("EBAY_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

# eBay API endpoints
SEARCH_URL = "https://svcs.ebay.com/services/search/FindingService/v1"
DETAIL_URL = "https://open.api.ebay.com/shopping"

# -----------------------------------------------------------
# Helper: Find items by keywords
# -----------------------------------------------------------
def find_items(keywords):
    params = {
        "OPERATION-NAME": "findItemsByKeywords",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": EBAY_API_KEY,
        "RESPONSE-DATA-FORMAT": "JSON",
        "REST-PAYLOAD": "",
        "keywords": keywords,
    }
    r = requests.get(SEARCH_URL, params=params)
    try:
        return r.json()["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"]
    except KeyError:
        return []

# -----------------------------------------------------------
# Helper: Get extra details (to check for Allstate / features)
# -----------------------------------------------------------
def get_item_details(itemId):
    detail_params = {
        "callname": "GetSingleItem",
        "responseencoding": "JSON",
        "appid": EBAY_API_KEY,
        "siteid": "0",
        "version": "967",
        "ItemID": itemId,
        "IncludeSelector": "ItemSpecifics,Description",
    }
    d = requests.get(DETAIL_URL, params=detail_params).json()
    return d.get("Item", {})

# -----------------------------------------------------------
# Laptop search (RTX 4070, 4080, 5070) — requires Allstate
# -----------------------------------------------------------
def search_laptops():
    items = find_items("RTX 5070 laptop")
    matches = []
    for item in items:
        title = item["title"][0]
        url = item["viewItemURL"][0]
        price = item["sellingStatus"][0]["currentPrice"][0]["__value__"]
        itemId = item["itemId"][0]

        details = get_item_details(itemId)
        description = details.get("Description", "").lower()
        subtitle = details.get("Subtitle", "").lower()

        if any(x in description or x in subtitle for x in ["allstate", "2-year protection", "protection plan"]):
            matches.append(f"[Laptop] {title} - ${price}\n{url}")

    return matches

# -----------------------------------------------------------
# Monitor search (Curved OLED 32/34 inch, ≥100hz, speakers)
# -----------------------------------------------------------
def search_monitors():
    items = find_items("Curved OLED Monitor 32 OR 34 inch 100hz speakers")
    matches = []
    for item in items:
        title = item["title"][0].lower()
        url = item["viewItemURL"][0]
        price = item["sellingStatus"][0]["currentPrice"][0]["__value__"]
        itemId = item["itemId"][0]
        
        details = get_item_details(itemId)
        description = details.get("Description", "").lower()
        specifics = details.get("ItemSpecifics", {}).get("NameValueList", [])

        # Basic keyword filters
        if "oled" in title or "oled" in description:
            if any(x in title or x in description for x in ["32", "34"]):
                if "100hz" in title or "100 hz" in description or "100hz" in description:
                    if "speaker" in title or "speaker" in description:
                        if price < 400:
                            matches.append(f"[Monitor] {item['title'][0]} - ${price}\n{url}")

    return matches

# -----------------------------------------------------------
# Run both searches
# -----------------------------------------------------------
laptop_matches = search_laptops()
monitor_matches = search_monitors()

all_matches = laptop_matches + monitor_matches

# -----------------------------------------------------------
# Email results
# -----------------------------------------------------------
if all_matches:
    msg = "Subject: eBay Matches Found!\n\n" + "\n\n".join(all_matches)
else:
    msg = "Subject: No matching laptops or monitors today.\n\nChecked eBay, nothing matched."

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, EMAIL_TO, msg.encode("utf-8"))
