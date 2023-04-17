import logging
import sqlite3
from sqlite3 import Error
import time
import math
from datetime import datetime
from statistics import variance, stdev
logging.basicConfig(filename='evoSL_sample.log', filemode='a',
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

def calculate_quartiles(list_of_vals, N=1):
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

	return str(math.floor(list_of_vals[0]/N+0.5))+"\t&"+str(math.floor(list_of_vals[n-1]/N+0.5))+"\t&"+str(math.floor(mean/N+0.5))+\
		   "\t&"+str(math.floor(median/N+0.5))+"\t&"+str(math.floor(stdev(list_of_vals)/N+0.5))


def calculate_ratios(list_of_vals,total):
	'''
	args:
		list_of_vals : sorted list
	'''
	sum_list = sum(list_of_vals)
	assert(len(list_of_vals) == 4)
	

	return str(round(list_of_vals[0]/sum_list*100,1))+"\t&"+str(round(list_of_vals[1]/sum_list*100,1))+"\t&"+str(round(list_of_vals[2]/sum_list*100,1))+\
		   "\t&"+str(round(list_of_vals[3]/sum_list*100,1))+"\t&"+str(round(sum_list/total*100,1))


def get_commits(conn,where_clause, project=True):
	'''
	returns number of commits per project or model in a list
	'''
	cur = conn.cursor()
	if project:
		col = 'total_number_of_commits'
	else:
		col = 'model_commits'
	cur.execute("Select "+col+" from Project_Commit_Summary "+where_clause+" order by total_number_of_commits")
	
	rows = cur.fetchall()
	return [r[0] for r in rows]


def get_number_of_authors(conn, where_clause = None):
	'''
	returns number of authors per project or model in a list
	'''
	cur = conn.cursor()
 
	cur.execute("Select number_of_authors from Project_Commit_Summary "+where_clause+"order by number_of_authors")
	
	rows = cur.fetchall()
	return [r[0] for r in rows]

def get_lifetime(conn, where_clause = None):
	'''
	returns absolute lifetime of project or model(days) in a list
	'''
	cur = conn.cursor()
	sql ="select LifeTime_in_days from Project_Commit_Summary"+where_clause+" order by LifeTime_in_days"
	
	cur.execute(sql)

	rows = cur.fetchall()
	return [r[0] for r in rows]

def get_largest_models(conn, where_clause = None):
	'''
	returns absolute lifetime of project or model(days) in a list
	'''
	cur = conn.cursor()
	sql ="select MAX(SCHK_Block_count) m, project_id from models"+where_clause+" group by project_id order by m"

	cur.execute(sql)

	rows = cur.fetchall()
	return [r[0] for r in rows]

def get_avg_models(conn, where_clause = None):
	'''
	returns absolute lifetime of project or model(days) in a list
	'''
	cur = conn.cursor()
	sql ="select AVG(SCHK_Block_count) m, project_id from models"+where_clause+" group by project_id order by m"

	cur.execute(sql)

	rows = cur.fetchall()
	return [r[0] for r in rows]

def get_unique_model(conn, where_clause = None):
	'''
	returns absolute lifetime of project or model(days) in a list
	'''
	cur = conn.cursor()
	sql ="select Count(Distinct model) m, project_id from Cleaned_Model_Element_Changes"+where_clause+" group by project_id order by m"

	cur.execute(sql)

	rows = cur.fetchall()
	return [r[0] for r in rows]

def convert_rows_to_set(rows):
	res = set()
	for r in rows:
		res.add(r[0])
	return res

def get_aggregate_ratio(lst, total):
	rows = len(lst)
	cols = 4
	all_cols = []
	for col in range(cols):
		col_sum = 0
		for row in range(rows):
			col_sum += lst[row][col]
		all_cols.append(col_sum/total*100)
	assert(len(all_cols) == 4)
	

	return str(round(all_cols[0],1))+"\t&"+str(round(all_cols[1],1))+"\t&"+str(round(all_cols[2],1))+\
		   "\t&"+str(round(all_cols[3],1))


def get_evoSL_sample_project_id(conn):
	sql = "Select Distinct project_id from Cleaned_Model_Element_Changes"

	cur = conn.cursor()
	cur.execute(sql)
	rows = cur.fetchall()

	ans =  [r[0] for r in rows]
	project_ids = [] 
	for r in ans:
		project_ids.append(str(r)) 
	return project_ids


def main():
	start = time.time()
	evosl_sample_database = ""
	
	# create a database connection
	conn = create_connection(evosl_sample_database)
	projectids = get_evoSL_sample_project_id(conn)#["64223824","476168345","588267715","20451353","68744081","250217878","366359636","337996515","100999374","261484515","305846578","317540119","595154955","287361574","301176100","267839196","13328139","204030363","60685110","468290383","14375685","237132537","355203229","184514360","194490625","312007661","130222499","295851609","124382232","211239358","118747568","334101825","470647234","113453905","54991377","12136324","126338636","296797895","93419327","213199113","546546451","370616572","39600731","389552676","432334495","299664596","789683","47131658","419153598","131173589"]
	
	where_clause = " where project_id in ("+",".join(projectids)+") "

	
	print("Project level metrics")
	print("Project Metric & Min. & Max. & Mean& Median & Std. Dev")

	largest_models  = calculate_quartiles(get_largest_models(conn,where_clause))
	print("Largest model size [blocks] &  "+ largest_models)

	avg_models  = calculate_quartiles(get_avg_models(conn,where_clause))
	print("Avg model size [blocks] &  "+ avg_models)

	unique_models  = calculate_quartiles(get_unique_model(conn,where_clause))
	print("Unique mdl/slx [blocks] &  "+ unique_models)


	no_of_commits  = calculate_quartiles(get_commits(conn,where_clause))
	print("Commits \t\t&  "+ no_of_commits)

	no_of_model_commits  = calculate_quartiles(get_commits(conn,where_clause,False))
	print("Commits\\textsubscript{MS} &    "+ no_of_model_commits)
	
	lifetime_in_days = calculate_quartiles(get_lifetime(conn,where_clause),30)
	print("Durations [Months]\t&    " + lifetime_in_days)
	number_of_authors = calculate_quartiles(get_number_of_authors(conn,where_clause))
	print("Authors \t\t&    " + number_of_authors)
	


	print("=======================================================")

	
	Cstudy_block = [192636	,401518,	368620,	648276]
	Cstudy_Line = [2074	,22814,	444958,	664416]
	Cstudy_port = [279,	25647,	25647,	41298]
	Cstudy_mask = [8,	10258,	8732,	32682]
	Cstudy_annotation = [992,	2542,	8371,	12596]
	Cstudy_configuration = [0,	640,	0,	10]

	CStudy = [Cstudy_block,Cstudy_Line,Cstudy_port,Cstudy_mask,Cstudy_annotation,Cstudy_configuration]
	total = 0 
	for lst in CStudy: 
		total+=sum(lst)

	for lst in CStudy:
		print(calculate_ratios(lst,total)) 
	print(get_aggregate_ratio(CStudy,total))

	print("=======================================================")
	'''
	evoSample_block = [24988, 84430, 64433, 82708]
	evoSample_Line = [504, 4255, 97774, 119080]
	evoSample_port = [0, 124, 10621, 13617]
	evoSample_mask = [0, 2768, 1497, 1984]
	evoSample_annotation = [390, 426, 2468, 2183]
	evoSample_configuration = [142, 4130, 220, 1862]
	'''
	evoSample_block = [30183 , 106093 , 69985 , 93295]
	evoSample_Line = [558 , 4385 , 106575 , 134340 ]
	evoSample_port = [0 , 124 , 10774 , 13951]
	evoSample_mask = [0 , 3148 , 1709 , 2343]
	evoSample_annotation = [ 407 , 482 , 2871 , 2723]
	evoSample_configuration = [142 , 4130 , 220 , 1862 ]

	evoSample = [evoSample_block,evoSample_Line,evoSample_port,evoSample_mask,evoSample_annotation,evoSample_configuration]
	total = 0 
	for lst in evoSample: 
		total+=sum(lst)

	for lst in evoSample:
		print(calculate_ratios(lst,total))
	print(get_aggregate_ratio(evoSample,total)) 
		




if __name__ == '__main__':
	main()