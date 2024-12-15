from const import TASKS_COLUMNS, ASSIGNEES_COLUMNS
from utils.utils import require_a_value_in_dict

task_col = TASKS_COLUMNS
task_id_col = task_col[0]
task_name_col = task_col[1]

assignee_col = ASSIGNEES_COLUMNS
assignee_name_col = assignee_col[1]
role_col = assignee_col[2]
assignee_name_role_col = assignee_col[3]


def implement_task_cleanup_constraints(task: dict):
    # Require TaskID to have value
    task_id_has_val = require_a_value_in_dict(task, task_id_col)
    if not task_id_has_val:
        return task_id_has_val

    # Require TaskName to have value
    task_name_has_val = require_a_value_in_dict(task, task_name_col)
    if not task_name_has_val:
        return task_name_has_val

    return True


def require_one_value_except_task_id(record: dict, task_id_col: str = "TaskID") -> bool:
    for key, value in record.items():
        if key != task_id_col and value:  # Exclude TaskID and check for value
            return True
    return False


def implement_assignees_cleanup_constraints(assignee: dict):
    # 01 Require AssigneeName-Role to have value
    assignee_name_has_val = require_a_value_in_dict(assignee, assignee_name_role_col)
    if not assignee_name_has_val:
        return assignee_name_has_val
    
    # 02 AssigneeName + Role OR AssigneeName ONLY is acceptable
    if assignee_name_role_col in assignee:
        left, right = assignee[assignee_name_role_col].split("-", 1) 
        has_name = bool(left.strip())
        
        if not has_name:
            return False
    
    return True


# def merge_assignee_name_and_role_col(assignee: dict):
#     has_passed = implement_assignees_cleanup_constraints(assignee)
#     if not has_passed:
#         return has_passed

#     # Begin the merge logic
#     if assignee_name_col in assignee and role_col in assignee:
