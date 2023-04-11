from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, load_only
from datetime import datetime
from sqlalchemy.schema import PrimaryKeyConstraint
Base = declarative_base()


class Comments_DAO(Base):
	'''
	Pull Request Data Access Object
	'''
	__tablename__ = "Issue_PR_Comments"

	issue_or_pr_id = Column('issue_pr_id', String)
	comment_id = Column('comment_id', Integer)

	comment_of = Column('comment_of', String)
	
	body = Column('body', String)
	
	api_url = Column('api_url', String)
	html_url = Column('html_url', String)
	user_url = Column('user_url', String)

	created_at = Column('created_at', DateTime)
	__table_args__ = (
		PrimaryKeyConstraint(
			issue_or_pr_id,
			comment_id),
		{})
	
	def __init__(self, issue_or_pr_id, comment_of, comment_obj):
		self.issue_or_pr_id = issue_or_pr_id
		self.comment_id = comment_obj.id

		self.comment_of = comment_of
		
		self.body = comment_obj.body

		self.user_url = comment_obj.user.url
		self.api_url = comment_obj.url
		self.html_url = comment_obj.html_url

		self.created_at = comment_obj.created_at
		



class Comments_DAO_controller(object):
	def __init__(self,db_name):
		# In memory SQlite database . URI : sqlite:///:memory:
		# URL = driver:///filename or memory
		self.engine = create_engine('sqlite:///'+db_name) # Hard coded Database Name . TODO : Make it user configurable/
		#Create Tables
		Base.metadata.create_all(bind=self.engine)
		self.Session = sessionmaker(bind=self.engine)

	def insert(self, issue_or_pr_id, comment_of, comment_obj):
		session = self.Session()
		tmp_obj = Comments_DAO(issue_or_pr_id, comment_of, comment_obj)
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
		session.query(Comments_DAO).filter_by(id=id).update(col_val) #{"name": u"Bob Marley"}

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
		result = session.query(Comments_DAO).options(load_only(col_name))#.filter_by(has_model_files=1)
		'''for row in x:
			print(row.model_files)
			count +=1
		'''
		session.close()
		return result