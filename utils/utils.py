import numpy as np
import plotly.graph_objects as go
from sentence_transformers import SentenceTransformer
import streamlit as st

@st.cache_resource
def load_model():
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Initialize model at module level
model = load_model()

def cosine_similarity(vec1, vec2):
    """
    Returns the cosine similarity between two vectors of n dimension using vectorized operations
    """
    # Vectorized computation of cosine similarity
    dot_product = np.dot(vec1, vec2)
    norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    return np.round((dot_product / norm_product) * 100, 2)

def find_similar_recipe(query, st, num_recipes):
    '''
    Calculates the similarity of a given query with rest of the recipes
    Returns a dataframe with the most similar recipes
    '''
    df = st.session_state['df']
    # Get query vector efficiently using boolean indexing 
    vector = model.encode(query)
    
    # Pre-compute embeddings array once
    embeddings = np.vstack(df["embedding"].values)
    
    # Vectorized similarity computation
    similarities = np.dot(embeddings, vector) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(vector)
    ) * 100
    
    # Get indices of top similar recipes
    # Changed to include all requested recipes
    top_indices = np.argsort(similarities)[-num_recipes:][::-1]
    
    # Create result dataframe efficiently
    df_result = df.iloc[top_indices].copy()
    df_result["similarity"] = similarities[top_indices]
    df_result.drop("embedding", axis=1, inplace=True)

    return df_result

def plot_nutrition(data):

    '''
    Plots a bar graph showing the nutritional facts of each recipe
    Returns a plotly.graph_objects
    '''
    x = data.index[8:13]
    y = data.values[8:13]

    fig = go.Figure(
        go.Bar(
            name="",
            x=x,
            y=y,
            width=0.2,
            uirevision=True,
            # marker=dict(color=list(map(setColor, y))),
            hovertemplate="<br><b>%{x}</b>: %{y:.2f}",
        ),
    )
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=20, b=20),
        width=500,
        height=200,
    )
    fig.update_xaxes(
        showgrid=False,
    )
    # fig.update_yaxes(
    #     showgrid=False,
    #     showticklabels=False
    # )
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    return fig