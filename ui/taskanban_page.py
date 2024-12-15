import streamlit as st
import pandas as pd
from db import init_db, get_latest_version
from ui.card_component import display_task_card
from utils.utils import upload_to_azure_blob, save_to_device, show_error
import time


def get_unique_values(merged_data, column_name, default_values=[]):
    unique_values = merged_data[column_name].dropna().unique().tolist()
    return default_values + sorted(unique_values)


def filter_tasks(
    tasks,
    selected_version,
    selected_sprint_value,
    selected_priority,
    selected_assignee,
    selected_due_date,
    status,
):
    if selected_version != "All Versions":
        tasks = tasks[tasks["version"] == selected_version]
    if selected_sprint_value != "All_Sprints":
        if status == "No Status":
            tasks = tasks[
                (tasks["Status"].isna())
                & (tasks["SprintName"] == selected_sprint_value)
            ]
        else:
            tasks = tasks[
                (tasks["Status"] == status)
                & (tasks["SprintName"] == selected_sprint_value)
            ]
    else:
        if status == "No Status":
            tasks = tasks[tasks["Status"].isna()]
        else:
            tasks = tasks[tasks["Status"] == status]
    if selected_priority != "All Priorities":
        tasks = tasks[tasks["Priority"] == selected_priority]
    if selected_assignee != "All Assignees":
        tasks = tasks[
            tasks["AssigneeName-Role"]
            .fillna("")
            .str.contains(selected_assignee, case=False)
        ]
    if selected_due_date != "All Due Dates":
        tasks = tasks[tasks["DueDate"] == selected_due_date]
    return tasks


def show_taskanban():
    st.markdown(
        "<h1 style='text-align: center;'>📋 TasKanban</h1>", unsafe_allow_html=True
    )

    conn, c = init_db()
    try:
        merged_data = pd.read_sql_query("SELECT * FROM merged_data", conn)
        latest_version = get_latest_version(c)
    except pd.errors.DatabaseError:
        st.write("No boards created yet.")
        conn.close()
        return
    conn.close()

    if merged_data.empty:
        st.write("No data available.")
        return

    status_order = ["No Status", "To Do", "In Progress", "Done"]
    statuses = [
        status
        for status in status_order
        if status in merged_data["Status"].dropna().unique().tolist()
    ]
    statuses.insert(0, "No Status")

    versions = get_unique_values(merged_data, "version", ["All Versions"])
    sprints = get_unique_values(merged_data, "SprintName", ["All Sprints", "No Sprint"])
    priorities = get_unique_values(merged_data, "Priority", ["All Priorities"])
    assignees = get_unique_values(merged_data, "AssigneeName-Role")
    assignee_names = ["All Assignees"] + sorted(
        list(set([assignee.split("-")[0] for assignee in assignees]))
    )
    due_dates = get_unique_values(merged_data, "DueDate", ["All Due Dates"])

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col1:
        selected_version = st.selectbox(
            "Select Version",
            versions,
            index=versions.index(latest_version) if latest_version in versions else 0,
            key="version_selector",
        )
    with col2:
        selected_sprint_label = st.selectbox(
            "Select Sprint",
            sprints,
            key="sprint_selector",
            format_func=lambda x: x.replace("_", " "),
        )
    with col3:
        selected_priority = st.selectbox(
            "Select Priority", priorities, key="priority_selector"
        )
    with col4:
        selected_assignee = st.selectbox(
            "Select Assignee", assignee_names, key="assignee_selector"
        )
    with col5:
        selected_due_date = st.selectbox(
            "Select Due Date", due_dates, key="due_date_selector"
        )

    selected_sprint_value = selected_sprint_label.replace(" ", "_")

    if st.button("⬆️ Upload to Azure"):
        connection_string = st.session_state.connection_string
        container_name = st.session_state.container_name
        try:
            upload_to_azure_blob(
                merged_data,
                connection_string,
                container_name,
                latest_version,
                file_type="csv",
            )
        except Exception as e:
            show_error(f"Error uploading data to Azure: {e}")

    save_to_device(merged_data, latest_version, "💾 Download to Device", "merged_data")

    if st.button("🗑️ Delete"):
        conn, c = init_db()
        if selected_version == "All Versions":
            c.execute("DELETE FROM merged_data")
        else:
            c.execute("DELETE FROM merged_data WHERE version = ?", (selected_version,))
        conn.commit()
        conn.close()
        show_error("Merged Data Version {selected_version} deleted successfully.")
        time.sleep(2)
        st.rerun()

    columns = st.columns(len(statuses))
    for status, column in zip(statuses, columns):
        with column:
            tasks = filter_tasks(
                merged_data.copy(),
                selected_version,
                selected_sprint_value,
                selected_priority,
                selected_assignee,
                selected_due_date,
                status,
            )
            task_count = len(tasks)
            st.markdown(
                f"<h6>{status.upper()} &nbsp;&nbsp;&nbsp; {task_count}</h6>",
                unsafe_allow_html=True,
            )
            for _, task in tasks.iterrows():
                display_task_card(task)

    # Inject JavaScript to scroll to the top
    st.markdown(
        """
        <script>
            window.scrollTo(0, 0);
        </script>
        """,
        unsafe_allow_html=True,
    )
