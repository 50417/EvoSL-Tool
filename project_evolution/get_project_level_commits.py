from pydriller import RepositoryMining
import logging
import sys

logging.basicConfig(filename='commits.log', filemode='a',
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

#logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def get_changed_files(modified_files_obj, commit , model_verbatim, project_id):
    CONTAINS_MODEL_FLAG = False
    file_change_list = []
    logging.debug("+++MODIFIED FILE LIST+++")
    for modified_file_obj in modified_files_obj:
        file_path = ''
        logging.debug("Name: {} ChangeType: {} OldPath: {} NewPath: {}".format(modified_file_obj.filename,modified_file_obj.change_type.name,modified_file_obj.old_path,modified_file_obj.new_path))
        if modified_file_obj.old_path is None: 
            file_path = modified_file_obj.new_path
        else:
            file_path = modified_file_obj.old_path
        file_change_list.append(file_path)

        # Models 
        if file_path.endswith('.mdl') or file_path.endswith('.slx'):
            CONTAINS_MODEL_FLAG = True
            try: 
                model_verbatim.insert(project_id, file_path, commit, modified_file_obj.change_type.name )
            except Exception as e:
                logging.error("Error inserting into database")
                logging.error(e) 

    logging.debug("+++MODIFIED FILE LIST END+++")
    return ",".join(file_change_list), CONTAINS_MODEL_FLAG


def get_project_level_commits(repo_url,hash,project_verbatim,id,model_verbatim,is_forked,start_from_commit):
    hashes_per_project = []
    commits_dates_per_project = []
    merge_commits_per_project = set()
    authors_per_project = set()
    commit_per_day = {}
    model_commits = []
    model_authors = set()
    print(start_from_commit)
    if is_forked:
        if start_from_commit is None:
            raise Exception("Something is wrong . Check")
        try: 
            all_commits = RepositoryMining(repo_url, from_commit=start_from_commit).traverse_commits()
        except Exception as e: 
            raise Exception("Something is wrong")
    else: 
        all_commits = RepositoryMining(repo_url).traverse_commits()

    for commit in all_commits:
        modified_files, CONTAINS_MODEL_FLAG = get_changed_files(commit.modifications, commit, model_verbatim,id)
        try: 
            project_verbatim.insert(id,commit,modified_files)
        except Exception as e:
            logging.error("Error inserting into database")
            logging.error(e) 
        if CONTAINS_MODEL_FLAG:
            model_commits.append(commit.hash)
            model_authors.add( commit.author.email)

        hashes_per_project.append(commit.hash)
        authors_per_project.add(commit.author.email)
        commits_dates_per_project.append(commit.author_date.astimezone())
        date_without_time = commit.author_date.astimezone().date()
        if date_without_time in commit_per_day:
            commit_per_day[date_without_time] = commit_per_day[date_without_time]+1
        else:
            commit_per_day[date_without_time] = 1
        if commit.merge:
            merge_commits_per_project.add(commit.hash)
        #logging.info('Hash {}, author {} , date {}'.format(commit.hash, commit.author.name, commit.author_date))
    commits_dates_per_project.sort()
    start_date = commits_dates_per_project[0]
    end_date = commits_dates_per_project[len(commits_dates_per_project)-1]

    project_lifetime =end_date-start_date
    #logging.info(type(end_date))


    logging.info("Number of Commits :{} ".format(len(hashes_per_project)))
    logging.info("Number of Merge Commits  :{} ".format(len(merge_commits_per_project)))
    logging.info("Number of Authors :{}".format(len(authors_per_project)))
    commit_per_day_sum = 0
    for k,no_of_commit in commit_per_day.items():
        #logging.info(v)
        commit_per_day_sum += no_of_commit
    #logging.info(commit_per_day_sum/(float(project_lifetime.days)))

    logging.info("Number of Model Commits :{}".format(len(model_commits)))
    logging.info("Number of Model Authors :{}".format(len(model_authors)))
    cpds = commit_per_day_sum
    proj_lt = project_lifetime.days + project_lifetime.seconds / 86400
    logging.info("Lifetime :{} days".format(proj_lt))
    if project_lifetime.days>0:
        cpds = commit_per_day_sum / (float(proj_lt))
    return len(hashes_per_project), len(merge_commits_per_project), len(authors_per_project) ,\
				 commits_dates_per_project[0], commits_dates_per_project[len(commits_dates_per_project)-1], \
           (proj_lt),cpds ,\
				 len(model_commits), len(model_authors)

#get_project_level_commits("https://github.com/alesgraz/kinect2-SDK-for-Simulink ")
