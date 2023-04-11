import sqlite3
from sqlite3 import Error
import sys
import logging
import os, shutil
logging.basicConfig(filename='remove_duplicate.log', filemode='a',
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

def get_project_commit_info(conn):
	sql = "Select * from Project_Commit_Summary order by total_number_of_commits"
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	results = [{'project_id':r[0],'commits':r[1],'merge_commits':r[2],'authors':r[3],'first_commit':r[4],'last_commit':r[5],'lifetime':r[6],'commit_per_day':r[7],'model_commit':r[8],'model_authors':r[9]} for r in rows]
	return results

def are_potential_dup(p1, p2):
	if p1['commits'] == p2['commits'] and p1['merge_commits'] == p2['merge_commits'] \
	and p1['authors'] == p2['authors'] and p1['first_commit'] == p2['first_commit'] \
	and p1['last_commit'] == p2['last_commit'] and p1['lifetime'] == p2['lifetime']\
	and p1['commit_per_day'] == p2['commit_per_day'] and p1['model_commit'] == p2['model_commit']\
	and p1['model_authors'] == p2['model_authors']:
		return True
	else:
		return False

def get_all_hashes(conn,file_id):
	sql = "select hash from project_commits where project_id = "+str(file_id)
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	ans = set()
	for r in rows:
		ans.add(r[0])

	return ans

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






def main():
	folder_where_data_is_stored = ''
	db = ''
	conn = create_connection(db)
	res = get_project_commit_info(conn)
	number_of_proj = len(res)
	logging.info("Number of projects : "+str(number_of_proj))
	prev = 0
	cur = 1 
	to_be_deleted = []
	while cur < number_of_proj:
		if are_potential_dup(res[prev], res[cur]):
			logging.info("======================================================")
			logging.info('%d and %d are potential duplicates' %(res[prev]['project_id'],res[cur]['project_id']))
			prev_hashes = get_all_hashes(conn, res[prev]['project_id'])
			cur_hashes = get_all_hashes(conn, res[cur]['project_id'])

			prev_cur_diff = prev_hashes.difference(cur_hashes)
			cur_prev_diff = cur_hashes.difference(prev_hashes)
			if len(prev_cur_diff) == 0 and len(cur_prev_diff) == 0: 
				logging.info('%d and %d are certainly duplicates' %(res[prev]['project_id'],res[cur]['project_id']))
				if res[prev]['project_id'] < res[cur]['project_id']:
					to_delete_id = res[cur]['project_id']
				else: 
					to_delete_id = res[prev]['project_id']
					prev = cur
				logging.info("DELETED PRoject id %d" %(to_delete_id))
				deleted_id = delete_from_table(conn,to_delete_id)

				if deleted_id != -1: 
					to_be_deleted.append(deleted_id)
			logging.info("======================================================")
			
		else:
			prev = cur
		cur += 1

	if folder_where_data_is_stored == '':
		tmp = []
		for s in to_be_deleted: 
			print(s)
			print(str(s))
			tmp.append(str(s))
		logging.info("Please deleted these project id %s"%(",".join(tmp)))
	else:
		for proj_id in to_be_deleted:  
			try: 
				to_delete = os.path.join(folder_where_data_is_stored, str(proj_id))
				shutil.rmtree(to_delete)
			except Exception as e: 
				logging.error(e)
				logging.info("Error Deleting %d . PLease delete yourself"%(proj_id))


main()
