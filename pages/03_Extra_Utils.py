import streamlit as st
import requests
from bs4 import BeautifulSoup
import html2text
import validators
from urllib.parse import urlsplit

from utils.prompts import (SYSTEM_PROMPT_FOR_PAGINATION_REQUEST, USER_REQUEST_FOR_PAGINATION_LINKS)
from utils.get_gpt_response import get_gpt_response

# Set page title and icon
st.set_page_config(
    page_title="Intelli Scrape - Extras",
    page_icon=":robot_face:"
)

@st.cache_data
def extract_base_url(url):
    try:
        parsed_url = urlsplit(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url
    except Exception as e:
        st.error(f"Error extracting base URL: {str(e)}")
        return None

# @st.cache_data
def scrape_body_from_url(url):
    try:
        # Use requests to get HTML content
        html_content_scrapped = requests.get(url).content
        return html_content_scrapped
    except Exception as e:
        st.error(f"Error scraping HTML content from URL: {str(e)}")
        return None

@st.cache_data
def scrape_and_convert(html_content, base_url=None):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Extract content within the <body> tag
        body_content = soup.body if soup.body else soup
        markdown_content = html2text.html2text(str(body_content), baseurl=base_url)
        return markdown_content
    except Exception as e:
        st.error(f"Error during HTML to Markdown conversion: {str(e)}")
        return ""


# @st.cache_data
def validate_url(url):
    try:
        return validators.url(url)
    except Exception as e:
        st.error(f"Error validating URL: {str(e)}")
        return False


def main():
    try:
        # Page layout with title
        st.title("Intelli Scrape")

        # Sidebar with app info
        st.sidebar.info(
            "This tool allows you to analyze the content of an HTML page, "
            "checking for pagination. Whether you input a URL or upload an HTML file, the app extracts "
            "and converts the content to Markdown. It then identifies pagination links and provides a JSON output."
        )

        # Input for URL or File Upload
        url_or_file = st.radio("Choose Input Type:", ("URL", "Upload HTML File"))

        if url_or_file == "URL":
            url = st.text_input(
                "Enter URL:", placeholder="https://books.toscrape.com")
        else:
            uploaded_file = st.file_uploader("Upload HTML file", type=["html"])

        if st.button("Process"):
            if url_or_file == "URL":
                if url:
                    # Validate the URL
                    if validate_url(url):
                        base_url = extract_base_url(url)
                        html_content = scrape_body_from_url(url=url)
                        markdown_content = scrape_and_convert(
                            html_content=html_content, base_url=base_url)
                    else:
                        st.error("Invalid URL. Please enter a valid URL.")
                        return
                else:
                    st.error("Please enter a URL.")
                    return
            elif url_or_file == "Upload HTML File" and uploaded_file:
                if uploaded_file.name.endswith(".html") or uploaded_file.name.endswith(".htm"):
                    base_url = extract_base_url(url=uploaded_file.name)
                    # Read HTML content from the uploaded file
                    html_content = uploaded_file.read()
                    # Scrape and convert HTML to Markdown
                    markdown_content = scrape_and_convert(html_content)
                else:
                    st.error("Please enter upload a valid HTML file.")
                    return
            else:
                st.error("Please enter a URL or upload an HTML file.")
                return

            with st.expander(label="Scraped Raw Markdown Content"):
                st.markdown(markdown_content)

            user_request = USER_REQUEST_FOR_PAGINATION_LINKS.replace("MARKDOWN_CONTENT",markdown_content)
            pagination_links = get_gpt_response(user_request=user_request,system_prompt=SYSTEM_PROMPT_FOR_PAGINATION_REQUEST)

            if len(pagination_links):
                with st.expander(label="Pagination Links"):
                    st.json(pagination_links)
            else:
                st.info("No pagination links found on the page.")

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()