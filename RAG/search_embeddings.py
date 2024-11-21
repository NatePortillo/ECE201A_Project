import json
import pandas as pd
import numpy as np

from RAG.create_embeddings import generate_embedding

DF_ANALOG = pd.read_json("../ECE201A_Project/RAG/analog_embedding_data.json")
DF_CONVOS = pd.read_json("../ECE201A_Project/RAG/convos_embedding_data.json")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_strict_syntax(df, input_description, n=3, model='text-embedding-3-small'):
    embedding = generate_embedding(input_description, model=model)

    df['similarities'] = df.embedding.apply(lambda x: cosine_similarity(x, embedding)) # Compute cosine similarities (according to openAI source code)
    
    res = df.sort_values('similarities', ascending=False).head(n) # Retrieve top `n` most relevant examples
    
    return res

def parse_embeddings(df, input_prompt):
    content_list = []
    results = search_strict_syntax(df, input_prompt)

    for idx, row in results.iterrows():
        content_list.append(row['content'])
    return content_list

# Test
#res_analog = search_strict_syntax(df=DF_ANALOG, input_description="Create a strong-arm latch using interdigitated placement to match the cross-coupled inverters")
#res_convos = search_strict_syntax(df=DF_CONVOS, input_description="Create a strong-arm latch using interdigitated placement to match the cross-coupled inverters")