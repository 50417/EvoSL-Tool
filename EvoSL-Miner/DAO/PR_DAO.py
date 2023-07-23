from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, load_only
from datetime import datetime
from sqlalchemy.schema import PrimaryKeyConstraint
Base = declarative_base()


class PR_DAO(Base):
	'''
	Pull Request Data Access Object
	'''
	__tablename__ = "PR"

	project_id = Column('project_id', Integer)
	pull_id = Column('pr_id', Integer)
	
	state = Column('state', String)

	title = Column('title', String)
	body = Column('body', String)
	labels = Column('labels',String)

	pull_number = Column('pull_number', Integer)
	
	api_url = Column('api_url', String)
	html_url = Column('html_url', String)
	user_url = Column('user_url', String)

	created_at = Column('created_at', DateTime)
	closed_at = Column('closed_at', DateTime)

	__table_args__ = (
		PrimaryKeyConstraint(
			project_id,
			pull_id),
		{})
	
	
	def __init__(self, project_id, labels, pull_obj):
		self.project_id = project_id
		self.pull_id = pull_obj.id
		
		self.state = pull_obj.state

		self.title = pull_obj.title
		self.body = pull_obj.body
		self.labels = labels

		self.pull_number = pull_obj.number
		
		self.api_url = pull_obj.url
		self.html_url = pull_obj.html_url
		self.user_url = pull_obj.user.url

		self.created_at = pull_obj.created_at
		self.closed_at = pull_obj.closed_at
		



class PR_DAO_controller(object):
	def __init__(self,db_name):
		# In memory SQlite database . URI : sqlite:///:memory:
		# URL = driver:///filename or memory
		self.engine = create_engine('sqlite:///'+db_name) # Hard coded Database Name . TODO : Make it user configurable/
		#Create Tables
		Base.metadata.create_all(bind=self.engine)
		self.Session = sessionmaker(bind=self.engine)

	def insert(self, project_id, labels, pull_obj):
		session = self.Session()
		tmp_obj = PR_DAO(project_id, labels, pull_obj)
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
		session.query(PR_DAO).filter_by(id=id).update(col_val) #{"name": u"Bob Marley"}

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
		result = session.query(PR_DAO).options(load_only(col_name))#.filter_by(has_model_files=1)
		'''for row in x:
			print(row.model_files)
			count +=1
		'''
		session.close()
		return result