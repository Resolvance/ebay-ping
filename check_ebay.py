import os
import smtplib
import requests

# Secrets
EBAY_API_KEY = os.getenv("EBAY_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

# eBay Finding API
SEARCH_URL = "https://svcs.ebay.com/services/search/FindingService/v1"
DETAIL_URL = "https://open.api.ebay.com/shopping"

params = {
    "OPERATION-NAME": "findItemsByKeywords",
    "SERVICE-VERSION": "1.0.0",
    "SECURITY-APPNAME": EBAY_API_KEY,
    "RESPONSE-DATA-FORMAT": "JSON",
    "REST-PAYLOAD": "",
    "keywords": "RTX 5070 laptop"
}

r = requests.get(SEARCH_URL, params=params)
results = r.json()

matches = []

try:
    items = results["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"]
    for item in items:
        title = item["title"][0]
        url = item["viewItemURL"][0]
        price = item["sellingStatus"][0]["currentPrice"][0]["__value__"]
        itemId = item["itemId"][0]

        # 🔍 Second API call to get detailed info
        detail_params = {
            "callname": "GetSingleItem",
            "responseencoding": "JSON",
            "appid": EBAY_API_KEY,
            "siteid": "0",
            "version": "967",
            "ItemID": itemId,
            "IncludeSelector": "ItemSpecifics"
        }
        d = requests.get(DETAIL_URL, params=detail_params).json()

        item_details = d.get("Item", {})
        description = item_details.get("Description", "")
        subtitle = item_details.get("Subtitle", "")

        # Check if Allstate Protection is mentioned
        if "allstate" in description.lower() or "allstate" in subtitle.lower():
            matches.append(f"{title} - ${price}\n{url}")

except KeyError:
    pass  # No items found

# Email results
if matches:
    msg = "Subject: RTX 5070 Laptops with Allstate Warranty!\n\n" + "\n\n".join(matches)
else:
    msg = "Subject: No RTX 5070 laptops with Allstate warranty today.\n\nChecked eBay, nothing matched."

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, EMAIL_TO, msg.encode("utf-8"))
