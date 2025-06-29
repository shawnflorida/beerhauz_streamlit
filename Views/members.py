import streamlit as st
from configs.firebase_config import get_firestore

def show_members():
    st.title("👥 Our Members")

    firestore_db = get_firestore()

    try:
        users_ref = firestore_db.collection("users")
        users = users_ref.stream()

        user_cards = []

        for user_doc in users:
            user_data = user_doc.to_dict()
            profile_pic = user_data.get("profile_pic_url") or "images/default.jpg"
            name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            role = user_data.get("role", "user").capitalize()
            email = user_data.get("email", "—")
            position = user_data.get("position", "—")
            company = user_data.get("company", "—")
            phone = user_data.get("phone", "—")
            address = user_data.get("address", {})
            city = address.get("city", "—")
            country = address.get("country", "—")
            skills = ", ".join(user_data.get("skills", []))
            bio = user_data.get("bio", "")

            card = {
                "name": name,
                "profile_pic": profile_pic,
                "role": role,
                "email": email,
                "position": position,
                "company": company,
                "phone": phone,
                "city": city,
                "country": country,
                "skills": skills,
                "bio": bio
            }

            user_cards.append(card)

        if not user_cards:
            st.info("No members found.")
            return

        # Single column display
        for card in user_cards:
            with st.container():
                cols = st.columns([1, 5])  # image | details
                with cols[0]:
                    try:
                        st.image(card["profile_pic"], width=100)
                    except Exception:
                        st.image("images/default.jpg", width=100)

                with cols[1]:
                    st.markdown(f"### {card['name']}")
                    st.markdown(f"**{card['role']}** — {card['position']} at {card['company']}")
                    st.markdown(f"📧 **Email:** {card['email']}")
                    st.markdown(f"📞 **Phone:** {card['phone']}")
                    st.markdown(f"🌍 **Location:** {card['city']}, {card['country']}")
                    if card["skills"]:
                        st.markdown(f"🛠️ **Skills:** {card['skills']}")
                    if card["bio"]:
                        st.markdown(f"📝 **Bio:** {card['bio'][:200]}{'...' if len(card['bio']) > 200 else ''}")
                st.markdown("---")

    except Exception as e:
        st.error(f"Failed to load members: {e}")
