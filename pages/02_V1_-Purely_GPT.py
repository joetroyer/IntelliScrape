import streamlit as st
from bs4 import BeautifulSoup
import html2text
import validators
from urllib.parse import urlsplit
from utils.enhance_instructions import enhance_user_instructions
from utils.prompts import (SYSTEM_PROMPT_FOR_GETTING_JSON_SCHEMA,
                           SYSTEM_PROMPT_FOR_DATA_EXTRACTION_ACCORDING_TO_THE_JSON_SCHEMA, SYSTEM_PROMPT_DEFAULT, USER_REQUEST_FOR_JSON_SCHEMA, USER_REQUEST_FOR_STRUCTURED_CONTENT)
from utils.get_gpt_response_json import get_gpt_response_json
from utils.ensure_limit import reduce_string_to_token_limit
from utils.scrape_html_using_scrapenetwork import scrape_body_from_url
# Set page title and icon
st.set_page_config(
    page_title="Intelli Scrape - Approach 1",
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

@st.cache_data
def validate_url(url):
    try:
        return validators.url(url)
    except Exception as e:
        st.error(f"Error validating URL: {str(e)}")
        return False

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

def main():
    try:
        # Page layout with title
        st.title("Intelli Scrape")

        # Input for URL or File Upload
        url_or_file = st.radio("Choose Input Type:", ("URL", "Upload HTML File"))

        if url_or_file == "URL":
            url = st.text_input(
                "Enter URL:", placeholder="https://books.toscrape.com")
        else:
            uploaded_file = st.file_uploader("Upload HTML file", type=["html"])

        # Input for instructions
        instruction = st.text_area(
            "Enter Instructions:", placeholder="I need a list of all the books and their respective prices on this page.")

        if st.button("Scrape and Analyze"):
            instruction = enhance_user_instructions(instruction)
            st.info(f"Enhanced user instructions:\n\n{instruction}")
            if url_or_file == "URL":
                if url:
                    # Validate the URL
                    if validate_url(url):
                        base_url = extract_base_url(url)
                        html_content = scrape_body_from_url(url=url)
                        # st.success(html_content)
                        # Scrape and convert HTML to Markdown
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

            markdown_content = reduce_string_to_token_limit(markdown_content)

            user_request_json_schema = USER_REQUEST_FOR_JSON_SCHEMA.replace(
                "<<INSTRUCTION>>", instruction).replace("<<SCRAPED_CONTENT>>", markdown_content)

            json_schema = get_gpt_response_json(
                user_request=user_request_json_schema, system_prompt=SYSTEM_PROMPT_FOR_GETTING_JSON_SCHEMA)

            with st.expander(label="JSON Schema"):
                st.json(json_schema)

            user_request_for_structured_content = USER_REQUEST_FOR_STRUCTURED_CONTENT.replace(
                "<<JSON_SCHEMA>>", str(json_schema)).replace("<<INSTRUCTION>>", instruction).replace("<<SCRAPED_CONTENT>>", markdown_content)

            extracted_structured_content = get_gpt_response_json(
                user_request=user_request_for_structured_content, system_prompt=SYSTEM_PROMPT_FOR_DATA_EXTRACTION_ACCORDING_TO_THE_JSON_SCHEMA)

            with st.expander(label="Extracted Structured Content"):
                st.json(extracted_structured_content)

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()