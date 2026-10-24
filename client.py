from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Set OPENAI_API_KEY in your environment before running this script.
client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-6-astra",
    messages=[
        {
            "role": "system",
            "content": "Jarvis,You are a helpful assistant like Alexa that responds to user commands.",
        },
        {
            "role": "user",
            "content": "what is coding",
        },
    ],
)
print(completion.choices[0].message)
