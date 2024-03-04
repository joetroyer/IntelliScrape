import streamlit as st
import requests
from bs4 import BeautifulSoup
import html2text
from openai import OpenAI
from dotenv import load_dotenv
import validators
from urllib.parse import urlsplit
import json
from utils.prompts import (SYSTEM_PROMPT_DEFAULT,
                           SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_SELECTORS,
                           USER_REQUEST_FOR_GETTING_THE_DESIRED_SELECTORS,
                           USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT, SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT)
from utils.get_gpt_response import get_gpt_response

# Set page title and icon
st.set_page_config(
    page_title="Intelli Scrape - Approach 2",
    page_icon=":robot_face:"
)


# def scrape_content_using_selectors(html_content, selectors):
#     try:
#         # Initialize BeautifulSoup with the HTML content
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # Dictionary to store scraped content
#         scraped_content = {}

#         # Iterate through each selector and extract content
#         for name, selector in selectors.items():
#             elements = soup.select(selector)
#             # Extract text content from each selected element
#             content = [element.get_text(strip=True) for element in elements]
#             # Store the content in the dictionary with the selector as the key
#             scraped_content[name] = content

#         return scraped_content
#     except Exception as e:
#         st.error(f"Error during content scraping: {str(e)}")
#         return {}

def scrape_content_using_selectors(html_content, selectors):
    scraped_content = {}
    # Initialize BeautifulSoup with the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    def scrape_nested(soup, selectors, content_dict):
        for name, selector in selectors.items():
            if isinstance(selector, dict):  # Nested structure
                content_dict[name] = {}
                scrape_nested(soup, selector, content_dict[name])
            else:
                elements = soup.select(selector)
                content = [element.get_text(strip=True) for element in elements]
                content_dict[name] = content

    scrape_nested(soup, selectors, scraped_content)
    return scraped_content

def truncate_text(text):
    return text[:70]


# def process_tag(tag, result_dict):
#     try:
#         # Remove empty lines
#         for element in tag.find_all():
#             if element.attrs:
#                 # Keep only class, id, and href attributes
#                 element_attrs = {
#                     key: value
#                     for key, value in element.attrs.items()
#                     if key in ['class', 'id'] and ('nav' not in value if isinstance(value, str) else all('nav' not in v for v in value))
#                 }
#                 class_name = element_attrs.get('class')
#                 if class_name and tuple(class_name) not in result_dict:
#                     key = ' '.join(class_name)
#                     result_dict[key] = truncate_text(
#                         element.get_text(strip=True))

#             if element.name in ['img', 'iframe', 'input', 'script', 'style', 'meta', 'link', 'comment', 'head', 'footer', 'nav', 'form', 'noscript']:
#                 element.decompose()
#             elif element.string:
#                 element.string.replace_with(
#                     truncate_text(element.string.strip()))
#             elif element.string and not len(element.string.strip()):
#                 element.decompose()
#     except Exception as e:
#         st.warning(f"Error during tag processing: {str(e)}")


# def summarize_body(html_content):
#     result_dict = {}
#     process_tag(html_content, result_dict)
#     return result_dict

def summarize_body(soup):
    # st.success("inside summarize body")
    # st.success(html_content)
    result_dict = {}
    # soup = BeautifulSoup(html_content, 'html.parser')
    # st.warning(soup)
    def process_tag(tag, result_dict):
        # st.success('inside process tag')
        if tag.name not in ['script', 'style', 'meta', 'link', 'comment', 'head', 'footer', 'nav', 'form', 'noscript']:
            # Create a key for the tag if it has a class or id
            key = None
            if 'class' in tag.attrs:
                key = 'class: ' + ' '.join(tag['class'])
            elif 'id' in tag.attrs:
                key = 'id: ' + tag['id']

            # If the key exists, create a nested structure
            if key:
                if key not in result_dict:
                    result_dict[key] = {'content': [], 'children': {}}
                result_dict[key]['content'].append(truncate_text(tag.get_text(strip=True)))
                for child in tag.children:
                    if child.name:
                        process_tag(child, result_dict[key]['children'])
            else:
                # Process children tags
                for child in tag.children:
                    if child.name:
                        process_tag(child, result_dict)

    # Start processing from the body tag
    process_tag(soup.body if soup.body else soup, result_dict)
    return result_dict

# @st.cache_data


def extract_base_url(url):
    try:
        parsed_url = urlsplit(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url
    except Exception as e:
        st.error(f"Error extracting base URL: {str(e)}")
        return None

# @st.cache_data


def validate_url(url):
    try:
        return validators.url(url)
    except Exception as e:
        st.error(f"Error validating URL: {str(e)}")
        return False


def scrape_body_from_html(html_content_raw):
    try:
        soup = BeautifulSoup(html_content_raw, 'html.parser')
        # Extract content within the <body> tag
        body_content = soup.body if soup.body else soup
        return html_content_raw, body_content
    except Exception as e:
        st.error(f"Error during HTML content extraction: {str(e)}")
        return None, None

# @st.cache_data


def scrape_body_from_url(url):
    try:
        # Use requests to get HTML content
        html_content_scrapped = requests.get(url).content
        soup = BeautifulSoup(html_content_scrapped, 'html.parser')
        # Extract content within the <body> tag
        body_content = soup.body if soup.body else soup
        return html_content_scrapped, body_content
    except Exception as e:
        st.error(f"Error scraping HTML content from URL: {str(e)}")
        return None, None

# Function to scrape and convert HTML to Markdown


@st.cache_data
def scrape_and_convert(html_content, base_url=None):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Extract content within the <body> tag
        body_content = soup.body if soup.body else soup
        markdown_content = html2text.html2text(
            str(body_content), baseurl=base_url)
        return markdown_content
    except Exception as e:
        st.error(f"Error during HTML to Markdown conversion: {str(e)}")
        return ""

def main():
    try:
        # Page layout with title
        st.title("Intelli Scrape - CSS Selectors Approach")

        # Input for URL or File Upload
        url_or_file = st.radio("Choose Input Type:",
                               ("URL", "Upload HTML File"))

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
                    if validate_url(url):
                        html_content_raw, html_content = scrape_body_from_url(
                            url=url)
                    else:
                        st.error("Invalid URL. Please enter a valid URL.")
                        return
                else:
                    st.error("Please enter a URL.")
                    return
            elif url_or_file == "Upload HTML File" and uploaded_file:
                if uploaded_file.name.endswith(".html") or uploaded_file.name.endswith(".htm"):
                    # Read HTML content from the uploaded file
                    html_content_raw = uploaded_file.read()
                    html_content_raw, html_content = scrape_body_from_html(
                        html_content_raw=html_content_raw)
                else:
                    st.error("Please enter upload a valid HTML file.")
                    return
            else:
                st.error("Please enter a URL or upload an HTML file.")
                return

            with st.expander(label="Raw HTML Content"):
                st.markdown(html_content)

            summarized_dict = summarize_body(html_content)

            user_request_for_desired_selectors = USER_REQUEST_FOR_GETTING_THE_DESIRED_SELECTORS.replace(
                "<<INSTRUCTION>>", instruction).replace("<<SELECTORS_TO_CONTENT_MAPPING>>", json.dumps(summarized_dict))

            with st.expander(label="Summarized Selectors"):
                st.json(summarized_dict)

            desired_selectors = get_gpt_response(
                user_request=user_request_for_desired_selectors, system_prompt=SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_SELECTORS)

            with st.expander(label="Desired Selectors GPT"):
                st.json(desired_selectors)

            scraped_content_after_applying_selectors = scrape_content_using_selectors(
                html_content=html_content_raw, selectors=desired_selectors)

            with st.expander(label="Scrapped Content after applying Selectors"):
                st.json(scraped_content_after_applying_selectors)

            user_request_for_enhancing_scrapped_content = USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT.replace(
                "<<INSTURCTION>>", instruction).replace("<<RAW_SCRAPPED_CONTENT_DICT>>", json.dumps(scraped_content_after_applying_selectors))

            # st.success(user_request_for_enhancing_scrapped_content)

            enhanced_scrapped_content = get_gpt_response(
                user_request=user_request_for_enhancing_scrapped_content, system_prompt=SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT)

            with st.expander(label="Enhanced Content"):
                st.json(enhanced_scrapped_content)

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
