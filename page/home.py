from pathlib import Path
import json
import utils.utils as utils
from utils.recipe_results import display_recipe_results

def load_ingredient_categories():
    """Load ingredient categories from JSON file"""
    categories_path = Path(__file__).parent.parent / "data" / "ingredients.json"
    with open(categories_path) as f:
        return json.load(f)

def render_ingredient_category(st, col, category_name, ingredients, session_key):
    """Render an ingredient category with its checkboxes"""
    with col:
        st.markdown(f"""
            <div class="category-header {category_name.lower()}">
                <h3 style='text-align: center;'>{category_name}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        selected_count = 0
        preferences = st.session_state.get('user_preferences', {}).get('dietary', {})
        
        for label, ingredient_id, color, dietary_info in ingredients:
            # Check if ingredient matches dietary preferences
            should_show = True
            if preferences.get('vegetarian') and not dietary_info.get('vegetarian'):
                should_show = False
            if preferences.get('gluten_free') and not dietary_info.get('gluten_free'):
                should_show = False  
            if preferences.get('dairy_free') and not dietary_info.get('dairy_free'):
                should_show = False
            if preferences.get('vegan') and not dietary_info.get('vegan'):
                should_show = False

            if should_show:
                if st.checkbox(label, key=f"{category_name.lower()}_{ingredient_id}"):
                    if ingredient_id not in st.session_state[session_key]:
                        st.session_state[session_key].append(ingredient_id)
                    selected_count += 1
                elif ingredient_id in st.session_state[session_key]:
                    st.session_state[session_key].remove(ingredient_id)
        
        if selected_count > 0:
            st.markdown(f"<p style='text-align: center; color: #666;'>{selected_count} selected</p>", 
                       unsafe_allow_html=True)

def initialize_session_state(st):
    """Initialize session state variables if they don't exist"""
    if 'selected_veggies' not in st.session_state:
        st.session_state.selected_veggies = []
    if 'selected_protein' not in st.session_state:
        st.session_state.selected_protein = []
    if 'selected_grain' not in st.session_state:
        st.session_state.selected_grain = []
    if 'selected_dairy' not in st.session_state:
        st.session_state.selected_dairy = []
    if 'favorite_recipes' not in st.session_state:
        st.session_state.favorite_recipes = set()

def show_home_page(st):
    # Initialize session state
    initialize_session_state(st)
    
    # Load custom CSS
    with open(Path(__file__).parent.parent / "static" / "style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Hero section
    st.markdown("""
        <div class="hero-container">
            <h1 style='color: white; font-size: 2.5rem; text-align: center;'>
                🥳 Welcome to our Food Recipe Recommender! 🍳
            </h1>
            <p style='color: white; text-align: center; font-size: 1.2rem;'>
                Discover delicious recipes tailored to your ingredients. 
                Let's make cooking an adventure!
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Tabs for Home and Favorites
    tab1, tab2 = st.tabs(["🏠 Home", "❤️ Favorites"])

    with tab1:
        # Ingredient Selection Container
        st.markdown("""
            <div style='background: #f8f9fa; padding: 2rem; border-radius: 1rem; 
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;'>
                <h2 style='color: #333; margin-bottom: 1.5rem;'>🥗 Select Your Ingredients</h2>
            </div>
        """, unsafe_allow_html=True)

        # In the ingredients section, add a clear button:
        col1, col2 = st.columns([4, 1])

        # Load and render ingredient categories
        categories = load_ingredient_categories()
        cols = st.columns(4)
        
        render_ingredient_category(st, cols[0], "Vegetables", categories["vegetables"], "selected_veggies")
        render_ingredient_category(st, cols[1], "Proteins", categories["proteins"], "selected_protein")
        render_ingredient_category(st, cols[2], "Grains", categories["grains"], "selected_grain")
        render_ingredient_category(st, cols[3], "Dairy", categories["dairy"], "selected_dairy")

        # Styled button container
        st.markdown(
            "<div style='text-align: center; margin: 2rem 0;'>", unsafe_allow_html=True)
        if st.button("🔍 Find My Perfect Recipe",
                     key="recipe_button",
                     help="Click to get personalized recipe recommendations",
                     type="primary"):
            # Initialize filtered_recipes based on original data
            filtered_recipes = st.session_state["df"]

            # Enhanced filtering logic with progress indication
            with st.spinner("Finding your perfect recipes..."):
                # Combine all selected ingredients into a search query
                search_ingredients = []
                if st.session_state.selected_veggies:
                    search_ingredients.extend(st.session_state.selected_veggies)
                if st.session_state.selected_protein:
                    search_ingredients.extend(st.session_state.selected_protein)
                if st.session_state.selected_grain:
                    search_ingredients.extend(st.session_state.selected_grain)
                if st.session_state.selected_dairy:
                    search_ingredients.extend(st.session_state.selected_dairy)

                # Use semantic search to find similar recipes
                if search_ingredients:
                    search_query = ", ".join(search_ingredients)
                    filtered_recipes = utils.find_similar_recipe(
                        search_query, st, 5)
            if filtered_recipes is not None:
                st.markdown("""
                    <div style='background: #f1f8e9; padding: 1.5rem; border-radius: 1rem; 
                               margin-top: 2rem; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h2 style='color: #33691e; text-align: center;'>✨ Your Personalized Recipes ✨</h2>
                    </div>
                """, unsafe_allow_html=True)
                display_recipe_results(
                    st, filtered_recipes[:5], prefix_key="filter")
            else:
                st.error(
                    "😔 No recipes found with your selected ingredients. Try different combinations!")

    with tab2:
        if not st.session_state.get('favorite_recipes'):
            st.session_state['favorite_recipes'] = set()

        st.markdown("""
            <div style='background: #ffebee; padding: 2rem; border-radius: 1rem; 
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
                <h2 style='color: #c62828; text-align: center;'>❤️ Your Favorite Recipes</h2>
            </div>
        """, unsafe_allow_html=True)

        favorite_ids = st.session_state['favorite_recipes']
        
        if favorite_ids:
            # Filter the dataframe to get favorite recipes
            favorite_recipes = st.session_state["df"][st.session_state["df"]['id'].isin(favorite_ids)]
            st.markdown(f"### You have {len(favorite_recipes)} favorite recipes")
            
            for _, recipe in favorite_recipes.iterrows():
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.markdown(f"<div class='favorite-recipe-card'>• {recipe['name'].capitalize()}</div>",
                              unsafe_allow_html=True)
                with col2:
                    if st.button("❌", key=f"remove_favorite_{recipe['id']}"):
                        st.session_state['favorite_recipes'].discard(recipe['id'])
                        st.rerun()
            
            if st.button("Clear All Favorites", key="clear_all_favorites", type="secondary"):
                st.session_state['favorite_recipes'] = set()
                st.rerun()
        else:
            st.info("No favorite recipes yet! Start exploring recipes to add some favorites.")
