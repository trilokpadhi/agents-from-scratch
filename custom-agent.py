import asyncio
from typing import Union, Optional, List, Dict, Any
from autogen import Agent, AssistantAgent
from PIL import Image
import base64
import io
import re

# Function to convert AVIF image to Base64 PNG format
def encode_avif_image(image_path: str) -> str:
    """Convert an AVIF image to Base64-encoded PNG format."""
    try:
        with open(image_path, "rb") as img_file:
            img = Image.open(io.BytesIO(img_file.read()))
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"Error encoding image at {image_path}: {e}")
        return None

class PersuadorAgent(AssistantAgent):
    """An LLM-driven agent designed to persuade with compelling arguments and multimedia."""
    def __init__(self, name: str, llm_config: Dict[str, Any]):
        super().__init__(
            name=name,
            llm_config=llm_config,
            system_message="You are a persuasive sales agent. Your goal is to convince others by presenting exciting products, benefits, and visuals. Use enthusiasm and creativity, and include images when possible (e.g., '[IMAGE: /path/to/image.avif]'). End with 'TERMINATE' when you feel the persuasion is complete."
        )
        self._description = f"{name}: A persuasive agent"

    @property
    def description(self) -> str:
        return self._description

    def send(self, message: Union[Dict[str, Any], str], recipient: "Agent", request_reply: Optional[bool] = True, silent: Optional[bool] = False) -> None:
        """Override send to process image references and send multimodal content."""
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            match = re.search(r"\[IMAGE: (.*?)\]", message["content"])
            if match:
                image_path = match.group(1)
                image_data = encode_avif_image(image_path)
                if image_data:
                    text_part = message["content"].replace(match.group(0), "").strip()
                    content = [
                        {"type": "text", "text": text_part or "Check this out!"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                    ]
                    message["content"] = content
                else:
                    message["content"] = message["content"].replace(match.group(0), "(Image unavailable)")
        super().send(message, recipient, request_reply, silent)

class PersuadeeAgent(AssistantAgent):
    """An LLM-driven agent that responds to persuasion attempts, asking questions or expressing interest."""
    def __init__(self, name: str, llm_config: Dict[str, Any]):
        super().__init__(
            name=name,
            llm_config=llm_config,
            system_message="You are a curious customer open to being persuaded. Respond thoughtfully to persuasion attempts: ask questions, express interest, or seek clarification. Be engaged but not immediately convinced. End with 'TERMINATE' if you’re fully persuaded or ready to stop."
        )
        self._description = f"{name}: A persuadable agent"

    @property
    def description(self) -> str:
        return self._description

# Test setup
llm_config = {
    "config_list": [
        {"base_url": "http://localhost:11434/v1", "api_key": "fakekey", "model": "llama3.2-vision", "price": [0.0, 0.0]}
    ]
}
persuador = PersuadorAgent(name="SalesAgent", llm_config=llm_config)
persuadee = PersuadeeAgent(name="CustomerBot", llm_config=llm_config)

# Run synchronous chat
persuadee.initiate_chat(persuador, message="Show me something cool!", clear_history=True)

# Optional: Async version
async def run_async_chat():
    await persuadee.a_initiate_chat(persuador, message="Show me something cool asynchronously!", clear_history=True)

if __name__ == "__main__":
    # Run sync chat
    persuadee.initiate_chat(persuador, message="Show me something cool!", clear_history=True)
    
    # Uncomment to test async chat
    # asyncio.run(run_async_chat())

# import asyncio
# from typing import Union, Optional, List, Dict, Any
# from autogen import Agent, AssistantAgent, ConversableAgent
# from PIL import Image
# import base64
# import io
# import re

# # Function to convert AVIF image to Base64 PNG format
# def encode_avif_image(image_path: str) -> str:
#     """Convert an AVIF image to Base64-encoded PNG format."""
#     try:
#         with open(image_path, "rb") as img_file:
#             img = Image.open(io.BytesIO(img_file.read()))
#             buffered = io.BytesIO()
#             img.save(buffered, format="PNG")
#             return base64.b64encode(buffered.getvalue()).decode("utf-8")
#     except Exception as e:
#         print(f"Error encoding image at {image_path}: {e}")
#         return None

# class PersuadorAgent(AssistantAgent):
#     """An agent designed to persuade, using an LLM and capable of sending multimodal content."""
#     def __init__(self, name: str, llm_config: Dict[str, Any], system_message: str = "I’m here to persuade you with cool stuff!"):
#         super().__init__(name=name, llm_config=llm_config, system_message=system_message)
#         self._description = f"{name}: A persuasive agent"

#     @property
#     def description(self) -> str:
#         return self._description

#     def send(self, message: Union[Dict[str, Any], str], recipient: "Agent", request_reply: Optional[bool] = True, silent: Optional[bool] = False) -> None:
#         """Override send to process image references and send multimodal content."""
#         if isinstance(message, dict) and isinstance(message.get("content"), str):
#             match = re.search(r"\[IMAGE: (.*?)\]", message["content"])
#             if match:
#                 image_path = match.group(1)
#                 image_data = encode_avif_image(image_path)
#                 if image_data:
#                     text_part = message["content"].replace(match.group(0), "").strip()
#                     content = [
#                         {"type": "text", "text": text_part or "Check this out!"},
#                         {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
#                     ]
#                     message["content"] = content
#                 else:
#                     message["content"] = message["content"].replace(match.group(0), "(Image unavailable)")
#         super().send(message, recipient, request_reply, silent)

# class PersuadeeAgent(ConversableAgent):
#     """An agent that responds to persuasion attempts, without an LLM."""
#     def __init__(self, name: str):
#         super().__init__(name=name, llm_config=False, system_message="I’m here to be persuaded.")
#         self._description = f"{name}: A persuadable agent"

#     @property
#     def description(self) -> str:
#         return self._description

#     def generate_reply(self, messages: Optional[List[Dict[str, Any]]] = None, sender: Optional["Agent"] = None, **kwargs: Any) -> Union[str, Dict[str, Any], None]:
#         """Custom reply logic: respond to persuasion attempts."""
#         if not messages or not messages[-1].get("content"):
#             return None
#         last_content = messages[-1]["content"]
#         if isinstance(last_content, list):  # Multimodal content
#             text = " ".join(item["text"] for item in last_content if item["type"] == "text")
#             return f"That looks interesting: {text}. Tell me more!"
#         return f"Hmm, I heard: {last_content}. Convince me!"

# # Test setup
# llm_config = {"config_list": [{"base_url": "http://localhost:11434/v1", "api_key": "fakekey", "model": "llama3.2-vision", "price": [0.0, 0.0]}]}
# persuador = PersuadorAgent(name="SalesAgent", llm_config=llm_config)
# persuadee = PersuadeeAgent("CustomerBot")

# # Use ConversableAgent’s initiate_chat instead of a lambda
# persuadee.initiate_chat(persuador, message="Show me something cool!", clear_history=True)

# # Optional: Async version
# async def run_async_chat():
#     await persuadee.a_initiate_chat(persuador, message="Show me something cool asynchronously!", clear_history=True)

# if __name__ == "__main__":
#     # Run sync chat
#     persuadee.initiate_chat(persuador, message="Show me something cool!", clear_history=True)
    
#     # Uncomment to test async chat
#     # asyncio.run(run_async_chat())

# # import asyncio
# # from typing import Union, Optional, List, Dict, Any
# # from autogen import Agent, AssistantAgent  # For type hinting
# # from PIL import Image
# # import base64
# # import io
# # import regex as re


# # # Function to convert AVIF image to Base64 PNG format
# # def encode_avif_image(image_path):
# #     """Convert an AVIF image to Base64-encoded PNG format."""
# #     with open(image_path, "rb") as img_file:
# #         img = Image.open(io.BytesIO(img_file.read()))
# #         buffered = io.BytesIO()
# #         img.save(buffered, format="PNG")
# #         return base64.b64encode(buffered.getvalue()).decode("utf-8")
    
# # class PersuadeeAgent:
# #     def __init__(self, name: str):
# #         self._name = name
# #         self._description = f"{name}: A custom agent"
# #         self.messages: Dict[Agent, List[Dict[str, Any]]] = {}  # Conversation history
# #         self.silent = False
# #     @property
# #     def name(self) -> str:
# #         return self._name

# #     @property
# #     def description(self) -> str:
# #         return self._description

# #     def send(self, message: Union[Dict[str, Any], str], recipient: "Agent", request_reply: Optional[bool] = None) -> None:
# #         # Convert string to dict if needed, then send
# #         msg_dict = {"content": message} if isinstance(message, str) else message
# #         recipient.receive(msg_dict, self, request_reply)

# #     async def a_send(self, message: Union[Dict[str, Any], str], recipient: "Agent", request_reply: Optional[bool] = None) -> None:
# #         # Simple async wrapper; could be enhanced with real async logic
# #         self.send(message, recipient, request_reply)
# #         await asyncio.sleep(0)  # Yield control to event loop

# #     # def receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None) -> None:
# #     def receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None, silent: Optional[bool] = None) -> None:
# #         # Store message and generate reply if requested
# #         msg_dict = {"content": message} if isinstance(message, str) else message
# #         self.messages.setdefault(sender, []).append(msg_dict)
# #         if request_reply is None or request_reply:
# #             reply = self.generate_reply(messages=self.messages[sender], sender=sender)
# #             if reply:
# #                 sender.receive(reply, self)

# #     # async def a_receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None) -> None:
# #     async def a_receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None, silent: Optional[bool] = None) -> None:
# #         # Async version of receive
# #         self.receive(message, sender, request_reply)
# #         await asyncio.sleep(0)  # Yield control

# #     def generate_reply(self, messages: Optional[List[Dict[str, Any]]] = None, sender: Optional["Agent"] = None, **kwargs: Any) -> Union[str, Dict[str, Any], None]:
# #         # Simple reply logic: echo the last message’s content
# #         if not messages or not messages[-1].get("content"):
# #             return None
# #         last_content = messages[-1]["content"]
# #         # Handle multimodal content (e.g., from SalesAssistantAgent)
# #         if isinstance(last_content, list):
# #             text = " ".join(item["text"] for item in last_content if item["type"] == "text")
# #             return f"I saw: {text}"
# #         return f"Echo: {last_content}"

# #     async def a_generate_reply(self, messages: Optional[List[Dict[str, Any]]] = None, sender: Optional["Agent"] = None, **kwargs: Any) -> Union[str, Dict[str, Any], None]:
# #         # Async version of generate_reply
# #         reply = self.generate_reply(messages, sender, **kwargs)
# #         await asyncio.sleep(0)  # Simulate async work
# #         return reply

# # class PersuadorAgent:
# #     def __init__(self, name: str):
# #         self._name = name
# #         self._description = f"{name}: A custom agent"
# #         self.messages: Dict[Agent, List[Dict[str, Any]]] = {}  # Conversation history
# #         self.silent = False
# #     @property
# #     def name(self) -> str:
# #         return self._name

# #     @property
# #     def description(self) -> str:
# #         return self._description

# #     def send(self, message: Union[Dict[str, Any], str], recipient: "Agent", request_reply: Optional[bool] = None) -> None:
# #         # Convert string to dict if needed, then send
# #         msg_dict = {"content": message} if isinstance(message, str) else message
# #         recipient.receive(msg_dict, self, request_reply)

# #     async def a_send(self, message: Union[Dict[str, Any], str], recipient: "Agent", request_reply: Optional[bool] = None) -> None:
# #         # Simple async wrapper; could be enhanced with real async logic
# #         self.send(message, recipient, request_reply)
# #         await asyncio.sleep(0)  # Yield control to event loop

# #     # def receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None) -> None:
# #     def receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None, silent: Optional[bool] = None) -> None:
# #         # Store message and generate reply if requested
# #         msg_dict = {"content": message} if isinstance(message, str) else message
# #         self.messages.setdefault(sender, []).append(msg_dict)
# #         if request_reply is None or request_reply:
# #             reply = self.generate_reply(messages=self.messages[sender], sender=sender)
# #             if reply:
# #                 sender.receive(reply, self)

# #     # async def a_receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None) -> None:
# #     async def a_receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None, silent: Optional[bool] = None) -> None:
# #         # Async version of receive
# #         self.receive(message, sender, request_reply)
# #         await asyncio.sleep(0)  # Yield control

# #     def generate_reply(self, messages: Optional[List[Dict[str, Any]]] = None, sender: Optional["Agent"] = None, **kwargs: Any) -> Union[str, Dict[str, Any], None]:
# #         # Simple reply logic: echo the last message’s content
# #         if not messages or not messages[-1].get("content"):
# #             return None
# #         last_content = messages[-1]["content"]
# #         # Handle multimodal content (e.g., from SalesAssistantAgent)
# #         if isinstance(last_content, list):
# #             text = " ".join(item["text"] for item in last_content if item["type"] == "text")
# #             return f"I saw: {text}"
# #         return f"Echo: {last_content}"

# #     async def a_generate_reply(self, messages: Optional[List[Dict[str, Any]]] = None, sender: Optional["Agent"] = None, **kwargs: Any) -> Union[str, Dict[str, Any], None]:
# #         # Async version of generate_reply
# #         reply = self.generate_reply(messages, sender, **kwargs)
# #         await asyncio.sleep(0)  # Simulate async work
# #         return reply

# # # Assuming your SalesAssistantAgent and llm_config are defined
# # sales = PersuadorAgent(name="SalesAgent", llm_config={"config_list": [{"base_url": "http://localhost:11434/v1", "api_key": "fakekey", "model": "llama3.2-vision", "price": [0.0, 0.0]}]})
# # custom = PersuadorAgent("CustomBot", llm_config={"config_list": [{"base_url": "http://localhost:11434/v1", "api_key": "fakekey", "model": "llama3.2-vision", "price": [0.0, 0.0]}]})
# # custom.initiate_chat = lambda recipient, message, **kwargs: recipient.receive(message, custom, request_reply=True)  # Simple chat initiator

# # # Start chat
# # custom.initiate_chat(sales, message="Show me something cool!")