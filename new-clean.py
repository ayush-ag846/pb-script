import requests
from datetime import datetime, timedelta

# Configuration
GITLAB_URL = "https://gitlab.example.com"
PRIVATE_TOKEN = "your_personal_access_token"
GROUP_ID = "your_group_id"
DRY_RUN = True  # Set to False to actually delete branches
TIME_LIMIT_DAYS = 180

headers = {
    "Private-Token": PRIVATE_TOKEN
}

def get_projects(group_id):
    url = f"{GITLAB_URL}/api/v4/groups/{group_id}/projects"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch projects: {response.status_code}")
        return []

def get_branches(project_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/branches"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch branches for project {project_id}: {response.status_code}")
        return []

def delete_branch(project_id, branch_name):
    if DRY_RUN:
        print(f"DRY RUN: Would delete branch {branch_name} in project {project_id}")
        return True
    else:
        url = f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/branches/{branch_name}"
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"Deleted branch {branch_name} in project {project_id}")
            return True
        else:
            print(f"Failed to delete branch {branch_name} in project {project_id}: {response.status_code}")
            return False

def is_branch_stale(branch):
    last_commit_date = datetime.strptime(branch['commit']['committed_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
    return last_commit_date < datetime.now() - timedelta(days=TIME_LIMIT_DAYS)

def main():
    projects = get_projects(GROUP_ID)
    for project in projects:
        project_id = project['id']
        project_name = project['name']
        branches = get_branches(project_id)
        for branch in branches:
            branch_name = branch['name']
            if branch_name not in ["main", "master"] and is_branch_stale(branch):
                delete_branch(project_id, branch_name)

if __name__ == "__main__":
    main()
