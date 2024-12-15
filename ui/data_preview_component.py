import streamlit as st
import pandas as pd

def preview_data(uploaded_files):
    uploaded_files = {name: file for name, file in uploaded_files.items() if file}

    if uploaded_files:
        st.write("Preview uploaded data and check for any issues. If everything looks good, proceed to the next step.")
        tabs = st.tabs([file_name.replace(".csv", "") for file_name in uploaded_files.keys()])
        for tab, (file_name, file) in zip(tabs, uploaded_files.items()):
            with tab:
                st.subheader(file_name.replace(".csv", ""))
                df = pd.read_csv(file)
                st.dataframe(df, use_container_width=True, hide_index=True)
