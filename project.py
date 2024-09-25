import streamlit as st
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import plotly.express as px

# Paths for files
credentials_file = 'credentials.json'
user_data_dir = 'user_data'  # Directory to store user-specific data

# Ensure credentials.json and user_data directory exists
if not os.path.exists(credentials_file):
    with open(credentials_file, 'w') as file:
        json.dump({}, file)

if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)

# Function to save credentials to JSON
def save_credentials(username, password, mobile, city):
    with open(credentials_file, 'r+') as file:
        credentials = json.load(file)
        credentials[username] = {'password': password, 'mobile': mobile, 'city': city}
        file.seek(0)
        json.dump(credentials, file, indent=4)

# Function to authenticate user login
def authenticate_user(username, password):
    with open(credentials_file, 'r') as file:
        credentials = json.load(file)
    return username in credentials and credentials[username]['password'] == password

# Function to create user-specific folder and marks CSV file after login
def create_user_marks_file(username):
    # Create user-specific directory
    user_dir = os.path.join(user_data_dir, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    
    # Path to the user's marks CSV file
    user_file_path = os.path.join(user_dir, f"{username}_marks.csv")
    
    # If the file does not exist, create it
    if not os.path.exists(user_file_path):
        df = pd.DataFrame(columns=['Subject', 'Marks'])
        df.to_csv(user_file_path, index=False)
    
    return user_file_path

# Function to save the user's marks into their CSV file
def save_user_marks(username, marks_data):
    user_file_path = create_user_marks_file(username)
    df = pd.DataFrame(list(marks_data.items()), columns=['Subject', 'Marks'])
    df.to_csv(user_file_path, index=False)

# Function to load the user's marks from their CSV file
def load_user_marks(username):
    user_file_path = create_user_marks_file(username)
    df = pd.read_csv(user_file_path)
    return df

# Initialize session state for tracking login status
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'marks_submitted' not in st.session_state:
    st.session_state['marks_submitted'] = False

# Sidebar for Login/Signup
st.sidebar.title("Welcome")
option = st.sidebar.radio("Choose an option", ["Login", "Sign Up"])

# Marks entry page after successful login
def marks_entry_page(username):
    # Personalized greeting with username
    st.title(f"Welcome {username}, enter your marks")

    # Sliders for subjects with default values set to 0
    maths_marks = st.slider("Maths", 0, 100, 0)  # Default value is 0
    science_marks = st.slider("Science", 0, 100, 0)  # Default value is 0
    cs_marks = st.slider("Computer Science", 0, 100, 0)  # Default value is 0
    english_marks = st.slider("English", 0, 100, 0)  # Default value is 0
    arts_marks = st.slider("Arts", 0, 100, 0)  # Default value is 0

    # Save button
    if st.button("Save Marks"):
        marks_data = {
            'Maths': maths_marks,
            'Science': science_marks,
            'Computer Science': cs_marks,
            'English': english_marks,
            'Arts': arts_marks
        }
        save_user_marks(username, marks_data)
        st.success(f"Marks saved for {username}!")
        st.session_state['marks_submitted'] = True  # Update session state to indicate marks are submitted

# Report page after saving marks
def report_page(username):
    st.title("Your Reports are Ready!")

    # Load user marks
    df = load_user_marks(username)

    # 1. Bar Graph: Average Marks
    st.subheader("Average Marks")
    avg_marks = df['Marks'].mean()

    # Plot bar chart for average marks
    fig, ax = plt.subplots()
    ax.bar("Average Marks", avg_marks, color="skyblue")
    ax.set_ylim([0, 100])
    st.pyplot(fig)

    # 2. Line Graph: Marks per Subject
    st.subheader("Marks per Subject (Line Chart)")
    fig_line = px.line(df, x="Subject", y="Marks", title="Marks per Subject")
    st.plotly_chart(fig_line)

    # 3. Pie Chart: Marks Distribution
    st.subheader("Marks Distribution (Pie Chart)")
    fig_pie = px.pie(df, names="Subject", values="Marks", title="Marks Distribution per Subject")
    st.plotly_chart(fig_pie)

    # Add a Sign Out button
    if st.button("Sign Out"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['marks_submitted'] = False

# Login page
if option == "Login" and not st.session_state['logged_in']:
    st.title("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if authenticate_user(login_username, login_password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = login_username
            create_user_marks_file(login_username)
            st.session_state['marks_submitted'] = False  # Reset marks submitted state
        else:
            st.error("Invalid username or password. Please try again.")

# Sign Up page
elif option == "Sign Up" and not st.session_state['logged_in']:
    st.title("Sign up for your journey")

    with st.form(key='signup_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        mobile = st.text_input("Mobile")
        city = st.text_input("City")
        
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if username and password and mobile and city:
                with open(credentials_file, 'r') as file:
                    credentials = json.load(file)
                if username in credentials:
                    st.error("This account already exists. Please choose a different username.")
                else:
                    save_credentials(username, password, mobile, city)
                    st.success("Sign-up successful!")
            else:
                st.error("Please fill all fields.")

# Load the appropriate page based on the session state
if st.session_state['logged_in']:
    if st.session_state['marks_submitted']:
        report_page(st.session_state['username'])
    else:
        marks_entry_page(st.session_state['username'])
