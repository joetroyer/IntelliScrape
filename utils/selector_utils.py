import re
import bs4
import logging
from typing import Dict, Any

# Compile the regex pattern once and reuse it
CSS_ESCAPE_PATTERN = re.compile(r'([!"#$%&\'()*+,./:;<=>?@[\\]^`{|}~])')

# Define the tags to decompose as a constant at the module level
TAGS_TO_DECOMPOSE = ['script', 'style', 'meta', 'link', 'comment', 'head', 'footer', 'nav', 'form', 'noscript']

# Define the truncate_text function
def truncate_text(text: str, max_length: int = 70) -> str:
    return text[:max_length] + '...' if len(text) > max_length else text

# Function to escape special characters in CSS identifiers
def escape_css_identifier(s: str) -> str:
    return CSS_ESCAPE_PATTERN.sub(r'\\\1', s)

def process_tag(tag: bs4.element.Tag, result_dict: Dict[str, Any]) -> None:
    try:
        key = None
        if 'id' in tag.attrs:
            key = f"#{escape_css_identifier(tag['id'])}"
        elif 'class' in tag.attrs and tag['class']:
            key = '.' + '.'.join(escape_css_identifier(cls) for cls in tag['class'])

        if key:
            if key not in result_dict:
                result_dict[key] = {'content': [], 'children': {}}
            text = tag.get_text(strip=True)
            if text:
                result_dict[key]['content'].append(truncate_text(text))
            for child in tag.children:
                if isinstance(child, bs4.element.Tag):  # Ensure child is a tag
                    process_tag(child, result_dict[key]['children'])
        else:
            for child in tag.children:
                if isinstance(child, bs4.element.Tag):
                    process_tag(child, result_dict)
    except Exception as e:
        logging.error(f"Error processing tag {tag}: {e}")

def clean_and_truncate(d: Dict[str, Any], max_content_items: int = 2) -> Dict[str, Any]:
    if not isinstance(d, dict):
        return d
    clean_dict = {}
    for key, value in d.items():
        if key == 'content':
            # Filter out empty strings and truncate the list to the first two items
            value = [item for item in value if item.strip()][:max_content_items]
        elif key == 'children':
            # Recursively clean and truncate children
            value = clean_and_truncate(value, max_content_items)
        else:
            value = clean_and_truncate(value, max_content_items)

        if value:
            clean_dict[key] = value

    return {k: v for k, v in clean_dict.items() if v}

# Update the summarize_body_using_dict_method function to pass the max_content_items parameter
def summarize_body_using_dict_method(soup: bs4.BeautifulSoup, max_content_items: int = 2) -> Dict[str, Any]:
    result_dict = {}

    for tag in soup(TAGS_TO_DECOMPOSE):
        tag.decompose()

    process_tag(soup.body if soup.body else soup, result_dict)
    return clean_and_truncate(result_dict, max_content_items)