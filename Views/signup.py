import streamlit as st
from configs.firebase_config import get_auth, get_firestore, get_storage
import datetime
import uuid
import time

def show_signup():
    auth = get_auth()
    firestore_db = get_firestore()
    storage_bucket = get_storage()

    st.markdown("## 📝 Create Your Account")
    # Authentication Info
    st.subheader("🔐 Account Credentials")
    email = st.text_input("📧 Email", value=st.session_state.get("email", ""), placeholder="you@example.com")
    password = st.text_input("🔑 Password", type="password", value=st.session_state.get("password", ""), placeholder="Create a strong password")

    # Profile Info
    st.subheader("🙋 Personal & Professional Info")
    # First row: First Name, Last Name
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name", value=st.session_state.get("first_name", ""))
    with col2:
        last_name = st.text_input("Last Name", value=st.session_state.get("last_name", ""))

    # Second row: Company (full width)
    company = st.text_input("Company", value=st.session_state.get("company", ""))

    # Third row: Position, Phone
    col1, col2 = st.columns(2)
    with col1:
        position = st.text_input("Position", value=st.session_state.get("position", ""))
    with col2:
        phone = st.text_input("Phone", value=st.session_state.get("phone", ""))

    # Fourth row: Street (full width)
    street = st.text_input("Street", value=st.session_state.get("street", ""))

    # Fifth row: City, State, Zip Code
    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.text_input("City", value=st.session_state.get("city", ""))
    with col2:
        state = st.text_input("State", value=st.session_state.get("state", ""))
    with col3:
        zip_code = st.text_input("Zip Code", value=st.session_state.get("zip_code", ""))

        # Sixth row: Country (full width)
    country = st.text_input("Country", value=st.session_state.get("country", ""))

    bio = st.text_area("🗒️ Bio", value=st.session_state.get("bio", ""), placeholder="Tell us something about yourself...")
    skills = st.text_input("🛠️ Skills (comma separated)", value=st.session_state.get("skills", ""), placeholder="e.g., Python, Machine Learning, SQL")

    profile_pic = st.file_uploader("📷 Upload Profile Picture", type=["jpg", "jpeg", "png"])

    if st.button("✅ Create Account"):
        try:
            # Firebase Auth
            user = auth.create_user(email=email, password=password)
            uid = user.uid

            # Upload profile picture (optional)
            profile_pic_url = ""
            if profile_pic:
                blob = storage_bucket.blob(f"profile_pics/{uid}_{uuid.uuid4()}")
                blob.upload_from_file(profile_pic, content_type=profile_pic.type)
                profile_pic_url = blob.generate_signed_url(datetime.timedelta(days=365), method='GET')

            # Firestore user document
            user_data = {
                'email': email,
                'created_at': datetime.datetime.utcnow(),
                'role': 'user',
                'first_name': first_name,
                'last_name': last_name,
                'company': company,
                'position': position,
                'phone': phone,
                'address': {
                    'street': street,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code,
                    'country': country
                },
                'profile_pic_url': profile_pic_url,
                'skills': [skill.strip() for skill in skills.split(',')] if skills else [],
                'bio': bio
            }

            firestore_db.collection("users").document(uid).set(user_data)

            st.success("🎉 Account created successfully! You can now log in.")
            time.sleep(2)
            st.session_state.current_page = "Login"
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error during sign-up: {e}")

    # Footer
    st.markdown("---")
    if st.button("👀 Already have an account?"):
        st.session_state.current_page = "Login"
        st.rerun()