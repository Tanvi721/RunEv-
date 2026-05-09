import streamlit as st
from backend.database import SessionLocal
from backend.services.booking_service import get_user_bookings

st.set_page_config(page_title="Dashboard - RunEV", page_icon="📊")

if not st.session_state.get('user'):
    st.warning("Please login to access this page.")
    st.stop()

st.title(f"{st.session_state.user['username']}'s Dashboard")

db = SessionLocal()
bookings = get_user_bookings(db, st.session_state.user['id'])

st.subheader("Your Bookings")

if not bookings:
    st.info("You haven't made any bookings yet.")
    if st.button("Find a station"):
        st.switch_page("pages/03_Search.py")
else:
    for booking in bookings:
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Station:** {booking.station.name}")
                st.write(f"**Slot:** {booking.slot.slot_number}")
            with col2:
                st.write(f"**Time:** {booking.booking_time.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Duration:** {booking.duration_hours} hours")
            with col3:
                st.write(f"**Price:** ${booking.total_price}")
                status_color = "green" if booking.status == "completed" else "orange"
                st.markdown(f"**Status:** <span style='color:{status_color}'>{booking.status.upper()}</span>", unsafe_allow_html=True)

db.close()
