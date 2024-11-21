import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# File Constants
EMPLOYEE_CSV = 'employee_list.csv'
WORK_CSV = 'employee_data_main.csv'
PLAN_CSV = 'tomorrow_plan_main.csv'

# Admin Credentials
ADMINS = {'rkis@admin.com': {'id': 'A001', 'password': 'rkis@0011'}}


# Helper Functions
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


def filter_data(df, filter_type, start_date=None, end_date=None, email_filter=None):
    today = datetime.now().date()
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    if filter_type == "Yesterday":
        df = df[df['Date'] == today - timedelta(days=1)]
    elif filter_type == "Weekly":
        current_week_start = today - timedelta(days=today.weekday())
        df = df[df['Date'] >= current_week_start]
    elif filter_type == "Monthly":
        df = df[df['Date'].apply(lambda x: x.month) == today.month]
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


# Main App Function
def main():
    st.set_page_config(page_title="Employee Management Dashboard", page_icon=":briefcase:", layout="wide")

    # Session State for Authentication
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
        choice = st.sidebar.selectbox("Choose your role", ["Employee 👤", "Admin 🛠️"], index=0)
        email = st.text_input("📧 Enter your Email ID")
        user_id = st.text_input("🔑 Enter your ID")
        password = st.text_input("🔒 Enter your Password", type="password")

        if st.button("Login"):
            if choice == "Admin 🛠️" and email in ADMINS and ADMINS[email]['id'] == user_id and ADMINS[email]['password'] == password:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_role = "Admin"
                st.success("🛠️ Admin login successful!")
            else:
                st.error("❌ Invalid credentials")

    elif st.session_state.user_role == "Admin":
        st.title("🛠️ Admin Dashboard")
        tabs = st.tabs(["📅 Search Data", "📈 Analytics", "➕ Add Employees"])

        # Search Data Tab
        with tabs[0]:
            st.subheader("📅 Search Employee Data")
            filter_type = st.radio("Select Filter Type:", ["Yesterday", "Weekly", "Monthly", "Date Range"], horizontal=True)
            email_filter = st.text_input("🔍 Filter by Email (Optional)", key="admin_filter_email")

            # Date Range Inputs
            start_date, end_date = None, None
            if filter_type == "Date Range":
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("📆 Start Date")
                with col2:
                    end_date = st.date_input("📆 End Date")

            # Load Data
            work_df = load_work_data()
            filtered_data = filter_data(work_df, filter_type, start_date, end_date, email_filter)
            st.dataframe(filtered_data)

            # Download Option
            if not filtered_data.empty:
                csv = filtered_data.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Data as CSV", data=csv, file_name='filtered_employee_data.csv', mime='text/csv')

        # Analytics Tab
        with tabs[1]:
            st.subheader("📈 Analytics")
            work_df = load_work_data()
            work_by_employee = work_df.groupby('Email')['Task'].count().reset_index().rename(columns={'Task': 'Total Tasks'})
            fig = px.bar(work_by_employee, x='Email', y='Total Tasks', title="Total Tasks by Employee", text_auto=True)
            st.plotly_chart(fig)

        # Add Employees Tab
        with tabs[2]:
            st.subheader("➕ Add Employees")
            new_employee_email = st.text_input("📧 Enter Employee Email ID")
            new_employee_id = st.text_input("🆔 Enter Employee ID")
            new_employee_password = st.text_input("🔒 Enter Employee Password", type="password")

            if st.button("Add Employee"):
                employee_df = load_employees()
                if not new_employee_email or not new_employee_id or not new_employee_password:
                    st.error("⚠️ All fields are mandatory.")
                elif new_employee_email in employee_df['Email'].values:
                    st.error("❌ Employee with this email already exists.")
                else:
                    new_employee = pd.DataFrame([{'Email': new_employee_email, 'ID': new_employee_id, 'Password': new_employee_password}])
                    employee_df = pd.concat([employee_df, new_employee], ignore_index=True)
                    save_employees(employee_df)
                    st.success("✅ Employee added successfully!")


if __name__ == "__main__":
    main()
