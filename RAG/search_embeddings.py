import json
import pandas as pd
import numpy as np

from create_embeddings import generate_embedding

# Load the preprocessed JSON into a DataFrame
df = pd.read_json("embedding_data.json")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_strict_syntax(df, input_description, n=3, model='text-embedding-3-small'):
    embedding = generate_embedding(input_description, model=model)
    
    # Compute cosine similarities (according to openAI source code)
    df['similarities'] = df.embedding.apply(lambda x: cosine_similarity(x, embedding))
    
    res = df.sort_values('similarities', ascending=False).head(n) # Retrieve top `n` most relevant examples
    
    return res

# Test
res = search_strict_syntax(df=df, input_description="Create a strong-arm latch using interdigitated placement to match the cross-coupled inverters")
print(res)

for idx, row in res.iterrows():
    print(row['content']) 
    print("\n---\n")