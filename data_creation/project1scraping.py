import requests
import os
import re
from urllib.parse import urljoin

BASE_URL = "https://tds.s-anand.net/2025-01/"
SIDEBAR_URL = urljoin(BASE_URL, "_sidebar.md")
SAVE_DIR = "tds_content"

print(f"Fetching sidebar from {SIDEBAR_URL}...")
response = requests.get(SIDEBAR_URL)

if response.status_code != 200:
    print(f"❌ Failed to fetch sidebar.md (status {response.status_code})")
    exit()

sidebar_md = response.text
print("Raw sidebar markdown:")
print(sidebar_md[:500], "..." if len(sidebar_md) > 500 else "")

# Regex: match any .md link inside parentheses
links = re.findall(r'\((.*?)\.md\)', sidebar_md)
# add '.md' back to matches, remove duplicates
links = list(set(link + ".md" for link in links))

print(f"✅ Found {len(links)} markdown files:")

for l in links:
    print(" -", l)

os.makedirs(SAVE_DIR, exist_ok=True)

for link in links:
    # resolve relative url
    url = urljoin(BASE_URL, link)
    filename = os.path.join(SAVE_DIR, os.path.basename(link))
    print(f"⬇️ Downloading {url} -> {filename} ...")

    res = requests.get(url)
    if res.status_code == 200:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(res.text)
        print(f"✅ Saved {filename}")
    else:
        print(f"❌ Failed to download {url} (status {res.status_code})")

print("\n🎉 Done downloading all markdown files.")
	 