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

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"
        }

        self.last_post_path = "data/last_post.txt"

    def fetch_html(self):
        # Building the Instagram profile URL using self.username
        url = f"https://www.instagram.com/{self.username}/"
        
        try:
            # Make a GET request with self.headers
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            logging.info(f"Fetched HTML for {self.username}")
            # Return the HTML content of the response
            return response.text
        except requests.RequestException as e:
            logging.error(f"Failed to fetch Instagram page: {e}")
            raise ConnectionError(f"Failed to fetch Instagram page: {e}")

    def parse_html(self, html):
        # Create a BeautifulSoup object from the HTML
        soup = BeautifulSoup(html, "html.parser")
        
        # Find the script tag containing JSON data
        script_tag = soup.find("script", {"type": "application/ld+json"})
        
        if not script_tag:
            logging.error("Could not find JSON data in Instagram page")
            raise ValueError("Could not find JSON data in Instagram page")
            
        # Extract the JSON data from the script tag
        try:
            json_data = json.loads(script_tag.string)
            logging.info("Parsed JSON data from Instagram page")
            return json_data
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON data from Instagram page")
            raise ValueError("Failed to parse JSON data from Instagram page")
    
    def get_latest_post(self):
        #Fetch the HTML content of the Instagram profile
        html = self.fetch_html()

        #Parse the HTML to extract the JSON data
        json_data = self.parse_html(html)

        #Extract the latest post from the JSON data
        latest_post = json_data["itemListElement"][0]["item"]

        #Return the latest post
        return latest_post

    def store_post(self, post_url):
        #Open the last_post.txt file in write mode
        with open(self.last_post_path, "w") as f:
            #Write the post URL to the file
            f.write(post_url)
        logging.info(f"Stored new post URL: {post_url}")

    def get_stored_post(self):
        #Check if the file exists
        if not os.path.exists(self.last_post_path):
            logging.info("No stored post found")
            return None
        with open(self.last_post_path, "r") as f:
            post_url = f.read().strip()
            logging.info(f"Retrieved stored post URL: {post_url}")
            return post_url

    def is_new_post(self, post_data):
        #Get the stored post
        stored_post = self.get_stored_post()

        #If there is no stored post, return True
        if not stored_post:
            logging.info("No stored post, treating as new post")
            return True
        
        #If the post URL is different from the stored post, return True
        if post_data["url"] != stored_post:
            logging.info("Detected a new post")
            return True
        
        #Otherwise, return False
        logging.info("No new post detected")
        return False

    def check_for_update(self):
        latest = self.get_latest_post()
        latest_url = latest["url"]

        if self.is_new_post(latest):
            self.store_post(latest_url)
            logging.info(f"New post detected and stored: {latest_url}")
            return latest_url

        logging.info("No update found")
        return None

 