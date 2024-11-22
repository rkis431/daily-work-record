import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# File paths
EMPLOYEE_CSV = 'employee_list.csv'
WORK_CSV = 'employee_data_main.csv'
PLAN_CSV = 'tomorrow_plan_main.csv'

# Admin credentials
ADMINS = {'rkis@admin.com': {'id': 'A001', 'password': 'rkis@0011'}}

# Utility functions to load and save data
def load_employees():
    try:
        return pd.read_csv(EMPLOYEE_CSV)
    except FileNotFoundError:
        return pd.DataFrame(columns=['Email', 'ID', 'Password'])

def save_employees(df):
    df.to_csv(EMPLOYEE_CSV, index=False)

def load_work_data():
    try:
        return pd.read_csv(WORK_CSV)
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Time', 'Email', 'Task', 'Remarks', 'Final Report'])

def save_work_data(df):
    df.to_csv(WORK_CSV, index=False)

def load_plan_data():
    try:
        df = pd.read_csv(PLAN_CSV)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        else:
            df['Date'] = pd.NaT
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Email', 'Tomorrow Plan', 'Start Time', 'End Time'])

def save_plan_data(df):
    df.to_csv(PLAN_CSV, index=False)

def filter_data(df, filter_type, start_date=None, end_date=None, email_filter=None):
    today = datetime.now().date()
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    if filter_type == "Today":
        df = df[df['Date'] == today]
    elif filter_type == "Yesterday":
        df = df[df['Date'] == today - timedelta(days=1)]
    elif filter_type == "Weekly":
        current_week_start = today - timedelta(days=today.weekday())
        df = df[df['Date'] >= current_week_start]
    elif filter_type == "Monthly":
        df = df[df['Date'].apply(lambda x: x.month) == today.month]
    elif filter_type == "Yearly":
        df = df[df['Date'].apply(lambda x: x.year) == today.year]
    elif filter_type == "Date Range" and start_date and end_date:
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if email_filter:
        df = df[df['Email'] == email_filter]

    return df

def display_employee_profile():
    profile_section = f"""
    <div style="background-color: #B6FFA1; color: white; padding: 10px; border-radius: 8px; text-align: right;">
        <h4>{st.session_state.user_email.split('@')[0]}</h4>
        <p style="margin: 0;">Role: {st.session_state.user_role}</p>
    </div>
    """
    st.markdown(profile_section, unsafe_allow_html=True)

# Main app logic
def main():
    st.set_page_config(page_title="Employee Management Dashboard", page_icon=":briefcase:", layout="wide")

    # Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_role = ""

    # Sidebar
    st.sidebar.title("🔐 Access Portal")

    if st.session_state.logged_in:
        st.sidebar.write(f"Logged in as: {st.session_state.user_email} ✅")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_role = ""

    if not st.session_state.logged_in:
        choice = st.sidebar.selectbox("Choose your role", ["Employee 👤", "Admin 🛠️"], index=0)
        if choice == "Employee 👤":
            employee_df = load_employees()
            employee_ids = employee_df['ID'].unique().tolist()
            selected_id = st.selectbox("🔑 Select Your Employee ID", options=employee_ids)
            email = st.text_input("📧 Enter your Email ID")
            password = st.text_input("🔒 Enter your Password", type="password")

            if st.button("Login"):
                employee = employee_df[(employee_df['ID'] == selected_id) & 
                                       (employee_df['Email'] == email) & 
                                       (employee_df['Password'] == password)]
                if not employee.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.user_role = "Employee"
                    st.success("👤 Employee login successful!")
                else:
                    st.error("❌ Invalid credentials")
        elif choice == "Admin 🛠️":
            email = st.text_input("📧 Enter your Email ID")
            user_id = st.text_input("🔑 Enter your ID")
            password = st.text_input("🔒 Enter your Password", type="password")

            if st.button("Login"):
                if email in ADMINS and ADMINS[email]['id'] == user_id and ADMINS[email]['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.user_role = "Admin"
                    st.success("🛠️ Admin login successful!")
                else:
                    st.error("❌ Invalid credentials")
    else:
        if st.session_state.user_role == "Employee":
            st.title("👤 Employee Dashboard")
            display_employee_profile()

            tabs = st.tabs(["📅 Today's Work", "📋 Tomorrow's Plan", "📖 Past Work Entries"])
            with tabs[0]:
                st.subheader("📅 Today's Work")
                time = st.time_input("⏰ Select Time")
                task = st.text_area("✍️ Enter Task for Today", placeholder="Describe your task here...")
                remarks = st.text_area("💬 Enter Remarks", placeholder="Add any remarks here...")
                report = st.selectbox("📊 Final Report Status", ["Complete ✅", "Process 🕒"])

                if st.button("📝 Submit Today's Work"):
                    if task and remarks:
                        work_df = load_work_data()
                        new_entry = pd.DataFrame([{
                            'Date': datetime.now().date(), 'Time': time, 'Email': st.session_state.user_email,
                            'Task': task, 'Remarks': remarks, 'Final Report': report
                        }])
                        work_df = pd.concat([work_df, new_entry], ignore_index=True)
                        save_work_data(work_df)
                        st.success("Work entry saved successfully! ✅")
                    else:
                        st.error("❗ Please complete all fields!")
            with tabs[1]:
                st.subheader("📋 Tomorrow's Plan")
                plan = st.text_area("✏️ Plan for Tomorrow", placeholder="Outline your plan for tomorrow...")
                start_time = st.time_input("🔜 Start Time")
                end_time = st.time_input("🔚 End Time")

                if st.button("📅 Submit Plan"):
                    if not plan:
                        st.error("⚠️ Please enter a plan for tomorrow.")
                    elif start_time >= end_time:
                        st.error("⚠️ Start Time must be earlier than End Time.")
                    else:
                        plan_df = load_plan_data()
                        new_plan = pd.DataFrame([{
                            'Date': datetime.now().date(), 'Email': st.session_state.user_email,
                            'Tomorrow Plan': plan, 'Start Time': start_time, 'End Time': end_time
                        }])
                        plan_df = pd.concat([plan_df, new_plan], ignore_index=True)
                        save_plan_data(plan_df)
                        st.success("Plan saved successfully! ✅")
            with tabs[2]:
                st.subheader("📖 Past Work Entries")
                work_df = load_work_data()
                user_entries = work_df[work_df['Email'] == st.session_state.user_email]
                st.dataframe(user_entries)

                st.markdown("### Tomorrow's Plan Entries")
                plan_df = load_plan_data()
                tomorrow_plan_entries = plan_df[plan_df['Email'] == st.session_state.user_email]
                st.dataframe(tomorrow_plan_entries)
        elif st.session_state.user_role == "Admin":
            st.title("🛠️ Admin Dashboard")
            tabs = st.tabs(["📅 Today's Work", "📋 Tomorrow's Plan", "Analytics", "Employee Data Filter", "➕ Add Employees"])
            with tabs[0]:
                st.subheader("📅 Today's Work Data")
                work_df = load_work_data()
                admin_filter_email = st.text_input("🔍 Filter by Email", key="admin_work_email")
                work_data = filter_data(work_df, "Today", email_filter=admin_filter_email)
                st.dataframe(work_data)
            with tabs[1]:
                st.subheader("📋 Tomorrow's Plan Data")
                plan_df = load_plan_data()
                plan_data = filter_data(plan_df, "Today")
                st.dataframe(plan_data)
            with tabs[2]:
                st.subheader("📊 Analytics")
                work_df = load_work_data()
                filtered_work_df = filter_data(work_df, "Monthly")
                email_counts = filtered_work_df['Email'].value_counts().reset_index()
                email_counts.columns = ['Email', 'Entries']

                fig = px.pie(email_counts, names='Email', values='Entries', title="Monthly Work Entry Distribution")
                st.plotly_chart(fig, use_container_width=True)
            with tabs[3]:
                st.subheader("📊 Employee Data Filter")
                work_df = load_work_data()
                admin_filter_type = st.selectbox("🔍 Filter by Type", ["Today", "Yesterday", "Weekly", "Monthly", "Yearly", "Date Range"])
                start_date, end_date = None, None
                if admin_filter_type == "Date Range":
                    start_date = st.date_input("📅 Start Date")
                    end_date = st.date_input("📅 End Date")
                email_filter = st.text_input("🔍 Filter by Email", key="admin_filter_email")

                filtered_data = filter_data(work_df, admin_filter_type, start_date=start_date, end_date=end_date, email_filter=email_filter)
                st.dataframe(filtered_data)
            with tabs[4]:
                st.subheader("➕ Add Employees")
                employee_df = load_employees()
                st.dataframe(employee_df)

                st.markdown("#### Add New Employee")
                new_email = st.text_input("📧 Email", key="new_employee_email")
                new_id = st.text_input("🆔 Employee ID")
                new_password = st.text_input("🔒 Password", type="password")
                if st.button("Add Employee"):
                    if not new_email or not new_id or not new_password:
                        st.error("⚠️ Please fill all fields.")
                    elif not employee_df[employee_df['ID'] == new_id].empty:
                        st.error("⚠️ Employee ID already exists.")
                    elif not employee_df[employee_df['Email'] == new_email].empty:
                        st.error("⚠️ Email already exists.")
                    else:
                        new_employee = pd.DataFrame([{
                            'Email': new_email, 'ID': new_id, 'Password': new_password
                        }])
                        employee_df = pd.concat([employee_df, new_employee], ignore_index=True)
                        save_employees(employee_df)
                        st.success("✅ New employee added successfully.")

                else:
                    st.error("❗ Please fill all fields to add a new employee!")

if __name__ == "__main__":
    main()
