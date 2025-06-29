import streamlit as st
from datetime import datetime, timedelta
from configs.firebase_config import get_firestore, get_storage
import uuid


@st.cache_data(show_spinner=False)
def get_user_data(_firestore_db, user_id):
    doc_ref = _firestore_db.collection("users").document(user_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else {}


def show_profile():
    firestore_db = get_firestore()
    storage_bucket = get_storage()

    st.title("👤 User Profile")
    st.markdown("---")

    if not st.session_state.get('is_authenticated', False):
        st.warning("🔒 Please login to view your profile")
        return

    user_email = st.session_state.user.email
    user_id = st.session_state.user.uid

    try:
        user_data = get_user_data(firestore_db, user_id)
    except Exception as e:
        st.error(f"Error loading profile: {e}")
        user_data = {}

    profile_pic_url = user_data.get('profile_pic_url', 'https://ui-avatars.com/api/?name=User&background=random')
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="{profile_pic_url}" 
                 style="border-radius: 50%; object-fit: cover; width: 300px; height: 300px; max-width: 90vw;" 
                 alt="Profile Picture"/>
        </div>
        """,
        unsafe_allow_html=True
    )

    edit_mode = st.toggle("✏️ Edit Profile", key="edit_toggle")

    if edit_mode:
        with st.form("profile_edit_form"):

            st.subheader("🔐 Account Credentials")
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("📧 Email", value=user_email, disabled=True)
            with col2:
                password = st.text_input("🔑 Password", value="", type="password", placeholder="Leave blank to keep current")

            st.subheader("🙋 Personal & Professional Info")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", value=user_data.get("first_name", ""))
                position = st.text_input("Position", value=user_data.get("position", ""))
                street = st.text_input("Street", value=user_data.get("address", {}).get("street", ""))
            with col2:
                last_name = st.text_input("Last Name", value=user_data.get("last_name", ""))
                phone = st.text_input("Phone", value=user_data.get("phone", ""))
                company = st.text_input("Company", value=user_data.get("company", ""))

            col1, col2, col3 = st.columns(3)
            with col1:
                city = st.text_input("City", value=user_data.get("address", {}).get("city", ""))
            with col2:
                state = st.text_input("State", value=user_data.get("address", {}).get("state", ""))
            with col3:
                zip_code = st.text_input("Zip Code", value=user_data.get("address", {}).get("zip_code", ""))

            country = st.text_input("Country", value=user_data.get("address", {}).get("country", ""))

            st.subheader("🗒️ Bio & Skills")
            bio = st.text_area("Bio", value=user_data.get("bio", ""), height=150)
            skills = st.text_input("Skills (comma-separated)", ", ".join(user_data.get("skills", [])))

            new_profile_pic = st.file_uploader("📷 Upload New Profile Picture", type=["jpg", "jpeg", "png"])

            submitted = st.form_submit_button("💾 Save Profile")

            if submitted:
                try:
                    new_profile_pic_url = profile_pic_url
                    if new_profile_pic:
                        if profile_pic_url and "profile_pics" in profile_pic_url:
                            try:
                                old_blob_name = profile_pic_url.split('/')[-1].split('?')[0]
                                old_blob = storage_bucket.blob(old_blob_name)
                                if old_blob.exists():
                                    old_blob.delete()
                            except Exception as e:
                                print(f"Could not delete old pic: {e}")
                        blob = storage_bucket.blob(f"profile_pics/{user_id}_{uuid.uuid4()}")
                        blob.upload_from_file(new_profile_pic, content_type=new_profile_pic.type)
                        new_profile_pic_url = blob.generate_signed_url(timedelta(days=365), method='GET')

                    updated_data = {
                        'email': user_email,
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
                        'profile_pic_url': new_profile_pic_url,
                        'skills': [s.strip() for s in skills.split(',')] if skills else [],
                        'bio': bio,
                        'last_updated': datetime.now()
                    }

                    doc_ref = firestore_db.collection("users").document(user_id)
                    doc_ref.set(updated_data, merge=True)
                    st.cache_data.clear()
                    st.success("✅ Profile updated!")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error saving profile: {e}")

    else:
        st.divider()

        st.subheader("🧑 Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**👤 First Name:** {user_data.get('first_name', '—')}")
            st.markdown(f"**🏢 Position:** {user_data.get('position', '—')}")
            st.markdown(f"**🏠 Street:** {user_data.get('address', {}).get('street', '—')}")
        with col2:
            st.markdown(f"**👤 Last Name:** {user_data.get('last_name', '—')}")
            st.markdown(f"**📞 Phone:** {user_data.get('phone', '—')}")
            st.markdown(f"**🏢 Company:** {user_data.get('company', '—')}")

        st.divider()

        st.subheader("📍 Address")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**🏙️ City:** {user_data.get('address', {}).get('city', '—')}")
        with col2:
            st.markdown(f"**🗺️ State:** {user_data.get('address', {}).get('state', '—')}")
        with col3:
            st.markdown(f"**🏷️ Zip Code:** {user_data.get('address', {}).get('zip_code', '—')}")

        st.markdown(f"**🌍 Country:** {user_data.get('address', {}).get('country', '—')}")

        st.divider()

        st.subheader("📝 Bio")
        st.markdown(f"{user_data.get('bio', '—')}")

        st.divider()

        if user_data.get('skills'):
            st.subheader("🛠️ Skills")
            st.markdown(f"`" + "` `".join(user_data['skills']) + "`")
        else:
            st.subheader("🛠️ Skills")
            st.markdown("—")

        st.divider()

        st.subheader("📧 Account Email")
        st.markdown(f"**{user_email}**")
