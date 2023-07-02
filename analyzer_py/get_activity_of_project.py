import logging
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import sqlite3
import numpy as np
"""matplotlib.use("pgf")"""
matplotlib.rcParams.update({
	'font.family': 'Times New Roman',
	'font.size' : 14,

})
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
def date_range(start, end, intv):

	diff = (end  - start ) / intv
	ans = []
	for i in range(intv):
		endpoint = (start + diff * i)
		date_string = endpoint.strftime('%Y-%m-%d %H:%M:%S')
		ans.append(date_string)
	return ans

def get_project_ids(conn,where_clause = None):
	cur = conn.cursor()
	project_ids_sql = "select project_id from Project_Commit_Summary"
	if where_clause is not None: 
		project_ids_sql += where_clause
	cur.execute(project_ids_sql)
	rows = cur.fetchall()
	project_ids = [r[0] for r in rows]
	return project_ids
def get_start_end_dates(conn,id):
	sql = "select first_commit,last_commit from Project_Commit_Summary where project_id ="+str(id)
	cur = conn.cursor()

	cur.execute(sql)
	rows = cur.fetchall()


	for r in rows:
		#x = time.strptime(r[0], '%Y-%m-%d %H:%M:%S')
		start_date = r[0].split(" ")
		start_date[-1] = start_date[-1][:-7]
		start_date = " ".join(start_date)

		start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

		end_date = r[1].split(" ")
		end_date[-1] = end_date[-1][:-7]
		end_date = " ".join(end_date)

		end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
		logging.info("Start Date : "+start_date.strftime('%Y-%m-%d %H:%M:%S'))
		logging.info("End Date : "+end_date.strftime('%Y-%m-%d %H:%M:%S'))
	return start_date,end_date

def project_total_commits(conn,id):
	cur = conn.cursor()
	sql = "select total_number_of_commits from Project_Commit_Summary where project_id  ="+str(id)
	cur.execute(sql)

	rows = cur.fetchall()
	count = int(rows[0][0])
	return count

def model_total_commits(conn,id):
	cur = conn.cursor()
	sql = "select count(distinct hash) from model_commits where project_id  ="+str(id)
	cur.execute(sql)

	rows = cur.fetchall()
	count = int(rows[0][0])
	return count

def model_modified_total_commits(conn,id):
	cur = conn.cursor()
	sql = "select count(*) from model_commits where project_id  ="+str(id)
	cur.execute(sql)

	rows = cur.fetchall()
	count = int(rows[0][0])
	return count

def get_number_of_model_under_development(conn,id):
	cur = conn.cursor()
	sql = "select count(distinct(model_name)) c from Model_commits where project_id  ="+str(id)
	cur.execute(sql)

	rows = cur.fetchall()
	count = int(rows[0][0])
	return count



def get_project_commit_distribution(conn,id,date_range_buckets):
	cur = conn.cursor()
	total_commits = project_total_commits(conn,id)
	rel_commits_distribution = []
	commit_counts = []
	logging.info(date_range_buckets)
	for i in range(len(date_range_buckets)-1):
		sql = "select count(*) as c from Project_commits where project_id ="+ \
			  str(id) +" and committer_date>="+"'"+date_range_buckets[i]+"' and "+\
														   "committer_date<" +"'"+date_range_buckets[i+1]+"'"
		logging.info("Project Commits Distribute SQL : "+ sql)
		cur.execute(sql)
		rows = cur.fetchall()
		count = int(rows[0][0])
		commit_counts.append(count)
		rel_commits_distribution.append((count/total_commits)*100)
	sql = "select count(*) as c from Project_commits where project_id =" + \
		  str(id) + " and committer_date>=" + "'" + date_range_buckets[len(date_range_buckets)-1]+"'"
	logging.info("Project Commits Distribute SQL : "+ sql)
	cur.execute(sql)
	rows = cur.fetchall()
	count = int(rows[0][0])
	commit_counts.append(count)
	rel_commits_distribution.append(count / total_commits*100)
	logging.info("Project ID {} LifeCycle: {}".format(id,rel_commits_distribution) )
	assert(total_commits == sum(commit_counts))
	return rel_commits_distribution


def get_model_commit_distribution(conn,id,date_range_buckets):
	cur = conn.cursor()
	total_commits = model_total_commits(conn,id)
	rel_commits_distribution = []
	commit_counts = []
	logging.info(date_range_buckets)
	for i in range(len(date_range_buckets)-1):
		sql = "select count(distinct hash) as c from Model_commits where project_id ="+ \
			  str(id) +" and committer_date>="+"'"+date_range_buckets[i]+"' and "+\
														   "committer_date<" +"'"+date_range_buckets[i+1]+"'"
		logging.info("Model Commits Distribute SQL : "+ sql)
		cur.execute(sql)
		rows = cur.fetchall()
		count = int(rows[0][0])
		commit_counts.append(count)
		rel_commits_distribution.append((count/total_commits)*100)
	sql = "select count(distinct hash) as c from Model_commits where project_id =" + \
		  str(id) + " and committer_date>=" + "'" + date_range_buckets[len(date_range_buckets)-1]+"'"
	logging.info("Model Commits Distribute SQL : "+ sql)
	cur.execute(sql)
	rows = cur.fetchall()
	count = int(rows[0][0])
	commit_counts.append(count)
	rel_commits_distribution.append(count / total_commits*100)
	logging.info("Project ID {} Model Commits: {}".format(id,rel_commits_distribution) )
	#assert(total_commits == sum(commit_counts))
	return rel_commits_distribution

def get_model_modified_commit_distribution(conn,id,date_range_buckets):
	cur = conn.cursor()
	total_commits = model_modified_total_commits(conn,id)
	rel_commits_distribution = []
	commit_counts = []
	logging.info(date_range_buckets)
	for i in range(len(date_range_buckets)-1):
		sql = "select count(*) as c from Model_commits where project_id ="+ \
			  str(id) +" and committer_date>="+"'"+date_range_buckets[i]+"' and "+\
														   "committer_date<" +"'"+date_range_buckets[i+1]+"'"
		logging.info("Model Commits Distribute SQL : "+ sql)
		cur.execute(sql)
		rows = cur.fetchall()
		count = int(rows[0][0])
		commit_counts.append(count)
		if total_commits==0:
			rel_commits_distribution.append(0)
		else:
			rel_commits_distribution.append((count / total_commits) * 100)
	sql = "select count(*) as c from Model_commits where project_id =" + \
		  str(id) + "  and committer_date>=" + "'" + date_range_buckets[len(date_range_buckets)-1]+"'"
	logging.info("Model Commits Distribute SQL : "+ sql)
	cur.execute(sql)
	rows = cur.fetchall()
	count = int(rows[0][0])
	commit_counts.append(count)
	if total_commits == 0:
		rel_commits_distribution.append(0)
	else:
		rel_commits_distribution.append((count / total_commits) * 100)
	logging.info("Project ID {} Model Modified: {}".format(id,rel_commits_distribution) )
	#assert(total_commits == sum(commit_counts))
	return rel_commits_distribution

def get_model_development_distribution(conn,id,date_range_buckets):
	cur = conn.cursor()
	total_models = get_number_of_model_under_development(conn,id)
	model_dev_ratio_distribution = []
	logging.info(date_range_buckets)
	for i in range(len(date_range_buckets)-1):
		sql = "select count(distinct(model_name)) c from Model_commits where project_id ="+ \
			  str(id) +"  and committer_date>="+"'"+date_range_buckets[i]+"' and "+\
														   "committer_date<" +"'"+date_range_buckets[i+1]+"'"
		logging.info("Model Commits Distribute SQL : "+ sql)
		cur.execute(sql)
		rows = cur.fetchall()
		count = int(rows[0][0])
		model_dev_ratio_distribution.append((count/total_models)*100)
	sql = "select count(distinct(model_name)) c from Model_commits where project_id =" + \
		  str(id) + "  and committer_date>=" + "'" + date_range_buckets[len(date_range_buckets)-1]+"'"
	logging.info("Model Commits Distribute SQL : "+ sql)
	cur.execute(sql)
	rows = cur.fetchall()
	count = int(rows[0][0])
	model_dev_ratio_distribution.append(count / total_models*100)
	logging.info("Project ID {} Model Ratio: {}".format(id,model_dev_ratio_distribution) )
	#assert(total_commits == sum(commit_counts))
	return model_dev_ratio_distribution


def plot_commits(data_lst, xlabel="Commits", ylabel=None, figure_name = None):
	xval = [x for x in range(1,len(data_lst)+1)]
	n_bars = len(data_lst[0])
	total_width  =0.01
	single_width =1
	bar_width = total_width/n_bars

	# Handles for legends
	bars =[]
	ax = plt.subplot()
	patterns = [ "\\", "OO", "--", "*"]

	proj_commit = [x[1] for x in data_lst]
	bins = [1,5,10,20,50,100,200]
	abc = plt.hist(proj_commit, bins=bins,log=True)
	print(abc)
	#ax.set_xticks(xtickpos)
	#ax.set_xticklabels(xticksLabel)
	#ax.set_yticks(ytickpos)
	#ax.set_yticklabels(ytickslabel)

	'''
	for i, values in enumerate(data_lst):
		x_offset = (i-n_bars/2) * bar_width + bar_width/2
		print(i)
		
		for x,y in enumerate(values):
			bar = ax.bar(x + x_offset, y, width=bar_width * single_width,hatch = patterns[x],color ='white',edgecolor='black')
		bars.append(bar[0])


	plt.xlabel(xlabel)
	'''
	plt.show()

def get_commits_lst(conn):
	cur = conn.cursor()
	SQL = "Select total_number_of_commits, model_commits from Project_Commit_Summary a JOIN \
			Root_Projects b on a.project_id = b.file_id \
			order by model_commits "
	cur.execute(SQL)
	rows = cur.fetchall()
	commits = [(r[0],r[1]) for r in rows]
	return commits





def get_average_by_col(a):
	return list(map(lambda x:sum(x)/len(x),zip(*a)))


def plot(data_lst,xlabel="Project life time", ylabel=None,figurename = None):
	xval = [1,2,3,4,5,6,7,8,9,10]
	xtickpos = [1,5,10]
	xticksLabel = ["0-10%","40-50%","90-100%"]
	max_y_val = round(max(data_lst))
	y_delta = 5
	if max_y_val>50:
		y_delta =10
	ytickpos = [ i for i in range(0,max_y_val,y_delta)]

	ytickslabel = ["{}%".format(i) for i in range(0,max_y_val,y_delta)]
	ax = plt.subplot()
	ax.set_xticks(xtickpos)
	ax.set_xticklabels(xticksLabel)
	ax.set_yticks(ytickpos)
	ax.set_yticklabels(ytickslabel)

	ax.bar(xval,data_lst,color ='white',edgecolor='black')
	#ax.bar(xval, data_lst, color='white', edgecolor='blue')
	#ax.bar(xval, data_lst, color='white', edgecolor='green')
	plt.grid(True,axis='y')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.savefig(figurename)
	plt.close()
	plt.show()
	plt.grid(True,axis='y')
	plt.xlabel(xlabel)
	#plt.ylabel(ylabel)
	#ax.legend(bars, data_lst.keys())


def plot_all(data_lst,xlabel="Project life time", ylabel=None,figurename = None):

	# Idea and Logic : https://stackoverflow.com/questions/14270391/python-matplotlib-multiple-bars/14270539
	xval = [1,2,3,4,5,6,7,8,9,10]
	xtickpos = [0,4,9]
	xticksLabel = ["0-10%","40-50%","90-100%"]
	max_y_val = 50#round(max(data_lst))
	y_delta = 5
	if max_y_val>50:
		y_delta =10
	ytickpos = [ i for i in range(0,max_y_val,y_delta)]

	ytickslabel = ["{}%".format(i) for i in range(0,max_y_val,y_delta)]
	patterns = [ "\\", "OO", "--", "*"]
	#Number of bars per xtick
	n_bars = len(data_lst)
	total_width  =0.8
	single_width =1
	bar_width = total_width/n_bars

	# Handles for legends
	bars =[]
	ax = plt.subplot()
	ax.set_xticks(xtickpos)
	ax.set_xticklabels(xticksLabel)
	ax.set_yticks(ytickpos)
	ax.set_yticklabels(ytickslabel)

	for i, (name,values) in enumerate(data_lst.items()):
		x_offset = (i-n_bars/2) * bar_width + bar_width/2
		for x,y in enumerate(values):
			bar = ax.bar(x + x_offset, y, width=bar_width * single_width,hatch = patterns[i],color ='white',edgecolor='black')
		bars.append(bar[0])
	#ax.bar(xval-0.1,data_lst,color ='white',edgecolor='black')
	#ax.bar(xval, data_lst, color='white', edgecolor='blue')
	#ax.bar(xval, data_lst, color='white', edgecolor='green')
	plt.grid(True,axis='y')
	plt.xlabel(xlabel)
	#plt.ylabel(ylabel)
	ax.legend(bars, data_lst.keys())
	figure = plt.gcf()

	figure.set_size_inches(8, 3)

	plt.savefig(figurename)
	plt.show()

def get_root_ids(conn):
	cur = conn.cursor()
	cur.execute("SELECT project_id FROM root_projects")

	rows = cur.fetchall()

	ans =  [r[0] for r in rows]
	project_ids = [] 
	for r in ans:
		project_ids.append(str(r)) 
	return project_ids


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
	#evoSL or EvoSLPlus or evoSLSample database depending on the plot
	evoSL_database =  ""
	evoSL_or_evoSLPlus_flag = True
	ten_plus_model_commits = True
	# create a database connection
	conn = create_connection(evoSL_database)

	if evoSL_or_evoSLPlus_flag: 
		root_projectids = get_root_ids(conn)
		if not ten_plus_model_commits:
			where_clause = " where project_id in ("+",".join(root_projectids)+")"
		else:
			where_clause = " where model_commits>=10 AND project_id in ("+",".join(root_projectids)+")"
		project_ids = get_project_ids(conn,where_clause)

	else:
		project_ids = get_evoSL_sample_project_id(conn) #["64223824","476168345","588267715","20451353","68744081","250217878","366359636","337996515","100999374","261484515","305846578","317540119","595154955","287361574","301176100","267839196","13328139","204030363","60685110","468290383","14375685","237132537","355203229","184514360","194490625","312007661","130222499","295851609","124382232","211239358","118747568","334101825","470647234","113453905","54991377","12136324","126338636","296797895","93419327","213199113","546546451","370616572","39600731","389552676","432334495","299664596","789683","47131658","419153598","131173589"]
		where_clause = " where project_id in ("+",".join(project_ids)+")"
	
	

	projects_commit_dist = []
	model_commit_dist = []
	model_modified_commit_dist = []
	model_development_dist = []

	#commits = get_commits_lst(conn)
	#plot_commits(commits)
	

	for id in project_ids:
		start_date, end_date = get_start_end_dates(conn,id)
		date_range_buckets = date_range(start_date, end_date, intv=10)
		projects_commit_dist.append(get_project_commit_distribution(conn,id,date_range_buckets))
		model_commit_dist.append(get_model_commit_distribution(conn,id,date_range_buckets))
		model_modified_commit_dist.append(get_model_modified_commit_distribution(conn,id,date_range_buckets))
		model_development_dist.append(get_model_development_distribution(conn,id,date_range_buckets))

	avg_project_commit_dist = get_average_by_col(projects_commit_dist)

	logging.info("Average Project Distribution of all projects:{}".format(avg_project_commit_dist))
	plot(avg_project_commit_dist,ylabel="Project Commits",figurename="Project_commit_dist.pdf")

	avg_model_commit_dist = get_average_by_col(model_commit_dist)
	logging.info("Average Model Distribution of all projects:{}".format(avg_model_commit_dist))
	plot(avg_model_commit_dist,ylabel="Model Commits",figurename="Model_commit_dist.pdf")

	avg_model_modified_commit_dist = get_average_by_col(model_modified_commit_dist)
	logging.info("Average Model Modified Distribution of all projects:{}".format(avg_model_modified_commit_dist))
	plot(avg_model_modified_commit_dist, ylabel = "Committed Model Modifications",figurename="modified_model_commit_dist.pdf")

	avg_model_development_dist = get_average_by_col(model_development_dist)

	logging.info("Average Model Development Ratio Distribution of all projects:{}".format(avg_model_development_dist))
	plot(avg_model_development_dist, ylabel="Models under development", figurename="model_under_development.pdf")

	project_lifecycles = {
		"Commits":avg_project_commit_dist,
		"$\mathregular{Commits_{MS}}$":avg_model_commit_dist,
		#"Committed Model Modifications":avg_model_modified_commit_dist,
		"Models under development":avg_model_development_dist
	}

	plot_all(project_lifecycles,xlabel="", ylabel=None,figurename = "all_project_evolution.pdf")
	#print(projects_commit_dist)
		#get_model_commit_distribution(conn,id)
		#get_model_commit_distribution(conn,id)

	



if __name__ == '__main__':
	#print(get_average_by_col([[10,2,3,4],[1,2,3,4],[1,2,3,4]]))
	main()