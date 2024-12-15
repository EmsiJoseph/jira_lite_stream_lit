from typing import Optional
from datetime import datetime
import pandas as pd

class DueDate:
    def __init__(self):
        self.__task_id: Optional[int] = None
        self.__due_date: Optional[str] = None
        self.__priority: Optional[str] = None

    # Getters
    @property
    def get_task_id(self):
        return self.__task_id

    @property
    def get_due_date(self):
        return self.__due_date

    @property
    def get_priority(self):
        return self.__priority

    @property
    def get_all(self):
        return {
            "task_id": self.get_task_id,
            "due_date": self.get_due_date,
            "priority": self.get_priority,
        }

    # Setters
    @get_task_id.setter
    def set_task_id(self, value):
        if not isinstance(value, int):
            raise Exception("Task ID should be an integer.")
        self.__task_id = value

    @get_due_date.setter
    def set_due_date(self, value):
        # Handle NaN Parsed Value from pandas
        if pd.isna(value):
            self.__due_date = None
            return
        if value is not None and not isinstance(value, str):
            raise Exception("Due Date should be str.")
        self.__due_date = value

    @get_priority.setter
    def set_priority(self, value):
        # Handle NaN Parsed Value from pandas
        if pd.isna(value):
            self.__priority = None
            return
        if value is not None and not isinstance(value, str):
            raise Exception("Priority should be a string.")
        self.__priority = value

    # Methods
    def set_all_values(self, due_date: dict):
        self.set_task_id = due_date["TaskID"]
        self.set_due_date = due_date["DueDate"]
        self.set_priority = due_date["Priority"]
