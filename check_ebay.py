import os
import smtplib
import requests

# Get secrets from environment variables
EBAY_API_KEY = os.getenv("EBAY_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

SEARCH_URL = "https://svcs.ebay.com/services/search/FindingService/v1"

params = {
    "OPERATION-NAME": "findItemsByKeywords",
    "SERVICE-VERSION": "1.0.0",
    "SECURITY-APPNAME": EBAY_API_KEY,
    "RESPONSE-DATA-FORMAT": "JSON",
    "REST-PAYLOAD": "",
    "keywords": "RTX 5070 laptop Certified Refurbished"
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
        if "5070" in title and "Refurbished" in title:
            matches.append(f"{title} - ${price}\n{url}")
except KeyError:
    pass  # No items found

if matches:
    msg = "Subject: eBay RTX 5070 Laptop Found!\n\n" + "\n\n".join(matches)
else:
    msg = "Subject: No RTX 5070 laptops found today.\n\nChecked eBay, nothing yet."

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, EMAIL_TO, msg.encode("utf-8"))
