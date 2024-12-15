
import streamlit as st

def save_to_device(merged_data):
    st.download_button(
        label="Download Merged Data",
        data=merged_data.to_csv(index=False),
        file_name="merged_data.csv",
        mime="text/csv",
    )