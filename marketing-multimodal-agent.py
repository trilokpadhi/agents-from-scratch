import base64
import os
import re
from autogen import AssistantAgent
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from PIL import Image
import io
import pillow_avif

# Set environment variable to disable Docker in AutoGen
os.environ["AUTOGEN_USE_DOCKER"] = "0"

# User profile for the Human Agent
user_profile = {
    "first_name": "Patricia",
    "last_name": "Bennett",
    "age": 69,
    "sex": "Female",
    "ethnicity": "Denmark",
    "race": "White",
    "detailed_race": "White",
    "hispanic_origin": "Not Hispanic",
    "street_address": "123 Prairie View Lane",
    "city": "Des Moines",
    "state": "IA",
    "political_views": "Liberal",
    "party_identification": "Strong democrat",
    "residence_at_16": "West North Central",
    "same_residence_since_16": "Different state",
    "family_structure_at_16": "Lived with parents",
    "family_income_at_16": "Average",
    "fathers_highest_degree": "High school",
    "mothers_highest_degree": "High school",
    "mothers_work_history": "Yes",
    "marital_status": "Divorced",
    "work_status": "Retired",
    "military_service_duration": "No active duty",
    "religion": "None",
    "religion_at_16": "Protestant",
    "born_in_us": "Yes",
    "us_citizenship_status": "A U.S. citizen",
    "highest_degree_received": "Graduate",
    "speak_other_language": "No",
    "total_wealth": "$75,000 to $100,000"
}

# Function to convert AVIF image to Base64 PNG format
def encode_avif_image(image_path):
    """Convert an AVIF image to Base64-encoded PNG format."""
    with open(image_path, "rb") as img_file:
        img = Image.open(io.BytesIO(img_file.read()))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Custom Sales Agent class with modified send method
class SalesAssistantAgent(AssistantAgent):
    def send(self, message, recipient, request_reply=True, silent=False):
        """Override send method to process image references and send multimodal content."""
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            match = re.search(r"\[IMAGE: (.*?)\]", message["content"])
            if match:
                image_path = match.group(1)
                try:
                    image_data = encode_avif_image(image_path)
                    text_part = message["content"].replace(match.group(0), "").strip()
                    content = [
                        {"type": "text", "text": text_part},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                    ]
                    message["content"] = content
                except Exception as e:
                    print(f"Error loading image at {image_path}: {e}")
                    message["content"] = message["content"].replace(match.group(0), "(Image unavailable)")
        super().send(message, recipient, request_reply, silent)

# Configuration for Sales Agent with Llama 3.2 Vision via Ollama
llm_config = {
    "config_list": [
        {
            "base_url": "http://localhost:11434/v1",
            "api_key": "fakekey",  # Replace with actual key if required by your Ollama setup
            "model": "llama3.2-vision",
        }
    ],
}

# Configuration for Human Agent with OpenAI GPT-4 Vision
openai_api_key = os.getenv("OPENAI_API_KEY_TP")
if not openai_api_key:
    raise ValueError("OpenAI API key not found in environment variables. Set OPENAI_API_KEY.")

human_llm_config = {
    "config_list": [
        {
            # "model": "gpt-4-vision-preview",
            "model": "gpt-4o-mini-2024-07-18",
            "api_key": openai_api_key,
            "temperature": 0.5,
            "max_tokens": 300,
        }
    ],
}

# Initialize Sales Agent
SalesAgent = SalesAssistantAgent(
    name="SalesAgent",
    llm_config=llm_config,
    system_message="You are an expert sales agent. Your goal is to persuade the user to buy a product using both "
                   "textual persuasion and visual analysis. You have access to a dataset of advertisements located in "
                   "'datasets/Supervolcano/'. When you want to show an image, include '[IMAGE: path/to/image]' in your "
                   "response, where 'path/to/image' is the relative path to the image file (e.g., "
                   "'datasets/Supervolcano/How To Play/3b32d710c07beba480b6497a93fdcad4_original.avif')."
)

# Initialize Human Agent with user profile as MultimodalConversableAgent
HumanAgent = MultimodalConversableAgent(
    name="HumanAgent",
    llm_config=human_llm_config,
    max_consecutive_auto_reply=10,
    system_message=f"You are {user_profile['first_name']} {user_profile['last_name']}, a {user_profile['age']}-year-old "
                   f"retired {user_profile['sex'].lower()} from {user_profile['city']}, {user_profile['state']}. You are "
                   f"a {user_profile['party_identification'].lower()} with {user_profile['political_views'].lower()} views. "
                   f"You are skeptical about buying new products and need strong reasons to be convinced. Ask questions, "
                   f"raise concerns, and see if the product is worth it."
)

# Function to extract text from message content for termination check
def extract_text(content):
    """Extract text from message content, handling both strings and multimodal lists."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return " ".join([item["text"] for item in content if item["type"] == "text"])
    return ""

# Termination condition
is_termination_msg = lambda msg: "no thanks" in extract_text(msg["content"]).lower() or "not interested" in extract_text(msg["content"]).lower()

# Start the conversation
HumanAgent.initiate_chat(
    SalesAgent,
    message="I'm not sure if I need this AI-powered gadget. Can you convince me?",
    max_turns=10,
    is_termination_msg=is_termination_msg
)


