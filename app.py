import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# User data
EMPLOYEES = {
    'rawatanmol0512@gmail.com': {'id': 'E001', 'password': 'password123'},
    'rawatanmol0512@gmail_2.com': {'id': 'E003', 'password': 'password123'},
    'vibhorvashistha3@gmail.com': {'id': 'E002', 'password': 'password456'}
}
ADMINS = {'admin@example.com': {'id': 'A001', 'password': 'adminpass'}}

# File paths
WORK_CSV = 'employee_data_main.csv'
PLAN_CSV = 'tomorrow_plan_main.csv'


# Data loading and saving functions
def load_work_data():
    try:
        return pd.read_csv(WORK_CSV)
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Time', 'Email', 'Task', 'Remarks', 'Final Report'])


def load_plan_data():
    try:
        df = pd.read_csv(PLAN_CSV, parse_dates=['Date'])
        df['Date'] = df['Date'].dt.date
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Email', 'Tomorrow Plan', 'Start Time', 'End Time'])


def save_work_data(df):
    df.to_csv(WORK_CSV, index=False)


def save_plan_data(df):
    df.to_csv(PLAN_CSV, index=False)


# Utility for filtering data
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


# Main function
def main():
    st.set_page_config(page_title="Employee Management App", layout="wide")

    # Hide Streamlit branding
    st.markdown(
        """
        <style>
        .stDeployButton {
            visibility: hidden;
        }
        footer {visibility: hidden;}
        .css-1q8dd3e.e1fqkh3o0 {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h1 style='text-align: center;'>👔 Employee Management Dashboard</h1>", unsafe_allow_html=True)

    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_role = ""

    st.sidebar.title("🔐 Access Portal")

    if st.session_state.logged_in:
        st.sidebar.write(f"Logged in as: {st.session_state.user_email} ✅")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_role = ""

    if not st.session_state.logged_in:
        # Login UI
        choice = st.sidebar.selectbox("Choose your role", ["Employee 👤", "Admin 🛠️"], index=0)
        email = st.text_input("📧 Enter your Email ID")
        user_id = st.text_input("🔑 Enter your ID")
        password = st.text_input("🔒 Enter your Password", type="password")

        if st.button("Login"):
            if choice == "Employee 👤" and email in EMPLOYEES and EMPLOYEES[email]['id'] == user_id and EMPLOYEES[email]['password'] == password:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_role = "Employee"
                st.success("👤 Employee login successful!")
            elif choice == "Admin 🛠️" and email in ADMINS and ADMINS[email]['id'] == user_id and ADMINS[email]['password'] == password:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_role = "Admin"
                st.success("🛠️ Admin login successful!")
            else:
                st.error("❌ Invalid credentials")

    elif st.session_state.user_role == "Employee":
        # Employee Dashboard
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
        # Admin Dashboard
        st.title("🛠️ Admin Dashboard")
        st.subheader("📊 View Work Data")

        tabs = st.tabs(["📅 Today's Work", "📋 Tomorrow's Plan", "Analytics", "Employee Data Filter"])

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
            st.subheader("📈 Analytics")
            work_df = load_work_data()
            work_by_employee = work_df.groupby('Email')['Task'].count().reset_index().rename(columns={'Task': 'Total Tasks'})
            fig = px.bar(work_by_employee, x='Email', y='Total Tasks', title="Total Tasks by Employee", text_auto=True)
            st.plotly_chart(fig)

        with tabs[3]:
            st.subheader("📂 Filter Employee Data")
            work_df = load_work_data()
            start_date = st.date_input("📆 Start Date", key="start_date_filter")
            end_date = st.date_input("📆 End Date", key="end_date_filter")
            email_filter = st.text_input("🔍 Filter by Email", key="admin_employee_email_filter")
            if st.button("🔍 Filter Data"):
                filtered_data = filter_data(work_df, "Date Range", start_date, end_date, email_filter)
                st.dataframe(filtered_data)


if __name__ == "__main__":
    main()
