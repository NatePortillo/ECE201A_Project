import json
import pandas as pd
import numpy as np

from RAG.create_embeddings import generate_embedding

DF_ANALOG = pd.read_json("../ECE201A_Project/RAG/analog_embedding_data.json")
DF_CONVOS = pd.read_json("../ECE201A_Project/RAG/convos_embedding_data.json")

def cosine_similarity(a, b):
    """
    Calculates the cosine similarity between two vectors.

    Cosine similarity measures the cosine of the angle between two vectors,
    providing a value between -1 (completely opposite) and 1 (completely identical).

    Args:
        a (numpy.ndarray): The first vector.
        b (numpy.ndarray): The second vector.

    Returns:
        float: The cosine similarity between the two vectors.
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_strict_syntax(df, input_description, n=3, model='text-embedding-3-small'):
    """
    Searches for the most relevant examples in a DataFrame based on input description.

    This function generates an embedding for the input description, computes the cosine similarity
    between the embedding and embeddings in the DataFrame, and retrieves the top `n` most relevant
    rows.

    Args:
        df (pandas.DataFrame): The DataFrame containing embeddings and their corresponding content.
            Must include a column named 'embedding' with vector data.
        input_description (str): The input description to be compared against the embeddings.
        n (int, optional): The number of top matches to retrieve. Defaults to 3.
        model (str, optional): The embedding model to use. Defaults to 'text-embedding-3-small'.

    Returns:
        pandas.DataFrame: A DataFrame containing the top `n` rows sorted by similarity in descending order.
    """
    embedding = generate_embedding(input_description, model=model)

    df['similarities'] = df.embedding.apply(lambda x: cosine_similarity(x, embedding)) # Compute cosine similarities (according to openAI source code)
    
    res = df.sort_values('similarities', ascending=False).head(n) # Retrieve top `n` most relevant examples
    
    return res

def parse_embeddings(df, input_prompt):
    """
    Extracts the content of the most relevant examples based on cosine similarity.

    This function performs a similarity search in the given DataFrame using the input prompt
    and retrieves the `content` field of the top matches.

    Args:
        df (pandas.DataFrame): The DataFrame containing embeddings and their corresponding content.
            Must include a column named 'embedding' with vector data.
        input_prompt (str): The input prompt to compare against the embeddings.

    Returns:
        list: A list of `content` strings from the most relevant examples.
    """
    content_list = []
    results = search_strict_syntax(df, input_prompt)

    for idx, row in results.iterrows():
        content_list.append(row['content'])
    return content_list

# Test
#res_analog = search_strict_syntax(df=DF_ANALOG, input_description="Create a strong-arm latch using interdigitated placement to match the cross-coupled inverters")
#res_convos = search_strict_syntax(df=DF_CONVOS, input_description="Create a strong-arm latch using interdigitated placement to match the cross-coupled inverters")