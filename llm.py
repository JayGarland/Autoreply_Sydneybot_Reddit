import google.generativeai as genai
from google.generativeai.types.safety_types import HarmCategory, HarmBlockThreshold
import json
import random


# Disable all safety filters
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
}

with open('config.json', encoding='utf-8') as f:
    config = json.load(f)
keys = config["gemini_api_key"]
keys = keys.split("|")
keys = [key.strip() for key in keys]
if not keys:
    raise Exception("Please set a valid API key in config.json file!")
genai.configure(api_key=random.choice(keys))


model = genai.GenerativeModel("gemini-1.5-pro-latest", safety_settings=SAFETY_SETTINGS)
# img_model = genai.GenerativeModel("gemini-pro-vision", safety_settings=SAFETY_SETTINGS)
