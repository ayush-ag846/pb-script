import requests
from datetime import datetime, timedelta
from time import sleep

# Configuration
GITLAB_URL = "https://gitlab.example.com"
PRIVATE_TOKEN = "your_personal_access_token"
GROUP_ID = "12345"  # Replace with your actual group ID
DRY_RUN = True  # Set to False to actually delete branches
TIME_LIMIT_DAYS = 180
REQUEST_TIMEOUT = 10  # Timeout for HTTP requests in seconds
MAX_RETRIES = 3  # Number of retries for failed requests
RETRY_DELAY = 5  # Delay between retries in seconds

headers = {
    "Private-Token": PRIVATE_TOKEN
}

def get_projects(group_id):
    url = "{GITLAB_URL}/api/v4/groups/{group_id}/projects"
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                sleep(RETRY_DELAY)
            else:
                print("Failed to fetch projects after {MAX_RETRIES} attempts.")
                return []

def get_branches(project_id):
    url = "{GITLAB_URL}/api/v4/projects/{project_id}/repository/branches"
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                sleep(RETRY_DELAY)
            else:
                print("Failed to fetch branches for project {project_id} after {MAX_RETRIES} attempts.")
                return []

def delete_branch(project_id, branch_name):
    if DRY_RUN:
        print("DRY RUN: Would delete branch '{branch_name}' in project {project_id}")
        return True
    else:
        url = "{GITLAB_URL}/api/v4/projects/{project_id}/repository/branches/{branch_name}"
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
                if response.status_code == 204:
                    print("Deleted branch '{branch_name}' in project {project_id}")
                    return True
                else:
                    print("Failed to delete branch '{branch_name}' in project {project_id}: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print("Attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    sleep(RETRY_DELAY)
                else:
                    print("Failed to delete branch '{branch_name}' in project {project_id} after {MAX_RETRIES} attempts.")
                    return False

def is_branch_stale(branch):
    last_commit_date = datetime.strptime(branch['commit']['committed_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
    return last_commit_date < datetime.now() - timedelta(days=TIME_LIMIT_DAYS)

def main():
    projects = get_projects(GROUP_ID)
    for project in projects:
        project_id = project['id']
        project_name = project['name']
        print("Checking project: {project_name} (ID: {project_id})")
        branches = get_branches(project_id)
        for branch in branches:
            branch_name = branch['name']
            last_commit_date = branch['commit']['committed_date']
            if branch_name not in ["main", "master"] and is_branch_stale(branch):
                print("Stale branch detected: {branch_name}, last commit date: {last_commit_date}")
                delete_branch(project_id, branch_name)

if __name__ == "__main__":
    main()
