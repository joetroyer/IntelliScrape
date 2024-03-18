import streamlit as st
import requests
from bs4 import BeautifulSoup
from utils.get_gpt_response import get_gpt_response
import validators
import json
from utils.prompts import (SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_SELECTORS,
                           USER_REQUEST_FOR_GETTING_THE_DESIRED_SELECTORS,
                           SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT,
                           USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT,
                           SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_XPATHS,  # Import the new XPath prompts
                           USER_REQUEST_FOR_GETTING_THE_DESIRED_XPATHS,
                           SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_XPATHS_CONTENT,
                           USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_XPATHS_CONTENT)
from lxml import etree
from typing import Dict, Any
from utils.selector_utils import summarize_body_using_dict_method
from utils.ascii_utils import summarize_body_using_ascii_tree
from utils.selector_utils import TAGS_TO_DECOMPOSE
from utils.ensure_limit import reduce_string_to_token_limit
import re

# Set page title and icon
st.set_page_config(
    page_title="Intelli Scrape - Approach 2",
    page_icon=":robot_face:"
)

def summarize_body_using_xpath_method(html_content: str, max_content_length: int = 70) -> Dict[str, Any]:
    result_dict = {}
    
    # Initialize BeautifulSoup to decompose unnecessary tags
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup(TAGS_TO_DECOMPOSE):
        tag.decompose()
    
    # Only process the <body> tag, if it exists
    body = soup.body if soup.body else soup
    html_content = str(body)
    
    # Parse the HTML content and create an ElementTree object
    tree = etree.HTML(html_content)
    tree = etree.ElementTree(tree)

    def process_element(element, result_dict, include_siblings=True):
        xpath = tree.getpath(element)
        # Normalize the xpath by removing list indices and keeping only the first sibling
        xpath = re.sub(r'\[\d+\]', '[1]', xpath)
        if xpath not in result_dict:
            result_dict[xpath] = {'content': [], 'children': {}}
            # Add class attribute if it exists
            class_name = element.get('class')
            if class_name:
                result_dict[xpath]['class'] = ' '.join(class_name).replace(' ', '')
        text = (element.text or '').strip()
        if text:
            # Truncate the text if it's longer than max_content_length
            truncated_text = text[:max_content_length] + '...' if len(text) > max_content_length else text
            result_dict[xpath]['content'].append(truncated_text)
        # Process only the first child of each type
        unique_children = {}
        for child in element:
            child_xpath = tree.getpath(child)
            child_tag = child_xpath.split('/')[-1]
            # If we haven't processed this type of child yet, do so now
            if child_tag not in unique_children:
                unique_children[child_tag] = True
                process_element(child, result_dict[xpath]['children'], include_siblings=False)

    process_element(tree.getroot(), result_dict)

    def clean_dict(d):
        if isinstance(d, dict):
            cleaned = {k: clean_dict(v) for k, v in d.items() if v}
            if 'content' in cleaned:
                # Filter out empty strings and truncate the list to the first two items
                cleaned['content'] = [item for item in cleaned['content'] if item.strip()][:2]
            if 'children' in cleaned and not cleaned['children']:
                del cleaned['children']  # Remove empty children dicts
            return cleaned if cleaned else None  # Remove empty dicts
        return d

    cleaned_result_dict = clean_dict(result_dict)
    return cleaned_result_dict if cleaned_result_dict else {}

def scrape_content_using_xpath(html_content, xpath_dict):
    scraped_content = {}
    tree = etree.HTML(html_content)

    for label, xpath in xpath_dict.items():
        try:
            elements = tree.xpath(xpath)
            # Extract text content from each element found by the XPath
            scraped_content[label] = [element.text for element in elements if element.text]
        except Exception as e:
            print(f"Error processing XPath {xpath} for label {label}: {e}")

    return scraped_content

def scrape_content_using_selectors(html_content, selectors):
    scraped_content = {}
    # Initialize BeautifulSoup with the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
   
    def scrape_nested(soup, selectors, content_dict):
        for name, selector in selectors.items():
            try:
                if isinstance(selector, dict):  # Nested structure
                    content_dict[name] = {}
                    scrape_nested(soup, selector, content_dict[name])
                elif isinstance(selector, list):  # Selector is a list
                    # Concatenate list elements to form a selector string
                    selector_string = ' '.join(selector)
                    elements = soup.select(selector_string)
                    content = [element.get_text(strip=True) for element in elements]
                    content_dict[name] = content
                else:  # Selector is a string
                    elements = soup.select(selector)
                    content = [element.get_text(strip=True) for element in elements]
                    content_dict[name] = content
            except Exception as e:
                # Log the error and continue with the next selector
                print(f"Error processing selector {name}: {e}")
                content_dict[name] = []

    scrape_nested(soup, selectors, scraped_content)
    return scraped_content

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

def scrape_body_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            html_content_scrapped = response.content
            soup = BeautifulSoup(html_content_scrapped, 'html.parser')
            # Extract content within the <body> tag
            body_content = soup.body if soup.body else soup
            return html_content_scrapped, body_content
        else:
            st.error(f"Error scraping HTML content from URL: HTTP {response.status_code} returned")
            return None, None
    except Exception as e:
        st.error(f"Error scraping HTML content from URL: {str(e)}")
        return None, None

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

        # Input for URL or File Upload
        st.session_state['summarizing_method'] = st.radio("Choose Input Type:",
                               ("Summarize body through CSS Selectors method","Summarize body through XML Xpaths method","Summarize body through ASCII tree method"),captions = ["Consumes less amount of tokens.", "", "Very token-hungry"],index=0)
        
        if st.button("Scrape and Analyze"):
            # st.info(instruction)
            if instruction:
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

                if html_content:

                    with st.expander(label="Summarized Selectors"):
                        if st.session_state.summarizing_method == "Summarize body through JSON method":
                            summarized_dict = summarize_body_using_dict_method(html_content)
                            st.json(summarized_dict)
                        elif st.session_state.summarizing_method == "Summarize body through XML method":
                            summarized_dict = summarize_body_using_xpath_method(html_content=str(html_content))
                            st.json(summarized_dict)
                        else:
                            summarized_dict = summarize_body_using_ascii_tree(html_content)
                            st.markdown(summarized_dict)

                    if st.session_state['summarizing_method'] == "Summarize body through XML method":
                        # Use XPath prompts
                        reduced_dict = reduce_string_to_token_limit(json.dumps(summarized_dict))
                        user_request_for_desired_selectors = USER_REQUEST_FOR_GETTING_THE_DESIRED_XPATHS.replace(
                            "<<INSTRUCTION>>", instruction).replace("<<XPATHS_TO_CONTENT_MAPPING>>", reduced_dict)

                        desired_selectors = get_gpt_response(
                            user_request=user_request_for_desired_selectors, system_prompt=SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_XPATHS)
                        
                        with st.expander(label="Desired Selectors GPT"):
                            st.json(desired_selectors)

                        if html_content_raw:
                            scraped_content_after_applying_selectors = scrape_content_using_xpath(
                                html_content=html_content_raw, xpath_dict=desired_selectors)

                            with st.expander(label="Scrapped Content after applying Selectors"):
                                st.json(scraped_content_after_applying_selectors)

                            user_request_for_enhancing_scrapped_content = USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_XPATHS_CONTENT.replace(
                                "<<INSTRUCTION>>", instruction).replace("<<RAW_SCRAPPED_CONTENT_DICT>>", json.dumps(scraped_content_after_applying_selectors))

                            enhanced_scrapped_content = get_gpt_response(
                                user_request=user_request_for_enhancing_scrapped_content, system_prompt=SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_XPATHS_CONTENT)
                            
                            with st.expander(label="Enhanced Content"):
                                st.json(enhanced_scrapped_content)
                    else:
                        reduced_dict = reduce_string_to_token_limit(json.dumps(summarized_dict))
                        user_request_for_desired_selectors = USER_REQUEST_FOR_GETTING_THE_DESIRED_SELECTORS.replace(
                            "<<INSTRUCTION>>", instruction).replace("<<SELECTORS_TO_CONTENT_MAPPING>>", reduced_dict)

                        desired_selectors = get_gpt_response(
                            user_request=user_request_for_desired_selectors, system_prompt=SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_SELECTORS)

                        with st.expander(label="Desired Selectors GPT"):
                            st.json(desired_selectors)

                        if html_content_raw:
                            scraped_content_after_applying_selectors = scrape_content_using_selectors(
                                html_content=html_content_raw, selectors=desired_selectors)

                            with st.expander(label="Scrapped Content after applying Selectors"):
                                st.json(scraped_content_after_applying_selectors)

                            user_request_for_enhancing_scrapped_content = USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT.replace(
                                "<<INSTRUCTION>>", instruction).replace("<<RAW_SCRAPPED_CONTENT_DICT>>", json.dumps(scraped_content_after_applying_selectors))

                            # st.warning(f"prompt: {user_request_for_enhancing_scrapped_content}")

                            enhanced_scrapped_content = get_gpt_response(
                                user_request=user_request_for_enhancing_scrapped_content, system_prompt=SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT)

                            with st.expander(label="Enhanced Content"):
                                st.json(enhanced_scrapped_content)

            else:
                st.error("Please enter instructions.")

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()