import streamlit as st
from azure.storage.blob import BlobServiceClient
from io import StringIO
from dotenv import load_dotenv
from db import init_db, get_config  # Update import

# Load environment variables from .env file
load_dotenv()

# Load configuration from SQLite
conn, c = init_db()
config = get_config(c)
st.session_state.connection_string = config[0] if config else ""
st.session_state.container_name = config[1] if config else ""


def initialize_session_state():
    if "imported_files" not in st.session_state:
        st.session_state.imported_files = {}
    if "blob_files" not in st.session_state:
        st.session_state.blob_files = {}
    if "selected_files" not in st.session_state:
        st.session_state.selected_files = []
    if "checklist" not in st.session_state:
        st.session_state.checklist = {
            "Tasks": False,
            "Assignees": False,
            "DueDates": False,
            "Sprints": False,
        }


def handle_file_upload(imported_files):
    for file in imported_files:
        st.session_state.imported_files[file.name] = StringIO(
            file.getvalue().decode("utf-8")
        )
        if "Tasks.csv" in file.name:
            st.session_state.checklist["Tasks"] = True
        elif "Assignees.csv" in file.name:
            st.session_state.checklist["Assignees"] = True
        elif "DueDates.csv" in file.name:
            st.session_state.checklist["DueDates"] = True
        elif "Sprints.csv" in file.name:
            st.session_state.checklist["Sprints"] = True


def fetch_blob_files():
    try:
        with st.spinner("Fetching files from Azure Blob..."):
            blob_service_client = BlobServiceClient.from_connection_string(
                st.session_state.connection_string
            )
            container_client = blob_service_client.get_container_client(
                st.session_state.container_name
            )
            blobs_list = container_client.list_blobs()
            st.session_state.blob_files = {
                blob.name: None for blob in blobs_list if blob.name.endswith(".csv")
            }
            st.success("Files fetched successfully from Azure Blob.")
    except Exception as e:
        st.error(f"Error fetching files from Azure Blob: {e}")


def download_selected_files():
    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            st.session_state.connection_string
        )
        container_client = blob_service_client.get_container_client(
            st.session_state.container_name
        )
        for file_name in st.session_state.selected_files:
            blob_client = container_client.get_blob_client(file_name)
            blob_data = blob_client.download_blob().readall()
            st.session_state.blob_files[file_name] = StringIO(blob_data.decode("utf-8"))
            if "Tasks.csv" in file_name:
                st.session_state.checklist["Tasks"] = True
            elif "Assignees.csv" in file_name:
                st.session_state.checklist["Assignees"] = True
            elif "DueDates.csv" in file_name:
                st.session_state.checklist["DueDates"] = True
            elif "Sprints.csv" in file_name:
                st.session_state.checklist["Sprints"] = True
    except Exception as e:
        st.error(f"Error downloading selected files from Azure Blob: {e}")


def upload_files():
    st.subheader("Option 1: Import from Device")
    st.write(
        "Upload all necessary files (Tasks.csv, Assignees.csv, DueDates.csv, Sprints.csv)."
    )

    initialize_session_state()

    imported_files = st.file_uploader(
        "Upload CSV files",
        type=["csv"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if imported_files:
        handle_file_upload(imported_files)

    st.subheader("Option 2: Download from Azure Blob")

    if not st.session_state.connection_string or not st.session_state.container_name:
        st.write("Setup your connection in settings first.")
        if st.button("Go to Settings"):
            st.session_state.page = "Settings"
            st.rerun()
    else:
        st.write("Connect to Azure Blob to import files.")
        if st.button("Fetch Files"):
            fetch_blob_files()

        if st.session_state.blob_files:
            selected_files = st.multiselect(
                "Select files to download",
                list(st.session_state.blob_files.keys()),
                default=st.session_state.selected_files,
            )
            if selected_files != st.session_state.selected_files:
                st.session_state.selected_files = selected_files
                st.rerun()

        if st.session_state.selected_files:
            download_selected_files()

    combined_files = st.session_state.imported_files.copy()
    for file_name, file in st.session_state.blob_files.items():
        if file_name in combined_files:
            if file is not None:
                combined_files[file_name] = StringIO(
                    combined_files[file_name].getvalue() + "\n" + file.getvalue()
                )
        else:
            combined_files[file_name] = file

    st.write("Files needed:")
    for key, value in st.session_state.checklist.items():
        st.checkbox(key, value=value, disabled=True)

    all_files_ready = all(st.session_state.checklist.values())

    return combined_files, all_files_ready
