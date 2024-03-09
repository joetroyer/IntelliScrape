import streamlit as st
import requests
from bs4 import BeautifulSoup
import bs4
import html2text
from utils.get_gpt_response import get_gpt_response
import re
import validators
from urllib.parse import urlsplit
import json
from utils.prompts import (SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_SELECTORS,
                           USER_REQUEST_FOR_GETTING_THE_DESIRED_SELECTORS,
                           USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT, SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT)

# Set page title and icon
st.set_page_config(
    page_title="Intelli Scrape - Approach 2",
    page_icon=":robot_face:"
)

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

def truncate_text(text):
    return text[:70]

class ContentNode:
    def __init__(self, tag=None, id=None, classes=None):
        self.tag = tag
        self.id = self.escape_css_identifier(id) if id else None
        self.classes = [self.escape_css_identifier(cls) for cls in classes] if classes else []
        self.content = []
        self.children = []

    def add_content(self, text):
        truncated_text = truncate_text(text)
        self.content.append(truncated_text)

    def add_child(self, child_node):
        self.children.append(child_node)

    def escape_css_identifier(self, identifier):
        # Escape special characters with a backslash
        return re.sub(r'([!"#$%&\'()*+,./:;<=>?@[\\]^`{|}~])', r'\\\1', identifier)

    def get_text(self):
        return ' '.join(self.content)

# Define the truncate_text function
def truncate_text(text, max_length=70):
    return text[:max_length] + '...' if len(text) > max_length else text

# Modify the process_tag function to work with ContentNode
def process_tag(tag, parent_node):
    # Create a ContentNode with the tag's name, id, and classes
    node = ContentNode(tag.name, tag.get('id'), tag.get('class'))
    text = tag.get_text(strip=True)
    if text:
        node.add_content(text)
    for child in tag.children:
        if isinstance(child, bs4.element.Tag):
            child_node = process_tag(child, node)
            node.add_child(child_node)
    return node

# Function to convert the tree of ContentNodes to a nested dictionary
def convert_to_dict(node):
    node_dict = {
        'tag': node.tag
    }
    if node.id is not None:
        node_dict['id'] = node.id
    if node.classes:
        node_dict['classes'] = node.classes
    if node.content:
        node_dict['content'] = node.content
    children = [convert_to_dict(child) for child in node.children]
    if children:
        node_dict['children'] = children
    return node_dict

def generate_ascii_tree(node, prefix=""):
    lines = []

    # Add the current node tag
    node_repr = f"{node.tag}"
    if node.id:
        node_repr += f"#{node.id}"
    if node.classes:
        node_repr += f".{'.'.join(node.classes)}"
    if node.content:
        content_str = ' '.join(node.content)
        node_repr += f" - {content_str}"

    lines.append(prefix + node_repr)

    # Process children with recursion
    children_prefix = prefix + "│   "
    last_child_prefix = prefix + "    "
    for i, child in enumerate(node.children):
        is_last = i == (len(node.children) - 1)
        child_lines = generate_ascii_tree(child, children_prefix if not is_last else last_child_prefix)
        if is_last:
            child_lines[0] = prefix + "└── " + child_lines[0][len(prefix):]
        else:
            child_lines[0] = prefix + "├── " + child_lines[0][len(prefix):]
        lines.extend(child_lines)

    return lines

# Function to get the ASCII tree as a string
def get_ascii_tree_string(root_node):
    lines = generate_ascii_tree(root_node)
    return "\n".join(lines)

# The summarize_body function using ContentNode
def summarize_body_using_ascii_tree(soup):
    # Decompose unwanted tags
    for tag in soup(['script', 'style', 'meta', 'link', 'comment', 'head', 'footer', 'nav', 'form', 'noscript']):
        tag.decompose()

    # Start processing from the body tag or the root of the soup
    root_node = process_tag(soup.body if soup.body else soup, None)
    # Convert the tree of ContentNodes to a nested dictionary
    # summarized_dict = convert_to_dict(root_node)
    summarized_dict = get_ascii_tree_string(root_node=root_node)
    with open('tst.txt','w', encoding='utf-8') as f:
        f.write(summarized_dict)
    return summarized_dict

def summarize_body_using_dict_method(soup):
    result_dict = {}

    # Function to escape special characters in CSS identifiers
    def escape_css_identifier(s):
        return re.sub(r'([!"#$%&\'()*+,./:;<=>?@[\\]^`{|}~])', r'\\\1', s)

    # Remove unwanted tags just once at the beginning
    for tag in soup(['script', 'style', 'meta', 'link', 'comment', 'head', 'footer', 'nav', 'form', 'noscript']):
        tag.decompose()

    def process_tag(tag, result_dict):
        try:
            key = None
            if 'id' in tag.attrs:
                key = f"#{escape_css_identifier(tag['id'])}"
            elif 'class' in tag.attrs and tag['class']:
                # Join classes with '.', escape each class identifier, and prefix with '.'
                key = '.' + '.'.join(escape_css_identifier(cls) for cls in tag['class'])

            if key:
                if key not in result_dict:
                    result_dict[key] = {'content': [], 'children': {}}
                result_dict[key]['content'].append(truncate_text(tag.get_text(strip=True)))
                for child in tag.children:
                    if isinstance(child, bs4.element.Tag):  # Ensure child is a tag
                        process_tag(child, result_dict[key]['children'])
            else:
                # Directly add text nodes to the content
                text = tag.get_text(strip=True)
                if text:
                    result_dict.setdefault('text_nodes', []).append(truncate_text(text))
                for child in tag.children:
                    if isinstance(child, bs4.element.Tag):
                        process_tag(child, result_dict)
        except Exception as e:
            # Log the error with the tag for debugging
            print(f"Error processing tag {tag}: {e}")

    def clean_empty_entries(d):
        if not isinstance(d, dict):
            return d
        clean_dict = {}
        for key, value in d.items():
            if key == 'content':
                # Remove empty strings from the content list
                value = [item for item in value if item.strip()]
            elif key == 'children':
                # Recursively clean children
                value = clean_empty_entries(value)
            else:
                value = clean_empty_entries(value)

            # Add to clean_dict only if value is not empty
            if value:
                clean_dict[key] = value

        # Remove any empty dictionaries that may have resulted from the above process
        clean_dict = {k: v for k, v in clean_dict.items() if v}
        return clean_dict

    def truncate_text_nodes(d):
        if 'text_nodes' in d:
            d['text_nodes'] = d['text_nodes'][:2]
        for key in d:
            if isinstance(d[key], dict):
                truncate_text_nodes(d[key])

    process_tag(soup.body if soup.body else soup, result_dict)
    cleaned_result_dict = clean_empty_entries(result_dict)
    truncate_text_nodes(cleaned_result_dict)

    return cleaned_result_dict

def extract_base_url(url):
    try:
        parsed_url = urlsplit(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url
    except Exception as e:
        st.error(f"Error extracting base URL: {str(e)}")
        return None

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

        # Input for URL or File Upload
        st.session_state['summarizing_method'] = st.radio("Choose Input Type:",
                               ("Summarize body through JSON method","Summarize body through ASCII tree method"),captions = ["Consumes less amount of tokens.", "Very token-hungry"],index=0)
        
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
                        else:
                            summarized_dict = summarize_body_using_ascii_tree(html_content)
                            st.markdown(summarized_dict)

                    user_request_for_desired_selectors = USER_REQUEST_FOR_GETTING_THE_DESIRED_SELECTORS.replace(
                        "<<INSTRUCTION>>", instruction).replace("<<SELECTORS_TO_CONTENT_MAPPING>>", json.dumps(summarized_dict))

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