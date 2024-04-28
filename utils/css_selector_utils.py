import streamlit as st
from bs4 import BeautifulSoup
from utils.get_gpt_response import get_gpt_response
import json
from utils.prompts import (SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_SELECTORS,
                           USER_REQUEST_FOR_GETTING_THE_DESIRED_SELECTORS,
                           SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT,
                           USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT)

from utils.selector_utils import summarize_body_using_dict_method
from utils.ensure_limit import reduce_string_to_token_limit
from utils.scrape_html_using_scrapenetwork import scrape_body_from_url as scrape_util

def scrape_body_from_url(url):
    try:
        html_content_scrapped = scrape_util(url=url)
        soup = BeautifulSoup(html_content_scrapped, 'html.parser')
        # Extract content within the <body> tag
        body_content = soup.body if soup.body else soup
        return html_content_scrapped, body_content
    except Exception as e:
        st.error(f"Error scraping HTML content from URL: {str(e)}")
        return None, None

def scrape_body_from_html(html_content_raw):
    try:
        soup = BeautifulSoup(html_content_raw, 'html.parser')
        # Extract content within the <body> tag
        body_content = soup.body if soup.body else soup
        return html_content_raw, body_content
    except Exception as e:
        st.error(f"Error during HTML content extraction: {str(e)}")
        return None, None


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


def process_using_approach_2(raw_html_content, instruction):
    try:
        # Process the HTML content
        html_content_raw, html_content = scrape_body_from_html(raw_html_content)

        if html_content:
            with st.expander(label="Raw HTML Content"):
                st.markdown(html_content)

            # Summarize the HTML content using BeautifulSoup
            summarized_dict = summarize_body_using_dict_method(html_content)
            with st.expander(label="Summarized Selectors"):
                st.json(summarized_dict)

            # Generate the desired selectors
            reduced_dict = reduce_string_to_token_limit(json.dumps(summarized_dict))
            user_request_for_desired_selectors = USER_REQUEST_FOR_GETTING_THE_DESIRED_SELECTORS.replace(
                "<<INSTRUCTION>>", instruction).replace("<<SELECTORS_TO_CONTENT_MAPPING>>", reduced_dict)
            desired_selectors = get_gpt_response(
                user_request=user_request_for_desired_selectors, system_prompt=SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_SELECTORS)

            with st.expander(label="Desired Selectors GPT"):
                st.json(desired_selectors)

            # Scrape content using the generated selectors
            scraped_content_after_applying_selectors = scrape_content_using_selectors(
                html_content=html_content_raw, selectors=desired_selectors)

            with st.expander(label="Scrapped Content after applying Selectors"):
                st.json(scraped_content_after_applying_selectors)

            # Enhance the scraped content
            user_request_for_enhancing_scrapped_content = USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT.replace(
                "<<INSTRUCTION>>", instruction).replace("<<RAW_SCRAPPED_CONTENT_DICT>>", json.dumps(scraped_content_after_applying_selectors))
            enhanced_scrapped_content = get_gpt_response(
                user_request=user_request_for_enhancing_scrapped_content, system_prompt=SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT)

            with st.expander(label="Enhanced Content"):
                st.json(enhanced_scrapped_content)

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")