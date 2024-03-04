import json
import os
import time
import requests
import base64
import yaml
from colorama import Fore, Back, Style


payload = json.loads(os.getenv('PAYLOAD', '{}'))
releasename = payload.get('ReleaseName')
token = os.getenv("GH_RELEASE")

if payload and 'Repositories' in payload and payload['Repositories']:
    repositories = list(set(repo.strip() for repo in payload.get('Repositories').split(',') if repo.strip()))
else:
    repositories = []

session = requests.Session()
session.headers.update({
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {os.getenv("GH_RELEASE")}',
    'X-GitHub-Api-Version': '2022-11-28',
})

def get_latest_run_status(repo):
    
    currentrepo = os.getenv('GITHUB_REPOSITORY')
    server_url = "https://api.github.com/"
    organization = currentrepo.split('/')[0]
    org_url = server_url+ "repos/" + organization + "/"
    action_filename = os.getenv('GOLDENCICD_FILENAME') 
    
    response = session.get(
        f"{org_url}{repo}/actions/workflows/{action_filename}/runs"
    )
    print(Fore.YELLOW + Style.DIM + f"GET: {org_url}{repo}/actions/workflows/{action_filename}/runs")
    if response.status_code == 200:
        print(Fore.GREEN + f"OK: 200")
        result = response.json()
        head_branch = result["workflow_runs"][0]["head_branch"]
        latest_run_status = result["workflow_runs"][0]["status"]
        latest_run_status_conclusion = result["workflow_runs"][0]["conclusion"]
        return latest_run_status, latest_run_status_conclusion, head_branch
    return None, None, None
        
def check_github_action_status(repo):
    latest_run_status, latest_run_status_conclusion, head_branch = get_latest_run_status(repo)
    if head_branch != releasename:
        return None
    if latest_run_status == "completed" and head_branch == releasename:
        if latest_run_status_conclusion == "success":
            print(Fore.RESET + Style.NORMAL + f"{repo} was successful")
            return "succeeded"
        else:
            print(Fore.RESET + Style.NORMAL + f"{repo} failed")
            return "failed"
    if (latest_run_status in ["cancelled", "timed_out", "failure", "queued", "in_progress"]) and head_branch == releasename:
        print(Fore.RESET + Style.NORMAL + f"{repo} is in progress")
        return "in_progress"
    return None
        
            
if __name__ == "__main__":
    results = "Succeeded"
    create_failed = os.getenv('CREATE_FAILED')
    try:
        if create_failed == "True":
            print(Fore.RED + Style.BRIGHT + f"Release creation failed. Skipping.")
            results = "Failed"
            raise Exception("Release creation failed. Skipping.")
        start_time = time.time()
        timeout = 30 * 60  # 30 minutes
        check_interval = 30  # 30 seconds
        completed_repos = {}
        skipped_repos = {}
        while True:
            for repo in repositories:
                if repo not in completed_repos:
                    status = check_github_action_status(repo)
                    if status is None:
                        if repo not in skipped_repos:
                            skipped_repos[repo] = "skipped" 
                            continue  # skip to the next repo if status is None
                        else:
                            completed_repos[repo] = "skipped" # if it was skipped before, add it to completed_repos so we won't try more than twice
                            continue
                    if status != "in_progress": # if status still in progress, keep going until it is success, failure or we timeout
                        completed_repos[repo] = status                
            if time.time() - start_time > timeout:
                print(Fore.RED + "Timeout reached")
                break
            

            if len(completed_repos) == len(repositories):
                
                for completed_repo in completed_repos:
                    status = completed_repos[completed_repo]
                    if status == 'succeeded':
                        print(Fore.GREEN + Style.BRIGHT + f'{completed_repo} >>> {status}')
                    if status != 'succeeded':
                        print(Fore.RED + Style.BRIGHT + f'{completed_repo} >>> {status}')
                        results = "Failed"  
                break

            time.sleep(check_interval)
            
    except Exception as e:
        results = "Failed"
    finally:
        command = f'echo results={results} >> "$GITHUB_OUTPUT"'
        os.system(command) 
       