import pandas as pd
from typing import Union
from clean_up_constraints import (
    implement_task_cleanup_constraints,
    require_one_value_except_task_id,
    implement_assignees_cleanup_constraints,
)
from classes.task import Task
from classes.task_list import TaskList
from classes.due_date import DueDate
from classes.assignee import Assignee
from classes.sprint import Sprint
from .csv_parsing_handlers import handle_parse_csv_to_dict
from const import NO_TASK_ID_PLACEHOLDER, ASSIGNEES_COLUMNS

no_task_id = NO_TASK_ID_PLACEHOLDER
assignee_col = ASSIGNEES_COLUMNS
task_id_col = assignee_col[0]
assignee_name_role_col = assignee_col[3]


def handle_parsed_csv_data_cleaning(parsed_data: dict):
    clean = []
    rejected = []

    clean_assignees = {}  # Dict of dicts

    for id, entry in parsed_data.items():
        # This is for data which originally do not have TaskID
        if id == no_task_id:
            rejected.extend(entry)
            continue

        # Parsed Assignees Handling
        first_dict = entry[0]
        if assignee_name_role_col in first_dict:
            is_handling_success = handle_assignees_csv_parsing(
                entry, rejected, clean_assignees, id
            )
            if not is_handling_success:
                continue

        if len(entry) == 1:
            single_entry = entry[0]
            # 01 Tasks Cleanup Constraints
            is_passed_task_constraints = implement_task_cleanup_constraints(
                single_entry
            )
            if not is_passed_task_constraints:
                rejected.extend(entry)
                continue

            # 02 General Constraint: Require at least 1 value except for TaskID
            has_min_of_one_value = require_one_value_except_task_id(single_entry)
            if not has_min_of_one_value:
                rejected.extend(entry)
                continue

            clean.append(entry[0])
            continue

        if len(entry) == 2:
            # Both are equal but both not empty
            if entry[0] and entry[0] == entry[1]:
                clean.append(entry[0])
                continue

        # If the entries are not identical or there are more than two entries
        # Add all entries to the rejected list and remove the task from the dictionary
        rejected.extend(entry)

    if clean_assignees:
        # print(clean_assignees)
        # print(type(clean_assignees))
        clean = list(clean_assignees.values())  # Convert dict_values to list

    return clean, rejected


def handle_assignees_csv_parsing(
    dict_list: list, rejected: list, clean_assignees: dict, task_id
):
    for dict_value in dict_list:
        # 01 Assignees Cleanup Constraints
        has_assignee_name = implement_assignees_cleanup_constraints(dict_value)
        if not has_assignee_name:
            rejected.extend(dict_list)
            return False

        # Just append ebreting.
        # Duplicate names but different roles is VALID.
        # Add / Update Value of the dict
        # If this ID has not been added to clean_assignees, initialize it with the current assignee's role
        assignee_role = dict_value.get(assignee_name_role_col)
        if task_id not in clean_assignees:
            clean_assignees[task_id] = {
                task_id_col: task_id,
                assignee_name_role_col: assignee_role,
            }  # Initialize with the first assignee role
        else:
            clean_assignees[task_id][assignee_name_role_col] += (
                "," + assignee_role
            )  # Append new assignee role

    return True


def handle_add_or_update_task_list(
    data_transformer: Union[Task, DueDate, Assignee, Sprint],
    task_list: TaskList,
    clean_data: list,
):
    if not clean_data:
        return

    for entry in clean_data:
        try:
            # Set values to obj
            data_transformer.set_all_values(entry)
            task_properties = data_transformer.get_all

            # # Task object constraints
            # # 01. ID and Task Name is Required
            # if isinstance(data_transformer, Task):

            # Other

            # Append to the Task List
            task_list.add_or_update_task(task_properties)
        except Exception:
            None


def handle_saving_cleaned_and_rejected_data(
    parsed_dictionary: dict,
    data_transformer: Union[Task, DueDate, Assignee, Sprint],
    task_list: TaskList,
    temp_excel_file: str,
):
    if not parsed_dictionary:
        return

    # 01. Handle Adding New Task / Updating Task
    clean, rejected = handle_parsed_csv_data_cleaning(parsed_dictionary)
    if clean:
        handle_add_or_update_task_list(data_transformer, task_list, clean)

    # 02 Handle Transfer of rejected data to a separate excel file
    # if rejected:
    #     # Convert the rejected arr of dict to dataframes
    #     rejected_df = pd.DataFrame(rejected)

    # # Save the DataFrame to a temporary excel file which you can call anytime
    # rejected_df.to_excel(temp_excel_file, index=False)


# # MAAAAIINN
# # Consts
# task_id_col_name = const.TASKS_COLUMNS[0]

# # 01 Instantiate all classes
# task_list = TaskList()
# task = Task()
# due_date = DueDate()
# assignee = Assignee()
# sprint = Sprint()

# # 02 Ask the user for all the file paths
# # NOTE: One file is required ONLY. It should have TaskID
# task_path = ""
# due_date_path = ""
# assignee_path = "Assignees.csv"
# sprint_path = ""

# # 03 Parse each file
# parsed_task = {}
# parsed_due_date = {}
# parsed_assignee = {}
# parsed_sprint = {}

# # 04 Parse every CSV to DICT format
# try:
#     if task_path:
#         parsed_task = handle_parse_csv_to_dict(task_path, task_id_col_name)

#     if due_date_path:
#         parsed_due_date = handle_parse_csv_to_dict(due_date_path, task_id_col_name)

#     if assignee_path:
#         parsed_assignee = handle_parse_csv_to_dict(assignee_path, task_id_col_name)

# except Exception as e:
#     print(e)

# # 05 Clean the data, append/update TaskList, and create temp file for rejected data
# handle_saving_cleaned_and_rejected_data(
#     parsed_task, task, task_list, const.REJECTED_TASKS
# )
# handle_saving_cleaned_and_rejected_data(
#     parsed_due_date, due_date, task_list, const.REJECTED_DUE_DATES
# )
# handle_saving_cleaned_and_rejected_data(
#     parsed_assignee, assignee, task_list, const.REJECTED_ASSIGNEES
# )
# # temp_df = pd.DataFrame(task_list.get_tasks.items())
# # print(temp_df)
# print(task_list.get_tasks)
# # temp_task_df = pd.read_excel(const.REJECTED_DUE_DATES)
# # print(temp_task_df)
