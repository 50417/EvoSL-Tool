import sqlite3
from sqlite3 import Error
import sys
import logging
import os, shutil
logging.basicConfig(filename='sample_evoSL_from_raw_projects.log', filemode='a',
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def create_connection( db_file):
	""" create a database connection to the SQLite database
		specified by the db_file
	:param db_file: database file
	:return: Connection object or None
	"""
	conn = None
	try:
		conn = sqlite3.connect(db_file)
	except Error as e:
		print("noooooo")

	return conn

def get_model_commit_info(conn,root_projectids):
	where_clause = " where project_id in ("+",".join(root_projectids)+") "
	sql = "select project_id, max(total_number_of_commits) m from Model_Commit_Summary"+where_clause+"group by project_id having m = 1"
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	results = [r[0] for r in rows]
	return results

def get_values_from_table(conn,sql):
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	ans = [str(r[0]) for r in rows]
	return ','.join(ans)

def delete_from_table(conn, project_id):
	try:
		cur = conn.cursor()
		
		issue_sql = "SELECT issue_id from Issues where project_id = "+str(project_id)
		issue_ids = get_values_from_table(conn, issue_sql)

		pr_sql = "SELECT pr_id from PR where project_id = "+str(project_id)
		pr_ids = get_values_from_table(conn, pr_sql)
		
		pr_tables = ['Issue_PR_Comments','Issue_PR_links','PR_Commits']

		for table in pr_tables:
			col = 'pr_id'
			if table == 'Issue_PR_Comments':
				col = 'issue_pr_id'
			sql = "DELETE FROM "+table+" WHERE "+col+" in ("+pr_ids+")"
			cur.execute(sql)
			logging.info("%d rows were affected in %s "%(cur.rowcount, table))

		issue_tables = ['Issue_PR_Comments','Issue_PR_links'] 
		for table in issue_tables:
			col = 'issue_id'
			if table == 'Issue_PR_Comments':
				col = 'issue_pr_id'
			sql = "DELETE FROM "+table+" WHERE "+col+" in ("+issue_ids+")"
			cur.execute(sql)
			logging.info("%d rows were affected in %s "%(cur.rowcount, table))

		tables = ['Project_Commit_Summary','Model_Commit_Summary','Project_commits',\
		'Model_commits', 'Root_Projects','Forked_Projects','Issues','PR']
		for table in tables:
			col_name = 'project_id'
			if table == 'Forked_Projects':
				col_name = 'forked_project_id'
			sql = "DELETE FROM "+table+" WHERE "+col_name+" in ("+str(project_id)+")"
			cur.execute(sql)
			logging.info("%d rows were affected in %s "%(cur.rowcount, table))
	except Exception as e:
		logging.error(e)
		logging.info('Error deleting %d' %(project_id))
		return -1 
	conn.commit()
	return project_id

def get_root_ids(conn):
	cur = conn.cursor()
	cur.execute("SELECT project_id FROM root_projects")

	rows = cur.fetchall()

	ans =  [r[0] for r in rows]
	project_ids = [] 
	for r in ans:
		project_ids.append(str(r)) 
	return project_ids




def main():
	# EvoSL is sampled from raw data. Make a copy of the data to preserve it.
	folder_where_data_is_stored = ''
	db = ''
	conn = create_connection(db)
	root_ids = get_root_ids(conn)
	
	res = get_model_commit_info(conn,root_ids)
	number_of_proj = len(res)
	logging.info("Number of projects : "+str(number_of_proj))
	
	for proj_id in res:
		delete_from_table(conn, proj_id) 


		if folder_where_data_is_stored == '':
			logging.info("Please deleted these project id %s"%(str(proj_id)))
		else:
			try: 
				to_delete = os.path.join(folder_where_data_is_stored, str(proj_id))
				shutil.rmtree(to_delete)
			except Exception as e: 
				logging.error(e)
				logging.info("Error Deleting %d . PLease delete yourself"%(proj_id))
	logging.info("%s"%(",".join(str(m) for m in res)))


main()