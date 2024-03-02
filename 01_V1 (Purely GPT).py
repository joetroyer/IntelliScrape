import streamlit as st
import requests
from bs4 import BeautifulSoup
import html2text
from openai import OpenAI
from dotenv import load_dotenv
import validators
from urllib.parse import urlsplit
from utils.prompts import (SYSTEM_PROMPT_FOR_GETTING_JSON_SCHEMA,
                           SYSTEM_PROMPT_FOR_DATA_EXTRACTION_ACCORDING_TO_THE_JSON_SCHEMA, SYSTEM_PROMPT_DEFAULT, USER_REQUEST_FOR_JSON_SCHEMA, USER_REQUEST_FOR_STRUCTURED_CONTENT)
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Set page title and icon
st.set_page_config(
    page_title="Intelli Scrape - Approach 1",
    page_icon=":robot_face:"
)


@st.cache_data
def extract_base_url(url):
    parsed_url = urlsplit(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url


@st.cache_data
def validate_url(url):
    return validators.url(url)

# Function to scrape and convert HTML to Markdown


@st.cache_data
def scrape_and_convert(html_content, base_url=None):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extract content within the <body> tag
    body_content = soup.body if soup.body else soup
    markdown_content = html2text.html2text(str(body_content), baseurl=base_url)
    return markdown_content

@st.cache_data
def get_gpt_response(user_request: str, system_prompt: str = SYSTEM_PROMPT_DEFAULT, model: str = "gpt-4-1106-preview"):
    result = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request}
        ],
        model=model,
        response_format={"type": "json_object"}
    )
    return json.loads(result.choices[0].message.content.strip())

def main():

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
        if url_or_file == "URL":
            if url:
                # Validate the URL
                if validate_url(url):
                    base_url = extract_base_url(url)
                    # Scrape and convert HTML to Markdown
                    markdown_content = scrape_and_convert(
                        url=url, base_url=base_url)

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

        user_request_json_schema = USER_REQUEST_FOR_JSON_SCHEMA.replace(
            "<<INSTRUCTION>>", instruction).replace("<<SCRAPED_CONTENT>>", markdown_content)

        json_schema = get_gpt_response(
            user_request=user_request_json_schema, system_prompt=SYSTEM_PROMPT_FOR_GETTING_JSON_SCHEMA)

        with st.expander(label="JSON Schema"):
            st.json(json_schema)

        user_request_for_structured_content = USER_REQUEST_FOR_STRUCTURED_CONTENT.replace(
            "<<JSON_SCHEMA>>", str(json_schema)).replace("<<INSTRUCTION>>", instruction).replace("<<SCRAPED_CONTENT>>", markdown_content)

        extracted_structured_content = get_gpt_response(
            user_request=user_request_for_structured_content, system_prompt=SYSTEM_PROMPT_FOR_DATA_EXTRACTION_ACCORDING_TO_THE_JSON_SCHEMA)

        with st.expander(label="Extracted Structured Content"):
            st.json(extracted_structured_content)

if __name__ == "__main__":
    main()
