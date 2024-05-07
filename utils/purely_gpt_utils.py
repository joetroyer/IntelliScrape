import streamlit as st
from bs4 import BeautifulSoup
import html2text
from utils.ensure_limit import reduce_string_to_token_limit
from utils.prompts import (USER_REQUEST_FOR_JSON_SCHEMA, SYSTEM_PROMPT_FOR_GETTING_JSON_SCHEMA, USER_REQUEST_FOR_STRUCTURED_CONTENT, SYSTEM_PROMPT_FOR_DATA_EXTRACTION_ACCORDING_TO_THE_JSON_SCHEMA)
from utils.get_gpt_response_json import get_gpt_response_json

# @st.cache_data
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

def process_using_approach_1(raw_html_content, instruction, base_url=None):
    try:
        # Scrape and convert HTML to Markdown
        markdown_content = scrape_and_convert(html_content=raw_html_content, base_url=base_url)
        with st.expander(label="Scraped Raw Markdown Content"):
            st.markdown(markdown_content)

        # Reduce content to fit token limit if necessary
        markdown_content = reduce_string_to_token_limit(markdown_content)

        # Generate JSON schema based on user instruction
        user_request_json_schema = USER_REQUEST_FOR_JSON_SCHEMA.replace(
            "<<INSTRUCTION>>", instruction).replace("<<SCRAPED_CONTENT>>", markdown_content)
        json_schema = get_gpt_response_json(
            user_request=user_request_json_schema, system_prompt=SYSTEM_PROMPT_FOR_GETTING_JSON_SCHEMA)

        with st.expander(label="JSON Schema"):
            st.json(json_schema)

        # Extract structured content based on JSON schema
        user_request_for_structured_content = USER_REQUEST_FOR_STRUCTURED_CONTENT.replace(
            "<<JSON_SCHEMA>>", str(json_schema)).replace("<<INSTRUCTION>>", instruction).replace("<<SCRAPED_CONTENT>>", markdown_content)
        extracted_structured_content = get_gpt_response_json(
            user_request=user_request_for_structured_content, system_prompt=SYSTEM_PROMPT_FOR_DATA_EXTRACTION_ACCORDING_TO_THE_JSON_SCHEMA)

        with st.expander(label="Extracted Structured Content"):
            st.json(extracted_structured_content)

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")