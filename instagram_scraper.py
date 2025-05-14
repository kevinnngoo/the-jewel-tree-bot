"""
instagram_scraper.py

This file is responsible for handling all Instagram-related logic
for the THE-JEWEL-TREE-BOT project.

Goals:
    - Connect to the public Instragram profile @thejeweltreecollection
    - Fetch and parse the profile's HTML to extract the latest post
    - Compare the latest post with the previously saved one
    - Store the new post if it hasn't been saved before

Structure:
    - InstagramScraper class in order to encapuslate the logic
    - Methods will include:
    - fetch_html()
    - parse_html()
    - get_stored_post()
    - store_post()
    - compare_posts()
    - is_new_post()

    
This file does not send Discord messages directly — it simply
detects and tracks the latest post so the bot can act on it.
"""
import requests
import json
import os
import logging
import time
from bs4 import BeautifulSoup
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

class InstagramScraper:
    def __init__(self):
        # to store the username, headers dictionary, and path to last_post.txt file
        self.username = "thejeweltreecollection"
        self.api_token = os.getenv("APIFY_TOKEN")
        self.last_post_path = "data/last_post.txt"

    def get_latest_post(self):
        logging.info(f"Starting Apify scrape for @{self.username}")

        # 1. Start Apify run
        run_url = f"https://api.apify.com/v2/acts/apify~instagram-profile-scraper/runs?token={self.api_token}&memory=1024&timeout=60"
        payload = {
            "usernames": [self.username],
            "resultsLimit": 1,
            "includeFeed": True,
            "includeStories": False
        }

        try:
            run_response = requests.post(run_url, json=payload)
            run_response.raise_for_status()
            run_id = run_response.json()["data"]["id"]
        except Exception as e:
            logging.error(f"Failed to start Apify run: {e}")
            return None

        # 2. Wait for run to complete
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.api_token}"
        for _ in range(30):  # Wait up to 90s max
            status_response = requests.get(status_url)
            status = status_response.json()["data"]["status"]
            if status == "SUCCEEDED":
                break
            elif status == "FAILED":
                logging.error("Apify run failed.")
                return None
            time.sleep(3)
        else:
            logging.error("Apify run timed out.")
            return None

        # 3. Get dataset results
        dataset_url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={self.api_token}"
        try:
            results = requests.get(dataset_url).json()
            print("Apify API results:", results)  # Debug print
            if results and "latestPosts" in results[0] and results[0]["latestPosts"]:
                latest_post = results[0]["latestPosts"][0]
                post_url = f"https://www.instagram.com/p/{latest_post['shortCode']}/"

                return {"url": post_url}
            else:
                logging.error("No latestPosts found in Apify results.")
                return None
        except Exception as e:
            logging.error(f"Failed to extract latest post: {e}")
            return None

    def get_stored_post(self):
        if not os.path.exists(self.last_post_path):
            return None
        with open(self.last_post_path, "r") as f:
            return f.read().strip()

    def store_post(self, post_url):
        with open(self.last_post_path, "w") as f:
            f.write(post_url)
        logging.info(f"Stored post URL: {post_url}")

    def is_new_post(self, post_data):
        stored = self.get_stored_post()
        if not stored:
            logging.info("No stored post, treating this as new.")
            return True
        if post_data["url"] != stored:
            logging.info("Detected a new post.")
            return True
        logging.info("No new post.")
        return False

    def check_for_update(self):
        latest = self.get_latest_post()
        if not latest:
            return None
        latest_url = latest["url"]
        if self.is_new_post(latest):
            self.store_post(latest_url)
            return latest_url
        return None

