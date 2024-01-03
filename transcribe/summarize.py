import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)



def summarize_transcription(text_to_summarize):

    # Format the prompt for summarization
    prompt = f"This is a segment of a radio show i would like put into show notes, which is around 1000 words. Try to exclude sponsorship messages from Terry Kroupon or any law firm. Dont include any summary of sponsorships mentioned, exclude it all together. If there is an email of the day winner. please let me know. Text to summarize: {text_to_summarize}"
    chat_completion = client.chat.completions.create(messages=[{"role":"user", "content": prompt}], model="gpt-3.5-turbo")

    # Print the summary
    print(chat_completion.choices[0].message.content)

    return chat_completion.choices[0].message.content
