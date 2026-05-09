import streamlit as st
from backend.database import SessionLocal
from backend.services.auth_service import authenticate_user, create_access_token

st.set_page_config(page_title="Login - RunEV", page_icon="🔐")

st.title("Login to RunEV")

if st.session_state.get('user'):
    st.success("You are already logged in!")
    if st.button("Go to Home"):
        st.switch_page("app.py")
else:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            db = SessionLocal()
            user = authenticate_user(db, email, password)
            if user:
                token = create_access_token(data={"sub": user.email})
                st.session_state.user = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                }
                st.session_state.jwt_token = token
                st.success("Login successful!")
                st.switch_page("app.py")
            else:
                st.error("Invalid email or password")
            db.close()
            
    st.info("Test Credentials:\n- **Admin**: admin@runev.com / admin123\n- **User**: john@example.com / password123")
