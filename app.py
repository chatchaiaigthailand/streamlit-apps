import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# --- Configuration ---
st.set_page_config(page_title="Team Work Status", layout="wide")

# --- Team Members ---
TEAM_MEMBERS = [
    "Pond","Bank","Pang"
]
STATUS_OPTIONS = ["WFO", "WFH"]
DATA_FILE = "wfh_wfo_status.csv"

# --- Helper Functions ---

def load_data():
    """Loads status data from CSV, creating the file if it doesn't exist."""
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Date", "Name", "Status"])
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

def save_data(df):
    """Saves the DataFrame to the CSV file."""
    df.to_csv(DATA_FILE, index=False)

def get_month_calendar(year, month, df):
    """Generates a dictionary representing the calendar with team status."""
    month_calendar = calendar.monthcalendar(year, month)
    status_calendar = {}

    for week in month_calendar:
        for day in week:
            if day == 0:
                continue # Days not in the current month
            
            date_obj = datetime(year, month, day).date()
            daily_status = df[df['Date'] == date_obj]
            
            status_calendar[day] = {
                "WFO": daily_status[daily_status['Status'] == 'WFO']['Name'].tolist(),
                "WFH": daily_status[daily_status['Status'] == 'WFH']['Name'].tolist()
            }
    return status_calendar, calendar.month_name[month]

# --- Main Application ---

st.title("🗓️ DDM-TH Workplace Tracker")
st.markdown("Log your daily work location and view the team's schedule for the current month.")

# Load existing data
df = load_data()

# --- 1. Input Section ---
st.header("✏️ Log Your Status")

col1, col2, col3 = st.columns(3)

with col1:
    selected_name = st.selectbox("Select Your Name:", options=TEAM_MEMBERS)

with col2:
    today = datetime.now().date()
    selected_date = st.date_input("Select Date:", value=today)

with col3:
    selected_status = st.selectbox("Select Status:", options=STATUS_OPTIONS)

if st.button("Submit Status"):
    # Check if an entry for this user and date already exists
    existing_entry = df[(df['Name'] == selected_name) & (df['Date'] == selected_date)]

    if not existing_entry.empty:
        # Update existing entry
        df.loc[existing_entry.index, 'Status'] = selected_status
        st.success(f"Updated status for {selected_name} on {selected_date} to {selected_status}.")
    else:
        # Add new entry
        new_entry = pd.DataFrame([{"Date": selected_date, "Name": selected_name, "Status": selected_status}])
        df = pd.concat([df, new_entry], ignore_index=True)
        st.success(f"Logged status for {selected_name} on {selected_date} as {selected_status}.")
    
    # Save the updated data
    save_data(df)


# --- 2. Calendar Visualization ---
st.header("📅 Monthly Calendar View")

current_date = datetime.now()
status_cal, month_name = get_month_calendar(current_date.year, current_date.month, df)

st.subheader(f"{month_name} {current_date.year}")

# Display calendar headers
days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
cols = st.columns(7)
for i, day_name in enumerate(days_of_week):
    with cols[i]:
        st.markdown(f"**{day_name}**")

# Get the first day of the week for the month (0=Monday, 6=Sunday)
first_day_of_month = calendar.weekday(current_date.year, current_date.month, 1)

# Display calendar days
day_counter = 1
total_days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]

while day_counter <= total_days_in_month:
    cols = st.columns(7)
    for i in range(7):
        # Before the first day of the month, leave columns empty
        if day_counter == 1 and i < first_day_of_month:
            cols[i].markdown("")
            continue
        
        if day_counter > total_days_in_month:
            break

        with cols[i]:
            st.markdown(f"**{day_counter}**")
            day_status = status_cal.get(day_counter, {"WFO": [], "WFH": []})
            
            if day_status["WFO"]:
                st.markdown("🏢 **WFO**")
                for name in day_status["WFO"]:
                    st.markdown(f"- {name}")
            
            if day_status["WFH"]:
                st.markdown("🏠 **WFH**")
                for name in day_status["WFH"]:
                    st.markdown(f"- {name}")
            
            # Add a divider for better visual separation
            st.markdown("---")

        day_counter += 1


# --- 3. Data Summary ---
if st.checkbox("Show Raw Data Log"):
    st.header("📋 Raw Data")
    st.dataframe(df.sort_values(by="Date", ascending=False).reset_index(drop=True))

