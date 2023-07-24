import sqlite3
from sqlite3 import Error
import pathlib
import logging
import sys
import os, shutil
import time
from datetime import datetime
from pydriller import GitRepository
import argparse

sys.path.insert(1, '../EvoSL-Miner/DAO')
from subprocess import Popen, PIPE

from Repo_DAO import SimulinkRepoInfoController

from Model_commits_info import Model_commits_info_Controller
from Project_commits_info import Project_commits_info_Controller
from Project_commits_verbatim import Project_commits_verbatim_Controller
from Model_commits_verbatim import Model_commits_verbatim_Controller

logging.basicConfig(filename='commits.log', filemode='a',
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
from get_project_level_commits import get_project_level_commits
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

def get_repo_id_urls(conn,is_forked):
	"""
	Query tasks
	:param conn: the Connection object
	:param
	:return:
	"""
	cur = conn.cursor()
	if is_forked: 
		cur.execute("SELECT forked_project_id,project_url,version_sha FROM Forked_Projects")
	else:
		cur.execute("SELECT project_id,project_url,version_sha FROM Root_Projects") 

	rows = cur.fetchall()
	return rows

def get_root_last_commit_sha(conn, project_id,path):
	cur = conn.cursor()
	sql = """
			Select hash, (julianday(created_at) - julianday(committer_date)) day_diff 
			from (
			Select a.forked_project_id, a.forked_from_id,a.created_at,b.committer_date,b.hash 

			from Forked_Projects a
			join Project_commits b 
			on a.forked_from_id = b.project_id  
			where created_at > committer_date
			) a
			where  forked_project_id = """+ str(project_id)+" order by day_diff Limit 10000"
	cur.execute(sql)

	rows = cur.fetchall()
	#assert(len(rows) == 1)
	commit_hashes = [r[0] for r in rows]
	repo = GitRepository(path)

	for commit_hash in commit_hashes: 

		try:
			commit = repo.get_commit(commit_hash)
			return commit_hash
		except Exception as e: 
			logging.error("Commit not found")
		
	return None



def get_id_name(conn):
	cur = conn.cursor()

	cur.execute("SELECT project_id FROM Project_Commit_Summary ")

	rows = cur.fetchall()

	cur.execute("SELECT model_name FROM Model_Commit_Summary ")
	mdl_name = cur.fetchall()

	return set([ r[0] for r in rows]),set([m[0] for m in mdl_name])

def write_project_commit_info(url,id, hash,controller,project_verbatim,model_verbatim,is_forked, from_commit=None):
	total_number_of_commits, number_of_merge_commits, number_of_authors, \
	first_commit, last_commit, lifeTime_in_days, commit_per_day, \
	model_commits, model_authors = get_project_level_commits(url,hash,project_verbatim,id,model_verbatim,is_forked,from_commit)

	try: 
		logging.info("Writing to Project_commit_info table")

		controller.insert(id, total_number_of_commits, number_of_merge_commits, number_of_authors, \
											first_commit, last_commit, lifeTime_in_days, commit_per_day, \
											model_commits, model_authors)
	except Exception as e: 
			logging.info(e)
			logging.info("Writing failted.")
			return -1

	return lifeTime_in_days


def write_model_commit_info(project_id,controller, project_lifetime, conn):
	cur = conn.cursor()
	cur.execute("select model_name, count(DISTINCT hash),count(distinct author_email), MIN(author_date), max(author_date) \
				from model_commits where project_id = "+str(project_id)+"\
				group by model_name")

	rows = cur.fetchall()
	for row in rows: 
		model_name = row[0]
		no_of_commits = int(row[1])
		no_of_authors = int(row[2])
		start_date = datetime.strptime(row[3],'%Y-%m-%d %H:%M:%S.%f')
		end_date = datetime.strptime(row[4],'%Y-%m-%d %H:%M:%S.%f')

		life_time = end_date-start_date
		model_lifetime = life_time.days + life_time.seconds / 86400

		relative_lifetime = 0

		if project_lifetime != 0:
			relative_lifetime = model_lifetime/project_lifetime
		try: 
			logging.info("Writing to Model_Commit_Summary table")
			controller.insert(project_id, model_name, no_of_commits, no_of_authors,start_date, end_date, model_lifetime,relative_lifetime)

		except Exception as e: 
			logging.info(e)
			logging.info("Writing failted.")

def check_and_delete(project_id , conn, pv, mv, pdc, mdc):
	cur = conn.cursor()
	tables = ['Project_Commit_Summary', 'Model_Commit_Summary','Project_commits','Model_commits']
	for table in tables: 
		cur.execute("SELECT count(*) FROM "+table+" WHERE project_id="+str(project_id))
		rows = cur.fetchall()
		if int(rows[0][0]) == 0: 
			pv.delete(project_id)
			mv.delete(project_id)
			pdc.delete(project_id)
			mdc.delete(project_id)

def get_most_recent_hash(url):
	p = Popen(['git', 'ls-remote', url, '|', 'grep', 'HEAD'], stdout=PIPE)
	output = p.communicate()[0].decode("utf-8")
	return output.split("\t")[0]
def main(is_forked,source_database,dst_database):
	start = time.time()

	path = "workdir"
	dest_project_database_controller = Project_commits_info_Controller(dst_database)
	dest_model_database_controller = Model_commits_info_Controller(dst_database)

	project_verbatim = Project_commits_verbatim_Controller(dst_database)
	model_verbatim = Model_commits_verbatim_Controller(dst_database)
	# create a database connection
	conn = create_connection(source_database)
	dst_conn = create_connection(dst_database)


	to_update_version_sha = dst_database #.replace('.sqlite','')
	databaseHandler = SimulinkRepoInfoController(to_update_version_sha)


	with dst_conn:
		processed_id,processed_mdl_name= get_id_name(dst_conn)

	with conn:
		id_urls = get_repo_id_urls(conn,is_forked)
		for id_url in id_urls:
			id, url ,hash = id_url
			if not os.path.exists(path):
				os.mkdir(path)
			try:             
				if id not in processed_id:
					logging.info("=============Processing {}===========".format(str(id)))
					
					clone = "git clone " + url + " " + path
					os.system(clone)  # Cloning
					recent_hash = get_most_recent_hash(url)

					if is_forked: 
						from_commit = get_root_last_commit_sha(conn,id,path)

					if hash == '' or recent_hash != hash:
						hash = recent_hash
						databaseHandler.update(id,{"version_sha":recent_hash})                    

					#gr = GitRepository(path)
					#gr.checkout(hash)
					url = path
					if is_forked:
						project_lifetime = write_project_commit_info(url,id, hash,dest_project_database_controller,project_verbatim, model_verbatim,is_forked,from_commit)
					else:
						project_lifetime = write_project_commit_info(url,id, hash,dest_project_database_controller,project_verbatim, model_verbatim,is_forked)
					 

					if project_lifetime != -1:
						logging.error("Successfully Inserted into database")
						write_model_commit_info(id,dest_model_database_controller,project_lifetime, dst_conn)
					else:
						logging.error("Error inserting into database")
				else:
					x = 1
					#logging.info("Skipping . ALready Processed {}".format(id))
			except Exception as e:
				logging.error(e)
				continue
			finally:
				if not is_forked:
					check_and_delete(id, dst_conn,project_verbatim,model_verbatim,dest_project_database_controller,dest_model_database_controller)
				#logging.info("=============Done Proessing {}===========".format(str(id)))
				shutil.rmtree(path)
	end = time.time()
	logging.info("IT took {} seconds".format(end - start))





if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Get argument for downloading')
	parser.add_argument('-s', '--src_db', dest="src_db", type=str,
						help='Source database (which has GitHub URLs)')
	parser.add_argument('-d', '--dst_db', dest="dst_db", type=str,
						help='Destination database')
	parser.add_argument('-f', '--forked', dest="forked_flag", default=False,action='store_true',
					help='Boolean value to determine to collect evolution data from forked project | Dont include it for root projects')

	args = parser.parse_args()

	source_database = args.src_db
	dst_database = args.dst_db # BASIC AUTH OR OAUTH 5000 requests per hour ||  30 requests per minute for using SEARCH API
	if dst_database is None: 
		dst_database = source_database
	is_forked = args.forked_flag


	main(is_forked,source_database,dst_database)
