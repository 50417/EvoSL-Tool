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
	sql = "SELECT * FROM Project_Commit_Summary order by model_commits desc limit "+str(topX)
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

def get_changes_count_with_nodetype(conn,table):
	sql = '''
			
				Select project_id, parent_sha, child_sha,
				 Case  
					 WHEN is_deleted > 0 THEN "Deleted" 
					 WHEN is_added > 0 THEN "Added" 
					 WHEN (is_modified = 1 and is_renamed=0) THEN "Modified" 
					 WHEN (is_modified = 0 and is_renamed=1) THEN "Renamed" 
					 WHEN (is_modified = 1 and is_renamed=1) THEN "ModifiedRenamed" 
				 END AS change_type,
				totalCount  FROM (	
				 SELECT project_id, parent_sha, child_sha, is_deleted, is_added, is_modified, is_renamed, count(*) as totalCount
				 FROM '''+table+'''
				  WHERE is_deleted = 1
				or is_added = 1
				 or is_modified = 1
				 or is_renamed = 1
				 group by project_id, parent_sha, child_sha, is_deleted, is_added, is_modified, is_renamed);
	'''
	cur = conn.cursor()
	cur.execute(sql)

	rows = cur.fetchall()
	ans = [{'project_id':r[0],'parent_sha':r[1],'child_sha':r[2],'change_type':r[3],'change_count':r[4]} for r in rows]

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

def sum_and_sort_count(count_with_nodetype,ids):
	#change_types = ['Renamed','Modified','Deleted','Added']
	modified_renamed_change_type = 'ModifiedRenamed'
	tmp_dict = {}
	for ele in count_with_nodetype:
		key = str(ele['project_id']) + "-" + ele['parent_sha']+ "-"+ele['child_sha']
		if  key not in  tmp_dict:
			tmp_dict[key] = 0
		
		if ele['change_type'] == modified_renamed_change_type:
			tmp_dict[key] += ele['change_count']
		tmp_dict[key] += ele['change_count']

	sorted_dict = sorted(tmp_dict.items(), key=lambda x:x[1])
	res = []
	for lst_ele in sorted_dict:

		k,val = lst_ele
		project_id, parent_sha, child_sha = k.split('-')
		project_id_int = int(project_id)

		res.append({'project_id':project_id_int,'parent_sha':parent_sha,'child_sha':child_sha,'change_count':val})


	new_res = sorted(res, key=lambda d: (d['parent_sha'],d['child_sha']))
	return new_res



		




	
def get_unknown_counts(conn, table): 
	where_clause = " WHERE node_type = 'unknown' "
	sql = "SELECT SUM(is_added),SUM(is_modified),SUM(is_renamed),SUM(is_deleted) FROM "+table+where_clause
	cur = conn.cursor()
	cur.execute(sql)
	rows = cur.fetchall()
	ans = rows[0][0] + rows[0][1] + rows[0][2]+ rows[0][3]	
	return ans

def main(): 
	db = ""
	conn = create_connection(db)

	ele_change_table = "Model_Element_Changes"
	dst_table ="Sample_Model_Element_Changes"
	delete_and_copy_table(conn, ele_change_table,dst_table)

	x = 50
	ids = get_topX_project_ids(conn,x)


	project_ids = [] 
	for r in ids:
		project_ids.append(str(r)) 
	discarded_change_counts = delete_all_except(conn,dst_table,project_ids)

	duplicate_change_counts = 0
	count_with_nodetype = get_changes_count_with_nodetype(conn,dst_table)
	res = sum_and_sort_count(count_with_nodetype,ids)
	total_res = len(res)
	prev = 0
	cur = 1 
	inital_count = res[prev]['change_count']
	while cur < total_res:
		inital_count += res[cur]['change_count']
		if are_duplicates(res[prev], res[cur]):
			rows_affected = delete_from_table(conn,dst_table,res[cur]['project_id'],res[cur]['parent_sha'],res[cur]['child_sha'])			
			logging.info("%d %d have duplicates. Count: %d"%(res[cur]['project_id'],res[prev]['project_id'],res[cur]['change_count']))
			duplicate_change_counts +=res[cur]['change_count']
			#assert(rows_affected==res[cur]['change_count'])
		else:
			prev = cur
		cur += 1
	unknown_count = get_unknown_counts(conn, dst_table)

	t=  duplicate_change_counts + unknown_count
	logging.info("Intial Count: %d\n"%(inital_count))
	logging.info("Discarded rows: %d\n Unknown Count:%d \n Duplicate Count:%d \n Total Discarded:%d"%(discarded_change_counts,unknown_count,duplicate_change_counts,t))

main()