import streamlit as st
from db import init_db, get_config, save_config  # Update import
from azure.storage.blob import BlobServiceClient

def fetch_container_names(connection_string):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        containers = blob_service_client.list_containers()
        return [container.name for container in containers]
    except Exception as e:
        st.error(f"Error fetching containers: {e}")
        return []

def show_settings():
    st.markdown("<h1 style='text-align: center;'>⚙️ Settings</h1>", unsafe_allow_html=True)
    st.subheader("Azure Blob Configuration")

    conn, c = init_db()
    config = get_config(c)
    connection_string = config[0] if config else ""
    container_name = config[1] if config else ""

    connection_string = st.text_input("Enter your connection string", value=connection_string, type="password")

    container_names = fetch_container_names(connection_string) if connection_string else []
    if container_names:
        container_name = st.selectbox("Select Blob Container", container_names, index=(container_names.index(container_name) if container_name in container_names else 0))

    if st.button("Save Configuration", disabled=not container_name):
        save_config(c, conn, connection_string, container_name)
        st.session_state.connection_string = connection_string
        st.session_state.container_name = container_name
        st.success("Configuration saved successfully.")
