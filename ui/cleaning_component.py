import pandas as pd
from handlers.csv_parsing_handlers import handle_parse_csv_to_dict
from handlers.handlers import (
    handle_parsed_csv_data_cleaning,
    handle_saving_cleaned_and_rejected_data,
)
import const
from classes.task import Task
from classes.task_list import TaskList
from classes.due_date import DueDate
from classes.assignee import Assignee
from classes.sprint import Sprint


def clean_data(uploaded_files, task_list: TaskList):
    task = Task()
    due_date = DueDate()
    assignee = Assignee()
    sprint = Sprint()

    file_names = ["Tasks", "Assignees", "DueDates", "Sprints"]

    cleaned_data = {key: pd.DataFrame() for key in file_names}
    rejected_data = {key: pd.DataFrame() for key in file_names}

    def process_file(file_name, parsed_data, entity, rejected_const):
        clean, rejected = handle_parsed_csv_data_cleaning(parsed_data)
        handle_saving_cleaned_and_rejected_data(
            {"cleaned": clean, "rejected": rejected}, entity, task_list, rejected_const
        )
        cleaned_data[file_name.replace(".csv", "")] = pd.DataFrame(clean)
        rejected_data[file_name.replace(".csv", "")] = pd.DataFrame(rejected)

    for file_name, file in uploaded_files.items():
        if file:
            file_content = file.getvalue()
            parsed_data = handle_parse_csv_to_dict(file_content, "TaskID")
            if file_name == "Tasks.csv":
                process_file(file_name, parsed_data, task, const.REJECTED_TASKS)
            elif file_name == "Assignees.csv":
                process_file(file_name, parsed_data, assignee, const.REJECTED_ASSIGNEES)
            elif file_name == "DueDates.csv":
                process_file(file_name, parsed_data, due_date, const.REJECTED_DUE_DATES)
            elif file_name == "Sprints.csv":
                process_file(file_name, parsed_data, sprint, const.REJECTED_SPRINTS)

    merged_tasks_values = task_list.get_tasks.values()

    return cleaned_data, rejected_data, merged_tasks_values
