import streamlit as st
from firebase_admin import auth as firebase_auth
from configs.firebase_config import get_auth

def show_login():
    auth = get_auth()
    
    st.title("Login")
    st.write("Welcome back! Please enter your credentials.")
    
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns([14, 3.8])
    with col1:
        if st.button("Login"):
            try:
                # In a real app, you would use Firebase Auth SDK to sign in
                # This is simplified for demonstration
                user = firebase_auth.get_user_by_email(login_email)
                st.session_state.user = user
                st.session_state.is_authenticated = True
                st.success(f"Welcome back, {user.email}!")
                st.rerun()  # This will refresh the page
            except firebase_auth.UserNotFoundError:
                st.error("User not found. Please check your email or sign up.")
            except Exception as e:
                st.error(f"Login failed: {e}")
    
    with col2:
        if st.button("Forgot Password?"):
            st.info("Password reset functionality would go here")

    # Add a divider and link to signup
    st.divider()
    if st.button("📝 Go to Sign Up"):
        st.session_state.current_page = "SignUp"
        st.rerun()