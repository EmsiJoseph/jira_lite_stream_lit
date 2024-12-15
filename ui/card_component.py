import streamlit as st
from utils.utils import format_friendly_date
import random

def truncate_text(text, max_length=100):
    return text[:max_length] + "..." if len(text) > max_length else text

def format_assignees(assignees, max_length=100):
    if assignees == "No assignee/s":
        return assignees
    assignee_list = assignees.split(",")
    formatted_assignees = ", ".join(
        [
            f"{assignee.split('-')[0]} ({assignee.split('-')[1] if len(assignee.split('-')) > 1 else 'No Role'})"
            for assignee in assignee_list
        ]
    )
    return truncate_text(formatted_assignees, max_length) + ", and more" if len(formatted_assignees) > max_length else formatted_assignees

def get_sprint_color(sprint_name):
    if sprint_name == "No Sprint":
        return "#808080"
    random.seed(int(sprint_name.split("_")[1]))
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def format_sprint_name(sprint_name):
    return sprint_name.replace("_", " ") if sprint_name != "No Sprint" else sprint_name

def get_priority_color(priority):
    priority_colors = {"High": "#FF0000", "Medium": "#FFA500", "Low": "#008000"}
    return priority_colors.get(priority, "#1E1E1E")

def get_text_color(bg_color):
    bg_color = bg_color.lstrip("#")
    r, g, b = int(bg_color[0:2], 16), int(bg_color[2:4], 16), int(bg_color[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "black" if brightness > 128 else "white"

def display_task_card(task):
    task_name = task["TaskName"] if task["TaskName"] else "No Task Name"
    description = task["Description"] if task["Description"] else "No description"
    assignee = task["AssigneeName-Role"] if task["AssigneeName-Role"] else "No assignee/s"
    sprint = task["SprintName"] if task["SprintName"] else "No Sprint"
    priority = task["Priority"] if task["Priority"] else "No Priority"
    formatted_assignees = format_assignees(assignee)
    sprint_color = get_sprint_color(sprint)
    sprint_text_color = get_text_color(sprint_color)
    formatted_sprint_name = format_sprint_name(sprint)
    sprint_tag = f"<span style='background-color: {sprint_color}; color: {sprint_text_color}; padding: 2px 5px; border-radius: 3px; margin-top: 5px;'>{formatted_sprint_name}</span>"
    priority_color = get_priority_color(priority)
    priority_text_color = get_text_color(priority_color)
    priority_tag = f"<span style='background-color: {priority_color}; color: {priority_text_color}; padding: 2px 5px; border-radius: 3px; margin-top: 5px;'>{priority}</span>"
    st.markdown(
        f"""
        <div style="border-radius: 5px; padding: 10px; margin-bottom: 10px; font-size: 12px; background-color: #1c2333; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);">
            <h4 style="margin: 0;">{task_name}</h4>
            <p style="margin: 0;">{truncate_text(description)}</p>
            <p style="margin: 0;"><strong>Assigned to</strong> {formatted_assignees}</p>
            <p style="margin: 0;"><strong>Due Date:</strong> {format_friendly_date(task['DueDate'])}</p>
            <p/>
            <p style="margin: 0;"><strong>{sprint_tag} {priority_tag}<strong/></p>
            <br/>
            <p style="margin: 0; color: gray;">{task['TaskID']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
