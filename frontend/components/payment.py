from __future__ import annotations

import html

import streamlit as st

from frontend.components.ui import money, safe_text, status_badge


def render_driver_card(provider: dict, eta: int | str = "Live") -> None:
    driver = provider.get("driver_name") or "Assigned driver"
    vehicle = provider.get("vehicle_number") or "Charging van"
    speed = provider.get("charging_speed") or "Standard"
    connector = provider.get("connector_types") or "Universal"
    phone = provider.get("phone") or "Not available"
    average_rating = provider.get("average_rating")
    rating_count = int(provider.get("rating_count") or 0)
    rating_label = (
        "No ratings yet"
        if average_rating is None or rating_count == 0
        else f"{float(average_rating):.1f}/5 from {rating_count} rating{'s' if rating_count != 1 else ''}"
    )
    initials = "".join(part[:1] for part in driver.split()[:2]).upper() or "EV"
    st.markdown(
        f"""
        <div class="runev-card runev-driver-card">
            <div class="runev-driver-top">
                <div class="runev-avatar">{safe_text(initials)}</div>
                <div>
                    <div class="runev-driver-name">{safe_text(driver)}</div>
                    <div class="runev-driver-meta">{safe_text(rating_label)} / {safe_text(vehicle)}</div>
                </div>
                {status_badge("online", "Assigned")}
            </div>
            <div class="runev-driver-grid">
                <div><span>ETA</span><strong>{safe_text(eta)} min</strong></div>
                <div><span>Speed</span><strong>{safe_text(speed)}</strong></div>
                <div><span>Connector</span><strong>{safe_text(connector)}</strong></div>
                <div><span>Mobile</span><strong>{safe_text(phone)}</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_charging_summary(request_status: dict, provider: dict, amount: float) -> None:
    units = float(request_status.get("charged_units_kwh") or 0)
    rate = float(provider.get("price_per_kwh") or 20)
    st.markdown(
        f"""
        <div class="runev-card runev-summary-card">
            <div class="runev-section-kicker">Charging summary</div>
            <h3>Invoice #{request_status.get("id")}</h3>
            <div class="runev-summary-grid">
                <div><span>Energy consumed</span><strong>{units:.2f} kWh</strong></div>
                <div><span>Rate</span><strong>Rs {rate:.2f}/kWh</strong></div>
                <div><span>Total</span><strong>{money(amount)}</strong></div>
            </div>
            <div class="runev-summary-line">
                <span>{safe_text(provider.get("vehicle_number") or "Charging van")}</span>
                <strong>{units:.2f} kWh charged successfully</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sample_upi_qr(label: str = "runev@upi") -> str:
    dark_cells = {
        1, 2, 3, 4, 5, 7, 8, 9, 10, 11,
        13, 17, 19, 21, 23, 24, 25, 27, 28, 29, 30,
        31, 35, 38, 40, 41, 43, 45, 48, 50, 52, 55, 57, 60,
        62, 64, 66, 69, 71, 74, 76, 79, 81, 82, 83, 84, 85,
        88, 91, 93, 95, 97, 99, 100,
    }
    cells = "".join(f'<i class="{"on" if idx in dark_cells else ""}"></i>' for idx in range(1, 101))
    return f"""
    <div class="runev-upi-qr">
        <div class="runev-qr-grid">{cells}</div>
        <div>
            <span>Scan to pay with any UPI app</span>
            <strong>{html.escape(label)}</strong>
        </div>
    </div>
    """


def render_payment_method_cards(request_id: int) -> str:
    current = st.session_state.setdefault(f"gateway_method_{request_id}", "UPI")
    st.markdown('<div class="runev-payment-card-grid">', unsafe_allow_html=True)
    col_upi, col_cash = st.columns(2)
    methods = [
        (col_upi, "UPI", "UPI apps", "Recommended", "Instant bank transfer"),
        (col_cash, "Cash", "Cash", "Offline fallback", "Pay directly to driver"),
    ]
    for col, value, title, tag, desc in methods:
        selected = current == value
        with col:
            st.markdown(
                f"""
                <div class="runev-payment-option {'selected' if selected else ''}">
                    <div>
                        <span>{safe_text(tag)}</span>
                        <strong>{safe_text(title)}</strong>
                        <p>{safe_text(desc)}</p>
                    </div>
                    <b>{'Selected' if selected else 'Choose'}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Use {title}", key=f"gateway_method_button_{request_id}_{value}", use_container_width=True):
                st.session_state[f"gateway_method_{request_id}"] = value
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    return st.session_state.get(f"gateway_method_{request_id}", "UPI")


def render_upi_app_selector(request_id: int) -> str | None:
    selected_key = f"gateway_upi_app_{request_id}"
    selected = st.session_state.get(selected_key)
    apps = [
        ("Google Pay", "G", "Fast UPI intent", "gpay"),
        ("PhonePe", "Pe", "Popular UPI app", "phonepe"),
        ("Paytm", "P", "Wallet and UPI", "paytm"),
        ("BHIM", "B", "NPCI UPI", "bhim"),
        ("Other UPI Apps", "UPI", "Any installed app", "other"),
    ]

    st.markdown(
        """
        <div class="runev-upi-shell">
            <div class="runev-upi-heading">
                <div>
                    <span>Secure UPI Payment via Razorpay</span>
                    <strong>Choose your preferred UPI app</strong>
                </div>
                <b>Protected</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rows = [apps[:2], apps[2:4], apps[4:]]
    for row in rows:
        columns = st.columns(2) if len(row) == 2 else st.columns(1)
        for idx, (name, mark, caption, slug) in enumerate(row):
            with columns[idx]:
                is_selected = selected == name
                st.markdown(
                    f"""
                    <div class="runev-upi-app-card {'selected' if is_selected else ''}">
                        <div class="runev-upi-app-top">
                            <div class="runev-upi-logo {safe_text(slug)}">{safe_text(mark)}</div>
                            <div class="runev-upi-check">{'&#10003;' if is_selected else ''}</div>
                        </div>
                        <strong>{safe_text(name)}</strong>
                        <span>{safe_text(caption)}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    f"{'Selected' if is_selected else 'Choose'} {name}",
                    key=f"gateway_upi_app_{request_id}_{slug}",
                    use_container_width=True,
                ):
                    st.session_state[selected_key] = name
                    st.rerun()
    if selected:
        st.markdown(
            f"""
            <div class="runev-upi-selected">
                <div class="runev-upi-selected-dot"></div>
                <span>Selected app</span>
                <strong>{safe_text(selected)}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="runev-upi-selected muted">
                <div class="runev-upi-selected-dot"></div>
                <span>Select an app to enable Pay Securely</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    return selected


def render_secure_payment_note() -> None:
    st.markdown(
        """
        <div class="runev-secure-note">
            <div class="runev-lock">SAFE</div>
            <div>
                <strong>Secure UPI Payment via Razorpay</strong>
                <span>Encrypted checkout. RunEV never stores your UPI PIN, bank details, or payment credentials.</span>
                <div class="runev-trust-badges">
                    <b>Razorpay Secure</b>
                    <b>UPI Enabled</b>
                    <b>PCI DSS</b>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_success_screen(amount: float, invoice_id: int | str, order_id: str | None = None) -> None:
    st.markdown(
        f"""
        <div class="runev-success-screen">
            <div class="runev-success-check">&#10003;</div>
            <div class="runev-eyebrow">Payment successful</div>
            <h1>{money(amount)} paid</h1>
            <p>Invoice #{safe_text(invoice_id)} is closed. Thank you for charging with RunEV.</p>
            <div class="runev-success-meta">
                <span>Invoice ID</span><strong>#{safe_text(invoice_id)}</strong>
                <span>Order ID</span><strong>{safe_text(order_id or "Confirmed")}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
