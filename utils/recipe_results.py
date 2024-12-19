import utils.utils as utils
import resend
import re
import time

resend.api_key = "re_3TfB9ALS_3uqWbj7fd6rCCZz7x2bodM4J"

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_recipe_email(recipe_details, recipient_email):
    """Send recipe details via email using Resend"""
    if not validate_email(recipient_email):
        return False
        
    html_content = f"""
        <h2>{recipe_details['name']}</h2>
        <h3>Ingredients:</h3>
        <ul>
            {''.join([f'<li>{ingredient}</li>' for ingredient in recipe_details['ingredients']])}
        </ul>
        <h3>Instructions:</h3>
        <ol>
            {''.join([f'<li>{step}</li>' for step in recipe_details['steps']])}
        </ol>
        <p>Cooking Time: {recipe_details['minutes']} minutes</p>
        <p>Calories: {recipe_details['calories']}</p>
    """
    
    params = {
        "from": "Recipe Recommender <nargiz@msba.food>",
        "to": [recipient_email],
        "subject": f"Recipe: {recipe_details['name']}",
        "html": html_content
    }
    
    try:
        resend.Emails.send(params)
        print("Email sent successfully") 
        return True
    except Exception:
        print("Email failed to send")
        return False

def display_recipe_results(st, recipes, prefix_key=""):
    """
    A reusable function to display recipe results in a consistent format
    
    Args:
        st: Streamlit instance
        recipes: DataFrame containing recipe results
        prefix_key: String prefix for unique plotly chart keys (default: "")
    """
    if recipes.empty:
        st.warning("No recipes found.")
        return
        
    # Get user's preferred difficulty level (0=Easy, 1=Medium, 2=Hard)
    user_difficulty = st.session_state['user_preferences']['difficulty_level']
    difficulty_labels = {0: "Easy", 1: "Medium", 2: "Hard"}
        
    for i, recipe in recipes.iterrows():
        recipe_name = recipe['name'].capitalize()
        expander_key = f"expander_{prefix_key}_{i}"
        recipe_id = recipe['id']
        
        # Calculate recipe difficulty based on steps and ingredients
        recipe_complexity = min(2, (recipe['n_steps'] + recipe['n_ingredients']) // 10)
        difficulty_match = "✅" if recipe_complexity == user_difficulty else ""
        
        # Create a styled expander header with emoji and better formatting
        with st.expander(f"{i + 1}. {recipe_name} {difficulty_match}", expanded=False):
            # Add like button and share button at the top of expander
            col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
            with col1:
                st.markdown(f"### {recipe_name}")
                st.markdown(f"*Difficulty: {difficulty_labels[recipe_complexity]}*")
            with col2:
                # Initialize favorite_recipes if it doesn't exist
                if 'favorite_recipes' not in st.session_state:
                    st.session_state['favorite_recipes'] = set()
                
                # Create a callback to handle favorite toggling
                def toggle_favorite(recipe_id=recipe_id):
                    if recipe_id in st.session_state['favorite_recipes']:
                        st.session_state['favorite_recipes'].discard(recipe_id)
                    else:
                        st.session_state['favorite_recipes'].add(recipe_id)
                
                # Check if recipe is favorite
                is_favorite = recipe_id in st.session_state['favorite_recipes']
                
                # Create button with callback and unique key
                st.button(
                    "❤️" if is_favorite else "🤍",
                    key=f"like_btn_{prefix_key}_{recipe_id}_{i}",
                    on_click=toggle_favorite,
                    kwargs={"recipe_id": recipe_id}
                )
            
            with col3:
                # Create unique key for email status
                email_status_key = f"email_status_{prefix_key}_{recipe_id}_{i}"
                
                # Initialize session state for email status if it doesn't exist
                if email_status_key not in st.session_state:
                    st.session_state[email_status_key] = None
                
                # Define a callback function to send the email
                def send_email_callback(recipe=recipe, email_status_key=email_status_key):
                    success = send_recipe_email(recipe, st.session_state['user_email'])
                    st.session_state[email_status_key] = "success" if success else "error_send"
                
                # Email button that triggers the callback
                st.button(
                    "📧",
                    key=f"share_btn_{prefix_key}_{recipe_id}_{i}",
                    on_click=send_email_callback
                )
                
                # Display status messages
                if st.session_state[email_status_key] == "success":
                    st.success("Recipe sent successfully!")
                elif st.session_state[email_status_key] == "error_send":
                    st.error("Failed to send recipe. Please try again.")

            # Styled tabs with custom CSS
            st.markdown("""
                <style>
                    .stTabs [data-baseweb="tab-list"] {
                        gap: 24px;
                    }
                    .stTabs [data-baseweb="tab"] {
                        padding: 10px 24px;
                        border-radius: 4px;
                    }
                </style>""", unsafe_allow_html=True)
            
            tab_1, tab_2, tab_3 = st.tabs(["📊 Summary", "🥗 Ingredients", "📝 Recipe"])

            with tab_1:
                # Enhanced metrics display with custom styling
                st.markdown("""
                    <style>
                        [data-testid="stMetricValue"] {
                            font-size: 1.8rem;
                            color: #FF6B6B;
                        }
                        [data-testid="stMetricLabel"] {
                            font-size: 1rem;
                            color: #4A4A4A;
                        }
                    </style>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(label="🔥 Calories", value=recipe["calories"])
                with col2:
                    st.metric(label="📝 Steps", value=recipe["n_steps"])
                with col3:
                    st.metric(label="🥘 Ingredients", value=recipe["n_ingredients"])
                with col4:
                    st.metric(label="⏱️ Cook Time", value=f"{recipe['minutes']} Mins")

                # Enhanced nutrition plot
                st.markdown("### 📊 Nutritional Information")
                fig = utils.plot_nutrition(recipe)
                st.plotly_chart(fig, key=f"nutrition_chart_{prefix_key}_{recipe_id}_{i}", use_container_width=True)

            with tab_2:
                st.markdown(f"""
                    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px;'>
                        <h4 style='color: #2c3e50; margin-bottom: 15px;'>
                            🥗 Ingredients ({recipe['n_ingredients']})
                        </h4>
                    </div>
                """, unsafe_allow_html=True)
                
                for idx, ingredient in enumerate(recipe["ingredients"]):
                    st.markdown(f"""
                        <div style='padding: 8px 15px; margin: 5px 0; background-color: white; 
                                border-left: 4px solid #FF6B6B; border-radius: 4px;'>
                            {ingredient.capitalize()}
                        </div>
                    """, unsafe_allow_html=True)

            with tab_3:
                st.markdown(f"""
                    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px;'>
                        <h4 style='color: #2c3e50; margin-bottom: 15px;'>
                            👩‍🍳 Cooking Instructions
                        </h4>
                    </div>
                """, unsafe_allow_html=True)
                
                for idx, step in enumerate(recipe["steps"]):
                    st.markdown(f"""
                        <div style='padding: 12px 15px; margin: 10px 0; background-color: white; 
                                border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                            <span style='color: #FF6B6B; font-weight: bold;'>Step {idx + 1}:</span> {step.capitalize()}
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("<hr style='margin: 30px 0; border: none; height: 1px; background-color: #eee;'>", 
                       unsafe_allow_html=True)