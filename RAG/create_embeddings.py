from openai import OpenAI
import json
import pandas as pd

openai_client = OpenAI(api_key = "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")

# Load JSON data (of strict syntax examples, gotten from convos folder)
with open(r"C:\Users\natha\Desktop\ECE201A_Project\scripts\convos.json", "r") as f:
    data = json.load(f)

convo_examples = [{"name": key, "content": value} for key, value in data.items()]

def generate_embedding(text, model="text-embedding-3-small"):
    """Generate embeddings for a given text."""
    text = text.replace("\n", " ")  # Normalize text
    return openai_client.embeddings.create(input = [text], model=model).data[0].embedding

for example in convo_examples: # Generate embeddings for each example of strict syntax
    example["embedding"] = generate_embedding(example["content"])

with open("embedding_data.json", "w") as f:
    json.dump(convo_examples, f, indent=4)

