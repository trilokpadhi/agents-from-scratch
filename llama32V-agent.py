##################################################################
# Below is a basic implementation of llama3.2 vision agent talking 
################################################################
import base64
import requests
from autogen import UserProxyAgent, AssistantAgent
from PIL import Image
import io
import pillow_avif
import os

# Set environment variable
os.environ["AUTOGEN_USE_DOCKER"] = "0"

# Convert image to Base64 format (for API call)
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Function to convert AVIF image to Base64 format
def encode_avif_image(image_path):
    with open(image_path, "rb") as img_file:
        img = Image.open(io.BytesIO(img_file.read()))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Image file to be used by the Sales Agent
image_path = "/staging/users/tpadhi1/mm-agents-llama-stack/datasets/Supervolcano/How To Play/3b32d710c07beba480b6497a93fdcad4_original.avif"  # Replace with your actual image path
image_data = encode_avif_image(image_path)

# Ollama Configuration with Llama 3.2 Vision
llm_config = {
    "config_list": [
        {
            "base_url": "http://localhost:11434/v1",  # Ollama's running server
            "api_key": "fakekey",
            "model": "llama3.2-vision",
        }
    ],
}

# Sales Agent - Uses Image + Persuasion Strategy
SalesAgent = AssistantAgent(
    name="SalesAgent",
    llm_config=llm_config,
    system_message="You are an expert sales agent. Your goal is to persuade the user to buy a product using both \
                    textual persuasion and visual analysis. Highlight key features from the image to enhance persuasion."
)

# Human Agent - Customer with Doubts
HumanAgent = UserProxyAgent(
    name="HumanAgent",
    # is_termination_msg=lambda x: "no thanks" in x.lower() or "not interested" in x.lower(),
    is_termination_msg=lambda x: isinstance(x, str) and ("no thanks" in x.lower() or "not interested" in x.lower()),
    system_message="You are a skeptical customer who needs strong reasons to buy the product. Ask questions, \
                    raise concerns, and see if the product is worth it."
)

# Start the conversation with an image
HumanAgent.initiate_chat(
    SalesAgent,
    message="I'm not sure if I need this AI-powered gadget. Can you convince me?",
    images=[{"data": image_data, "type": "base64"}]  # Passing encoded image
)