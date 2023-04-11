from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, load_only
from datetime import datetime
from sqlalchemy.schema import PrimaryKeyConstraint,ForeignKeyConstraint
Base = declarative_base()


class Issues_DAO(Base):
	'''
	Data Access Object
	'''
	__tablename__ = "Issues"

	project_id = Column('project_id', Integer)
	issue_id = Column('issue_id', Integer)
	
	state = Column('state', String)


	title = Column('title', String)
	body = Column('body', String)
	labels = Column('labels',String)

	issue_number = Column('issue_number', Integer)

	user = Column('user_api_url', String)
	api_url = Column('api_url', String)
	html_url = Column('html_url', String)

	created_at = Column('created_at', DateTime)
	closed_at = Column('closed_at', DateTime)

	__table_args__ = (
		PrimaryKeyConstraint(
			project_id,
			issue_id),
		{})
	
	def __init__(self, project_id, labels, issue_obj):
		self.project_id = project_id
		self.issue_id = issue_obj.id
		
		self.state = issue_obj.state

		self.title = issue_obj.title
		self.body = issue_obj.body
		self.labels = labels

		self.issue_number = issue_obj.number
		
		self.user = issue_obj.user.url
		self.api_url = issue_obj.url
		self.html_url = issue_obj.html_url

		self.created_at = issue_obj.created_at
		self.closed_at = issue_obj.closed_at
		



class Issues_DAO_controller(object):
	def __init__(self,db_name):
		# In memory SQlite database . URI : sqlite:///:memory:
		# URL = driver:///filename or memory
		self.engine = create_engine('sqlite:///'+db_name) # Hard coded Database Name . TODO : Make it user configurable/
		#Create Tables
		Base.metadata.create_all(bind=self.engine)
		self.Session = sessionmaker(bind=self.engine)

	def insert(self, project_id, labels, issue_obj):
		session = self.Session()
		tmp_obj = Issues_DAO(project_id, labels, issue_obj)
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
		session.query(Issues_DAO).filter_by(id=id).update(col_val) #{"name": u"Bob Marley"}

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
		result = session.query(Issues_DAO).options(load_only(col_name))#.filter_by(has_model_files=1)
		'''for row in x:
			print(row.model_files)
			count +=1
		'''
		session.close()
		return result


