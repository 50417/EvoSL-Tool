import sqlite3
from sqlite3 import Error
import sys
import logging
import os, shutil
from statistics import variance, stdev

logging.basicConfig(filename='get_model_change_project_metrics.log', filemode='a',
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

def get_project_ids(conn,table): 
	sql = "SELECT DISTINCT project_id from "+table
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	ans = [r[0] for r in rows]
	return ans

def domain(conn, ids):
	
	sql = "SELECT description, topics from github_projects where project_id in ("+ids+")"
	print(sql)	

def get_avg_block_size(conn,all_ids):
	sql = "SELECT file_id, AVG(SCHK_BLOCK_COUNT) from Github_models GROUP BY file_id HAVING file_id in ("+all_ids+")"
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	ans = [r[1] for r in rows]
	return ans

def get_max_block_size(conn,all_ids):
	sql = "SELECT file_id, MAX(SCHK_BLOCK_COUNT) from Github_models GROUP BY file_id HAVING file_id in ("+all_ids+")"
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	ans = [r[1] for r in rows]
	return ans
def calculate_quartiles(list_of_vals, lifetime=False):
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
    if lifetime:
    	return str(round(list_of_vals[0]/365,2))+"\t&"+str(round(list_of_vals[n-1]/365,2))+"\t&"+str(round(mean/365,2))+\
           "\t&"+str(round(median/365,2))+"\t&"+str(round(stdev(list_of_vals)/365,2))

    return str(round(list_of_vals[0],2))+"\t&"+str(round(list_of_vals[n-1],2))+"\t&"+str(round(mean,2))+\
           "\t&"+str(round(median,2))+"\t&"+str(round(stdev(list_of_vals),2))

def get_commit_metadata(conn,metadata,all_ids ):
	sql = "SELECT "+metadata+" from Project_Commit_Summary WHERE project_id in ("+all_ids+")"
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	ans = [r[0] for r in rows]
	return ans

def get_unique_model_file_analyzed(conn,table, all_ids):
	sql = "SELECT project_id, count(DISTINCT model) from "+table+" GROUP BY project_id HAVING project_id in ("+all_ids+")"
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	ans = [r[1] for r in rows]
	return ans


def main():
	#EvoSL Sample DB
	db = ""
	conn = create_connection(db)

	ele_change_table = "Model_Element_Changes"
	dst_table ="Github_models"
	proj_ids = get_project_ids(conn, dst_table)
	all_ids  = ",".join([str(proj) for proj in proj_ids])

	ans = []
	ans.append(get_avg_block_size(conn,all_ids))
	ans.append(get_max_block_size(conn,all_ids))

	ans.append(get_commit_metadata(conn,"total_number_of_commits",all_ids))
	ans.append(get_commit_metadata(conn,"model_commits",all_ids))
	ans.append(get_commit_metadata(conn,"lifetime_in_days",all_ids))
	ans.append(get_commit_metadata(conn,"number_of_authors",all_ids))

	ans.append(get_unique_model_file_analyzed(conn,ele_change_table , all_ids))
	for i in range(len(ans)):
		val = ans[i]
		#print(len(a))
		if i == 4:
			print(calculate_quartiles(val, True) + "\\\\")

		else: 	
			print(calculate_quartiles(val) + "\\\\")


main()