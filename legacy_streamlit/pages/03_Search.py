import streamlit as st
from backend.database import SessionLocal
from backend.services.recommendation_service import get_recommended_stations
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Search Stations - RunEV", page_icon="🔍", layout="wide")

if not st.session_state.get('user'):
    st.warning("Please login to access this page.")
    st.stop()

st.title("Find EV Charging Stations")

# Mock user location (e.g., somewhere in San Francisco)
user_lat = 37.7749
user_lng = -122.4194

st.sidebar.header("Filters")
max_distance = st.sidebar.slider("Max Distance (km)", 1.0, 50.0, 20.0)

db = SessionLocal()
recommendations = get_recommended_stations(db, user_lat, user_lng, max_distance)

col1, col2 = st.columns([2, 1])

with col1:
    m = folium.Map(location=[user_lat, user_lng], zoom_start=12)
    # Add user marker
    folium.Marker(
        [user_lat, user_lng], tooltip="You are here", icon=folium.Icon(color="red", icon="user")
    ).add_to(m)
    
    for rec in recommendations:
        station = rec["station"]
        folium.Marker(
            [station.location_lat, station.location_lng],
            tooltip=f"{station.name} (${station.price_per_hour}/hr)",
            popup=f"<b>{station.name}</b><br>{station.address}<br>Distance: {rec['distance']} km",
            icon=folium.Icon(color="green", icon="bolt", prefix='fa')
        ).add_to(m)
        
    st_data = st_folium(m, width=700, height=500)

with col2:
    st.subheader("Recommended for you")
    if not recommendations:
        st.info("No stations found within the selected distance.")
    else:
        for rec in recommendations:
            station = rec["station"]
            with st.container(border=True):
                st.markdown(f"**{station.name}**")
                st.write(f"📍 {rec['distance']} km away")
                st.write(f"💰 ${station.price_per_hour}/hr")
                if st.button("Book Now", key=f"book_{station.id}"):
                    st.session_state.selected_station_id = station.id
                    st.switch_page("pages/05_Booking.py")

db.close()
