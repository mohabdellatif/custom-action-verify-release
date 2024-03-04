# custom-action-cd-jira-post-release
This Python script checks the status of GitHub Actions for a list of repositories. It's designed to be run as post release step after https://github.com/GumGum-Inc/custom-action-cd-jira-release

## Scope 
The scope of this custom action is limited to:  
- Prints the result of the execuation of release tag creation for all repositiories found in the `PAYLOAD` based on  `releasename`
- Create an overall result environment variable to be used by the subsequent action in the release automation workflow.

## Features
- Checks the status of the pipeline.yaml GitHub Action for each repository in a list.
- Skips repositories where the latest run of the action was not triggered by a release tag that matches the `releasename` in the `PAYLOAD`.
- Prints the status of each repository's action to the console.
- Writes the overall result (success or failure) to an environment variable.


## Inputs
It expects the following inputs from https://github.com/GumGum-Inc/custom-action-cd-jira-release

| Name                         | Type    | Required | Default Value                                               | Description                                                                                                        |
| ---------------------------- | ------- |--------- | ----------------------------------------------------------- |------------------------------------------------------------------------------------------------------------------- |
| `PAYLOAD`                 | String  | No      | Passed by git event      |    A JSON string containing the Repositories key, which should be a comma-separated list of repository names. 
| `GITHUB_REPOSITORY`                 | String  | No      | Passed by git event                                                       | The name of the current repository (used to determine the organization name).  
| `CREATE_FAILED`                 | String  | No      | False      |    Set to "True" if the release creation failed and the script should exit immediately.  
| `GH_RELEASE`                 | String  | No      | Org parameter      |    Your GitHub token, used to authenticate with the
| `CICD_FILENAME`                 | String  | No      | Org parameter      |    Your github actions filename



