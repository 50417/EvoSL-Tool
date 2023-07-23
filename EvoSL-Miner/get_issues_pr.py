import logging
import argparse
import os,sys
from github import Github , GithubException, RateLimitExceededException
from urllib.error import HTTPError
import time, datetime
import sqlite3
sys.path.append('./DAO')
from Issues_DAO import Issues_DAO_controller
from PR_DAO import PR_DAO_controller
from Comment_DAO import Comments_DAO_controller
from Commit_DAO import Commit_DAO_controller
from Issue_PR_link_DAO import Issue_PR_Link_DAO_controller
logging.basicConfig(filename='logs/github_issue_pr.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
class Issues_PR():
	'''


	'''

	def __init__(self,token,dbname ):
		self.common_url = "https://github.com/"
		self.pygithub = Github(token)

		self.issueDBHandler = Issues_DAO_controller(dbname)
		self.prDBHandler = PR_DAO_controller(dbname)
		self.commentDBHandler = Comments_DAO_controller(dbname)
		self.commitDBHandler = Commit_DAO_controller(dbname)
		self.linkDBHandler = Issue_PR_Link_DAO_controller(dbname)

		self.cur_api_call  = 0 
		self.start_time = time.time()



	def get_labels(self,labels):
		label_list = [label.name for label in labels]
		return  ",".join(label_list)

	def fetch_paginated_list(self,all_pages):
		'''
			Converts Github.paginatedList into list
			returns : 
				result: converted list
				pages: number of pages . This is number of API call to get the results
		'''
		result = []
		page_size = all_pages._PaginatedList__requester.per_page
		pages = (all_pages.totalCount - 1) // page_size + 1
		#num_api_call = 1
		for page in range(0, pages):
			# Retry loading page 
			while len(result) < min((page+1) * page_size, all_pages.totalCount):
				#num_api_call += 1
				#self.sleep_check()
				# if required due to weird condition: https://github.com/PyGithub/PyGithub/blob/001970d4a828017f704f6744a5775b4207a6523c/github/PaginatedList.py#L242
				elements = all_pages.get_page(-1 if page == 0 else page)
				if len(elements) == page_size or page == pages-1 and len(elements) == all_pages.totalCount % page_size:
					result.extend(elements)
		return result

	def get_and_store_proj_issues(self,project_url, project_id):
		'''
			stores Issues only. In GitHub, every pull request is an issue but every issue is not a pull request 
			Here we separate issues from pull request 
		'''
		project_name = project_url.replace(self.common_url,"")
		repo = self.pygithub.get_repo(project_name)
		repo_issues = repo.get_issues(state='all')
		#self.sleep_check()
		for issue in repo_issues:
			if issue.pull_request is None: 
				labels = self.get_labels(issue.get_labels())
				try: 
					self.issueDBHandler.insert(project_id, labels, issue)
					x = 0 
				except Exception as e:
					logging.error("Error inserting into database")
					logging.error(e) 


				# Adding Comments 
				comments = issue.get_comments()
				for comment in comments:
					try:
						self.commentDBHandler.insert(issue.id, 'Issue', comment)
					except Exception as e:
						logging.error("Error inserting into database")
						logging.error(e) 

				timeline_events = issue.get_timeline()
	
				# Populating Links between Issues and PR
				for event in timeline_events:
					if event.source is not None:
						if event.source.type == 'issue' and event.source.issue.pull_request is not None:
							pull_request_id = event.source.issue.id
							try:
								self.linkDBHandler.insert(pull_request_id,issue.id)
							except Exception as e:
								logging.error("Error inserting into database")
								logging.error(e) 


	def get_and_store_proj_pr(self,project_url, project_id):
		'''
			
		'''
		project_name = project_url.replace(self.common_url,"")
		repo = self.pygithub.get_repo(project_name)
		repo_prs = repo.get_pulls(state='all')
		#self.sleep_check()
		for repo_pr in repo_prs:
			labels = self.get_labels(repo_pr.get_labels())
			try: 
				self.prDBHandler.insert(project_id, labels, repo_pr)
			except Exception as e:
				logging.error("Error inserting into database")
				logging.error(e) 


			# Adding Comments 
			comments = repo_pr.get_issue_comments()
			for comment in comments:
				try:
					self.commentDBHandler.insert(repo_pr.id, 'PR', comment)
				except Exception as e:
					logging.error("Error inserting into database")
					logging.error(e) 


			#Adding commit
			commits = repo_pr.get_commits()
			for commit in commits:
				try:
					self.commitDBHandler.insert(repo_pr.id,commit)
				except Exception as e:
						logging.error("Error inserting into database")
						logging.error(e) 


	def go(self,project_url, project_id):
		self.get_and_store_proj_issues(project_url, project_id)
		self.get_and_store_proj_pr(project_url, project_id)



						
def create_connection(db_file):
	""" create a database connection to the SQLite database
		specified by the db_file
	:param db_file: database file
	:return: Connection object or None
	"""
	conn = None
	try:
		conn = sqlite3.connect(db_file)
	except Error as e:
		print(e)
	return conn


def get_repo_id_urls(conn,get_from_forked_FLAG):
	"""
	Query tasks
	:param conn: the Connection object
	:param
	:return:
	"""
	cur = conn.cursor()
	if get_from_forked_FLAG: 
		cur.execute("SELECT forked_project_id,project_url FROM Forked_Projects order by forked_project_id")

	else:

		cur.execute("SELECT project_id,project_url FROM Root_Projects order by project_id")

	rows = cur.fetchall()
	return rows						
			


def main():
	parser = argparse.ArgumentParser(description='Get argument for downloading')
	parser.add_argument('-db', '--dbname', dest="db_name", type=str,
					help='Name of sqlite database (e.g. "a.sqlite") to get as well as store metadata')
	parser.add_argument("-t", '--token', dest="token", type=str,
					help = 'https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line')
	parser.add_argument('-f', '--forked', dest="f_flag", default=False,action='store_true',
					help='Boolean value to determine to include only those project with license| Dont include the file if downloading all projects')

	args = parser.parse_args()

	dbname = args.db_name
	token = args.token # BASIC AUTH OR OAUTH 5000 requests per hour ||  30 requests per minute for using SEARCH API
	get_from_forked_FLAG = args.f_flag

	project_obj = Issues_PR(token, dbname)
	conn = create_connection(dbname)
	
	processed_ones = []
	if ~os.path.exists('issue_cached.csv'):
		f = open('issue_cached.csv','a')
		f.close()

	with open('issue_cached.csv','r') as processed_file_id:
		line = processed_file_id.readline()
		processed_till = line.strip()
		if processed_till == '':
			processed_till = 0
		else:
			processed_till = int(processed_till)
	#processed_file_ids = set(processed_ones)

	with conn: 
		id_urls = get_repo_id_urls(conn,get_from_forked_FLAG)


	

	for id_url in id_urls:

		file_id, url  = id_url
		if file_id <= processed_till:
			#logging.info("===================Already Processed======================")
			continue
		logging.info("=============Processing {}===========".format(str(file_id)))
		try:
			project_obj.go(url,file_id)
		except RateLimitExceededException as e:
			time.sleep(3600)
			logging.info("==========Sleeping 1 hour========")
			main()
			break
		except Exception as e:
			logging.error("Error Processing the Project")
			logging.error(e) 
		
		with open('issue_cached.csv','w') as cached_p_id:
			cached_p_id.write(str(file_id))


		logging.info("=============DONE Processing {}===========".format(str(file_id)))





if __name__ == '__main__':
	main()

