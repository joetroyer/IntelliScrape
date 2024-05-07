# Import necessary modules
from utils.prompts import SYSTEM_PROMPT_FOR_ENHANCING_THE_INSTRUCTIONS, USER_REQUEST_FOR_ENHANCING_THE_INSTRUCTIONS
from utils.get_gpt_response import get_gpt_response

def enhance_user_instructions(raw_user_instructions: str):
    # Replace the placeholder in the user request template
    user_request = USER_REQUEST_FOR_ENHANCING_THE_INSTRUCTIONS.replace("<<INSTRUCTION>>", raw_user_instructions)
    
    # Call the GPT function to enhance user instructions
    enhanced_instructions = get_gpt_response(user_request, SYSTEM_PROMPT_FOR_ENHANCING_THE_INSTRUCTIONS)
    
    return enhanced_instructions