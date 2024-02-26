import streamlit as st
import requests
from bs4 import BeautifulSoup
import html2text
import os
from openai import OpenAI
from dotenv import load_dotenv
import validators

load_dotenv()

client = OpenAI()

# Function to validate if the URL is correct
def validate_url(url):
    if validators.url(url):
        return True
    else:
        return False

# Function to scrape and convert HTML to Markdown


def scrape_and_convert(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    html_content = str(soup)

    # Convert HTML to Markdown
    markdown_content = html2text.html2text(html_content)

    return markdown_content

# Function to interact with ChatGPT


def chat_with_gpt(instruction, markdown_content):
    # Make a call to ChatGPT
    prompt = f"Instruction: {instruction}\n\nContent: {markdown_content}"
    result = client.chat.completions.create(
        messages=[
            {"role":"system","content":"You are a helpful assistant."},
            {"role":"user","content":prompt}
        ],
        model="gpt-3.5-turbo",
    )

    return result.choices[0].message.content

# Streamlit App


def main():
    st.title("Intelli Scrape")

    # Input for URL
    url = st.text_input("Enter URL:")

    # Input for instructions
    instruction = st.text_area("Enter Instructions:")

    if st.button("Scrape and Analyze"):
        # Validate the URL
        if validate_url(url):
            # Scrape and convert HTML to Markdown
            markdown_content = scrape_and_convert(url)
            st.markdown(markdown_content)
            # Call ChatGPT
            # result = chat_with_gpt(instruction, markdown_content)

            # # Display the result
            # st.markdown(f"**Result:**\n\n{result}")
        else:
            st.error("Invalid URL. Please enter a valid URL.")


if __name__ == "__main__":
    main()