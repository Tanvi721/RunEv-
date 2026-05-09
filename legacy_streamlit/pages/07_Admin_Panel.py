import streamlit as st
import pandas as pd
import plotly.express as px
from backend.database import SessionLocal
from backend.models import Booking, Station

st.set_page_config(page_title="Admin Dashboard - RunEV", page_icon="🛠️", layout="wide")

if not st.session_state.get('user') or st.session_state.user.get('role') != 'admin':
    st.error("Unauthorized access. Admin privileges required.")
    st.stop()

st.title("Admin Dashboard")

db = SessionLocal()

# Analytics Metrics
bookings = db.query(Booking).all()
stations = db.query(Station).all()

total_revenue = sum([b.total_price for b in bookings if b.status == "completed"])
total_bookings = len(bookings)
active_stations = len([s for s in stations if s.is_active])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Revenue", f"${total_revenue}")
with col2:
    st.metric("Total Bookings", total_bookings)
with col3:
    st.metric("Active Stations", active_stations)

st.markdown("---")

# Charts
if bookings:
    st.subheader("Booking Trends")
    # Prepare data for Plotly
    df = pd.DataFrame([{
        "date": b.booking_time.date(),
        "revenue": b.total_price,
        "station": b.station.name
    } for b in bookings])
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Revenue over time
        daily_revenue = df.groupby("date")["revenue"].sum().reset_index()
        fig1 = px.bar(daily_revenue, x="date", y="revenue", title="Daily Revenue", labels={"date": "Date", "revenue": "Revenue ($)"})
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_chart2:
        # Bookings by Station
        station_bookings = df["station"].value_counts().reset_index()
        station_bookings.columns = ["station", "count"]
        fig2 = px.pie(station_bookings, values="count", names="station", title="Bookings per Station")
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Not enough data to display analytics yet.")

st.markdown("---")
st.subheader("Manage Stations")

station_data = []
for s in stations:
    station_data.append({
        "ID": s.id,
        "Name": s.name,
        "Address": s.address,
        "Price/Hr": s.price_per_hour,
        "Slots": s.total_slots,
        "Active": s.is_active
    })

if station_data:
    st.dataframe(pd.DataFrame(station_data), use_container_width=True)

with st.expander("Add New Station (Simulation)"):
    st.write("Adding new stations programmatically is part of Phase 2.")
    with st.form("add_station_form"):
        st.text_input("Station Name")
        st.text_input("Address")
        st.number_input("Slots", min_value=1)
        st.form_submit_button("Add Station")

db.close()
