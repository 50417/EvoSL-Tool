1. [Repository Mining for Changes in Simulink Models]


We have different tools in the repository that work with each other:
1. [SimMiner]
2. [Project Evolution]
3. [Compare Model Snapshot]

Clone the project and install the dependencies
```sh
$ git clone <gitlink>
$ cd SimEvolutionTool
```

## Installation

Tested on Ubuntu 18.04 

First, create virtual environment using  [Anaconda] so that the installation does not conflict with system wide installs.
```sh
$ conda create -n <envname> python=3.8
```

Activate environment and Install the dependencies.
```sh
$ conda activate <envname>
$ pip install -r requirements.txt
```
(maybe adapt exact versions in `requirements.txt` and upgrade pip before: `pip install --upgrade pip` or execute everything with `pip3`)

## Usage

### 1. SimMiner
The tool mines Simulink repository from GitHub and searches for project since 2008. The repository is a cloned one. Make sure you have enough storage in your system.
- Change  to `SimMiner` directory and Run
```sh
$ python downloadRepoFromGithub.py --query=<QUERY> --dir=<DIRECTORY_TO_STORE_PROJECTS> --dbname=<DATABASE_TO_STORE_COMMIT_METADATA> --token=<GITHUB_AUTHENTICATION_TOKEN>
``` 

Getting Authetication token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token


- To get project's forks

```sh
$ python get_forked_project.py --dir=<DIRECTORY_TO_STORE_PROJECTS> --dbname=<DATABASE_TO_STORE_COMMIT_METADATA> --token=<GITHUB_AUTHENTICATION_TOKEN>
``` 
Use the same database that you use to mine the projects. 
Use either same dir  or different directory if you want to save forked projects innto different directory.

- To get Projects Issue and PR
```sh
$ python get_issues_pr.py --dbname=<DATABASE_TO_STORE_COMMIT_METADATA> --token=<GITHUB_AUTHENTICATION_TOKEN>
``` 
Use the same database that you use to mine the projects. 

Adding -f flag in the get_forked_project.py and get_issues_pr.py will get the metadata for forked projects. Otherwise only root is processed. 

### 2. Project Evolution
The tool extracts project and model commit history of GitHub Projects. The tool leverages the mined data from [SimMiner]. The mined data consist of GitHub urls which this tool uses to extract project/model commit information. All project evolution data is stored in SQLite database.

In this work, we mined GitHub based simulink project evolution data. But the tool can be used to mine the project commit data of any GitHub project. The model commit data will be mined if the project is a Simulink project. 
- Update the database on the proj_evol.py file
- run python project_evol.py

### 3. Compare Model Snapshot
The tool extracts Simulink model element data of a GitHub Project over the project lifecycle. The tool leverages [Model Comparision Utility] and [Project Evolution]. The tool can be used to extract Simulink model element change data of any GitHub based Simulink project.

In this work, we mined model element change data of EvoSL projects. 
- Download and extract [Model Comparision Utility] 
- Download project evolution data from EvoSL. 
- Open Matlab. [MATLAB Installation]
- Update dependenc, project_commit_db, project_location in driver.m
- In command window, 
```sh
$ driver
```
All data will be stored in database you listed as  project_commit_db. 

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
   [Anaconda]: <https://www.anaconda.com/distribution/>
   [SimMiner]: <https://github.com/Anonymous-double-blind/SimEvolutionTool/tree/main/SimMiner>
   [Compare Model Snapshot]: <https://github.com/Anonymous-double-blind/SimEvolutionTool/tree/main/%40compareModelSnapshot>
   [Project Evolution]: <https://github.com/Anonymous-double-blind/SimEvolutionTool/tree/main/project_evolution> 
   [Model Comparision Utility]: <https://zenodo.org/record/6410073#.Y-VQINLMK-Y>
   [EPHCC]: <https://github.com/PowerSystemsHIL/EPHCC>
   [Repository Mining for Changes in Simulink Models]: <https://ieeexplore.ieee.org/document/9592466>
   [MATLAB Installation]: <https://github.com/Anonymous-double-blind/SimEvolutionTool/tree/main/MATLABConfiguration.md>

