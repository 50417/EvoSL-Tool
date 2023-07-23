from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, load_only
from datetime import datetime
from sqlalchemy.schema import PrimaryKeyConstraint,ForeignKeyConstraint
Base = declarative_base()


class Commit_DAO(Base):
	'''
	Pull Request Data Access Object
	'''
	__tablename__ = "PR_Commits"

	pr_id = Column('pr_id', Integer)
	commit_sha = Column('commit_sha', String)
	
	api_url = Column('api_url', String)
	html_url = Column('html_url', String)
	__table_args__ = (
		PrimaryKeyConstraint(
			pr_id,
			commit_sha),
		{})
	
	def __init__(self, pr_id, commit_obj):
		self.pr_id = pr_id
		self.commit_sha = commit_obj.sha

		self.api_url = commit_obj.url
		self.html_url = commit_obj.html_url

		



class Commit_DAO_controller(object):
	def __init__(self,db_name):
		# In memory SQlite database . URI : sqlite:///:memory:
		# URL = driver:///filename or memory
		self.engine = create_engine('sqlite:///'+db_name) # Hard coded Database Name . TODO : Make it user configurable/
		#Create Tables
		Base.metadata.create_all(bind=self.engine)
		self.Session = sessionmaker(bind=self.engine)

	def insert(self,  pr_id, commit_obj):
		session = self.Session()
		tmp_obj = Commit_DAO( pr_id, commit_obj)
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
		session.query(Commit_DAO).filter_by(id=id).update(col_val) #{"name": u"Bob Marley"}

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
		result = session.query(Commit_DAO).options(load_only(col_name))#.filter_by(has_model_files=1)
		'''for row in x:
			print(row.model_files)
			count +=1
		'''
		session.close()
		return result