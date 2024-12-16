import pandas as pd
from typing import Union
from clean_up_constraints import (
    implement_task_cleanup_constraints,
    require_one_value_except_task_id,
    implement_assignees_cleanup_constraints,
    check_two_entries_of_same_task_id,
    single_entry_check,
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

    clean_assignees = {}  # Dicts within a dict

    for id, entry in parsed_data.items():
        # This is for data which originally do not have TaskID
        if id == no_task_id:
            rejected.extend(entry)
            continue

        # Specifically check for TWO equal entries
        # Regardless of file
        has_two_entries_of_equal_value = check_two_entries_of_same_task_id(entry, clean)
        if has_two_entries_of_equal_value:
            continue

        # Assignees Cleanup
        is_assignees = handle_assignees_csv_parsing(entry, rejected, clean_assignees, id)
        if is_assignees:
            continue  # Cleanup below are no longer for Assignees

        # Every other CSV Cleanup
        has_single_entry = single_entry_check(entry, clean, rejected)
        if has_single_entry:
            continue

        # Add all entries to the rejected list and remove the task from the dictionary
        rejected.extend(entry)

    if clean_assignees:
        clean = list(clean_assignees.values())  # Convert dict_values to list

    return clean, rejected


def handle_assignees_csv_parsing(
    dict_list: list, rejected: list, clean_assignees: dict, task_id
):
    first_dict = dict_list[0]
    if assignee_name_role_col in first_dict:
        for dict_value in dict_list:
            # Require 1 Value
            has_min_of_one_value = require_one_value_except_task_id(dict_value)
            if not has_min_of_one_value:
                rejected.append(dict_value)
                continue

            # Has AssigneeName
            has_assignee_name = implement_assignees_cleanup_constraints(dict_value)
            if not has_assignee_name:
                rejected.append(dict_value)
                continue

            # Duplicate names but different roles is VALID.
            assignee_role = dict_value.get(assignee_name_role_col)
            if task_id not in clean_assignees:
                # Handle first occurrence
                clean_assignees[task_id] = {**dict_value}
            else:
                # Append another assignee role occurence
                clean_assignees[task_id][assignee_name_role_col] += "," + assignee_role
        
        return True
    
    return False


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

            # Append to the Task List
            task_list.add_or_update_task(task_properties)
        except Exception as e:
            print(e)


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

    # MC implemented his own Excel Export
    # 02 Handle Transfer of rejected data to a separate excel file
    # if rejected:
    #     # Convert the rejected arr of dict to dataframes
    #     rejected_df = pd.DataFrame(rejected)

    # # Save the DataFrame to a temporary excel file which you can call anytime
    # rejected_df.to_excel(temp_excel_file, index=False)
