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
        return assignee_name_has_val  # False

    # 02 AssigneeName + Role OR AssigneeName ONLY is acceptable
    if assignee_name_role_col in assignee:
        left, sep, right = assignee[assignee_name_role_col].partition("-")
        has_name = bool(left.strip())

        if not has_name:
            return False

    return True


def check_two_entries_of_same_task_id(entry: list, clean: list):
    if len(entry) == 2:
        # Both are equal but both not empty
        if entry[0] and entry[0] == entry[1]:
            clean.append(entry[0])
            return True
    
    return False
            
def single_entry_check(entry: list, clean: list, rejected: list):
    # Every other CSV Cleanup
    if len(entry) == 1:
        single_entry = entry[0]
        # 01 Tasks Cleanup Constraints
        is_passed_task_constraints = implement_task_cleanup_constraints(
            single_entry
        )
        if not is_passed_task_constraints:
            rejected.extend(entry)
            return True

        # 02 General Constraint: Require at least 1 value except for TaskID
        has_min_of_one_value = require_one_value_except_task_id(single_entry)
        if not has_min_of_one_value:
            rejected.extend(entry)
            return True

        clean.append(entry[0])
        return True
    
    return False