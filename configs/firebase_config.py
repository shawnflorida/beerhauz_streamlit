import json
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import streamlit as st

# Initialize Firebase services
def initialize_firebase():
    key_dict = json.loads(st.secrets["KEY"])
    storage_bucket = st.secrets["BUCKET"]  
    
    # Initialize Firebase app if not already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(key_dict)
        firebase_app = firebase_admin.initialize_app(
            cred,
            {
                'storageBucket': storage_bucket
            }
        )
    
    # Initialize individual services
    firestore_db = firestore.client()
    auth_client = auth
    storage_client = storage.bucket(storage_bucket)  # Explicitly specify the bucket name
    
    return firestore_db, auth_client, storage_client

try:
    firestore_db, auth_client, storage_client = initialize_firebase()
except ValueError as e:
    st.error(f"Firebase initialization error: {e}")
    raise

def get_firestore():
    """Return Firestore database instance"""
    return firestore_db

def get_auth():
    """Return Firebase Auth instance"""
    return auth_client

def get_storage():
    """Return Cloud Storage bucket instance"""
    return storage_client
