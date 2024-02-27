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
    page_title="Intelli Scrape",
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
def scrape_and_convert(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Extract content within the <body> tag
    body_content = soup.body if soup.body else soup
    base_url = extract_base_url(url=url)
    markdown_content = html2text.html2text(str(body_content),baseurl=base_url)
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

# Streamlit App
def main():

    # Page layout with title
    st.title("Intelli Scrape")

    # Input for URL
    url = st.text_input("Enter URL:")

    # Input for instructions
    instruction = st.text_area("Enter Instructions:")

    if st.button("Scrape and Analyze"):

        if url:
            if instruction:
                # Validate the URL
                if validate_url(url):
                    # Scrape and convert HTML to Markdown
                    markdown_content = scrape_and_convert(url)

                    with st.expander(label="Scraped Raw Markdown Content"):
                        st.markdown(markdown_content)

                    user_request_json_schema = USER_REQUEST_FOR_JSON_SCHEMA.replace(
                        "<<INSTRUCTION>>", instruction).replace("<<SCRAPED_CONTENT>>", markdown_content)

                    json_schema = get_gpt_response(
                        user_request=user_request_json_schema, system_prompt=SYSTEM_PROMPT_FOR_GETTING_JSON_SCHEMA)

                    with st.expander(label="JSON Schema"):
                        st.json(json_schema)
                        # st.write(json_schema)

                    user_request_for_structured_content = USER_REQUEST_FOR_STRUCTURED_CONTENT.replace(
                        "<<JSON_SCHEMA>>", str(json_schema)).replace("<<INSTRUCTION>>", instruction).replace("<<SCRAPED_CONTENT>>", markdown_content)

                    extracted_structured_content = get_gpt_response(
                        user_request=user_request_for_structured_content, system_prompt=SYSTEM_PROMPT_FOR_DATA_EXTRACTION_ACCORDING_TO_THE_JSON_SCHEMA)


                    with st.expander(label="Extracted Structured Content"):
                        # st.markdown(extracted_structured_content)
                        st.json(extracted_structured_content)

                else:
                    st.error("Invalid URL. Please enter a valid URL.")
            else:
                st.error("Please enter the instructions.")
        else:
            st.error("Please enter a URL.")

if __name__ == "__main__":
    main()