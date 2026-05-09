import streamlit as st
import time
from backend.database import SessionLocal
from backend.services.booking_service import create_booking
from backend.services.payment_service import process_payment

st.set_page_config(page_title="Payment - RunEV", page_icon="💳")

if not st.session_state.get('user'):
    st.warning("Please login to access this page.")
    st.stop()

if 'booking_details' not in st.session_state:
    st.warning("No pending booking found. Please select a slot first.")
    if st.button("Go to Search"):
        st.switch_page("pages/03_Search.py")
    st.stop()

details = st.session_state.booking_details
total_price = details["total_price"]

st.title("Secure Payment")
st.write("Complete your booking by securely paying with Razorpay (Mock).")

with st.container(border=True):
    st.subheader("Order Summary")
    st.write(f"**Duration:** {details['duration_hours']} hours")
    st.write(f"**Amount to Pay:** ${total_price}")

st.markdown("---")
st.subheader("Payment Details")

with st.form("payment_form"):
    card_name = st.text_input("Name on Card", value=st.session_state.user['username'])
    card_number = st.text_input("Card Number (Dummy)", placeholder="XXXX XXXX XXXX XXXX", max_chars=19)
    col1, col2 = st.columns(2)
    with col1:
        expiry = st.text_input("Expiry Date", placeholder="MM/YY", max_chars=5)
    with col2:
        cvv = st.text_input("CVV", type="password", max_chars=3)
        
    submit = st.form_submit_button(f"Pay ${total_price}")
    
    if submit:
        if not card_number or not expiry or not cvv:
            st.error("Please fill in all dummy card details.")
        else:
            with st.spinner("Processing payment via Razorpay..."):
                time.sleep(2) # Simulate network delay
                
                db = SessionLocal()
                try:
                    # 1. Create booking in DB
                    booking = create_booking(
                        db=db,
                        user_id=st.session_state.user['id'],
                        station_id=details['station_id'],
                        slot_id=details['slot_id'],
                        duration_hours=details['duration_hours']
                    )
                    
                    # 2. Process payment
                    payment = process_payment(
                        db=db,
                        booking_id=booking.id,
                        user_id=st.session_state.user['id'],
                        amount=total_price
                    )
                    
                    st.success(f"Payment successful! Payment ID: {payment.razorpay_payment_id}")
                    
                    # Clear session parameters
                    if 'booking_details' in st.session_state:
                        del st.session_state.booking_details
                    if 'selected_station_id' in st.session_state:
                        del st.session_state.selected_station_id
                    
                    st.balloons()
                    time.sleep(1.5)
                    st.switch_page("pages/04_Dashboard.py")
                    
                except Exception as e:
                    st.error(f"Error during payment: {str(e)}")
                    db.rollback()
                finally:
                    db.close()
