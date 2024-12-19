import utils.utils as utils
from utils.recipe_results import display_recipe_results

def show_recipe_search(st):
    st.title("Recipe Search")

    # Initialize session state variables
    if "result" not in st.session_state:
        st.session_state["result"] = None

    # Search bar for recipes
    recipe = st.text_input(
        "Search for a recipe:",
        key="recipe_search_input"
    )

    if recipe:
        # Filter recipes that contain the search term
        matching_recipes = st.session_state["df"][st.session_state["df"]["name"].str.contains(recipe, case=False, na=False)]
        
        if not matching_recipes.empty:
            # Get first matching recipe
            recipe_name = matching_recipes["name"].iloc[0]
            num_recipes = 5  # Default number of similar recipes to show

            st.session_state["result"] = utils.find_similar_recipe(
                recipe_name, st, num_recipes
            )

            # Display results if available
            if st.session_state["result"] is not None:
                display_recipe_results(st, st.session_state["result"], prefix_key="search")
        else:
            st.warning("No recipes found matching your search.")
