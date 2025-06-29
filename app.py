import streamlit as st

st.set_page_config(
    page_title="Beerhaus Community Page",
    page_icon="🍺",
)

from Views.home import show_home
from Views.login import show_login
from Views.members import show_members
from Views.signup import show_signup
from Views.announcements import show_announcements
from Views.profile import show_profile

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Login"
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

def logout():
    """Handle logout functionality"""
    st.session_state.is_authenticated = False
    st.session_state.user = None
    st.session_state.current_page = "Login"
    st.rerun()

def navigate_to(page):
    """Handle navigation to a specific page"""
    st.session_state.current_page = page
    st.rerun()

def main():
    # Custom CSS for better styling
    st.markdown("""
    <style>
        .stButton button {
            border: none !important;
        }
        .success-message {
            text-align: center;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .sidebar .sidebar-content {
            background-color: var(--secondary-background-color);
        }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.is_authenticated:
        # Sidebar navigation
        with st.sidebar:
            st.title("🍺 Beerhaus Community Page")

            if st.button("🏠 Home", key="home_btn"):
                if st.session_state.current_page == "Home":
                    st.rerun()
                else:
                    navigate_to("Home")

            if st.button("📢 Announcements", key="announcements_btn"):
                if st.session_state.current_page == "Announcements":
                    st.rerun()
                else:
                    navigate_to("Announcements")

            if st.button("👤 Profile", key="profile_btn"):
                if st.session_state.current_page == "Profile":
                    st.rerun()
                else:
                    navigate_to("Profile")

            if st.button("👥 Members", key="members_btn"):
                if st.session_state.current_page == "Members":
                    st.rerun()
                else:
                    navigate_to("Members")

            st.markdown("---")

            if st.button("🔒 Logout", key="logout_btn", type="primary", use_container_width=True):
                logout()

        # Main content area - switch based on current_page
        if st.session_state.current_page == "Home":
            show_home()
        elif st.session_state.current_page == "Announcements":
            show_announcements()
        elif st.session_state.current_page == "Profile":
            show_profile()
        elif st.session_state.current_page == "Members":
            show_members()
        else:
            # Default to home if unknown page
            st.session_state.current_page = "Home"
            st.rerun()
    else:
        # Unauthenticated view - show login or signup
        if st.session_state.current_page == "Login":
            show_login()
        elif st.session_state.current_page == "SignUp":
            show_signup()
        else:
            # Default to login if unknown page
            st.session_state.current_page = "Login"
            st.rerun()

if __name__ == "__main__":
    main()
