NO_TASK_ID_PLACEHOLDER = 0

TASKS_COLUMNS = [
    "TaskID",
    "TaskName",
    "Description",
    "Status"
]
TASK_ID = TASKS_COLUMNS[0]
ASSIGNEES_COLUMNS = [
    TASK_ID,
    "AssigneeName",
    "Role",
    "AssigneeName-Role"
]
DUE_DATES_COLUMNS = [
    TASKS_COLUMNS[0],
    "DueDate",
    "Priority"
]
SPRINTS_COLUMNS = [
    TASKS_COLUMNS[0],
    "SprintID",
    "SprintName",
    "SprintGoal"
]

FINAL_TASK_LIST = "final_task_list.xlsx"
REJECTED_TASKS = 'rejected_tasks.xlsx'
REJECTED_DUE_DATES = 'rejected_due_dates.xlsx'
REJECTED_ASSIGNEES = 'rejected_assignees.xlsx'
REJECTED_SPRINTS = 'rejected_sprints.xlsx'


