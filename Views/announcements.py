import streamlit as st
from datetime import datetime
from configs.firebase_config import get_firestore
import streamlit as st_cache_resource
@st_cache_resource.cache_resource
def get_cached_firestore():
    return get_firestore()

def show_announcements():
    firestore_db = get_cached_firestore()
    
    st.title("📢 Announcements")
    st.markdown("---")
    
    # Post creation form for authenticated users
    if st.session_state.get('is_authenticated', False):
        _render_announcement_form(firestore_db)
    
    # Announcement feed
    st.header("Latest Announcements")
    _render_announcement_feed(firestore_db)

def _render_announcement_form(firestore_db):
    """Render the new announcement creation form"""
    with st.expander("✍️ Create New Announcement", expanded=False):
        with st.form("announcement_form"):
            title = st.text_input("Title", max_chars=100)
            content = st.text_area("Content", height=150)
            submit_button = st.form_submit_button("Post Announcement")

            # Autofill author name if possible
            user = st.session_state.get('user')
            author_name = ""
            if user:
                user_id = getattr(user, "uid", None)
                if user_id:
                    try:
                        user_doc = firestore_db.collection("users").document(user_id).get()
                        if user_doc.exists:
                            user_data = user_doc.to_dict()
                            first_name = user_data.get('first_name', '')
                            last_name = user_data.get('last_name', '')
                            author_name = f"{first_name} {last_name}".strip()
                        if not author_name:
                            first_name = getattr(user, 'first_name', '')
                            last_name = getattr(user, 'last_name', '')
                            author_name = f"{first_name} {last_name}".strip()
                        if not author_name or author_name == " ":
                            author_name = getattr(user, "email", "")
                    except Exception:
                        author_name = getattr(user, "email", "")
            
            if submit_button:
                if not title or not content:
                    st.warning("Please fill in both title and content")
                    return
                
                try:
                    announcement_data = {
                        "title": title,
                        "content": content,
                        "author": author_name,
                        "timestamp": datetime.now(),
                        "comments": []
                    }
                    firestore_db.collection("announcements").add(announcement_data)
                    st.success("Announcement posted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error posting announcement: {e}")

def _render_announcement_feed(firestore_db):
    """Render the list of announcements with comments"""
    try:
        announcements = firestore_db.collection("announcements")\
                                .order_by("timestamp", direction="DESCENDING")\
                                .limit(10)\
                                .stream()
        
        announcements_list = []
        for announcement in announcements:
            announcement_data = announcement.to_dict()
            announcement_data["id"] = announcement.id
            announcements_list.append(announcement_data)
            
        if not announcements_list:
            st.info("No announcements yet. Be the first to post!")
            return
            
        for post in announcements_list:
            _render_single_announcement(firestore_db, post)
            st.markdown("---")
            
    except Exception as e:
        st.error(f"Error loading announcements: {e}")

def _render_single_announcement(firestore_db, post):
    """Render a single announcement with its comments"""
    st.markdown(f"### {post.get('title', 'No title')}")
    st.caption(
        f"Posted by {post.get('author', 'Anonymous')} • "
        f"{post.get('timestamp').strftime('%b %d, %Y %H:%M') if post.get('timestamp') else ''}"
    )
    st.markdown(f"> {post.get('content', '')}")
    
    # Comments section
    with st.expander(f"💬 Comments ({len(post.get('comments', []))})"):
        if st.session_state.get('is_authenticated', False):
            _render_comment_form(firestore_db, post)
        
        _render_comments_list(post.get('comments', []))

def _render_comment_form(firestore_db, post):
    """Render the form to add a new comment"""
    with st.form(key=f"comment_form_{post['id']}"):
        comment_text = st.text_input("Add a comment", key=f"comment_input_{post['id']}")
        if st.form_submit_button("Post Comment") and comment_text:
            try:
                user = st.session_state.user
                user_id = getattr(user, "uid", None)
                
                # Get user profile data
                profile_pic_url, author_name = _get_user_profile_data(firestore_db, user_id, user)
                
                # Create new comment
                new_comment = {
                    "text": comment_text,
                    "author": author_name,
                    "timestamp": datetime.now(),
                    "author_pic": profile_pic_url
                }
                
                # Update comments in Firestore
                doc_ref = firestore_db.collection("announcements").document(post['id'])
                current_comments = doc_ref.get().to_dict().get('comments', [])
                current_comments.append(new_comment)
                doc_ref.update({"comments": current_comments})
                st.rerun()
                
            except Exception as e:
                st.error(f"Error adding comment: {e}")

def _get_user_profile_data(firestore_db, user_id, user):
    """Get user profile picture and display name"""
    # Default values
    profile_pic_url = 'https://ui-avatars.com/api/?name=User&background=random'
    author_name = "Anonymous"
    
    if not user_id:
        return profile_pic_url, author_name
    
    try:
        # Try to get from Firestore user document
        user_doc = firestore_db.collection("users").document(user_id).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            profile_pic_url = user_data.get('profile_pic_url', profile_pic_url)
            
            # Get name from Firestore
            first_name = user_data.get('first_name', '')
            last_name = user_data.get('last_name', '')
            author_name = f"{first_name} {last_name}".strip()
            
            # Fallback to auth user if no name in Firestore
            if not author_name:
                first_name = getattr(user, 'first_name', '')
                last_name = getattr(user, 'last_name', '')
                author_name = f"{first_name} {last_name}".strip()
    except Exception:
        pass
    
    # Final fallback to email if no name found
    if not author_name or author_name == " ":
        author_name = getattr(user, "email", "Anonymous")
    
    return profile_pic_url, author_name

def _render_comments_list(comments):
    """Render the list of comments for an announcement"""
    for comment in comments:
        col1, col2 = st.columns([1, 16])
        with col1:
            author_pic = comment.get('author_pic', f"https://ui-avatars.com/api/?name={comment.get('author', '')}")
            st.image(author_pic, width=50)
        with col2:
            st.text(f"{comment.get('author', 'Anonymous')}: {comment.get('text', '')}")
            timestamp = comment.get('timestamp')
            if hasattr(timestamp, 'strftime'):
                st.caption(timestamp.strftime('%b %d, %Y %H:%M'))
            elif isinstance(timestamp, str):
                st.caption(timestamp)
