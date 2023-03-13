import sqlite3
from sqlite3 import Error
import pathlib
import logging
import sys
import os, shutil
import time
from datetime import datetime
from pydriller import GitRepository

from Model_commits_info import Model_commits_info_Controller
from Project_commits_info import Project_commits_info_Controller
from Project_commits_verbatim import Project_commits_verbatim_Controller
from Model_commits_verbatim import Model_commits_verbatim_Controller

logging.basicConfig(filename='commits.log', filemode='a',
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
from get_project_level_commits import get_project_level_commits
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

def get_repo_id_urls(conn):
    """
    Query tasks
    :param conn: the Connection object
    :param
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT file_id,project_url,model_files,version_sha FROM GitHub_Projects ")

    rows = cur.fetchall()
    return rows

def get_id_name(conn):
    cur = conn.cursor()

    cur.execute("SELECT project_id FROM GitHub_Projects_Commit_Info ")

    rows = cur.fetchall()

    cur.execute("SELECT model_name FROM GitHub_Model_Commit_Info ")
    mdl_name = cur.fetchall()

    return set([ r[0] for r in rows]),set([m[0] for m in mdl_name])

def write_project_commit_info(url,id, hash,controller,project_verbatim,model_verbatim):
    total_number_of_commits, number_of_merge_commits, number_of_authors, \
    first_commit, last_commit, lifeTime_in_days, commit_per_day, \
    model_commits, model_authors = get_project_level_commits(url,hash,project_verbatim,id,model_verbatim)

    try: 
        logging.info("Writing to Project_commit_info table")

        controller.insert(id, total_number_of_commits, number_of_merge_commits, number_of_authors, \
                                            first_commit, last_commit, lifeTime_in_days, commit_per_day, \
                                            model_commits, model_authors)
    except Exception as e: 
            logging.info(e)
            logging.info("Writing failted.")
            return -1

    return lifeTime_in_days


def write_model_commit_info(project_id,controller, project_lifetime, conn):
    cur = conn.cursor()
    cur.execute("select model_name, count(DISTINCT hash),count(distinct author_email), MIN(author_date), max(author_date) \
                from model_commits where project_id = "+str(project_id)+"\
                group by model_name")

    rows = cur.fetchall()
    for row in rows: 
        model_name = row[0]
        no_of_commits = int(row[1])
        no_of_authors = int(row[2])
        start_date = datetime.strptime(row[3],'%Y-%m-%d %H:%M:%S.%f')
        end_date = datetime.strptime(row[4],'%Y-%m-%d %H:%M:%S.%f')

        life_time = end_date-start_date
        model_lifetime = life_time.days + life_time.seconds / 86400

        relative_lifetime = 0

        if project_lifetime != 0:
            relative_lifetime = model_lifetime/project_lifetime
        try: 
            logging.info("Writing to Github_model_commit_info table")
            controller.insert(project_id, model_name, no_of_commits, no_of_authors,start_date, end_date, model_lifetime,relative_lifetime)

        except Exception as e: 
            logging.info(e)
            logging.info("Writing failted.")

def check_and_delete(project_id , conn, pv, mv, pdc, mdc):
    cur = conn.cursor()
    tables = ['GitHub_Projects_Commit_Info', 'GitHub_Model_Commit_Info','Project_commits','Model_commits']
    for table in tables: 
        cur.execute("SELECT count(*) FROM "+table+" WHERE project_id="+str(project_id))
        rows = cur.fetchall()
        if int(rows[0][0]) == 0: 
            pv.delete(project_id)
            mv.delete(project_id)
            pdc.delete(project_id)
            mdc.delete(project_id)


def main():
    start = time.time()
    # Source and Destination can be same database
    source_database =""
    dst_database = ""

    path = "workdir"
    dest_project_database_controller = Project_commits_info_Controller(dst_database)
    dest_model_database_controller = Model_commits_info_Controller(dst_database)

    project_verbatim = Project_commits_verbatim_Controller(dst_database)
    model_verbatim = Model_commits_verbatim_Controller(dst_database)
    # create a database connection
    conn = create_connection(source_database)
    dst_conn = create_connection(dst_database)

    with dst_conn:
        processed_id,processed_mdl_name= get_id_name(dst_conn)
    with conn:
        id_urls = get_repo_id_urls(conn)
        for id_url in id_urls:
            id, url , model_files,hash = id_url
            if not os.path.exists(path):
                os.mkdir(path)
            try:
                if id not in processed_id:
                    logging.info("=============Processing {}===========".format(str(id)))
                    clone = "git clone " + url + " " + path
                    os.system(clone)  # Cloning
                    gr = GitRepository(path)
                    gr.checkout(hash)
                    url = path
                    project_lifetime = write_project_commit_info(url,id, hash,dest_project_database_controller,project_verbatim, model_verbatim)
                    if project_lifetime != -1:
                        logging.error("Successfully Inserted into database")
                        write_model_commit_info(id,dest_model_database_controller,project_lifetime, dst_conn)
                    else:
                        logging.error("Error inserting into database")
                else:
                    logging.info("Skipping . ALready Processed {}".format(id))
            except Exception as e:
                logging.error(e)
                continue
            finally:
                check_and_delete(id, dst_conn,project_verbatim,model_verbatim,dest_project_database_controller,dest_model_database_controller)
                logging.info("=============Done Proessing {}===========".format(str(id)))
                shutil.rmtree(path)
    end = time.time()
    logging.info("IT took {} seconds".format(end - start))





if __name__ == '__main__':
    main()
