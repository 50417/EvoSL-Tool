
import os
import sqlite3
import requests
# defining the libraries
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from itertools import accumulate  
matplotlib.rcParams.update({
	'font.family': 'Times New Roman',
	'font.size' : 14,

})

def create_connection(db):
	conn = None
	try: 
		conn = sqlite3.connect(db)
	except Error as e: 
		print(e)
	return conn

def get_root_ids(conn):
	cur = conn.cursor()
	cur.execute("SELECT project_id FROM root_projects")

	rows = cur.fetchall()

	ans =  [r[0] for r in rows]
	project_ids = [] 
	for r in ans:
		project_ids.append(str(r)) 
	return project_ids

def get_total_project_count(conn,project_ids):
	where_clause = " WHERE project_id in ("+",".join(project_ids)+")"
	cur = conn.cursor()
	cur.execute("SELECT count(*) FROM Project_Commit_Summary" + where_clause)

	rows = cur.fetchall()

	return rows[0][0]



def get_commits(conn,project_ids,col):
	where_clause = " WHERE project_id in ("+",".join(project_ids)+") "
	cur = conn.cursor()
	cur.execute("SELECT "+col+" FROM Project_Commit_Summary "+where_clause+" order by "+col)

	rows = cur.fetchall()

	return [r[0] for r in rows]

def get_issues(conn,project_ids,num_of_projects):
	where_clause = " WHERE project_id in ("+",".join(project_ids)+") "
	cur = conn.cursor()
	cur.execute("SELECT project_id, count(issue_id) c FROM Issues "+where_clause+" group by project_id order by c")

	rows = cur.fetchall()
	'''
	res = []
	total = 0 
	for r in rows:
		total += r[1]
		res.append(r[1])
	tmp = [0] * (num_of_projects-total)
	ans = tmp+res
	return ans
	'''
	return [r[1] for r in rows]

def get_pr(conn,project_ids,num_of_projects):
	where_clause = " WHERE project_id in ("+",".join(project_ids)+") "
	cur = conn.cursor()
	cur.execute("SELECT project_id, count(pr_id) c FROM pr "+where_clause+"group by project_id order by c")

	rows = cur.fetchall()

	return [r[1] for r in rows]

def get_outliers_range(sorted_lst):
	n_len = len(sorted_lst)
	median_idx = (n_len +1)//2
	q1_idx = (n_len +1)//4
	q3_idx = ((n_len +1)//4) * 3

	print(sorted_lst[median_idx])

	q1 = sorted_lst[q1_idx]
	q3 = sorted_lst[q3_idx]

	iqr = q3 - q1
	upper_fence = q3 +  1.5 * iqr
	lower_fence = q1 - 1.5 * iqr
	if lower_fence<0:
		lower_fence = 0
	return lower_fence, upper_fence

def count_values(sorted_lst, lower,upper):
	ele = []
	counts = []
	for val in sorted_lst:
		#if val < lower or val > upper:
		#	continue
		if len(ele)==0 or ele[-1] != val:
			ele.append(val)
			counts.append(1)
		else:
			counts[-1] = counts[-1]+1
	return ele, counts


def get_cumulative_ratio(sorted_lst):
	counts_cumul = list(accumulate(sorted_lst))
	total = counts_cumul[-1]
	cumulative_ratio = [r/total for r in  counts_cumul]
	return cumulative_ratio, total

def get_ele_and_cumulative_ratio(sorted_lst):
	lower, upper = get_outliers_range(sorted_lst)
	ele, counts = count_values(sorted_lst, lower,upper)
	cumulative_ratio, total = get_cumulative_ratio(counts)
	return ele, cumulative_ratio, total 


def get_project_count_lt_xcommits(conn,project_ids, x):
	where_clause = " AND project_id in ("+",".join(project_ids)+") "
	
	cur = conn.cursor()
	cur.execute("SELECT count(*) FROM Project_Commit_Summary where total_number_of_commits<"+str(x)+where_clause)

	rows = cur.fetchall()

	return rows[0][0]

def get_project_count_lt_1modelcommits(conn,project_ids):
	where_clause = " AND project_id in ("+",".join(project_ids)+") "
	cur = conn.cursor()
	cur.execute("SELECT count(*) FROM Project_Commit_Summary where model_commits=1"+ where_clause)

	rows = cur.fetchall()

	return rows[0][0]

def get_percentage(num,deno):
	return num/deno*100

def main(): 

	our_db = ""
	raw_db = ""
	fig = plt.figure()
	ax1 = fig.add_subplot(111, label="1")
	ax2 = fig.add_subplot(111, label="1", frame_on=False)

	markers_choices = [["p","+","s","x"],["p","+","s","x"]]
	label_suffix = ["EvoSL+",'EvoSL']
	linestyles = ['dashed','solid']
	cnt = 0 
	for db in [raw_db,our_db]:
		a_conn = create_connection(db) 
		project_ids = get_root_ids(a_conn)
		marker_choice = markers_choices[cnt]
		
		with a_conn:
			proj_commmit = get_commits(a_conn, project_ids,"total_number_of_commits")
			model_commit = get_commits(a_conn, project_ids, "model_commits")

			total_project = get_total_project_count(a_conn,project_ids)
			issues = get_issues(a_conn,project_ids,total_project)
			pr = get_pr(a_conn,project_ids,total_project)

			proj_count_lt_50commits = get_project_count_lt_xcommits(a_conn,project_ids,50)
			print("Project Percentage less than 50 commits %5.3f" %get_percentage(proj_count_lt_50commits,total_project))
			
			proj_count_lt_2commits = get_project_count_lt_xcommits(a_conn,project_ids,3)
			print("Project Percentage 2 or less commits %5.3f" %get_percentage(proj_count_lt_2commits,total_project))
			
			proj_count_1modelcommit = get_project_count_lt_1modelcommits(a_conn,project_ids)
			print("Project Percentage 1 mdel commits %5.3f" %get_percentage(proj_count_1modelcommit,total_project))
			
		p_ele, p_c_ratio, p_total = get_ele_and_cumulative_ratio(proj_commmit)
		m_ele, m_c_ratio, m_total = get_ele_and_cumulative_ratio(model_commit)
		i_ele, i_c_ratio, i_total = get_ele_and_cumulative_ratio(issues)
		pr_ele, pr_c_ratio, pr_total = get_ele_and_cumulative_ratio(pr)



		print("Percentage of Projects with zero Pull requests "+ str((total_project - pr_total)/total_project*100))
		print("Percentage of Projects with zero issuess "+ str((total_project - i_total)/total_project* 100))

		
		
		

		ax1.plot(m_ele,m_c_ratio, color='black', linestyle=linestyles[cnt],marker=marker_choice[0],label="$\mathregular{Commits_{MS("+label_suffix[cnt]+")}}$",linewidth=1,markersize=4)
		ax1.plot(i_ele,i_c_ratio, color='black',linestyle=linestyles[cnt], marker=marker_choice[1],label="$\mathregular{Issues_{("+label_suffix[cnt]+")}}$",linewidth=1,markersize=4)
		ax1.plot(pr_ele,pr_c_ratio,color='black',linestyle=linestyles[cnt],marker=marker_choice[2],label="$\mathregular{Pull request_{("+label_suffix[cnt]+")}}$",linewidth=1,markersize=4)
		

		
		ax2_color = 'C0'
		ax2.plot(p_ele,p_c_ratio,color=ax2_color,linestyle=linestyles[cnt], marker=marker_choice[3],label="$\mathregular{Commits_{("+label_suffix[cnt]+")}}$", linewidth=1,markersize=4)
		
		
		
		cnt += 1
		#plt.savefig("metric_distribution.pdf")
	ax1.axis(xmin=0,xmax=16,ymin=0, ymax=1.0)
	ax1.set_xlabel("Number of (Model Commits | Issues | Pull request) in Project", color="black")
	ax1.set_ylabel("Cumulative Proportion of Projects", color="black")
	ax1.legend(loc=4,prop={'size': 11})

	ax2.xaxis.tick_top()
	#ax2.yaxis.tick_right()
	ax2.set_xlabel("Number of Project Commits in Project", color=ax2_color)
	#ax2.set_ylabel("Cumulative Proportion of Projects", color=ax2_color)
	ax2.xaxis.set_label_position('top') 
	#ax2.yaxis.set_label_position('right') 
	ax2.tick_params(axis='x', colors=ax2_color)
	#ax2.tick_params(axis='y', colors=ax2_color)
	ax2.axis(xmin=0,xmax=180,ymin=0, ymax=1.0)
	ax2.legend(loc=7,labelcolor='linecolor',prop={'size': 11}) # 4 =lower right	
	plt.show()

	 

main()