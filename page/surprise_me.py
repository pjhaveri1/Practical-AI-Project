from utils.recipe_results import display_recipe_results

def show_surprise_me(st):
    st.title("✨ Surprise Me with a Recipe!")

    num_random_recipes = 5  # Specify how many random recipes to display
    random_recipes = st.session_state["df"].sample(n=num_random_recipes)  # Sample random recipes
    st.session_state["result"] = random_recipes

    # Display random recipes
    st.subheader("Here are your surprise recipes!")
    display_recipe_results(st, random_recipes, prefix_key="random")
