from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, load_only
from datetime import datetime
from sqlalchemy.schema import PrimaryKeyConstraint
Base = declarative_base()


class Issue_PR_Link_DAO(Base):
	'''
	Pull Request Data Access Object
	'''
	__tablename__ = "Issue_PR_Links"

	pr_id = Column('pr_id', Integer)
	issue_id = Column('issue_id', Integer)

	__table_args__ = (
		PrimaryKeyConstraint(
			pr_id,
			issue_id),
		{})
	
	def __init__(self, pr_id, issue_id):
		self.pr_id = pr_id
		self.issue_id = issue_id

		



class Issue_PR_Link_DAO_controller(object):
	def __init__(self,db_name):
		# In memory SQlite database . URI : sqlite:///:memory:
		# URL = driver:///filename or memory
		self.engine = create_engine('sqlite:///'+db_name) # Hard coded Database Name . TODO : Make it user configurable/
		#Create Tables
		Base.metadata.create_all(bind=self.engine)
		self.Session = sessionmaker(bind=self.engine)

	def insert(self, pr_id, issue_id):
		session = self.Session()
		tmp_obj = Issue_PR_Link_DAO(pr_id, issue_id)
		session.add(tmp_obj)
		session.commit()
		session.close()

	def update(self,id,col_val): #TODO: Table is fixed , Change it to user configurable tables
		'''

		:param id:
		:param col_val: is the dictionary with {coln : updated_val }
		:return:
		'''
		session = self.Session()
		session.query(Issue_PR_Link_DAO).filter_by(id=id).update(col_val) #{"name": u"Bob Marley"}

		session.commit()
		session.close()

	def delete(self):
		pass

	def select(self,col_name,where_clause=None): #TODO : Support for where clause AND REMOVE HARDCODED VALUES
		'''

		:param col_name:
		:param where_clause:
		:return: object corresponding to the class : Load_only(col_name) restricts objects attributes
		'''
		session = self.Session()
		count = 0
		result = session.query(Issue_PR_Link_DAO).options(load_only(col_name))#.filter_by(has_model_files=1)
		'''for row in x:
			print(row.model_files)
			count +=1
		'''
		session.close()
		return result