from typing import Dict


class TaskList:
    def __init__(self):
        self.__tasks: Dict[str, dict] = {}

    # Getters
    @property
    def get_tasks(self):
        return self.__tasks

    # Methods
    def add_or_update_task(self, new_or_updated_task: dict):
        if not isinstance(new_or_updated_task, dict):
            raise TypeError("Only objects can be added.")

        # Ensure the 'task_id' key exists in the provided task dict
        if "task_id" not in new_or_updated_task:
            raise ValueError("The task must have a 'task_id' key.")

        task_id = new_or_updated_task["task_id"]

        # Check if the task already exists in task list
        if task_id in self.__tasks:
            # Update the existing task with new values from task
            if "task_name" in self.__tasks and self.__tasks[task_id]["task_name"]:
                self.__tasks[task_id].update(new_or_updated_task)
        else:
            # Add the new task
            self.__tasks[task_id] = {**new_or_updated_task}
