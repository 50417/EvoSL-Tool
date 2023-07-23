# EvoSL-Tool

EvoSL-Tool is modular framework that can systematically search for Simulink repositories without human intervention. The framework can extract projects' associated issues, pull request, commit information and forked repositories. The framework can be used to enlarge the [EvoSL](https://zenodo.org/record/7806457) dataset with new Git repositories in the future. 

The tool also mines element (i.e., block, lines, configuration, ports, mask) level changes of Simulink model versions. The tool can be used to extract element level change data of Simulink models that are stored and versioned on GitHub.

The EvoSL-Tool can be obtained [here](https://zenodo.org/record/8111020)

-------------------------------

## Recent News

"EvoSL: A Large Open-Source Corpus of
Changes in Simulink Models & Projects" is accepted in [MODELS 2023](https://conf.researchr.org/track/models-2023/models-2023-technical-track) (CORE A, acceptance rate: 24.6%)

-------------------------------

In this repository, we have three different tools that work with each other:
1. [EvoSL-Miner]
2. [Project Evolution]
3. [Compare Model Snapshot]

Clone the repository and install the dependencies
```sh
$ git clone <gitlink>
$ cd EvoSL-Tool
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

Alternatively, if you wish to install a non-Debian-packaged Python package, create a virtual environment using python3 -m venv path/to/venv. Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make sure you have python3-full installed.



## Usage

### 1. EvoSL-Miner
The tool mines Simulink repository from GitHub and searches for project since 2008. The repository is a cloned one. Make sure you have enough storage in your system.
Change  to `EvoSL-Miner` directory

#### 1.1 To get Simulink projects
```sh
$ python downloadRepoFromGithub.py --query=<QUERY> --dir=<DIRECTORY_TO_STORE_PROJECTS> --dbname=<DATABASE_TO_STORE_COMMIT_METADATA> --token=<GITHUB_AUTHENTICATION_TOKEN>
``` 
We used 
- `query=simulink`  OR `query=language:MATLAB` 
- `dbname=evosl.sqlite`
The two queries have to run in two different python execution.

Getting Authetication token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token


#### 1.2 To get project's forks 

```sh
$ python get_forked_project.py --dir=<DIRECTORY_TO_STORE_PROJECTS> --dbname=<DATABASE_TO_STORE_COMMIT_METADATA> --token=<GITHUB_AUTHENTICATION_TOKEN>
``` 
Use the same database that you use to mine the projects. 
Use either same dir  or different directory if you want to save forked projects into different directory.

#### 1.3 To get Projects Issue and PR
```sh
$ python get_issues_pr.py --dbname=<DATABASE_TO_STORE_COMMIT_METADATA> --token=<GITHUB_AUTHENTICATION_TOKEN>
``` 
Use the same database that you use to mine the projects. 

Adding -f flag in the get_forked_project.py and get_issues_pr.py will get the metadata for forked projects. Otherwise only root is processed. 

### 2. Project Evolution
The tool extracts project and model commit history of GitHub Projects. The tool leverages the mined data from [EvoSL-Miner]. The mined data consist of GitHub urls which this tool uses to extract project/model commit information. All project evolution data is stored in SQLite database.

In this work, we mined Simulink project's evolution data. But the tool can be used to mine the project commit data of any GitHub project. The model commit data will be mined if the project is a Simulink project. 

Change to `project_evolution` folder

#### 2.1 To get commit metadata of root and forked projects 
* Update the project_evol.py file, In line 167-170, <br>

```
source_database: assign path of the same db as used in EvoSL-Miner module 
dst_database: Ideally assign same path as source database
is_forked: Set to true when you want to collect forked projects repository. 
```

NOTE: You need to mine root projects' commit first (i.e. set **is_forked=False**). To avoid extracting duplicate commit metadata, the tool only tries to extract commit of forked projects since when it was forked. 

- run 
```
$ python project_evol.py
```
### 3. Compare Model Snapshot
The tool extracts Simulink model element data of a GitHub Project over the project lifecycle. The tool leverages [Model Comparision Utility] and [Project Evolution]. The tool can be used to extract Simulink model element change data of any Simulink project that are stored and versioned on GitHub.

Change to the root directory of the project.
In this work, we mined model element change data of EvoSL projects. 
- Download and extract [Model Comparision Utility] 
- Download project evolution data (EvoSL_v1.sqlite) from [EvoSL](https://zenodo.org/record/7806457). 
- Open Matlab R2019a. [MATLAB Installation]
- In driver.m <nr>
-- Update 
```
dependency=<Model Comparison Utility location>
project_commit_db=<EvoSL.sqlite>
project_location=<leave as blank if use_URL is set to true>
		use_URL=<if false, set project_location to evoSL's projects(all the project need to unzipped.)>
```

- In MATLAB's command window, 
```sh
>> driver
```

NOTE: `use_URL = true` will clone the project from GitHub and disregard project_location. 
EvoSL already has Model_Element_Canges table that has all the element-level changes of all EvoSL projects. 

All data will be stored in database you listed as  project_commit_db. 

## To reproduce numbers presented in the paper.

Use R2022b to reproduce the numbers. 

### 1. Reproduce numbers of EvoSL_36
- Download  Analysis Data from [FigShare](https://figshare.com/articles/dataset/EvoSL_A_Large_Open-Source_Corpus_of_Changes_in_Simulink_Models_Projects_Analysis_Data_/22298812/1) 
-  In the @analyzer/analyzer.m file
-- In line 6, Update model_evol_db = < path to EvoSL_36_2019a.sqlite >
- Change directory to root of the project
- In MATLAB command window, run
```
>> x = analyzer();
>> x.plot_and_print_results();
```
The above will reproduce TABLE V, Figure 9 and  Table VII

### 2. To generate Figure 6.
- Download EvoSL_36_2019a.sqlite from [FigShare](https://figshare.com/articles/dataset/EvoSL_A_Large_Open-Source_Corpus_of_Changes_in_Simulink_Models_Projects_Analysis_Data_/22298812/1) 
- Download EvoSL_v1.sqlite and EvoSL+_v1.sqlite from [Zenodo](https://zenodo.org/record/7806457)
- Change directory to analyzer_py
- In get_activity_of_project.py, 
```
-- Update evoSL_database (database location) as well as relevant boolean flags (i.e. evoSL_or_evoSLPlus_flag, ten_plus_model_commits in main() function
---- For Figure 6 (a), in line 393 ``evoSL_database=<EvoSL+ location>`` ``evoSL_or_evoSLPlus_flag=True``, ``ten_plus_model_commits=False``
---- For Figure 6 (b), in line 393 ``evoSL_database=<EvoSL location>`` ``evoSL_or_evoSLPlus_flag=True``, ``ten_plus_model_commits=False``
---- For Figure 6 (c), in line 393 ``evoSL_database=<EvoSL location>`` ``evoSL_or_evoSLPlus_flag=True``, ``ten_plus_model_commits=True``
---- For Figure 6 (d), in line 393 ``evoSL_database=<EvoSL 36 location>`` ``evoSL_or_evoSLPlus_flag=False``, ``ten_plus_model_commits=False``
-- Run 
$ python get_activity_of_project.py

```

### 3. To reproduce Table III
- Change directory to analyzer_py
- Download EvoSL_36_2019a.sqlite from [FigShare](https://figshare.com/articles/dataset/EvoSL_A_Large_Open-Source_Corpus_of_Changes_in_Simulink_Models_Projects_Analysis_Data_/22298812/1) 
- Download EvoSL_v1.sqlite and EvoSL+_v1.sqlite from [Zenodo](https://zenodo.org/record/7806457)
- Change directory to analyzer_py
- In get_evolution_distribution.py, 
-- Update database location in main() function. In line 200,
`evosl_database = <evosl_v1.sqlite location>`
`evoslplus_database = <evosl+_v1.sqlite location>`
`evoslsample_database = <EvoSL_36_2019a.sqlite location>`
-- Run 
```
$ python get_evolution_distribution.py
```

### 4. To reproduce Table V
- Change directory to analyzer_py
- Download EvoSL_36_2019a.sqlite from [FigShare](https://figshare.com/articles/dataset/EvoSL_A_Large_Open-Source_Corpus_of_Changes_in_Simulink_Models_Projects_Analysis_Data_/22298812/1) 
- Change directory to analyzer_py
- In get_evoSL_sample_metrics.py, 
```
-- Update database location in main() function. In line 172, 
`evosl_sample_database = <evolSL_36_2019a.sqlite location>`
-- Run 
$ python get_evoSL_sample_metrics.py
```

### 5. To generate Figure 5 
- Change directory to analyzer_py
- Download EvoSL_v1.sqlite and EvoSL+_v1.sqlite from [Zenodo](https://zenodo.org/record/7806457)
- Change directory to analyzer_py
- In get_and_plot_cumulative_metric_distribution.py, 
```
-- Update database location in main() function. In line 152,
`our_db = <evoSL.sqlite location>`
`raw_db = <evoSL+.sqlite location>`
-- Run 
$ python get_and_plot_cumulative_metric_distribution.py
```

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
   [Anaconda]: <https://www.anaconda.com/>
   [EvoSL-Miner]: <https://github.com/50417/EvoSL-Tool/tree/main/EvoSL-Miner>
   [Compare Model Snapshot]: <https://github.com/50417/EvoSL-Tool/tree/main/%40compareModelSnapshot>
   [Project Evolution]: <https://github.com/50417/EvoSL-Tool/tree/main/project_evolution> 
   [Model Comparision Utility]: <https://zenodo.org/record/6410073#.Y-VQINLMK-Y>
   [Repository Mining for Changes in Simulink Models]: <https://ieeexplore.ieee.org/document/9592466>
   [MATLAB Installation]: <https://github.com/50417/EvoSL-Tool/tree/main/MATLABConfiguration.md>
