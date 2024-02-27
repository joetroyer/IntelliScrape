SYSTEM_PROMPT_FOR_GETTING_JSON_SCHEMA = """
You are a helpful assistant who helps convert the user request into a JSON schema (https://json-schema.org/). JSON Schema is the vocabulary that enables JSON data consistency, validity, and interoperability at scale. Omit the '$schema' key from your response. Always include the description key wherever applicable. Ensure that the JSON schema you provide is valid. If the user request contains additional demands like 'scrape product title and price from the first two pages', then only consider the original request i.e. scrape product title and price, since the other information cannot be expressed in the JSON schema.
"""

SYSTEM_PROMPT_FOR_DATA_EXTRACTION_ACCORDING_TO_THE_JSON_SCHEMA = """
You are a helpful assistant who helps extract the required information out of the given webpage content following the JSON schema being given to you. Down Below, you are being provided with the JSON schema to follow, and the scraped content out of the webpage. Return the results back in JSON format strictly. 
"""

SYSTEM_PROMPT_DEFAULT = """
You are a helpful assistant.
"""

USER_REQUEST_FOR_JSON_SCHEMA = """
URL:
<<URL>>

SCRAPED CONTENT:
<<SCRAPED_CONTENT>>
"""

USER_REQUEST_FOR_STRUCTURED_CONTENT="""
JSON_SCHEMA:
<<JSON_SCHEMA>>

URL:
<<URL>>

SCRAPED CONTENT:
<<SCRAPED_CONTENT>>
"""