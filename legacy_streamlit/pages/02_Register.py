import streamlit as st
from backend.database import SessionLocal
from backend.models import User
from backend.services.auth_service import get_password_hash

st.set_page_config(page_title="Register - RunEV", page_icon="📝")

st.title("Create an Account")

if st.session_state.get('user'):
    st.info("You are already logged in.")
else:
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        phone = st.text_input("Phone Number")
        
        submit = st.form_submit_button("Register")
        
        if submit:
            if not username or not email or not password:
                st.error("Please fill all required fields")
            else:
                db = SessionLocal()
                existing_user = db.query(User).filter(User.email == email).first()
                if existing_user:
                    st.error("Email already registered")
                else:
                    new_user = User(
                        username=username,
                        email=email,
                        hashed_password=get_password_hash(password),
                        phone=phone
                    )
                    db.add(new_user)
                    db.commit()
                    st.success("Registration successful! You can now access the login page.")
                db.close()
