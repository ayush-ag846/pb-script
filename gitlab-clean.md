## This is python script to clean stale branches from repo
### Run with initial hardcoded value of project id and group id

```
import requests
from datetime import datetime, timedelta

# Configuration
GITLAB_URL = "https://gitlab.example.com"
PRIVATE_TOKEN = "your_personal_access_token"
GROUP_ID = "your_group_id"
DRY_RUN = True  # Set to False to actually delete branches

headers = {
    "Private-Token": PRIVATE_TOKEN
}

def get_projects(group_id):
    projects = []
    url = f"{GITLAB_URL}/api/v4/groups/{group_id}/projects"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        projects = response.json()
    return projects

def get_branches(project_id):
    branches = []
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/branches"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        branches = response.json()
    return branches

def delete_branch(project_id, branch_name):
    if DRY_RUN:
        print(f"DRY RUN: Would delete branch {branch_name} in project {project_id}")
        return True
    else:
        url = f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/branches/{branch_name}"
        response = requests.delete(url, headers=headers)
        return response.status_code == 204

def is_branch_stale(branch):
    # Define your criteria for staleness here
    # Example: no commits in the last 6 months
    last_commit_date = datetime.strptime(branch['commit']['committed_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
    return last_commit_date < datetime.now() - timedelta(days=180)

def main():
    projects = get_projects(GROUP_ID)
    for project in projects:
        project_id = project['id']
        branches = get_branches(project_id)
        for branch in branches:
            if branch['name'] not in ["main", "master"] and is_branch_stale(branch):
                if delete_branch(project_id, branch['name']):
                    print(f"Deleted branch {branch['name']} in project {project['name']}")

if __name__ == "__main__":
    main()
```

**For review code in dry run set 'DRY_RUN = True'**
