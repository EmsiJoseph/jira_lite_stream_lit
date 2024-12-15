
from azure.storage.blob import BlobServiceClient
from utils import show_error, show_success

def upload_to_azure_blob(merged_data, connection_string, container_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob="merged_data.csv")
        blob_client.upload_blob(merged_data.to_csv(index=False), overwrite=True)
        show_success("Data uploaded to Azure Blob successfully.")
    except Exception as e:
        show_error(f"Error uploading to Azure Blob: {e}")