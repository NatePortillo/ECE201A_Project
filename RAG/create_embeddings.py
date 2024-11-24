from openai import OpenAI
import json
import pandas as pd

from prompts import API_KEY

openai_client = OpenAI(api_key=API_KEY)

with open(r"C:\Users\pmpin\Documents\GitHub\ECE201A_Project\scripts\convos.json", "r") as f: # Load JSON data (of strict syntax examples, gotten from convos folder)
    data = json.load(f)

convo_examples = [{"name": key, "content": value} for key, value in data.items()]

def generate_embedding(text, model="text-embedding-3-small"):
    """
    Generates embeddings for a given text.
    """
    text = text.replace("\n", " ")  # Normalize text
    return openai_client.embeddings.create(input = [text], model=model).data[0].embedding

for example in convo_examples: # Generate embeddings for each example of strict syntax
    example["embedding"] = generate_embedding(example["content"])

with open("embedding_data.json", "w") as f:
    json.dump(convo_examples, f, indent=4)

