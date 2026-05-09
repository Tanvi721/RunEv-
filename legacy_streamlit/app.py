import streamlit as st

st.set_page_config(page_title="RunEV - EV Charging Platform", page_icon="⚡", layout="wide")

# UI Styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
        color: #212529;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None
if 'jwt_token' not in st.session_state:
    st.session_state.jwt_token = None

def main():
    st.title("⚡ RunEV - EV Charging Platform")
    
    if st.session_state.user is None:
        st.write("### Welcome to RunEV! Please login or register to find and book charging stations.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("Log in to your account from the **Login** page on the sidebar to start booking.")
            try:
                st.page_link("pages/01_Login.py", label="Go to Login", icon="🔑")
            except:
                pass
        with col2:
            st.success("New here? Create an account on the **Register** page.")
            try:
                st.page_link("pages/02_Register.py", label="Go to Register", icon="📝")
            except:
                pass
    else:
        st.write(f"### Hello, {st.session_state.user['username']}! 👋")
        
        st.markdown("#### Quick Links:")
        try:
            st.page_link("pages/03_Search.py", label="Search Stations", icon="🌍")
            st.page_link("pages/04_Dashboard.py", label="Dashboard", icon="📊")
        except:
            pass
        
        if st.session_state.user.get('role') == 'admin':
            st.markdown("#### Admin Links:")
            try:
                st.page_link("pages/07_Admin_Panel.py", label="Admin Panel", icon="🛠️")
            except:
                pass
            
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.jwt_token = None
            st.rerun()

if __name__ == "__main__":
    main()
