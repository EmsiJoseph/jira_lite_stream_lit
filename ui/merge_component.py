import pandas as pd
from utils.utils import show_error, show_success


def merge_data(cleaned_data):
    try:
        merged_data = pd.DataFrame()
        for file_name, df in cleaned_data.items():
            if not df.empty:
                merged_data = (
                    df
                    if merged_data.empty
                    else pd.merge(merged_data, df, how="outer", on="TaskID")
                )
        show_success("Data merged successfully.")
        return merged_data
    except Exception as e:
        show_error(f"Error merging data: {e}")
        return pd.DataFrame()
