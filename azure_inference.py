# Azure AI Inference integration for Reddit bot
import re
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from config import logger, conf

endpoint = conf().get("azure_endpoint", "https://redditreplybot.services.ai.azure.com/models")
key = conf().get("azure_key")
deployment_name = conf().get("azure_deployment", "DeepSeek-R1-2")
client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

def azure_generate_reply(system_prompt, user_prompt, max_tokens=8192, model=None):
    """
    Generate a reply using Azure AI Inference.
    :param system_prompt: The system prompt string (persona, rules, etc)
    :param user_prompt: The user message string
    :param max_tokens: Max tokens for the response
    :param model: Model/deployment name (optional)
    :return: The generated reply string
    """
    logger.info(f"[persona]:" + system_prompt)
    response = client.complete(
        messages=[
            SystemMessage(content=system_prompt),
            UserMessage(content=user_prompt)
        ],
        max_tokens=max_tokens,
        model=model or deployment_name,
    )
    reply_text = response.choices[0].message.content
    logger.info(f"Generated reply: {reply_text}")
    # If using DeepSeek, clean <think>...</think> tags
    if (model or deployment_name).lower().startswith("deepseek"):
        reply_text = re.sub(r'<think>.*?</think>', '', reply_text, flags=re.DOTALL).strip()
    return reply_text
