from typing import Optional
import pandas as pd
from const import ASSIGNEES_COLUMNS

assignee_cols = ASSIGNEES_COLUMNS
task_id_col = assignee_cols[0]
assignee_name_role_col = assignee_cols[3]

class Assignee:
    def __init__(self):
        self.__task_id: Optional[int] = None
        self.__assignee_name_role: Optional[str] = None

    # Getters
    @property
    def get_task_id(self):
        return self.__task_id

    @property
    def get_assignee_name_role(self):
        return self.__assignee_name_role

    @property
    def get_all(self):
        return {
            "task_id": self.get_task_id,
            "assignee_name": self.get_assignee_name_role,
        }

    # Setters
    @get_task_id.setter
    def set_task_id(self, value):
        if not isinstance(value, int):
            raise Exception("Task ID should be an integer.")
        self.__task_id = value

    @get_assignee_name_role.setter
    def set_assignee_name_role(self, value):
        # Handle NaN Parsed Value from pandas
        if pd.isna(value):
            self.__assignee_name_role = None
            return
        if value is not None and not isinstance(value, str):
            raise Exception("AssigneeName-Role should be a string.")

        # Do not accept role only val
        name_part = value.split('-') 
        if not name_part:
            raise ValueError("AssigneeName is required though role is optional.")
        
        self.__assignee_name_role = value


    # Methods
    def set_all_values(self, assignee: dict):
        self.set_task_id = assignee[task_id_col]
        self.set_assignee_name_role = assignee[assignee_name_role_col]