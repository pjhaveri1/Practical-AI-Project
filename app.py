import streamlit as st
import json
from datetime import datetime
import time

# Configuration Constants
APP_CONFIG = {
    'page_title': "Food Recipe Recommender",
    'layout': "wide", 
    'initial_sidebar_state': "expanded",
    'page_icon': "./data/logo.png",
    'menu_items': {
        'Get Help': 'mailto:nargiz.seisek@gmail.com',
        'About': "# Food Recipe Recommender\nYour personal cooking assistant!"
    }
}

# Must be first Streamlit command
st.set_page_config(**APP_CONFIG)

from utils.data_loader import load_data, load_css
from page.home import show_home_page
from page.recipe_search import show_recipe_search
from page.surprise_me import show_surprise_me
import utils.utils as utils

INITIAL_USER_PREFERENCES = {
    'dietary': {
        'vegetarian': False,
        'vegan': False,
        'gluten_free': False,
        'dairy_free': False
    },
    'difficulty_level': None,
}

# Initialize session state
def initialize_session_state():
    if 'page_views' not in st.session_state:
        st.session_state['page_views'] = {'🏠 Home': 0, '🔍 Recipe Search': 0, '✨ Surprise Me!': 0}
    if 'last_visit' not in st.session_state:
        st.session_state['last_visit'] = datetime.now()
    if 'favorite_recipes' not in st.session_state:
        st.session_state['favorite_recipes'] = set()
    if 'user_preferences' not in st.session_state:
        st.session_state['user_preferences'] = INITIAL_USER_PREFERENCES.copy()
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = "🏠 Home"

# Enhanced data loading with proper error handling
@st.cache_data(ttl=3600, show_spinner=False)
def load_recipe_data():
    try:
        with st.spinner('Loading recipe database...'):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)  # Reduced sleep time for better performance
                progress_bar.progress(i + 1)
            data = load_data()
            progress_bar.empty()
            return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def render_sidebar():
    with st.sidebar:
        st.title("🍽️ Recipe Recommender")
        st.header("Explore Our Features")
        
        render_user_preferences()
        render_favorite_recipes()
        render_analytics()
        render_email_form()

def render_user_preferences():
    with st.sidebar.expander("⚙️ User Preferences"):
        preferences = st.session_state['user_preferences']
        
        # Difficulty level preferences
        difficulty_options = ["Easy", "Medium", "Hard"]
        difficulty_values = [0, 1, 2]
        
        current_display = preferences.get('difficulty_level')
        if current_display is None:
            current_display = 1  # Default to Medium (1)
        
        selected_display = st.select_slider(
            "Cooking Difficulty",
            options=difficulty_options,
            value=difficulty_options[1]  # Default to Medium
        )
        
        new_difficulty = difficulty_values[difficulty_options.index(selected_display)]
        
        # Dietary preferences
        st.write("Dietary Preferences:")
        col1, col2 = st.columns(2)
        
        with col1:
            vegetarian = st.checkbox("Vegetarian", value=preferences['dietary']['vegetarian'])
            vegan = st.checkbox("Vegan", value=preferences['dietary']['vegan'])
            gluten_free = st.checkbox("Gluten Free", value=preferences['dietary']['gluten_free'])
        
        with col2:
            dairy_free = st.checkbox("Dairy Free", value=preferences['dietary']['dairy_free'])
        
        # Update preferences if changed
        if (preferences['difficulty_level'] != new_difficulty or
            preferences['dietary']['vegetarian'] != vegetarian or
            preferences['dietary']['vegan'] != vegan or
            preferences['dietary']['gluten_free'] != gluten_free or
            preferences['dietary']['dairy_free'] != dairy_free):
            
            preferences['difficulty_level'] = new_difficulty
            preferences['dietary']['vegetarian'] = vegetarian
            preferences['dietary']['vegan'] = vegan
            preferences['dietary']['gluten_free'] = gluten_free
            preferences['dietary']['dairy_free'] = dairy_free
            
            # Filter recipes based on all preferences
            filtered_df = st.session_state['all_records'].copy()
            
            # Apply difficulty filter
            recipe_complexity = [(r['n_steps'] + r['n_ingredients']) // 10 for _, r in filtered_df.iterrows()]
            recipe_complexity = [min(2, c) for c in recipe_complexity]
            filtered_df = filtered_df[[c == new_difficulty for c in recipe_complexity]]
            
            # Apply dietary filters
            if vegetarian:
                filtered_df = filtered_df[filtered_df['is_vegetarian']]
            if vegan:
                filtered_df = filtered_df[filtered_df['is_vegan']]
            if gluten_free:
                filtered_df = filtered_df[filtered_df['is_gluten_free']]
            if dairy_free:
                filtered_df = filtered_df[filtered_df['is_dairy_free']]
                
            st.session_state['df'] = filtered_df
            st.rerun()

def render_favorite_recipes():
    with st.sidebar.expander("❤️ Favorite Recipes"):
        favorite_ids = st.session_state.get('favorite_recipes', set())
        if not favorite_ids:
            st.write("No favorite recipes yet!")
            return
            
        try:
            # Filter the dataframe to get favorite recipes
            favorite_recipes = st.session_state["df"][st.session_state["df"]['id'].isin(favorite_ids)]
            
            st.write(f"You have {len(favorite_recipes)} favorite recipes:")
            
            for _, recipe in favorite_recipes.iterrows():
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.write(f"• {recipe['name'].capitalize()}")
                with col2:
                    if st.button("❌", key=f"sidebar_remove_{recipe['id']}"):
                        st.session_state['favorite_recipes'].discard(recipe['id'])
                        st.rerun()
            
            if st.button("Clear All Favorites"):
                st.session_state['favorite_recipes'] = set()
                st.rerun()
                
        except Exception as e:
            st.error(f"Error displaying favorites: {str(e)}")
            st.session_state['favorite_recipes'] = set()

def render_analytics():
    with st.sidebar.expander("📊 Your Activity"):
        st.write(f"Total Recipes Available: {st.session_state.get('total_recipes', 0)}")
        st.write(f"Favorite Recipes: {len(st.session_state['favorite_recipes'])}")
        st.write(f"Last Visit: {st.session_state['last_visit'].strftime('%Y-%m-%d %H:%M')}")

def render_email_form():
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = ""  
    st.text_input(
        "Enter email:", 
        value=st.session_state['user_email'],
        key="email_input",
        on_change=lambda: setattr(st.session_state, 'user_email', st.session_state.email_input)
    )

def render_navigation():
    col1, col2, col3 = st.columns(3)
    pages = {
        "🏠 Home": col1,
        "🔍 Recipe Search": col2,
        "✨ Surprise Me!": col3
    }
    
    for page_name, col in pages.items():
        with col:
            if st.button(page_name):
                st.session_state['current_page'] = page_name
                st.session_state['page_views'][page_name] += 1

def main():
    # Initialize session state
    initialize_session_state()
    load_css()
    # Load custom CSS
    st.markdown("""
        <style>
            .reportview-container { margin-top: -2em; }
            #MainMenu {visibility: hidden;}
            .stAppDeployButton {display:none;}
            footer {visibility: hidden;}
            #stDecoration {display:none;}
        </style>
    """, unsafe_allow_html=True)
    
    # Load data if not already loaded
    if 'df' not in st.session_state or 'all_records' not in st.session_state:
        df = load_recipe_data()
        if df is not None:
            st.session_state['all_records'] = df.copy()  # Store complete dataset
            st.session_state['df'] = df  # Current filtered dataset
            st.session_state['total_recipes'] = len(df)
            st.session_state['cuisines'] = df['cuisine'].unique().tolist() if 'cuisine' in df.columns else []
            st.session_state['avg_cooking_time'] = df['cooking_time'].mean() if 'cooking_time' in df.columns else 0
        else:
            st.error("Critical Error: Failed to load recipe database")
            st.warning("Please try refreshing the page or contact support")
            st.stop()
    
    # Render sidebar
    render_sidebar()
    
    # Render navigation
    render_navigation()
    
    # Route to appropriate page
    pages = {
        "🏠 Home": show_home_page,
        "🔍 Recipe Search": show_recipe_search,
        "✨ Surprise Me!": show_surprise_me
    }
    
    current_page = st.session_state['current_page']
    if current_page in pages:
        pages[current_page](st)
    
    # Update last visit timestamp
    st.session_state['last_visit'] = datetime.now()

if __name__ == "__main__":
    main()