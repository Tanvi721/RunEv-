import streamlit as st
import folium
from streamlit_folium import folium_static
from streamlit_geolocation import streamlit_geolocation
import time
import math

st.set_page_config(page_title="Live Tracking - RunEV", page_icon="🗺️")

st.title("Live Charging Van Tracking 🗺️")

if not st.session_state.get('user'):
    st.warning("Please login to properly use live tracking.")
    st.stop()

st.markdown("Please allow location access to continue tracking.")

# Get User real-time location
geolocation = streamlit_geolocation()

if geolocation and geolocation.get('latitude') is not None and geolocation.get('longitude') is not None:
    user_lat = geolocation['latitude']
    user_lon = geolocation['longitude']
    
    st.success(f"Location Found! Lat: {user_lat:.4f}, Lon: {user_lon:.4f}")
    
    # Initialize the charging van's location in session state
    # We simulate it starting a fixed distance away (e.g., +0.005 lat/lon approx 500m)
    if 'van_lat' not in st.session_state:
        st.session_state.van_lat = user_lat + 0.005
        st.session_state.van_lon = user_lon + 0.005
        
    van_lat = st.session_state.van_lat
    van_lon = st.session_state.van_lon
    
    # Calculate distance to see if it arrived
    def calculate_distance(lat1, lon1, lat2, lon2):
        # basic euclidean approximation for quick check
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
    
    distance = calculate_distance(user_lat, user_lon, van_lat, van_lon)
    
    # --- Map Construction ---
    # We center the map between the user and the van
    center_lat = (user_lat + van_lat) / 2
    center_lon = (user_lon + van_lon) / 2
    
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=15,
        # Using a Google Maps replica styling link for aesthetics
        tiles='http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}',
        attr='Google Maps'
    )
    
    # User Marker
    folium.Marker(
        [user_lat, user_lon], 
        popup="You are here", 
        icon=folium.Icon(color="green", icon="user")
    ).add_to(m)
    
    # Van Marker
    folium.Marker(
        [van_lat, van_lon], 
        popup="Charging Van", 
        icon=folium.Icon(color="blue", icon="truck", prefix='fa')
    ).add_to(m)
    
    # Render Map
    folium_static(m, width=700, height=500)
    
    # --- Van Movement Simulation ---
    if distance > 0.0003: # Not arrived yet (approx 30m)
        st.info("The Charging Van is approaching your location...")
        # Move the van 10% closer to the user on every re-run
        st.session_state.van_lat = van_lat + (user_lat - van_lat) * 0.1
        st.session_state.van_lon = van_lon + (user_lon - van_lon) * 0.1
        
        # We enforce a small sleep and rerun to animate the location updates!
        time.sleep(2)
        st.rerun()
    else:
        st.success("🎉 The Charging Van has arrived at your location!")
        
else:
    st.info("Waiting for location permissions... Click the 'Get Location' button above if it didn't trigger automatically.")
