import streamlit as st
import pandas as pd
import os
import ast
import numpy as np

def safe_eval(x):
    """Safely evaluate string representations of lists"""
    if isinstance(x, (list, np.ndarray)):
        return x
    try:
        return ast.literal_eval(x)
    except (ValueError, SyntaxError):
        if isinstance(x, str):
            return x.strip('[]').replace("'", "").replace('"', "").split(',')
        return x

def clean_ingredients(ingredients):
    """Clean ingredient list items"""
    if isinstance(ingredients, (list, np.ndarray)):
        return [str(i).strip() for i in ingredients if str(i).strip()]
    return []

def load_css():
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_data():
    parquet_directory = "./data/recipes.parquet"

    if not parquet_directory:
        st.error("No Parquet files found in the specified directory.")
        st.stop()

    try:
        df = pd.read_parquet(parquet_directory)
        df['id'] = df.index.astype(str)
        
        # Process ingredients column with improved error handling
        df["ingredients"] = df["ingredients"].apply(safe_eval)
        df["ingredients"] = df["ingredients"].apply(clean_ingredients)
        
        return df
    except Exception as e:
        st.error(f"Error reading parquet files: {e}")
        return None