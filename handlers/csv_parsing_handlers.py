import const
import pandas as pd
from collections import defaultdict
from io import StringIO

no_task_id = const.NO_TASK_ID_PLACEHOLDER

assignee_cols = const.ASSIGNEES_COLUMNS
assignee_name_col = assignee_cols[1]
role_col = assignee_cols[2]
assignee_name_role_col = assignee_cols[3]

sprint_cols = const.SPRINTS_COLUMNS
sprint_id_col = sprint_cols[1]


# !!!Currently not handling null / nan value from given TaskID Key
def handle_parse_csv_to_dict(file_content: str, key: str):
    if not file_content:
        raise ValueError("No file content was given.")
    parent_dict = {}

    try:
        df = pd.read_csv(StringIO(file_content))
        # Replace NaN values with None
        df = df.where(pd.notnull(df), None)

        # Merge AssigneeName and Role Cols if both exists
        handle_merge_assignee_name_and_role_col(df)

        # Delete SprintID Col
        handle_remove_sprint_id_col(df)
    except FileNotFoundError:
        raise Exception("File not found. Please check the file path.")

    # Initialize a default dict with lists
    parent_dict = defaultdict(list)

    # Iterate over the DataFrame rows
    for _, row in df.iterrows():
        # Convert the entire row into a dictionary and append it to the list for the corresponding ID
        parent_dict[row[key]].append(row.to_dict())

    # Convert defaultdict back to a regular dictionary
    parent_dict = dict(parent_dict)

    return parent_dict


def combine_assignee_and_role(row, assignee_name_col, role_col):
    if row[assignee_name_col] and row[role_col]:
        return f"{row[assignee_name_col]}-{row[role_col]}"
    elif row[assignee_name_col]:
        return f"{row[assignee_name_col]}"
    elif row[role_col]:
        return f"-{row[role_col]}"
    else:
        return None


def handle_merge_assignee_name_and_role_col(df: pd.DataFrame):
    # Combine 'AssigneeName' and 'Role' columns, handling None values
    if assignee_name_col in df.columns and role_col in df.columns:
        df[assignee_name_role_col] = df.apply(
            lambda row: combine_assignee_and_role(row, assignee_name_col, role_col),
            axis=1,
        )
        # Drop the original columns
        df.drop([assignee_name_col, role_col], axis=1, inplace=True)


def handle_remove_sprint_id_col(df: pd.DataFrame):
    if sprint_id_col in df:
        # Drop the SprintID col for Sprint CSV
        df.drop([sprint_id_col], axis=1, inplace=True)
