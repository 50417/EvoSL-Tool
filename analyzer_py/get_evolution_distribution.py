import logging
import sqlite3
from sqlite3 import Error
import time
import sys
import math
from datetime import datetime
from statistics import variance, stdev
logging.basicConfig(filename='analyze_projects.log', filemode='a',
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

#logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
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

def get_commits(conn,where_clause=None):
	'''
	returns number of commits per project or model in a list
	'''
	cur = conn.cursor()
	if where_clause is None: 
		sql = "Select total_number_of_commits from Project_Commit_Summary order by total_number_of_commits"
	else:
		sql = "Select total_number_of_commits from Project_Commit_Summary"+where_clause+" order by total_number_of_commits"
	cur.execute(sql)
	logging.info(sql)

	rows = cur.fetchall()
	return [r[0] for r in rows]

def get_merge_commits_projects(conn, where_clause=None):
	cur = conn.cursor()
	if where_clause is  None: 
		sql = "select cast(Number_of_merge_commits as float)/cast(Total_number_of_commits as float)*100 per from Project_Commit_Summary order by per"
	else: 
		sql = "select cast(Number_of_merge_commits as float)/cast(Total_number_of_commits as float)*100 per from Project_Commit_Summary"+where_clause+" order by per"
	cur.execute(sql)
	logging.info(sql)
	rows = cur.fetchall()
	return [r[0] for r in rows]

def calculate_quartiles(list_of_vals):
	'''
	args:
		list_of_vals : sorted list
	'''
	list_of_vals.sort()
	sum_list = sum(list_of_vals)
	n = len(list_of_vals)
	mean = sum_list/n
	if n % 2 == 0:
		median1 = list_of_vals[n // 2]
		median2 = list_of_vals[n // 2 - 1]
		median = (median1 + median2) / 2
	else:
		median = list_of_vals[n // 2]

	return str(math.floor(list_of_vals[0]+0.5))+"\t&"+str(math.floor(list_of_vals[n-1]+0.5))+"\t&"+str(math.floor(mean+0.5))+\
		   "\t&"+str(math.floor(median+0.5))+"\t&"+str(math.floor(stdev(list_of_vals)+0.5))

def get_number_of_authors(conn, where_clause = None):
	'''
	returns number of authors per project or model in a list
	'''
	cur = conn.cursor()

	if where_clause is  None: 
		sql = "Select number_of_authors from Project_Commit_Summary order by number_of_authors"
	else:
		sql = "Select number_of_authors from Project_Commit_Summary" + where_clause+" order by number_of_authors"
	cur.execute(sql)
	logging.info(sql)
	rows = cur.fetchall()
	return [r[0] for r in rows]

def get_lifetime(conn,where_clause = None):
	'''
	returns absolute lifetime of project or model(days) in a list
	'''
	cur = conn.cursor()
	sql ="select LifeTime_in_days from Project_Commit_Summary order by LifeTime_in_days"
	if where_clause is not None: 
		sql ="select LifeTime_in_days from Project_Commit_Summary"+where_clause+" order by LifeTime_in_days"
	logging.info(sql)
	cur.execute(sql)

	rows = cur.fetchall()
	return [r[0] for r in rows]

def get_commit_per_day(conn,where_clause = None):
	cur = conn.cursor()
	if where_clause is None: 
		sql = "select Commit_per_day from Project_Commit_Summary order by Commit_per_day"
	else: 
		sql = "select Commit_per_day from Project_Commit_Summary"+where_clause+"order by Commit_per_day"
	cur.execute(sql)
	logging.info(sql)
	rows = cur.fetchall()
	return [r[0] for r in rows]

def convert_rows_to_set(rows):
	res = set()
	for r in rows:
		res.add(r[0])
	return res

def get_model_author_per(conn,where_clause = None):
	model_author_per = []
	cur = conn.cursor()
	if where_clause is None: 
		project_ids_sql  = "select project_id from Project_Commit_Summary"
	else: 
		project_ids_sql  = "select project_id from Project_Commit_Summary"+where_clause
	logging.info(project_ids_sql)
	cur.execute(project_ids_sql)
	rows = cur.fetchall()
	project_ids = [r[0] for r in rows]
	for id in project_ids:
		model_author_sql = "select author_email from Model_commits where project_id = " + str(id)
		cur.execute(model_author_sql)
		model_author_set = convert_rows_to_set(cur.fetchall())

		project_author_sql = "select author_email from Project_commits where project_id = " + str(id)
		cur.execute(project_author_sql)
		project_author_set = convert_rows_to_set(cur.fetchall())

		model_author_per.append(len(model_author_set)/len(project_author_set)*100)
		#print(model_commits_per)
	return sorted(model_author_per)

def get_model_commits_per(conn,where_clause=None):
	model_commits_per = []
	cur = conn.cursor()

	project_ids_sql  = "select project_id from Project_Commit_Summary"
	if where_clause is not None:
		project_ids_sql+= where_clause
	cur.execute(project_ids_sql)
	logging.info(project_ids_sql)
	rows = cur.fetchall()
	project_ids = [r[0] for r in rows]
	for id in project_ids:
		model_hash_sql = "select hash from Model_commits where project_id = " + str(id)
		cur.execute(model_hash_sql)
		model_hash_set = convert_rows_to_set(cur.fetchall())

		project_hash_sql = "select hash from Project_commits where project_id = " + str(id)
		cur.execute(project_hash_sql)
		project_hash_set = convert_rows_to_set(cur.fetchall())
		if len(model_hash_set) == 0 :
			print("jere")
		model_commits_per.append(len(model_hash_set)/len(project_hash_set)*100)
		#print(model_commits_per)
	return sorted(model_commits_per)



def get_root_ids(conn):
	cur = conn.cursor()
	cur.execute("SELECT project_id FROM root_projects")

	rows = cur.fetchall()

	ans =  [r[0] for r in rows]
	project_ids = [] 
	for r in ans:
		project_ids.append(str(r)) 
	return project_ids

#sql = "select cast(Model_commits as float)/cast(Total_number_of_commits as float)*100 per from Project_Commit_Summary order by per"

def main():
	start = time.time()
	evosl_database = ""
	evoslplus_database = ""

	# create a database connection
	plus_conn = create_connection(evoslplus_database)

	#To get only root projects information. Comment the where clause to consider everything
	plus_root_projectids = get_root_ids(plus_conn)
	print(len(plus_root_projectids))
	plus_where_clause = " where project_id in ("+",".join(plus_root_projectids)+") "

	print("Project level metrics")
	print("Project Metric & Min. & Max. & Mean& Median & Std. Dev")

	plus_no_of_commits  = calculate_quartiles(get_commits(plus_conn,plus_where_clause))
	print("Number of commits &"+ plus_no_of_commits)
	plus_merge_percent = calculate_quartiles(get_merge_commits_projects(plus_conn,plus_where_clause))
	print("Merge commits in %&" + plus_merge_percent)
	plus_number_of_authors = calculate_quartiles(get_number_of_authors(plus_conn,plus_where_clause))
	print("Number of authors&" + plus_number_of_authors)
	plus_lifetime_in_days = calculate_quartiles(get_lifetime(plus_conn,plus_where_clause))
	print("Lifetime in days&" + plus_lifetime_in_days)
	plus_commit_per_day= calculate_quartiles(get_commit_per_day(plus_conn,plus_where_clause))
	print("Commit per day&" + plus_commit_per_day)
	plus_model_commits_per = calculate_quartiles(get_model_commits_per(plus_conn,plus_where_clause))
	print("Model commits in %&"+ plus_model_commits_per)
	plus_model_author_per = calculate_quartiles(get_model_author_per(plus_conn,plus_where_clause))
	print("Model authors in %&"+ plus_model_author_per)


	print("=======================================================")

	# create a database connection
	conn = create_connection(evosl_database)

	#To get only root projects information. Comment the where clause to consider everything
	root_projectids = get_root_ids(conn)
	print(len(root_projectids))
	where_clause = " where project_id in ("+",".join(root_projectids)+") "

	print("Project level metrics")
	print("Project Metric & Min. & Max. & Mean& Median & Std. Dev")

	evosl_no_of_commits  = calculate_quartiles(get_commits(conn,where_clause))
	print("Number of commits &"+ evosl_no_of_commits)
	evosl_merge_percent = calculate_quartiles(get_merge_commits_projects(conn,where_clause))
	print("Merge commits in %&" + evosl_merge_percent)
	evosl_number_of_authors = calculate_quartiles(get_number_of_authors(conn,where_clause))
	print("Number of authors&" + evosl_number_of_authors)
	evosl_lifetime_in_days = calculate_quartiles(get_lifetime(conn,where_clause))
	print("Lifetime in days&" + evosl_lifetime_in_days)
	evosl_commit_per_day= calculate_quartiles(get_commit_per_day(conn,where_clause))
	print("Commit per day&" + evosl_commit_per_day)
	evosl_model_commits_per = calculate_quartiles(get_model_commits_per(conn,where_clause))
	print("Model commits in %&"+ evosl_model_commits_per)
	evosl_model_author_per = calculate_quartiles(get_model_author_per(conn,where_clause))
	print("Model authors in %&"+ evosl_model_author_per)

	print("=======================================================")


	sample_ids = ["64223824","476168345","588267715","20451353","68744081","250217878","366359636","337996515","100999374","261484515","305846578","317540119","595154955","287361574","301176100","267839196","13328139","204030363","60685110","468290383","14375685","237132537","355203229","184514360","194490625","312007661","130222499","295851609","124382232","211239358","118747568","334101825","470647234","113453905","54991377","12136324","126338636","296797895","93419327","213199113","546546451","370616572","39600731","389552676","432334495","299664596","789683","47131658","419153598","131173589"]
	print(len(sample_ids))
	
	# create a database connection
	conn = create_connection(evosl_database)
	where_clause = " where project_id in ("+",".join(sample_ids)+") "

	print("Project level metrics")
	print("Project Metric & Min. & Max. & Mean& Median & Std. Dev")

	sample_no_of_commits  = calculate_quartiles(get_commits(conn,where_clause))
	print(sample_no_of_commits)
	print("Number of commits &"+ sample_no_of_commits)
	sample_merge_percent = calculate_quartiles(get_merge_commits_projects(conn,where_clause))
	print("Merge commits in %&" + sample_merge_percent)
	sample_number_of_authors = calculate_quartiles(get_number_of_authors(conn,where_clause))
	print("Number of authors&" + sample_number_of_authors)
	sample_lifetime_in_days = calculate_quartiles(get_lifetime(conn,where_clause))
	print("Lifetime in days&" + sample_lifetime_in_days)
	sample_commit_per_day= calculate_quartiles(get_commit_per_day(conn,where_clause))
	print("Commit per day&" + sample_commit_per_day)
	sample_model_commits_per = calculate_quartiles(get_model_commits_per(conn,where_clause))
	print("Model commits in %&"+ sample_model_commits_per)
	sample_model_author_per = calculate_quartiles(get_model_author_per(conn,where_clause))
	print("Model authors in %&"+ sample_model_author_per)

	print("=======================================================")

	print("Project Metric & Min. & Max. & Mean& Median & Std. Dev & Min. & Max. & Mean& Median & Std. Dev")

	print("Commits &"+ plus_no_of_commits+"&"+ evosl_no_of_commits+"&"+ sample_no_of_commits + "\\\\")
	
	print("Commits / day  &" + plus_commit_per_day+"&"+evosl_commit_per_day+"&"+sample_commit_per_day+ "\\\\")
	
	print("Commits\\textsubscript{$\\succ$} [\%] & " + plus_merge_percent+"&"+evosl_merge_percent+"&"+sample_merge_percent+ "\\\\")
	#
	
	print("Commits\\textsubscript{MS} &"+ plus_model_commits_per+"&"+evosl_model_commits_per+"&"+sample_model_commits_per+ "\\\\")

	print("Authors &" + plus_number_of_authors+"&"+evosl_number_of_authors+"&"+sample_number_of_authors+ "\\\\")

	
	print("Authors\\textsubscript{MS} [\%] & "+ plus_model_author_per+"&"+evosl_model_author_per+"&"+sample_model_author_per+ "\\\\")

	print("Durations [days] &" + plus_lifetime_in_days+"&"+evosl_lifetime_in_days+"&"+sample_lifetime_in_days+ "\\\\")

	
	

	

	




if __name__ == '__main__':
	main()