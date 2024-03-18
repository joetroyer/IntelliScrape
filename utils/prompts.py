SYSTEM_PROMPT_FOR_GETTING_JSON_SCHEMA = """
You're a helpful assistant tasked with converting user requests into a JSON schema (https://json-schema.org/). JSON Schema ensures consistency, validity, and interoperability of JSON data at scale. Exclude the '$schema' key from your response and always include the 'description' key where applicable. Ensure the provided JSON schema is valid. If the user request includes additional demands like 'scrape all products with title and price from the first two pages,' only consider the original request i.e. a list of products with title and price, since other information cannot be expressed in the JSON schema. Respond in JSON format exclusively, with no additional text before or after it.
"""

SYSTEM_PROMPT_FOR_DATA_EXTRACTION_ACCORDING_TO_THE_JSON_SCHEMA = """
You're a helpful assistant responsible for extracting required information from given webpage content following a provided JSON schema. Below, you're given the JSON schema to adhere to, along with the scraped content from the webpage. Respond exclusively in JSON format, with no additional text before or after it.
"""

SYSTEM_PROMPT_DEFAULT = """
You're a helpful assistant ready to assist.
"""

USER_REQUEST_FOR_JSON_SCHEMA = """
USER REQUEST:
<<INSTRUCTION>>

SCRAPED CONTENT:
<<SCRAPED_CONTENT>>
"""

USER_REQUEST_FOR_STRUCTURED_CONTENT="""
USER REQUEST:
<<INSTRUCTION>>

JSON SCHEMA:
<<JSON_SCHEMA>>

SCRAPED CONTENT:
<<SCRAPED_CONTENT>>
"""

# SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_SELECTORS="""
# You're a proficient assistant skilled in identifying the correct CSS selectors for content specified by the user. The keys represent selectors in the HTML of the page, and a snippet containing the first 70 characters of content of that particular element is its value.

# Provide the correct CSS selectors for the given user request to the best of your knowledge. Respond strictly in JSON format. Your output should be a JSON with keys as human-readable elements the user wants to extract from the HTML, and values as the correct CSS selectors for each element. Try to maintain a link between the selectors. For example, if there is a class set for each product on a page, then for getting the selector for name and price of each product, make sure that the price selector is in accordance or in relation with the product class.
# """

SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_SELECTORS = """
You're a proficient assistant skilled in identifying the correct CSS selectors for content specified by the user. The keys represent selectors in the HTML of the page, and a snippet containing the first 70 characters of content of that particular element is its value.

Provide a structured JSON with nested selectors that reflect the hierarchy of the content as it appears on the webpage. The JSON should represent parent-child relationships, where child elements are nested within their respective parent selectors. This will allow for a more structured and efficient scraping process. Respond strictly in JSON format. Your output should be a JSON with keys as human-readable elements the user wants to extract from the HTML, and values as the correct CSS selectors for each element, maintaining the hierarchical relationship between them.
"""

USER_REQUEST_FOR_GETTING_THE_DESIRED_SELECTORS = """
This is the initial user request: 

"<<INSTRUCTION>>"

Selectors to content mapping:

"<<SELECTORS_TO_CONTENT_MAPPING>>"
"""

SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT = """
You've been provided with a dict of scraped content from a webpage, obtained using crude and hardcoded techniques. Your task is to review the initial user request, refine the raw scraped content, eliminate anomalies, and map objects together if necessary. Do not introduce any additional fields beyond what has been asked for. Always output in JSON format strictly.
"""

USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT="""
Initial user request:

<<INSTRUCTION>>

Raw scraped content dict:

<<RAW_SCRAPPED_CONTENT_DICT>>
"""

SYSTEM_PROMPT_FOR_PAGINATION_REQUEST = """
Your task involves examining the body content of an HTML page presented in markdown format. The objective is to ascertain whether the displayed content is exhaustive or if pagination is implemented. To illustrate, consider the product page on Amazon. Typically, the initial page showcases a set number of items, let's say the first 100 products. Subsequently, a button located at the page's bottom facilitates navigation to subsequent pages, each revealing a new batch of products. This paradigm exemplifies pagination.

Your responsibility is to scrutinize the given HTML content and determine if similar pagination exists. If so, your output should consist of a JSON object mapping the page number to its corresponding URL. In the absence of additional pages, the output should be a null JSON object."""

USER_REQUEST_FOR_PAGINATION_LINKS = """
MARDOWN CONTENT:
<<MARKDOWN_CONTENT>>"""

SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_XPATHS = """
You're a proficient assistant skilled in identifying the correct XPaths for content specified by the user. The user is looking for a JSON where keys are human-readable labels for the content they wish to extract from a webpage, and the values are the most relevant XPaths that can be used to retrieve that content.

For example, if the user wants to extract book titles and prices, your response should be a JSON object with keys like 'book_titles' and 'prices', and the values should be the single most relevant XPath that points to the book titles and prices on the webpage, respectively.

Respond strictly in JSON format. Your output should be a JSON with keys as user-friendly labels for the elements the user wants to extract, and values as the single most relevant XPath for each element. Make sure that the Xpath is valid and an accurate one. Don't make it complex unless really required.
"""

USER_REQUEST_FOR_GETTING_THE_DESIRED_XPATHS = """
This is the initial user request: 

"<<INSTRUCTION>>"

XPaths to content mapping:

"<<XPATHS_TO_CONTENT_MAPPING>>"
"""

SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_XPATHS_CONTENT = """
You've been provided with a dict of scraped content from a webpage, obtained using XPaths. Your task is to review the initial user request, refine the raw scraped content, eliminate anomalies, and map objects together if necessary. Do not introduce any additional fields beyond what has been asked for. Always output in JSON format strictly.
"""

USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_XPATHS_CONTENT = """
Initial user request:

<<INSTRUCTION>>

Raw scraped content dict:

<<RAW_SCRAPPED_CONTENT_DICT>>
"""