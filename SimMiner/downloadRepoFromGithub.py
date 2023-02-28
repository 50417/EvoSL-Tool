# Install PyGithub
'''
DOC for PyGithub https://readthedocs.org/projects/pygithub/downloads/pdf/stable/
'''
from github import Github , GithubException
import argparse
# import urllib.request as urllib2
import requests
import os
from pathlib import Path
from zipfile import ZipFile
import datetime
import logging
from Simulinkrepoinfo import SimulinkRepoInfoController
import sys
import time
import shutil
from subprocess import Popen, PIPE
import pytz  
logging.basicConfig(filename='github.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

class GithubRepoDownload():
	githubURL = "https://github.com"
	REQUEST_COUNTER = 0 


	def __init__(self, dir_name, token,dbname,l_flag=False,processed_file_ids = None):
		'''
		:args:
			dir_name : Name /Path of the directory to store all the downloaded files .

		'''
		self.gObj = Github(token)
		self.l_flag = l_flag
		# TODOS
		# Maintains count of mdl or slx files stored in each project
		self.simulinkmodels_count = {}
		# Argument check if valid
		self.dir_name = dir_name
		# Database
		self.databaseHandler = SimulinkRepoInfoController(dbname)
		if not os.path.exists(self.dir_name):
			os.mkdir(self.dir_name)
			logging.info("Directory " + self.dir_name + " Created ")

		else:
			logging.info("Directory " + self.dir_name + " already exists")

		self.cached_processed_file_id = processed_file_ids


	def getRepositoryFromAPI(self, query):
		# UPTO 1000 results for each search
		'''
		 https://help.github.com/en/github/searching-for-information-on-github/searching-for-repositories
		 :return:
		'''
		results = self.gObj.search_repositories(query, sort='updated')
		#self.gObj.search_commits()
		logging.info("Total Search Results for %s query : %s " % ( query,str(results.totalCount)))
		return results

	def get_version_sha(self,repo):
		repoLink = GithubRepoDownload.githubURL + "/" + \
							 repo.owner.login + "/" + repo.name + ".git"
		p = Popen(['git', 'ls-remote', repoLink, '|', 'grep', 'refs/heads/master'], stdout=PIPE)
		output = p.communicate()[0].decode("utf-8")
		return output.split("\t")[0]

	def get_repo_languages(self,repo):
		language_list = list(repo.get_languages().keys())
		return  ",".join(language_list)

	def get_repositores(self,query,start_date):
		latest_date = start_date + self.interval 
		full_query = query + " created:" + str(start_date) + ".." + str(latest_date)
		if GithubRepoDownload.REQUEST_COUNTER > 5: 
			logging.info("================Sleeping for 60 Seconds============")
			time.sleep(60)
		repositories = self.getRepositoryFromAPI(full_query)
		GithubRepoDownload.REQUEST_COUNTER += 1
		if repositories.totalCount >= 1000:
			for i in range(25):
				self.REQUEST_COUNTER += 1
				self.interval  = self.interval /2
				latest_date = start_date + self.interval 
				full_query = query + " created:" + str(start_date) + ".." + str(latest_date)
				repositories = self.getRepositoryFromAPI(full_query)
				logging.info("Query : " + str(full_query))
				
				if repositories.totalCount < 1000:
					logging.info("Search Count : " + str(repositories.totalCount))
					break
		else: 
			self.interval  = self.interval * 2
			return self.get_repositores(query,start_date)
		return repositories


	def LocalDateTimeFromUTC(self,utc):
	    tzLocal = pytz.timezone('America/Chicago')  # insert your time zone here (list available here: https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones)
	    return tzLocal.localize(utc)

	def downloadAllRepository(self, query):
		'''
		Download the repositories
		 30 requests per minute for using SEARCH API
		 HENCE TIMEOUT 60 Seconds between query

		:param query: query to download repositiory
		SEE https://help.github.com/en/github/searching-for-information-on-github/searching-for-repositories
		:return:
		'''
		cached_no_sim_mdl_project = open('cached.csv','a+')
		

		start_date = datetime.date(2008, 1, 1) 
		end_date = datetime.date.today()
		self.interval = datetime.timedelta(365)

		self.counter = 0
		self.skipped_counter_license = 0
		self.skipped_counter_no_mdl = 0
		self.download_counter = 0

		while (start_date < end_date):
			GithubRepoDownload.REQUEST_COUNTER  = 0
			repositories = self.get_repositores(query,start_date)
			logging.info("Start Date : " + str(start_date) + " Interval : " + str(self.interval ) + " Search Repo Count : " + str(repositories.totalCount))

			start_date += self.interval 
			for repo in repositories:
				self.counter  += 1
				logging.info("======START %d ========="%self.counter)
				logging.info("Search Result #%d: %s" %(self.counter, repo.name))

				if str(repo.id) in self.cached_processed_file_id:
					logging.info("Already Processed")
					continue


				
				destination_path = os.path.join(self.dir_name ,str(repo.id))
				has_license = 0
				license_type = ""
				# Check the repo Id in the directory before downloading to avoid duplicates
				# Check If the filename exists before downloading
				# FileName is Id  as Id provided by Github are unique for two different repo
				if os.path.exists(destination_path):
					logging.info("Project %s already exists" % repo.name +"__"+ str(repo.id))
					continue

				# Cloning the project
				logging.info("Cloning the project %s" %(repo.clone_url + " "+ destination_path))
				try: 
					os.system("git clone "+repo.clone_url + " "+ destination_path)
				except Exception as e: 
					logging.info("Cloning failed")
					logging.info(e)
					continue


				# Getting License
				try:
					license_type = repo.get_license().license.name
					has_license = 1
					logging.info("License Type : "+repo.get_license().license.name)
				except Exception as e:
					#Skipping the repository since it doesnot have License
					if self.l_flag == True:
						self.skipped_counter_license += 1
						logging.info("Skipping the repository : %s since it does not have License" %repo.name)
						continue
					logging.info(e)



				# getting sha and download file
				version_sha = self.get_version_sha(repo)

				# Check and Delete
				model_file_count,model_file_names = self.checkIfProjecthasSimulinkModel(destination_path)
				if model_file_count>0:
					try:
						self.write_to_database(repo, license_type,model_file_count,model_file_names,version_sha)
					except Exception as e:
						logging.info("Error inserting into database")
						logging.info(e)
					self.download_counter += 1
				else:
					self.skipped_counter_no_mdl += 1
					projectname = os.path.basename(destination_path)
					cached_no_sim_mdl_project.write(","+projectname)

			logging.info("================Sleeping for 60 Seconds============")
			time.sleep(60)

	def checkIfProjecthasSimulinkModel(self, folder):
		'''
		checks if project contains slx or mdl files.
		If not deletes the project files  .
		Update Flag in the database with no relevant files in the download projects

		:return:
		'''
		projectname = os.path.basename(folder)
		fileName_csv = ""
		count = 0
		for path,subdirs,files in os.walk(folder):
			# check if current path is a file
			for filename in files:
				if filename.endswith(".slx") or filename.endswith(".mdl"):
					count = count + 1
					fileName_csv=filename+","+fileName_csv
		if count > 0:
			self.simulinkmodels_count[projectname] = count
			shutil.rmtree(folder,ignore_errors=True)
			#self.update_model_file_info_in_db(repo.id,{"model_files":fileName_csv})
			#self.update_model_file_info_in_db(repo.id, {"has_model_files":1})
			#self.update_model_file_info_in_db(repo.id,{"num_model_file":count})
			return  count, fileName_csv
		else:
			self.skipped_counter_no_mdl += 1
			#self.update_model_file_info_in_db(repo.id, {"has_model_files": 0})
			
			logging.info("No Model Files : Deleting %s" % folder)
			shutil.rmtree(folder,ignore_errors=True)
			return 0,""

	def printDict(self):
		sum = 0
		for k, v in self.simulinkmodels_count.items():
			logging.info(k + " : ", str(v))
			sum = sum + v
		logging.info("Total Simulink models : " + str(sum))
		logging.info("Total Skipped License : %d"%self.skipped_counter_license )
		logging.info("Total Skipped No model files : %d"%self.skipped_counter_no_mdl )
		logging.info("Total Downloaded : %d"%self.download_counter)
		logging.info("Total Search Results : %d" % self.counter)

	def write_to_database(self, repo,license_type,no_of_model_file, model_file_csv,version_sha):
		'''
		Insert into Database
		:param repo:
		:param license_type:
		:param has_license:
		:return:
		'''
		topic = ",".join(repo.get_topics())
		languages = self.get_repo_languages(repo)
		if(topic != ""):
			logging.info("Topics : "+ topic)
		if(languages != ""):
			logging.info("Languages : "+ languages)
		self.databaseHandler.insert(repo.id,repo.name,repo.owner.login,repo.owner.type, repo.owner.id, repo.private,
									repo.html_url, repo.description, repo.fork, repo.url,
									repo.created_at, repo.updated_at, repo.pushed_at,
									repo.homepage, repo.size,
									repo.stargazers_count, repo.subscribers_count, languages,repo.forks_count,
			   						repo.open_issues_count, repo.master_branch, repo.default_branch,
									topic,license_type, model_file_csv, no_of_model_file,version_sha)



	def update_model_file_info_in_db(self,id, col_val):
		self.databaseHandler.update(id, col_val)


parser = argparse.ArgumentParser(description='Get argument for downloading')
parser.add_argument('-q', '--query', dest="query", type=str,
					help='https://help.github.com/en/articles/understanding-the-search-syntax')
parser.add_argument('-d', '--dir', dest="dir_name", type=str,
					help='Name of directory to store downloaded files ')
parser.add_argument('-db', '--dbname', dest="db_name", type=str,
					help='Name of sqlite database to store metadata files ')
parser.add_argument('-flag', '--license', dest="l_flag", type=bool,
					help='Boolean value to determine to include only those project with license| Dont include the file if downloading all projects')
parser.add_argument("-t", '--token', dest="token", type=str,
					help = 'https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line')
args = parser.parse_args()

processed_ones = []
if ~os.path.exists('cached.csv'):
	f = open('cached.csv','a')
	f.close()

with open('cached.csv','r') as processed_file_id:
	line = processed_file_id.readline()
	processed_ones = line.split(",")
processed_file_ids = set(processed_ones)

query = args.query
dbname = args.db_name
l_flag = args.l_flag
logging.info("Query Argument: %s " % query)

token = args.token # BASIC AUTH OR OAUTH 5000 requests per hour ||  30 requests per minute for using SEARCH API

gitObj = GithubRepoDownload(args.dir_name,token, dbname,l_flag,processed_file_ids)
gitObj.downloadAllRepository(query)

gitObj.printDict()

