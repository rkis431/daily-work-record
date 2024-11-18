import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

EMPLOYEE_EMAILS = [
    'rawatanmol0512@gmail.com',
    'employee1@example.com',
    'employee2@example.com',
    'employee3@example.com',
    'employee4@example.com',
    'employee5@example.com',
    'employee6@example.com',
    'employee7@example.com',
    'employee8@example.com',
    'employee9@example.com',
    'employee10@example.com',
    'employee11@example.com',
    'employee12@example.com',
    'employee13@example.com',
    'employee14@example.com',
    'employee15@example.com',
    'employee16@example.com',
    'employee17@example.com',
    'employee18@example.com',
    'employee19@example.com',
    'employee20@example.com'
]
ADMIN_EMAILS = ['admin@example.com']

WORK_CSV = 'employee_data.csv'
PLAN_CSV = 'tomorrow_plan.csv'

def load_work_data():
    try:
        return pd.read_csv(WORK_CSV)
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Time', 'Email', 'Task', 'Remarks', 'Final Report'])

def load_plan_data():
    try:
        return pd.read_csv(PLAN_CSV)
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Email', 'Tomorrow Plan'])

def save_work_data(df):
    df.to_csv(WORK_CSV, index=False)

def save_plan_data(df):
    df.to_csv(PLAN_CSV, index=False)

def filter_data(df, filter_type):
    today = datetime.now().date()
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    if filter_type == "Today":
        return df[df['Date'] == today]
    elif filter_type == "Yesterday":
        return df[df['Date'] == today - timedelta(days=1)]
    elif filter_type == "Weekly":
        current_week_start = today - timedelta(days=today.weekday())
        return df[df['Date'] >= current_week_start]
    return df

def visualize_data(df, filter_type, chart_type):
    if df.empty:
        st.info(f"No entries available for {filter_type}.")
        return

    status_counts = df['Final Report'].value_counts()

    if chart_type == "Pie Chart":
        fig = px.pie(
            values=status_counts,
            names=status_counts.index,
            title=f'Task Completion Status for {filter_type}'
        )
        st.plotly_chart(fig)

    elif chart_type == "Bar Chart":
        fig = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            labels={'x': 'Status', 'y': 'Count'},
            title=f'Task Completion Status for {filter_type}'
        )
        st.plotly_chart(fig)

    elif chart_type == "Line Chart":
        fig = px.line(
            x=status_counts.index,
            y=status_counts.values,
            labels={'x': 'Status', 'y': 'Count'},
            title=f'Task Completion Status for {filter_type}'
        )
        st.plotly_chart(fig)

def main():
    st.set_page_config(page_title="Employee Management App", layout="centered")
    
    hide_st_style = """
    <style>
    body {
        background-color: #FCF596;  /* Set background color to #FCF596 */
        font-family: 'Arial', sans-serif;
    }

    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    
    h1, h2, h3, h4 {
        color: #333333;  /* Dark color for text */
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
    }

    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        font-size: 16px;
        padding: 10px 20px;
        transition: background-color 0.3s ease;
    }

    .stButton>button:hover {
        background-color: None;
    }

    .stSelectbox, .stTextInput, .stTextArea, .stRadio {
        background-color: #FCF596;
        color: #B9E5E8;
        border-radius: 5px;
        border: none;
        padding: 10px;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #3c3c3c;
        color: white;
    }

    .css-16cvbvn {
        background-color: #333333;
    }

    /* Styling cards for data tables */
    .card {
        background-color: #B9E5E8;
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Add some margin around data tables */
    .data-table {
        margin-top: 20px;
    }
    </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    st.title("Employee Management System")

    st.sidebar.title("Access Portal")
    choice = st.sidebar.selectbox("Choose your role", ["Employee", "Admin"])

    if choice == "Employee":
        st.subheader("Employee Login")
        email = st.text_input("Enter your Email ID")

        if email in EMPLOYEE_EMAILS:
            st.success("Welcome, Employee!")
            today = datetime.now().date()
            
            st.write(f"Date: {today}")
            time = st.time_input("Select Time", None)
            task = st.text_area("Enter Task for Today")  
            remarks = st.text_area("Enter Today's Work Remarks")
            report = st.selectbox("Final Report Status", ["Complete", "Processing"])
            tomorrow_plan = st.text_area("Plan for Tomorrow")

            
            if st.button("Submit Today's Work"):
                if not task.strip():  
                    st.error("Please enter the task you worked on today.")
                elif not remarks.strip():  
                    st.error("Please enter your remarks for today.")
                else:
                    work_df = load_work_data()
                    new_work_entry = pd.DataFrame([{
                        'Date': today, 
                        'Time': time, 
                        'Email': email,
                        'Task': task,  
                        'Remarks': remarks,
                        'Final Report': report
                    }])
                    work_df = pd.concat([work_df, new_work_entry], ignore_index=True)
                    save_work_data(work_df)
                    st.success("Today's work entry saved successfully!")

                    if tomorrow_plan.strip():
                        plan_df = load_plan_data()
                        new_plan_entry = pd.DataFrame([{
                            'Date': today, 
                            'Email': email, 
                            'Tomorrow Plan': tomorrow_plan
                        }])
                        plan_df = pd.concat([plan_df, new_plan_entry], ignore_index=True)
                        save_plan_data(plan_df)
                        st.success("Tomorrow's plan saved successfully!")

    elif choice == "Admin":
        st.subheader("Admin Login")
        admin_email = st.text_input("Enter Admin Email ID")

        if admin_email in ADMIN_EMAILS:
            st.success("Welcome, Admin!")
            
            work_df = load_work_data()

            st.write("### Data Options")
            data_option = st.selectbox("Choose an option", ["View Data", "Download CSV"])
            
            if data_option == "Download CSV":
                st.download_button("Download Work Data CSV", work_df.to_csv(index=False), file_name='employee_data.csv')
                st.download_button("Download Plan Data CSV", load_plan_data().to_csv(index=False), file_name='tomorrow_plan.csv')
            
            elif data_option == "View Data":
                user_filter = st.selectbox("Select User", ["All"] + work_df['Email'].unique().tolist())
                filter_type = st.selectbox("Select Time Range", ["Today", "Yesterday", "Weekly"])

                if user_filter != "All":
                    work_df = work_df[work_df['Email'] == user_filter]

                filtered_df = filter_data(work_df, filter_type)

                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.dataframe(filtered_df)
                st.markdown('</div>', unsafe_allow_html=True)

                if not filtered_df.empty:
                    st.write(f"### Visualization for {user_filter} ({filter_type})")

                    chart_type = st.selectbox("Select Chart Type", ["Pie Chart", "Bar Chart", "Line Chart"])
                    visualize_data(filtered_df, filter_type, chart_type)

                st.write("### All Employee Plans for Tomorrow")
                plan_df = load_plan_data()

        
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.dataframe(plan_df)
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.error("Invalid Admin Email! Access Denied.")

if __name__ == "__main__":
    main()
