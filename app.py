import os
import re
import sqlite3
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "heroes.db"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

st.set_page_config(
    page_title="Super Power HQ",
    page_icon="🦸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main { padding: 2rem 1rem; }
    .stTitle { color: #667eea; }
    h1, h2, h3 { color: #667eea; }
    .hero-table { width: 100%; }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .admin-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def validate_signup(data):
    errors = {}

    hero_name = data.get("hero_name", "").strip()
    if not hero_name:
        errors["hero_name"] = "Hero name is required."
    elif len(hero_name) > 200:
        errors["hero_name"] = "Hero name is too long."

    powers = data.get("powers", "").strip()
    if not powers:
        errors["powers"] = "Powers are required."
    elif len(powers) > 500:
        errors["powers"] = "Powers description is too long."

    age = data.get("age", "").strip()
    if not age:
        errors["age"] = "Age is required."
    elif not age.isdigit() or not (0 < int(age) <= 150):
        errors["age"] = "Age must be a number between 1 and 150."

    location = data.get("location", "").strip()
    if not location:
        errors["location"] = "Location is required."
    elif len(location) > 200:
        errors["location"] = "Location is too long."

    email = data.get("email", "").strip()
    if not email:
        errors["email"] = "Email is required."
    elif not EMAIL_RE.match(email):
        errors["email"] = "Please enter a valid email address."
    elif len(email) > 200:
        errors["email"] = "Email is too long."

    return errors, {
        "hero_name": hero_name,
        "powers": powers,
        "age": age,
        "location": location,
        "email": email,
    }


def check_admin_auth(password):
    """Simple password check for admin panel."""
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not admin_password:
        return False
    return password == admin_password


# Sidebar for navigation
page = st.sidebar.radio(
    "🦸 Super Power HQ",
    ["Sign Up", "Admin Review"],
    label_visibility="collapsed",
)

if page == "Sign Up":
    st.title("Register Your Powers")
    st.write("Tell us about yourself and join our network of extraordinary individuals.")

    if st.session_state.get("show_success"):
        st.markdown(
            '<div class="success-box"><strong>Welcome, hero!</strong> Your application has been received. The HQ team will review it shortly.</div>',
            unsafe_allow_html=True,
        )
        if st.button("Submit another application"):
            st.session_state.show_success = False
            st.rerun()

    with st.form("signup_form"):
        col1, col2 = st.columns(2)

        with col1:
            hero_name = st.text_input(
                "Hero Name *", max_chars=200, key="hero_name_input"
            )
            age = st.text_input("Age *", max_chars=3, key="age_input")

        with col2:
            location = st.text_input(
                "Location *", max_chars=200, key="location_input"
            )
            email = st.text_input("Email *", max_chars=200, key="email_input")

        powers = st.text_area(
            "Powers *", max_chars=500, height=100, key="powers_input"
        )

        submitted = st.form_submit_button("Submit Application", use_container_width=True)

        if submitted:
            form_data = {
                "hero_name": hero_name,
                "powers": powers,
                "age": age,
                "location": location,
                "email": email,
            }

            errors, cleaned_data = validate_signup(form_data)

            if errors:
                st.error("⚠️ Please fix the following errors:")
                for field, error in errors.items():
                    st.write(f"- **{field}**: {error}")
            else:
                db = get_db()
                db.execute(
                    """
                    INSERT INTO submissions (hero_name, powers, age, location, email)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        cleaned_data["hero_name"],
                        cleaned_data["powers"],
                        cleaned_data["age"],
                        cleaned_data["location"],
                        cleaned_data["email"],
                    ),
                )
                db.commit()
                db.close()

                st.session_state.show_success = True
                st.rerun()

else:  # Admin Review
    st.title("Admin Review")

    # Password protection
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        st.markdown(
            '<div class="admin-warning"><strong>🔐 Admin Access</strong> — Enter the admin password to view applications.</div>',
            unsafe_allow_html=True,
        )

        password = st.text_input(
            "Admin Password",
            type="password",
            key="admin_password_input",
        )

        if st.button("Login", use_container_width=True):
            if check_admin_auth(password):
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error(
                    "❌ Incorrect password. If you don't have access, contact HQ."
                )
    else:
        # Show logout button and admin content
        col1, col2 = st.columns([0.9, 0.1])
        with col2:
            if st.button("🚪 Logout"):
                st.session_state.admin_authenticated = False
                st.rerun()

        # Fetch applications
        db = get_db()
        rows = db.execute(
            "SELECT id, hero_name, powers, age, location, email FROM submissions ORDER BY id DESC"
        ).fetchall()
        db.close()

        st.write(f"**Total applications:** {len(rows)}")

        if rows:
            # Convert rows to list of dicts for display
            data = []
            for row in rows:
                data.append(
                    {
                        "ID": row["id"],
                        "Hero Name": row["hero_name"] or "—",
                        "Powers": row["powers"] or "—",
                        "Age": row["age"] or "—",
                        "Location": row["location"] or "—",
                        "Email": row["email"] or "—",
                    }
                )

            st.dataframe(data, use_container_width=True, hide_index=True)

            # Export to CSV
            import csv
            import io

            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

            st.download_button(
                label="📥 Download as CSV",
                data=csv_buffer.getvalue(),
                file_name="hero_applications.csv",
                mime="text/csv",
            )
        else:
            st.info("No applications yet.")
