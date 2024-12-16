import streamlit as st
import os
from ui.upload_component import upload_files
from ui.data_preview_component import preview_data
from ui.cleaning_component import clean_data
from ui.merge_component import merge_data
from utils.utils import (
    show_error,
    show_success,
    upload_to_azure_blob,
    save_to_device,
    create_excel_from_dict,
)
from classes.task_list import TaskList
from ui.settings_page import show_settings
from ui.taskanban_page import show_taskanban
from db import init_db, save_merged_data_to_db


class TaskMainUI:
    def __init__(self):
        self.setup_ui()

    def setup_ui(self):
        st.set_page_config(page_title="Jira Lite", page_icon="🎫", layout="wide")

        # Sidebar with navigation
        st.sidebar.title("🎫 Jira Lite")
        if "page" not in st.session_state:
            st.session_state.page = "TasKlean"
        page = st.sidebar.radio(
            "Navigation",
            ["TasKlean", "TasKanban", "Settings"],
            index=["TasKlean", "TasKanban", "Settings"].index(st.session_state.page),
            label_visibility="collapsed",
        )

        if st.session_state.page != page:
            st.session_state.page = page
            st.rerun()

        if page == "TasKlean":
            self.show_tasklean()
        elif page == "TasKanban":
            show_taskanban()
        elif page == "Settings":
            show_settings()

    def initialize_session_state(self):
        if "step" not in st.session_state:
            st.session_state.step = 1
        if "clean_data_successful" not in st.session_state:
            st.session_state.clean_data_successful = False
        if "uploaded_files" not in st.session_state:
            st.session_state.uploaded_files = {}
        if "cleaned_data" not in st.session_state:
            st.session_state.cleaned_data = {}
        if "rejected_data" not in st.session_state:
            st.session_state.rejected_data = {}
        if "merged_tasks_values" not in st.session_state:
            st.session_state.merged_tasks_values = {}
        if "merged_data" not in st.session_state:
            st.session_state.merged_data = {}
        if "version" not in st.session_state:
            st.session_state.version = 1
        if "checklist" not in st.session_state:
            st.session_state.checklist = {
                "Tasks": False,
                "Assignees": False,
                "DueDates": False,
                "Sprints": False,
            }
        if "imported_files" not in st.session_state:
            st.session_state.imported_files = {}
        if "blob_files" not in st.session_state:
            st.session_state.blob_files = {}
        if "selected_files" not in st.session_state:
            st.session_state.selected_files = []
        if "connection_string" not in st.session_state:
            st.session_state.connection_string = ""
        if "container_name" not in st.session_state:
            st.session_state.container_name = ""

    def show_tasklean(self):
        # Initialize task list
        task_list = TaskList()
        self.initialize_session_state()

        # Show app title and description.
        st.markdown(
            """
            <h1 style="text-align: center;">📝 TasKlean</h1>
            """,
            unsafe_allow_html=True,
        )

        # Step 1: Upload files
        if st.session_state.step == 1:
            st.header("Step 1: Upload Files")
            combined_files, all_files_uploaded = upload_files()
            if all_files_uploaded:
                st.session_state.uploaded_files = combined_files

        # Step 2: Preview Data
        if st.session_state.step == 2:
            st.header("Step 2: Preview Data")
            try:
                with st.spinner("Loading data preview..."):
                    preview_data(st.session_state.uploaded_files)
            except Exception as e:
                show_error(f"Error previewing data: {e}")

        # Step 3: Clean Data
        if st.session_state.step == 3:
            if not st.session_state.clean_data_successful:
                st.header("Step 3: Clean Data")
                try:
                    with st.spinner("Cleaning data..."):
                        cleaned_data, rejected_data, merged_tasks_values = clean_data(
                            st.session_state.uploaded_files, task_list
                        )
                    st.session_state.cleaned_data = cleaned_data
                    st.session_state.rejected_data = rejected_data
                    st.session_state.merged_tasks_values = merged_tasks_values
                    st.session_state.clean_data_successful = True

                    # Display cleaned and rejected datasets
                    if cleaned_data:
                        file_tabs = st.tabs(
                            [
                                file_name.replace(".csv", "")
                                for file_name in cleaned_data.keys()
                            ]
                        )
                        for file_tab, file_name in zip(file_tabs, cleaned_data.keys()):
                            with file_tab:
                                st.subheader(file_name.replace(".csv", ""))
                                sub_tabs = st.tabs(["Cleaned Data", "Rejected Data"])
                                with sub_tabs[0]:
                                    st.dataframe(
                                        cleaned_data[file_name],
                                        use_container_width=True,
                                        hide_index=True,
                                    )
                                with sub_tabs[1]:
                                    st.dataframe(
                                        rejected_data[file_name],
                                        use_container_width=True,
                                        hide_index=True,
                                    )

                    show_success("Data cleaned successfully.")
                except Exception as e:
                    show_error(f"Error cleaning data: {e}")

        # Step 4: Merge Data
        if st.session_state.step == 4:
            st.header("Merged Data Tables")
            merged_data = merge_data(st.session_state.cleaned_data)
            st.session_state.merged_data = merged_data
            st.dataframe(merged_data, use_container_width=True, hide_index=True)

            # Upload to Azure Blob
            if st.session_state.connection_string and st.session_state.container_name:
                if st.button("⬆️ Upload Merged Data"):
                    connection_string = st.session_state.connection_string
                    container_name = st.session_state.container_name
                    upload_to_azure_blob(
                        merged_data,
                        connection_string,
                        container_name,
                        st.session_state.version,
                        file_type="csv",
                    )
            else:
                st.write("Setup your connection in settings first to upload to azure.")
                if st.button("Go to Settings", key="settings_button"):
                    st.session_state.page = "Settings"
                    st.rerun()

            # Download Merged Data
            save_to_device(
                merged_data,
                st.session_state.version,
                "💾 Download Merged Data",
                "merged_data",
            )

            # Display rejected data
            st.header("Rejected Data")
            rejected_data = st.session_state.rejected_data
            if rejected_data:
                file_tabs = st.tabs(
                    [
                        file_name.replace(".csv", "")
                        for file_name in rejected_data.keys()
                    ]
                )
                for file_tab, file_name in zip(file_tabs, rejected_data.keys()):
                    with file_tab:
                        st.subheader(file_name.replace(".csv", ""))
                        st.dataframe(
                            rejected_data[file_name],
                            use_container_width=True,
                            hide_index=True,
                        )

            # Create an Excel file of rejected data with each key in its own sheet
            rejected_data_file = create_excel_from_dict(
                rejected_data,
                st.session_state.version,
                "rejected_data",
            )

            # Upload Rejected Data to Azure Blob
            if st.session_state.connection_string and st.session_state.container_name:
                if st.button("⬆️ Upload Rejected Data"):
                    connection_string = st.session_state.connection_string
                    container_name = st.session_state.container_name
                    upload_to_azure_blob(
                        rejected_data,
                        connection_string,
                        container_name,
                        st.session_state.version,
                        file_type="xlsx",
                        file_name="rejected_data",
                    )
            else:
                st.write("Setup your connection in settings first to upload to azure.")
                if st.button("Go to Settings"):
                    st.session_state.page = "Settings"
                    st.rerun()

            # Download Rejected Data
            with open(rejected_data_file, "rb") as f:
                st.download_button(
                    label="💾 Download Rejected Data",
                    data=f,
                    file_name=rejected_data_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            os.remove(rejected_data_file)  # Delete the temporary file

            # Add space above the navigation buttons
            st.markdown("<br>", unsafe_allow_html=True)

            # Navigation buttons for the last step
            col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 6, 3])
            with col1:
                if st.button("Process Again", type="secondary"):
                    self.restart_process()
            with col5:
                if st.button("View in TasKanban", type="primary"):
                    conn, c = init_db()
                    save_merged_data_to_db(
                        c, st.session_state.merged_data, st.session_state.version
                    )
                    conn.commit()
                    conn.close()
                    st.session_state.page = "TasKanban"
                    st.rerun()

        # Navigation buttons for steps 1 to 3
        if st.session_state.step < 4:
            # Add space above the navigation buttons
            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 14, 4])
            with col1:
                if st.session_state.step > 1:
                    if st.button("Cancel", type="secondary"):
                        self.restart_process()
            with col5:
                next_disabled = (
                    (st.session_state.step == 1 and not all_files_uploaded)
                    or (
                        st.session_state.step == 2
                        and not st.session_state.uploaded_files
                    )
                    or (
                        st.session_state.step == 3
                        and not st.session_state.clean_data_successful
                    )
                )
                next_button_text = (
                    "Next: Preview"
                    if st.session_state.step == 1
                    else (
                        "Next: Clean Data"
                        if st.session_state.step == 2
                        else "Next: Merge Data"
                    )
                )
                if st.button(
                    next_button_text,
                    disabled=next_disabled,
                    key="next_button",
                    type="primary",
                ):
                    st.session_state.step += 1
                    st.rerun()

        # Footer
        st.markdown(
            """
            <footer style="text-align: center; margin-top: 50px;">
            Mc Joseph Agbanlog and John Christian Berbon © 2024
            </footer>
            """,
            unsafe_allow_html=True,
        )

    def restart_process(self):
        st.session_state.step = 1
        st.session_state.clean_data_successful = False
        st.session_state.uploaded_files = {}
        st.session_state.cleaned_data = {}
        st.session_state.rejected_data = {}
        st.session_state.merged_tasks_values = {}
        st.session_state.merged_data = {}
        st.session_state.version += 1
        st.session_state.checklist = {
            "Tasks": False,
            "Assignees": False,
            "DueDates": False,
            "Sprints": False,
        }
        st.session_state.imported_files = {}
        st.session_state.blob_files = {}
        st.session_state.selected_files = []
        st.rerun()

        # Inject JavaScript to scroll to the top
        st.markdown(
            """
            <script>
                window.scrollTo(0, 0);
            </script>
            """,
            unsafe_allow_html=True,
        )
