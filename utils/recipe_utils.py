import streamlit as st
from utils.utils import plot_nutrition

def display_recipe_results(results):
    for i in range(results.shape[0]):
        dfx = results.iloc[i]

        with st.expander(f"{i + 1}. {dfx['name'].capitalize()}"):
            tab_1, tab_2, tab_3 = st.tabs(["Summary", "Ingredients", "Recipe"])

            with tab_1:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(label="Calories", value=dfx["calories"])
                with col2:
                    st.metric(label="Number of Steps", value=dfx["n_steps"])
                with col3:
                    st.metric(label="Number of Ingredients", value=dfx["n_ingredients"])
                with col4:
                    st.metric(label="Cooking Time", value=f"{dfx['minutes']} Mins")

                # Plot nutritional details
                fig = plot_nutrition(dfx)
                st.plotly_chart(fig, key=f"nutrition_chart_{i}")

            with tab_2:
                st.text(f"Number of Ingredients: {dfx['n_ingredients']}")
                for idx, ingredient in enumerate(dfx["ingredients"]):
                    st.markdown(f"{idx + 1}. {ingredient}")

            with tab_3:
                st.text("Recipe")
                for idx, step in enumerate(dfx["steps"]):
                    st.markdown(f"{idx + 1}. {step}")