import sqlite3
from sqlite3 import Error
import sys
import logging
import os, shutil
logging.basicConfig(filename='top_X_filter.log', filemode='a',
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

def get_topX_project_ids(conn,topX):
	sql = "SELECT * FROM GitHub_Projects_Commit_Info order by model_commits desc limit "+str(topX)
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	ans = [r[0] for r in rows]
	return ans

def delete_and_copy_table(conn, src_table, dest_table):
	cursor = conn.cursor()

	drop_table_sql = 'DROP TABLE IF EXISTS '+dest_table
	cursor.execute(drop_table_sql)

	copy_table_sql = "CREATE TABLE "+dest_table + " AS SELECT * FROM "+src_table
	print(copy_table_sql)
	cursor.execute(copy_table_sql)
	conn.commit()

def get_changes_count(conn,table):
	sql = "SELECT project_id, parent_sha, child_sha, count(*) c from "+table+" group by project_id, parent_sha, child_sha order by c,parent_sha, child_sha"
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	ans = [{'project_id':r[0],'parent_sha':r[1],'child_sha':r[2],'change_count':r[3]} for r in rows]

	return ans

def are_duplicates(p1, p2):

	if p1['parent_sha'] == p2['parent_sha'] and p1['child_sha'] == p2['child_sha']:
		if p1['change_count'] == p2['change_count']:
			return True
	return False

def delete_from_table(conn, table, project_id, parent_sha, child_sha):
	sql = "DELETE FROM "+table+" WHERE  project_id="+str(project_id)+" AND parent_sha='"+parent_sha+"'"+" AND child_sha='"+child_sha+"'"
	cur = conn.cursor()
	cur.execute(sql)
	conn.commit()
	return cur.rowcount

def delete_all_except(conn, table, project_ids):
	where_clause = " WHERE project_id not in ("+",".join(project_ids)+")"
	sql = "DELETE FROM "+table+where_clause
	cur = conn.cursor()
	cur.execute(sql)
	conn.commit()
	return cur.rowcount
	

def main(): 
	db = ""
	conn = create_connection(db)

	dst_table =""
	delete_and_copy_table(conn, "Model_evolution",dst_table)


	ids = get_topX_project_ids(conn,50)


	project_ids = [] 
	for r in ids:
		project_ids.append(str(r)) 
	discarded_change_counts = delete_all_except(conn,dst_table,project_ids)

	duplicate_change_counts = 0
	res = get_changes_count(conn,dst_table)
	total_res = len(res)
	prev = 0
	cur = 1 
	while cur < total_res:
		if are_duplicates(res[prev], res[cur]):
			rows_affected = delete_from_table(conn,dst_table,res[cur]['project_id'],res[cur]['parent_sha'],res[cur]['child_sha'])			
			logging.info("%d %d have duplicates. Count: %d"%(res[cur]['project_id'],res[prev]['project_id'],res[cur]['change_count']))
			duplicate_change_counts +=res[cur]['change_count']
			assert(rows_affected==res[cur]['change_count'])
		else:
			prev = cur
		cur += 1
	t= discarded_change_counts + duplicate_change_counts
	logging.info("Discarded Counts: %d\n Duplicate Count:%d \n Total Discarded:%d"%(discarded_change_counts,duplicate_change_counts,t))

main()