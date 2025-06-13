# image_scraper_playwright.py
import os
import json
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests

# ===== CONFIG =====
TOPIC_LIST_FILE = "filtered_topics.json"
IMAGE_OUTPUT_DIR = "scraped_images"
OUTPUT_MAP_FILE = "image_topic_map.json"
SCROLL_DELAY = 2  # optional if you want to scroll like in your post scraper

# ===== UTILS =====
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name)

def download_image(url, path):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            print(f"✅ Saved: {path}")
        else:
            print(f"❌ Failed ({r.status_code}) {url}")
    except Exception as e:
        print(f"❌ Exception downloading {url}: {e}")

# ===== SCRAPER =====
def scrape_images_from_topic(page, topic, image_topic_map):
    topic_id = topic["id"]
    topic_title = sanitize_filename(topic["title"]).replace(" ", "_")
    topic_url = topic["link"]

    print(f"\n📘 Scraping Topic: {topic_title} ({topic_id})")

    try:
        page.goto(topic_url, timeout=60000, wait_until="domcontentloaded")
        # Ensure we landed on the correct topic (Discourse sometimes redirects!)
        current_url = page.url
        if topic_id not in current_url:
            print(f"⚠️ Redirected to {current_url}, skipping topic {topic_id}")
            return

        page.wait_for_selector("img", timeout=10000)
        images = page.query_selector_all("img")
        saved_count = 0

        for i, img in enumerate(images):
            src = img.get_attribute("src")
            if not src or "emoji" in src or "avatar" in src:
                continue

            full_url = urljoin(topic_url, src)
            ext = os.path.splitext(urlparse(full_url).path)[-1] or ".jpg"
            filename = f"{topic_id}_img{i+1}{ext}"
            filepath = os.path.join(IMAGE_OUTPUT_DIR, filename)

            download_image(full_url, filepath)

            image_topic_map[filename] = {
                "topic_id": topic_id,
                "title": topic["title"],
                "link": topic["link"],
                "date": topic["date"],
                "local_path": filepath.replace("\\", "/")
            }

            saved_count += 1

        print(f"📷 {saved_count} images saved for topic {topic_id}")

    except Exception as e:
        print(f"❌ Error scraping topic {topic_id}: {e}")

# ===== MAIN =====
def scrape_all_images():
    ensure_dir(IMAGE_OUTPUT_DIR)

    with open(TOPIC_LIST_FILE, "r", encoding="utf-8") as f:
        all_topics = json.load(f)

    start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
    end_date = datetime.strptime("2025-04-14", "%Y-%m-%d")

    filtered_topics = [
        t for t in all_topics
        if start_date <= datetime.strptime(t["date"], "%Y-%m-%d") <= end_date
    ]

    image_topic_map = {}

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(user_data_dir="user_data", headless=False)
        page = browser.new_page()

        input("⏸️ Log in manually if needed, then press ENTER to start scraping images...")

        for topic in filtered_topics:
            try:
                scrape_images_from_topic(page, topic, image_topic_map)
            except Exception as e:
                print(f"❌ Skipping {topic['id']} due to error: {e}")

        browser.close()

    with open(OUTPUT_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(image_topic_map, f, indent=2)

    print(f"\n📝 Image-topic map saved to {OUTPUT_MAP_FILE}")

if __name__ == "__main__":
    scrape_all_images()
