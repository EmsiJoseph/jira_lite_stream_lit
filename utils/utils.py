import pandas as pd
import streamlit as st
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import tempfile
import os

"""
    Convert empty csv values from NaN to None
"""


def convert_nan_to_none_in_dict(input_dict: dict):
    for key, value in input_dict.items():
        if pd.isna(value):  # Check if the value is NaN
            input_dict[key] = None  # Replace NaN with None


def show_error(message: str):
    st.error(message, icon="❌")


def show_success(message: str):
    st.success(message, icon="✅")


def get_file_name(base_name, version, extension="csv"):
    return f"{base_name}_v{version}.{extension}"


def upload_to_azure_blob(
    data,
    connection_string,
    container_name,
    version,
    file_type="csv",
    file_name="merged_data",
):
    try:
        file_name = get_file_name(file_name, version, extension=file_type)
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=file_name
        )

        if file_type == "csv":
            blob_client.upload_blob(data.to_csv(index=False), overwrite=True)
        elif file_type == "xlsx":
            with pd.ExcelWriter(file_name) as writer:
                for sheet_name, df in data.items():
                    if df is not None and not df.empty:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            with open(file_name, "rb") as f:
                blob_client.upload_blob(f, overwrite=True)

        show_success(f"Data uploaded to Azure Blob successfully as {file_name}.")
    except Exception as e:
        show_error(f"Error uploading to Azure Blob: {e}")


def save_to_device(merged_data, version, label, file_name):
    file_name = get_file_name(file_name, version)
    st.download_button(
        label=label,
        data=merged_data.to_csv(index=False),
        file_name=file_name,
        mime="text/csv",
    )


def create_excel_from_dict(data_dict, version, file_name):
    temp_dir = tempfile.gettempdir()
    file_name = get_file_name(file_name, version, extension="xlsx")
    file_path = os.path.join(temp_dir, file_name)
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, df in data_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return file_path


def check_keys_exists_in_dict(keys: list, dict: dict):
    boolean_value = []
    for key in keys:
        if key in dict:
            boolean_value.append(True)
        else:
            boolean_value.append(True)

    return boolean_value


def require_a_value_in_dict(dict: dict, key_of_required_val):
    if key_of_required_val in dict and not dict.get(key_of_required_val):
        return False

    return True


def format_friendly_date(date_str):
    if pd.isna(date_str) or not date_str:
        return "No Due Date"
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime("%B %d, %Y")
        except ValueError:
            continue
    return "Invalid Date Format"
