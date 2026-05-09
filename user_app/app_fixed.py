import streamlit as st
import sys
import os
from dotenv import load_dotenv
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from backend.database import SessionLocal
from backend.models import Provider
from backend.services.auth_service import authenticate_user, create_access_token, register_user

st.set_page_config(page_title="RunEV - User App", page_icon="⚡", initial_sidebar_state="collapsed", layout="wide")

st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
        header { visibility: hidden; }
        .block-container { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user = None

def render_login():
    st.title("RunEV ⚡")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.markdown("Welcome back! Request a charging van directly to your location.")
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
                    st.rerun()
                else:
                    st.error("Invalid email or password")
                db.close()

    with tab2:
        st.markdown("New here? Create an account.")
        with st.form("signup_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            signup_submit = st.form_submit_button("Sign Up")
            
            if signup_submit:
                if not new_username or not new_email or not new_password:
                    st.error("Please fill all fields")
                else:
                    db = SessionLocal()
                    user = register_user(db, new_username, new_email, new_password, role="user")
                    if user:
                        st.success("Account created successfully! You can now login.")
                    else:
                        st.error("Email already registered.")
                    db.close()

def load_available_providers():
    db = SessionLocal()
    try:
        providers = db.query(Provider).filter(Provider.is_available == True).all()
        return [
            {
                "id": p.id,
                "vehicle_number": p.vehicle_number,
                "current_lat": p.current_lat,
                "current_lng": p.current_lng,
                "charging_speed": p.charging_speed or "Standard",
                "connector_types": p.connector_types or "Universal",
                "price_per_kwh": p.price_per_kwh or 20.0,
                "driver_name": p.driver_name,
                "address": p.address,
            }
            for p in providers
        ]
    finally:
        db.close()

def render_map_dashboard():
    st.title(f"Hello, {st.session_state.user['username']} 👋")
    
    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()
            
    st.markdown("### 🚚 Request a Charging Van")

    provider_list = load_available_providers()
    
    if not provider_list:
        st.warning("❌ No charging vans available right now. Please try again later.")
    else:
        # Display map with Folium
        import folium
        from streamlit_folium import st_folium
        
        default_lat, default_lng = 18.5204, 73.8567
        
        m = folium.Map(
            location=[default_lat, default_lng],
            zoom_start=14,
            tiles="OpenStreetMap"
        )
        
        # Add user location marker
        folium.Marker(
            location=[default_lat, default_lng],
            popup="Your Location",
            icon=folium.Icon(color="blue", icon="user", prefix="fa"),
            tooltip="You are here"
        ).add_to(m)
        
        # Add provider markers
        for provider in provider_list:
            if provider.get('current_lat') and provider.get('current_lng'):
                popup_text = f"""
                <b>{provider['vehicle_number']}</b><br>
                Driver: {provider.get('driver_name', 'Driver')}<br>
                Speed: {provider['charging_speed']}<br>
                Connector: {provider['connector_types']}<br>
                Price: ₹{provider['price_per_kwh']}/kWh
                """
                folium.Marker(
                    location=[provider['current_lat'], provider['current_lng']],
                    popup=folium.Popup(popup_text, max_width=250),
                    icon=folium.Icon(color="green", icon="bolt", prefix="fa"),
                    tooltip=provider['vehicle_number']
                ).add_to(m)
        
        col_map, col_info = st.columns([2, 1])
        
        with col_map:
            st_folium(m, width=700, height=500)
        
        with col_info:
            st.markdown("#### Available Vans")
            for provider in provider_list:
                with st.container(border=True):
                    st.markdown(f"**🚚 {provider['vehicle_number']}**")
                    if provider.get('driver_name'):
                        st.caption(f"Driver: {provider['driver_name']}")
                    st.caption(f"⚡ {provider['charging_speed']}")
                    st.caption(f"📌 {provider['connector_types']}")
                    st.caption(f"💰 ₹{provider['price_per_kwh']}/kWh")
                    
                    if st.button("Request Van ⚡", key=f"request_{provider['id']}", use_container_width=True):
                        try:
                            response = requests.post(
                                "http://localhost:8000/api/request-charge",
                                json={
                                    "user_id": st.session_state.user['id'],
                                    "pickup_lat": default_lat,
                                    "pickup_lng": default_lng
                                },
                                timeout=5
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                st.success(f"✅ Request sent!")
                                st.info(f"🚗 {data['provider']['vehicle_number']} is {data['estimated_distance_km']} km away")
                                st.balloons()
                            else:
                                error_msg = response.json().get('detail', 'Unable to send request')
                                st.error(f"❌ {error_msg}")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Connection error: {str(e)}")

if st.session_state.user is None:
    render_login()
else:
    render_map_dashboard()
