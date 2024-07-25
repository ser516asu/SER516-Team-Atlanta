import getpass
import json
from datetime import datetime, timedelta
from taigaApi.authenticate import authenticate
from taigaApi.project.getProjectBySlug import get_project_by_slug
from taigaApi.project.getProjectTaskStatusName import (
    get_project_task_status_name)
from taigaApi.userStory.getUserStory import get_user_story
from taigaApi.task.getTaskHistory import get_task_history, get_task_cycle_times
from taigaApi.task.getTasks import get_closed_tasks
# test for branch change

# Function to format datetime objects for JSON serialization
def default_encoder(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d")


# Function to get Taiga authentication token from user input
def get_auth_token():
    taiga_username = input("Enter your Taiga username: ")
    taiga_password = getpass.getpass("Enter your Taiga password: ")
    auth_token = authenticate(taiga_username, taiga_password)
    return auth_token


# Function to get project slug and display project details
def get_project_slug(auth_token):
    project_slug = input("Enter the Taiga project slug: ")
    project_info = get_project_by_slug(project_slug, auth_token)
    task_status_name = get_project_task_status_name
    (project_info["id"], auth_token)

    project_details = {
        "name": project_info["name"],
        "team_members":
        [member["full_name"] for member in project_info.get("members", [])],
        "taskboard_column": [status["name"] for status in task_status_name],
    }

    print("\n***********************************\n")
    print(json.dumps(project_details, indent=2))
    print("\n***********************************\n")
    return project_info["id"]


# Function to get open user stories in the project
def get_open_user_stories(project_id, auth_token):
    user_stories = get_user_story(project_id, auth_token)
    open_user_stories = [story for story in user_stories if
                         not story["is_closed"]]

    project_details = {
        "open_user_stories": [
            {
                "name": story["subject"],
                "description": story.get("description", "")
            }
            for story in open_user_stories
        ]
    }
    print("\n***********************************\n")
    print(json.dumps(project_details, indent=2))
    print("\n***********************************\n")


# Function to calculate and display closed tasks per week
def get_closed_tasks_per_week(project_id, auth_token):
    closed_tasks = get_closed_tasks(project_id, auth_token)
    task_groups = []

    for task in closed_tasks:
        finished_date = datetime.fromisoformat(task["finished_date"])
        week_start = finished_date - timedelta(days=finished_date.weekday())
        week_start = week_start.replace(hour=0, minute=0,
                                        second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59,
                                          seconds=59, microseconds=999999)

        existing_week = next((week for week in task_groups
                              if week["weekEnding"] == week_end), None)

        if existing_week:
            existing_week["closedTasks"] += 1
        else:
            task_groups.append({"weekEnding": week_end, "closedTasks": 1})

    print("\n***********************************\n")
    print(json.dumps(task_groups, indent=2, default=default_encoder))
    print("\n***********************************\n")


# Function to calculate and display average lead time
def get_lead_time(project_id, auth_token):
    tasks = get_closed_tasks(project_id, auth_token)
    lead_time = 0
    closed_tasks = 0
    for task in tasks:
        created_date = datetime.fromisoformat(task["created_date"])
        finished_date = datetime.fromisoformat(task['finished_date'])
        lead_time += (finished_date - created_date).days
        closed_tasks += 1

    avg_lead_time = round((lead_time / closed_tasks), 2)
    print("\n***********************************\n")
    print("Average Lead Time: ", avg_lead_time)
    print("\n***********************************\n")


# Function to calculate and display average cycle time
def get_cycle_time(project_id, auth_token):
    tasks = get_closed_tasks(project_id, auth_token)
    cycle_time, closed_task = get_task_history(tasks, auth_token)
    avg_cycle_time = round((cycle_time / closed_task), 2)

    print("\n***********************************\n")
    print("Average Cycle Time: ", avg_cycle_time)
    print("\n***********************************\n")


def get_cycle_times(project_id, auth_token):
    """Calculates and prints average cycle time for each task
    with start and end dates.

    Args:
        project_id: The ID of the project.
        auth_token: The Taiga API authorization token.
    """

    tasks = get_closed_tasks(project_id, auth_token)
    task_data = get_task_cycle_times(tasks, auth_token)

    print("\n***********************************\n")

    for cycle_time, start_date, end_date in task_data:
        print(f"Task Cycle Time: {cycle_time} days")
        print(f"Start Date: {start_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"End Date: {end_date.strftime('%Y-%m-%d %H:%M')}\n")

    print("\n***********************************\n")


# Function to handle user actions and provide options
def handle_user_action(project_id, auth_token):
    while True:
        action = input(
            "What do you want to do next?\n"
            "(1) Show open user stories\n"
            "(2) Calculate number of task closed per week metric\n"
            "(3) Calculate average lead time\n"
            "(4) Calculate average cycle time\n"
            "(5) Calculate cycle time for each task\n"
            "(6) Exit\n"
            "Enter action: "
        )
        if action == "1":
            print("\nGetting list of all open user stories...")
            get_open_user_stories(project_id, auth_token)

        elif action == "2":
            print("\nCalculating throughput metric...")
            get_closed_tasks_per_week(project_id, auth_token)

        elif action == "3":
            print("\nCalculating average lead time...")
            get_lead_time(project_id, auth_token)

        elif action == "4":
            print("\nCalculating average cycle time...")
            get_cycle_time(project_id, auth_token)

        elif action == "5":
            print("\nCalculating cycle time for each task...")
            get_cycle_times(project_id, auth_token)

        elif action == "6":
            print("\nExiting...")
            break
        else:
            print("\nInvalid choice. Please enter a valid option.")


# Main function to execute the program
def main():
    auth_token = get_auth_token()
    if auth_token:
        print("Authentication successful.")
        project_id = get_project_slug(auth_token)

        if project_id:
            handle_user_action(project_id, auth_token)


if __name__ == "__main__":
    main()
