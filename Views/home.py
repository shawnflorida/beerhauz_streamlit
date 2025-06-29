import streamlit as st
from datetime import datetime
import uuid
from configs.firebase_config import get_firestore

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

def show_home():
    st.title("🏠 Welcome to Our Community")
    st.markdown("---")
    
    if st.session_state.get('user'):
        user_email = st.session_state.user.email
        st.success(f"👋 Welcome back, {user_email.split('@')[0]}!")
    
    st.markdown("""
    ## About This Platform
    
    This is a community platform where you can:
    - 📢 Share announcements with others
    - 💬 Engage in discussions
    - 👤 Build your professional profile
    
    Use the sidebar to navigate between different sections.
    """)


def show_profile():
    st.title("👤 Your Profile")
    st.markdown("---")
    
    if st.session_state.get('is_authenticated', False):
        user_email = st.session_state.user.email
        st.subheader(f"Account Information")
        st.write(f"**Email:** {user_email}")
        
        # Add more profile fields here
        with st.form("profile_form"):
            st.subheader("Update Profile")
            name = st.text_input("Full Name")
            bio = st.text_area("Bio")
            skills = st.text_input("Skills (comma separated)")
            
            if st.form_submit_button("Update Profile"):
                st.success("Profile updated successfully!")
    else:
        st.warning("Please login to view your profile")

# Sidebar navigation
with st.sidebar:
    st.title("Navigation")
    if st.button("🏠 Home"):
        st.session_state.current_page = "Home"
    if st.button("📢 Announcements"):
        st.session_state.current_page = "Announcements"
    if st.button("👤 Profile"):
        st.session_state.current_page = "Profile"

