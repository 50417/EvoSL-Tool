import sqlite3
from sqlite3 import Error
import subprocess
import os
import glob

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

def get_all_rows(conn,table):
	cur = conn.cursor()
	cur.execute("SELECT project_id, parent_sha, child_sha, model, block_path, node_type, block_type,is_deleted, is_modified, is_added, is_renamed,id FROM "+table+ " WHERE project_id in (150076757,12136324,194490625,202525754,59244003) and node_type = 'block'")
	rows = cur.fetchall()
	
	ans = {}
	for row in rows: 
		project_id = row[0]
		parent_sha = row[1]
		child_sha = row[2]
		model = row[3]
		block_path = row[4]
		node_type = row[5]
		block_type = row[6]
		is_deleted = row[7]
		is_modified = row[8]
		is_added = row[9]
		is_renamed = row[10] 
		chksum = row[11]

		#print(project_id, parent_sha, child_sha, model, block_path, node_type, block_type,is_deleted, is_modified, is_added, is_renamed)
		new_ele = parent_sha + "-" + child_sha + "-" +  model+ "-" + block_path+ "-" + node_type+ "-" + block_type+ "-" +str(is_deleted)+ "-" + str(is_modified)+ "-" + str(is_added)+ "-" + str(is_renamed)

		if project_id not in ans: 
			ans[project_id] = set()
		ans[project_id].add(new_ele)
	return ans
	

def compare(old, new,project_id ):
	inold_not_inNew = old.difference(new)
	print("2019 IONLY")
	nine = len(inold_not_inNew)

	with open("2019-block.csv",'a') as f:
		for ele in inold_not_inNew: 
			f.write(str(project_id)+","+ele+"\n")
	print("2022 ONLY")
	innew_not_in_old = new.difference(old)
	twenty = len(innew_not_in_old)
	with open("2022-block.csv",'a') as f:
		for ele in innew_not_in_old: 
			f.write(str(project_id)+","+ele+"\n")
	return nine, twenty





def main():
	#evoSL_2019avs2022b_5sampleProjects.sqlite
	db = "" 
	conn = create_connection(db)

	change_2022 = get_all_rows(conn,"model_element_changes_22b")

	change_2019 = get_all_rows(conn,"five_sample_element_changes_19a")
	only_in_19 = 0 
	only_in_22= 0
	total_in_19 = 0 
	total_in_22 = 0
	for project_id in [150076757,12136324,194490625,202525754,59244003]:
		print("=====================================")
		print(project_id)
		
		try:
			total_in_19 += len(change_2019[project_id])
			total_in_22 += len(change_2022[project_id])
			nine, twenty = compare(change_2019[project_id], change_2022[project_id],project_id)
			only_in_19 += nine 
			only_in_22 += twenty
		except Exception as e: 
			print(e)
		print("=====================================")
	print("Total")
	print("Total Number of element changes on 2019a: %d"%total_in_19)
	print("Total Number of element changes  on 2022b: %d"%total_in_22)
	print("Non-overlap")
	print("Number of element changes only on 2019a (but on on 2022b): %d"%only_in_19)
	print("Number of element changes only on 2022b (but on on 2019a): %d"%only_in_22)
	print("fraction")
	x = only_in_19/total_in_19*100
	print("Percentage of 2019a  element changes only on 2019a: %f"%round(x,2))
	print("Percentage of 2022b  element changes only on 2022b: %f"%round(only_in_22/total_in_22*100,2))
	print("Percentage of non overlapping  element changes out of total number of changes in both versions: %f"%round((only_in_19+only_in_22)/(total_in_19+total_in_22)*100,2))







main()