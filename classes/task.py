from typing import Optional
import pandas as pd
from classes.assignee import Assignee
from classes.due_date import DueDate

class Task(DueDate, Assignee):
    def __init__(self):
        super().__init__()
        self.__task_id: Optional[int] = None
        self.__task_name: Optional[str] = None
        self.__task_description: Optional[str] = None
        self.__task_status: Optional[str] = None

    # Getters
    @property
    def get_task_id(self):
        return self.__task_id

    @property
    def get_task_name(self):
        return self.__task_name

    @property
    def get_task_description(self):
        return self.__task_description

    @property
    def get_task_status(self):
        return self.__task_status

    @property
    def get_all(self):
        return {
            "task_id": self.get_task_id,
            "task_name": self.get_task_name,
            "task_description": self.get_task_description,
            "task_status": self.get_task_status,
        }

    # Setters
    @get_task_id.setter
    def set_task_id(self, value):
        if not isinstance(value, int):
            raise Exception("Id should be int.")
        self.__task_id = value

    @get_task_name.setter
    def set_task_name(self, value):
        # Handle NaN Parsed Value from pandas
        if pd.isna(value):
            self.__task_name = None
            return
        if not value or not isinstance(value, str):
            raise Exception("Task name should not be empty and should be a string.")
        self.__task_name = value

    @get_task_description.setter
    def set_task_description(self, value):
        # Handle NaN Parsed Value from pandas
        if pd.isna(value):
            self.__task_description = None
            return
        if value is not None and not isinstance(value, str):
            raise Exception("Description should be a string.")
        self.__task_description = value

    @get_task_status.setter
    def set_task_status(self, value):
        # Handle NaN Parsed Value from pandas
        if pd.isna(value):
            self.__task_status = None
            return
        if value is not None and not isinstance(value, str):
            raise Exception("Status should be a string.")
        self.__task_status = value
        

    # Methods
    def set_all_values(self, task: dict):
        try:
            self.set_task_id = task["TaskID"]
            self.set_task_name = task["TaskName"]
            self.set_task_description = task["Description"]
            self.set_task_status = task["Status"]
        except Exception as e:
            raise Exception(e)
