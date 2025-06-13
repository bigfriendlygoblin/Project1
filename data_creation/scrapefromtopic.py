from playwright.sync_api import sync_playwright
import json
import os
import time
from datetime import datetime

TOPIC_LIST_FILE = "filtered_topics.json"
OUTPUT_DIR = "topic_posts"
SCROLL_DELAY = 2

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def load_cookies(context):
    cookies_path = "cookies.json"
    if os.path.exists(cookies_path):
        with open(cookies_path, "r") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        print("✅ Loaded cookies.")

def wait_for_all_posts_to_load(page):
    last_count = -1
    stable_rounds = 0
    while stable_rounds < 3:
        page.keyboard.press("End")
        time.sleep(SCROLL_DELAY)
        posts = page.query_selector_all("div.topic-post")
        if len(posts) == last_count:
            stable_rounds += 1
        else:
            stable_rounds = 0
        last_count = len(posts)

def scrape_posts_from_topic(page, topic):
    print(f"🔍 Scraping topic: {topic['title']}")
    page.goto(topic["link"], timeout=60000)
    page.wait_for_selector("div.topic-post")
    wait_for_all_posts_to_load(page)

    posts = []
    post_elements = page.query_selector_all("div.topic-post")

    for post_elem in post_elements:
        try:
            content_elem = post_elem.query_selector("div.cooked")
            content = content_elem.inner_text().strip()

            author_elem = post_elem.query_selector("div.names a")
            author = author_elem.inner_text().strip() if author_elem else "Unknown"

            time_elem = post_elem.query_selector("time")
            time_str = time_elem.get_attribute("datetime") if time_elem else None
            timestamp = time_str if time_str else "Unknown"

            post_number = post_elem.get_attribute("data-post-number")
            is_reply = post_number != "1"

            posts.append({
                "author": author,
                "timestamp": timestamp,
                "is_reply": is_reply,
                "content": content
            })
        except Exception as e:
            print(f"⚠️ Failed to parse a post: {e}")

    return posts

def scrape_all_posts():
    ensure_output_dir()

    with open(TOPIC_LIST_FILE, "r", encoding="utf-8") as f:
        topics = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(user_data_dir="user_data", headless=False)
        page = browser.new_page()

        load_cookies(browser)
        input("⏸️ Log in manually if needed, then press ENTER to start scraping posts...")

        for topic in topics:
            try:
                posts = scrape_posts_from_topic(page, topic)
                output_path = os.path.join(OUTPUT_DIR, f"{topic['id']}.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "topic": topic,
                        "posts": posts
                    }, f, indent=2)
                print(f"✅ Saved {len(posts)} posts to {output_path}")
            except Exception as e:
                print(f"❌ Error scraping topic {topic['id']}: {e}")

        browser.close()

if __name__ == "__main__":
    scrape_all_posts()
