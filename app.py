import streamlit as st
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime
import base64

# SQLAlchemy engine and session setup
DATABASE_URI = 'mysql+pymysql://root:823f2987c3b2@localhost/courier_management'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()
metadata.reflect(bind=engine)

# Define tables
couriers = Table('couriers', metadata, autoload_with=engine)
shipments = Table('shipments', metadata, autoload_with=engine)
users = Table('users', metadata, autoload_with=engine)

# Create a database connection
def create_connection():
    try:
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="#########",
            database="courier_management"
        )
        if con.is_connected():
            return con
    except Error as e:
        st.error(f"Error connecting to MySQL database: {e}")
        return None

# Validate login credentials
def validate_login(con, username, password):
    try:
        cur = con.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user and check_password_hash(user[0], password):
            return True
        return False
    except Error as e:
        st.error(f"Error: {e}")
        return False

# Register new user
def register_user(con, username, password):
    try:
        cur = con.cursor()
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        con.commit()
        st.success("Registration successful! You can now log in.")
    except Error as e:
        st.error(f"Error: {e}")

# Function to encode image to base64
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Add CSS for background image and styling
background_image = "Blog-119-2.jpg"
background_base64 = get_base64(background_image)
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{background_base64}");
        background-size: cover;
        background-position: center;
    }}
    .stTextInput, .stSelectbox, .stButton {{
        background-color: rgba(255, 255, 255, 0.8);
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 8px;
        color: #333;
        font-weight: bold;
    }}
    .stTextInput::placeholder, .stTextInput, .stText {{
        color: #333;
    }}
    .stButton>button {{
        background-color: #444 !important;
        color: white !important;
    }}
    .stSidebar .stSelectbox, .stSidebar .stButton {{
        background-color: rgba(255, 255, 255, 0.8);
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 8px;
        color: #333;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# User Authentication
st.title("Courier Management System")

# Check if the user is logged in
if 'logged_in' in st.session_state and st.session_state.logged_in:
    st.sidebar.title("Options")
    option = st.sidebar.selectbox("Select Operation", ["View Couriers", "Add Courier", "Update Courier", "Delete Courier", "View Shipments", "Add Shipment", "Update Shipment", "Delete Shipment"])

    if option == "View Couriers":
        st.header("Couriers")
        couriers_df = pd.read_sql_table('couriers', con=engine)
        st.write(couriers_df)

    elif option == "Add Courier":
        st.header("Add New Courier")
        name = st.text_input("Name")
        contact_info = st.text_input("Contact Info")
        vehicle = st.text_input("Vehicle")
        if st.button("Add Courier"):
            insert = couriers.insert().values(name=name, contact_info=contact_info, vehicle=vehicle)
            session.execute(insert)
            session.commit()
            st.success("Courier added successfully!")

    elif option == "Update Courier":
        st.header("Update Courier")
        courier_id = st.number_input("Courier ID", min_value=1)
        name = st.text_input("Name")
        contact_info = st.text_input("Contact Info")
        vehicle = st.text_input("Vehicle")
        if st.button("Update Courier"):
            update = couriers.update().where(couriers.c.courier_id == courier_id).values(name=name, contact_info=contact_info, vehicle=vehicle)
            session.execute(update)
            session.commit()
            st.success("Courier updated successfully!")

    elif option == "Delete Courier":
        st.header("Delete Courier")
        courier_id = st.number_input("Courier ID", min_value=1)
        if st.button("Delete Courier"):
            delete = couriers.delete().where(couriers.c.courier_id == courier_id)
            session.execute(delete)
            session.commit()
            st.success("Courier deleted successfully!")

    elif option == "View Shipments":
        st.header("Shipments")
        shipments_df = pd.read_sql_table('shipments', con=engine)
        st.write(shipments_df)

    elif option == "Add Shipment":
        st.header("Add New Shipment")
        courier_id = st.number_input("Courier ID", min_value=1)
        recipient_name = st.text_input("Recipient Name")
        recipient_address = st.text_area("Recipient Address")
        shipment_date = st.date_input("Shipment Date", datetime.now())
        status = st.selectbox("Status", ["Pending", "In Transit", "Delivered"])
        if st.button("Add Shipment"):
            insert = shipments.insert().values(courier_id=courier_id, recipient_name=recipient_name, recipient_address=recipient_address, shipment_date=shipment_date, status=status)
            session.execute(insert)
            session.commit()
            st.success("Shipment added successfully!")

    elif option == "Update Shipment":
        st.header("Update Shipment")
        shipment_id = st.number_input("Shipment ID", min_value=1)
        courier_id = st.number_input("Courier ID", min_value=1)
        recipient_name = st.text_input("Recipient Name")
        recipient_address = st.text_area("Recipient Address")
        shipment_date = st.date_input("Shipment Date", datetime.now())
        status = st.selectbox("Status", ["Pending", "In Transit", "Delivered"])
        if st.button("Update Shipment"):
            update = shipments.update().where(shipments.c.shipment_id == shipment_id).values(courier_id=courier_id, recipient_name=recipient_name, recipient_address=recipient_address, shipment_date=shipment_date, status=status)
            session.execute(update)
            session.commit()
            st.success("Shipment updated successfully!")

    elif option == "Delete Shipment":
        st.header("Delete Shipment")
        shipment_id = st.number_input("Shipment ID", min_value=1)
        if st.button("Delete Shipment"):
            delete = shipments.delete().where(shipments.c.shipment_id == shipment_id)
            session.execute(delete)
            session.commit()
            st.success("Shipment deleted successfully!")

else:
    st.sidebar.title("Account")
    register_option = st.sidebar.radio("Select Option", ["Login", "Register"])
    
    if register_option == "Register":
        st.header("Register")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            con = create_connection()
            if con:
                register_user(con, new_username, new_password)
                con.close()
    elif register_option == "Login":
        st.header("Login")
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            con = create_connection()
            if con:
                authentication_status = validate_login(con, username_input, password_input)
                con.close()
                
                if authentication_status:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                else:
                    st.error("Username/password is incorrect")

# Close session
session.close()
