import os
import azure.cognitiveservices.speech as speechsdk
import openai
from dotenv import load_dotenv

load_dotenv()

# Set up Azure OpenAI API credentials
openai.api_type = "azure"
openai.api_base = os.getenv("API_BASE")
openai.api_version = os.getenv("API_VERSION")
openai.api_key = os.getenv("API_KEY")


from pathlib import Path

file_system = Path("./app/content/content_system.txt")
system_content = file_system.read_text(encoding="utf-8")
file_assistant = Path("./app/content/content_assistant.txt")
assistant_content = file_system.read_text(encoding="utf-8")


def generate_message(prompt):
    response = openai.ChatCompletion.create(
        engine=os.getenv("ENGINE"),
        messages=[
            {"role": "system", "content": str(system_content)},
            {"role": "assistant", "content": str()},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )
    return response["choices"][0]["message"]["content"]
