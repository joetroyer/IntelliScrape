import streamlit as st
import validators
from urllib.parse import urlsplit
from utils.prompts import (SYSTEM_PROMPT_FOR_SELECTING_APPROACH_DYNAMICALLY,
                           USER_REQUEST_FOR_SELECTING_APPROACH_DYNAMICALLY)
from utils.get_gpt_response import get_gpt_response
from utils.purely_gpt_utils import process_using_approach_1
from utils.scrape_html_using_scrapenetwork import scrape_body_from_url
from utils.css_selector_utils import process_using_approach_2
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Set page title and icon
st.set_page_config(
    page_title="Intelli Scrape - Dynamic Scraper",
    page_icon=":robot_face:"
)

def select_approach_dynamically(url, instruction):
    with st.spinner("Selecting approach dynamically"):
        user_request = USER_REQUEST_FOR_SELECTING_APPROACH_DYNAMICALLY.replace(
        "<<INSTRUCTION>>", instruction).replace("<<URL>>", url)
        st.write("Calling GPT")

        response = get_gpt_response(
            user_request=user_request, system_prompt=SYSTEM_PROMPT_FOR_SELECTING_APPROACH_DYNAMICALLY)
        approach = int(response['approach'])

    if approach == 1:
        st.success(f"Selected Approach: Purely GPT")
    else: 
        st.success(f"Selected Approach: CSS Selectors")
    
    return approach

def get_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def get_top_2_urls_out_of_the_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)
    
    url_tally = {}
    
    for link in links:
        url = link['href']
        if url.startswith("http://") or url.startswith("https://"):
            base_url = get_base_url(url)
            if base_url in url_tally:
                url_tally[base_url] += 1
            else:
                url_tally[base_url] = 1
    
    sorted_urls = sorted(url_tally.items(), key=lambda x: x[1], reverse=True)
    top_two_urls = ""
    for i, (base_url, count) in enumerate(sorted_urls[:2], 1):
        top_two_urls += f"{i}. {base_url}: {count} times\n"
    
    return top_two_urls

@st.cache_data
def extract_base_url(url):
    try:
        parsed_url = urlsplit(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url
    except Exception as e:
        st.error(f"Error extracting base URL: {str(e)}")
        return None

@st.cache_data
def validate_url(url):
    try:
        return validators.url(url)
    except Exception as e:
        st.error(f"Error validating URL: {str(e)}")
        return False
  
def main():
    try:
        # Page layout with title
        st.title("Intelli Scrape - Dynamic Approach")

        # Input for URL or File Upload
        url_or_file = st.radio("Choose Input Type:", ("URL", "Upload HTML File"))

        url = None
        instruction = None
        base_url = None  # Initialize base_url here

        if url_or_file == "URL":
            url = st.text_input(
                "Enter URL:", placeholder="https://books.toscrape.com")
        else:
            uploaded_file = st.file_uploader("Upload HTML file", type=["html"])

        # Input for instructions
        instruction = st.text_area(
            "Enter Instructions:", placeholder="I need a list of all the books and their respective prices on this page.")

        if st.button("Scrape and Analyze"):
            if url_or_file == "URL":
                if url:
                    # Validate the URL
                    if validate_url(url):
                        base_url = extract_base_url(url)
                        html_content = scrape_body_from_url(url=url)
                    else:
                        st.error("Invalid URL. Please enter a valid URL.")
                        return
                else:
                    st.error("Please enter a URL.")
                    return
            elif url_or_file == "Upload HTML File" and uploaded_file:
                if uploaded_file.name.endswith(".html") or uploaded_file.name.endswith(".htm"):
                    # Read HTML content from the uploaded file
                    html_content = uploaded_file.read()
                else:
                    st.error("Please enter upload a valid HTML file.")
                    return
            else:
                st.error("Please enter a URL or upload an HTML file.")
                return

            if html_content:
                if not url:
                    urls = get_top_2_urls_out_of_the_html(html_content=html_content)
                    approach = select_approach_dynamically(url=urls, instruction=instruction)
                else:
                    approach = select_approach_dynamically(url=url,instruction=instruction)
                if approach == 1:
                    if base_url:
                        process_using_approach_1(raw_html_content=html_content,instruction=instruction,base_url=base_url)
                    else:
                        process_using_approach_1(raw_html_content=html_content,instruction=instruction,base_url=None)
                else:
                    process_using_approach_2(raw_html_content=html_content,instruction=instruction)
                    
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()