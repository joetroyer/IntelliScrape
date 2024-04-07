import requests
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

@st.cache_data
def scrape_body_from_url(url):
    try:
        # Use Scrapenetwork API to get HTML content
        api_url = "https://app.scrapenetwork.com/api"
        params = {
            'api_key': os.getenv("SCRAPENETWORK_API_KEY"),
            'request_url': url,
            'js_render': 'true'
        }
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        html_content_scrapped = response.content
        return html_content_scrapped
    except Exception as e:
        st.error(f"Error scraping HTML content from URL: {str(e)}")
        return None