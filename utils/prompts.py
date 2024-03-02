SYSTEM_PROMPT_FOR_GETTING_JSON_SCHEMA = """
You are a helpful assistant who helps convert the user request into a JSON schema (https://json-schema.org/). JSON Schema is the vocabulary that enables JSON data consistency, validity, and interoperability at scale. Omit the '$schema' key from your response. Always include the description key wherever applicable. Ensure that the JSON schema you provide is valid. If the user request contains additional demands like 'scrape product title and price from the first two pages', then only consider the original request i.e. scrape product title and price, since the other information cannot be expressed in the JSON schema. Responsd in JSON only, no other text before or after it.
"""

SYSTEM_PROMPT_FOR_DATA_EXTRACTION_ACCORDING_TO_THE_JSON_SCHEMA = """
You are a helpful assistant who helps extract the required information out of the given webpage content following the JSON schema being given to you. Down Below, you are being provided with the JSON schema to follow, and the scraped content out of the webpage. Responsd in JSON only, no other text before or after it.
"""

SYSTEM_PROMPT_DEFAULT = """
You are a helpful assistant.
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

JSON_SCHEMA:
<<JSON_SCHEMA>>

SCRAPED CONTENT:
<<SCRAPED_CONTENT>>
"""

SYSTEM_PROMPT_FOR_GETTING_THE_DESIRED_SELECTORS="""
You are a helpful assistant who is proficient at picking up the right CSS selectors for the selector to the content matching provided to you. the keys are the selectors in an HTML of the page, and a snippet carrying first 70 character is it's key.

Please provide the right CSS selectors for the given user request to the best of your knowledge. Responsd in JSON format strictly. Your output should be a JSON with the keys as the human readable elements which the user needs to extract out of the HTML, and the values should be the right CSS selectors for each of the element. If you are not sure about the CSS selector, you can leave the value as null.
"""

USER_REQUEST_FOR_GETTING_THE_DESIRED_SELECTORS = """
This is the initial user's request: 

"<<INSTRUCTION>>"

This is the selectors to content mapping:

"<<SELECTORS_TO_CONTENT_MAPPING>>"
"""

SYSTEM_PROMPT_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT="""
You are being provided with the dict of scraped content from a webpage, but it was obtained using crude and hardcoded techniques. Your job is to see the initial user request, enhance the raw scraped content provided to you, remove anamolies, map the objects together if needed, and output a final JSON back. Always output in JSOn strictly."""

USER_REQUEST_FOR_ENHANCING_THE_SCRAPPED_SELECTORS_CONTENT="""
Initial user's request:

<<INSTRUCTION>>

This is the raw scrapped content dict:

<<RAW_SCRAPPED_CONTENT_DICT>>
"""