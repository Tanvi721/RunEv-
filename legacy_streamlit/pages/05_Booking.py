import streamlit as st
from backend.database import SessionLocal
from backend.services.station_service import get_station_by_id, get_slots_for_station

st.set_page_config(page_title="Book Slot - RunEV", page_icon="📅")

if not st.session_state.get('user'):
    st.warning("Please login to access this page.")
    st.stop()

if 'selected_station_id' not in st.session_state:
    st.warning("No station selected. Please go to Search.")
    if st.button("Go to Search"):
        st.switch_page("pages/03_Search.py")
    st.stop()

db = SessionLocal()
station_id = st.session_state.selected_station_id
station = get_station_by_id(db, station_id)
slots = get_slots_for_station(db, station_id)

st.title(f"Book Slot at {station.name}")
st.write(f"📍 {station.address}")
st.write(f"💰 ${station.price_per_hour}/hr")

st.subheader("Select an available slot:")
available_slots = [s for s in slots if s.is_available]

if not available_slots:
    st.error("No slots currently available at this station.")
else:
    with st.form("booking_form"):
        selected_slot_format = st.selectbox("Choose a slot:", [f"Slot {s.slot_number}" for s in available_slots])
        duration = st.number_input("Duration (hours)", min_value=1, max_value=24, value=1)
        
        total_price = duration * station.price_per_hour
        st.write(f"**Total Price:** ${total_price}")
        
        submit = st.form_submit_button("Proceed to Payment")
        if submit:
            selected_slot_obj = next(s for s in available_slots if f"Slot {s.slot_number}" == selected_slot_format)
            
            st.session_state.booking_details = {
                "station_id": station.id,
                "slot_id": selected_slot_obj.id,
                "duration_hours": duration,
                "total_price": total_price
            }
            st.switch_page("pages/06_Payment.py")

db.close()
