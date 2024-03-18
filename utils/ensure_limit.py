import tiktoken
import streamlit as st

def reduce_string_to_token_limit(input_string: str, token_limit: int = 100000, chunk_size: int = 1000, verbose: bool = True) -> str:
    try:
        if verbose:
            st.info(f"Received input string of length: {len(input_string)}")
        # Get the encoding for the model, assuming "gpt-4" as an example
        enc = tiktoken.get_encoding("cl100k_base")
        if verbose:
            st.info("Encoding model loaded.")

        # Count the initial number of tokens
        total_tokens = len(enc.encode(input_string))
        if verbose:
            st.info(f"Initial number of tokens: {total_tokens}")

        # Check if the total tokens are within the limit
        if total_tokens <= token_limit:
            if verbose:
                st.info("Total tokens are within the limit, returning the original string.")
            return input_string

        if verbose:
            st.info(f"Total tokens exceed the limit of {token_limit}, starting reduction process.")
        # If tokens exceed the limit, start removing chunks from the end
        while total_tokens > token_limit and len(input_string) > 0:
            # Determine the size of the chunk to remove
            actual_chunk_size = min(chunk_size, len(input_string))
            if verbose:
                st.info(f"Attempting to remove a chunk of size: {actual_chunk_size}")

            # Remove the chunk from the end of the string
            input_string = input_string[:-actual_chunk_size]
            if verbose:
                st.info(f"Chunk removed. New string length: {len(input_string)}")

            # Count the tokens in the updated string
            total_tokens = len(enc.encode(input_string))
            if verbose:
                st.info(f"New total number of tokens: {total_tokens}")

        if verbose:
            st.info("Reduction process completed. Returning the reduced string.")
        return input_string
    except Exception as e:
        if verbose:
            st.error(f"An error occurred while reducing the string to the token limit: {e}")
        return ""