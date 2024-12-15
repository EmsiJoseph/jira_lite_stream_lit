from typing import Optional
import pandas as pd

class Sprint:
    def __init__(self):
        self.__sprint_id: Optional[int] = None
        self.__task_id: Optional[int] = None
        self.__sprint_name: Optional[str] = None
        self.__sprint_goal: Optional[str] = None
        
    # Getters
    @property
    def get_sprint_id(self):
        return self.__sprint_id
    
    @property
    def get_task_id(self):
        return self.__task_id
    
    @property
    def get_sprint_name(self):
        return self.__sprint_name
    
    @property
    def get_sprint_goal(self):
        return self.__sprint_goal
    
    @property
    def get_all(self):
        return {
            "sprint_id": self.get_sprint_id,
            "task_id": self.get_task_id,
            "sprint_name": self.get_sprint_name,
            "sprint_goal": self.get_sprint_goal
        }
        
    # Setters
    @get_sprint_id.setter
    def set_sprint_id(self, value):
        if not isinstance(value, int):
            raise Exception("Sprint ID should be an integer.")
        self.__sprint_id = value

    @get_task_id.setter
    def set_task_id(self, value):
        if not isinstance(value, int):
            raise Exception("Task ID should be an integer.")
        self.__task_id = value

    @get_sprint_name.setter
    def set_sprint_name(self, value):
        # Handle NaN Parsed Value from pandas
        if pd.isna(value):
            self.__sprint_name = None
            return
        if value is not None and not isinstance(value, str):
            raise Exception("Sprint name should be a string.")
        self.__sprint_name = value

    @get_sprint_goal.setter
    def set_sprint_goal(self, value):
        # Handle NaN Parsed Value from pandas
        if pd.isna(value):
            self.__sprint_name = None
            return
        if value is not None and not isinstance(value, str):
            raise Exception("Sprint goal should be a string.")
        self.__sprint_goal = value
        
    # Methods
    def set_all_values(self, sprint: dict):
        self.set_sprint_id = sprint['SprintID']
        self.set_task_id = sprint['TaskID']
        self.set_sprint_name = sprint['SprintName']
        self.set_sprint_goal = sprint['SprintGoal']