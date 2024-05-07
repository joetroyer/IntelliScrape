import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from utils.prompts import (SYSTEM_PROMPT_DEFAULT)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# @st.cache_data
def get_gpt_response(user_request: str, system_prompt: str = SYSTEM_PROMPT_DEFAULT, model: str = "gpt-4-1106-preview"):
    try:
        result = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ],
            model=model
        )
        return result.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error getting GPT response: {str(e)}")
        return {}
