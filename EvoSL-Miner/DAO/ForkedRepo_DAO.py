from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, load_only
from datetime import datetime
Base = declarative_base()


class SimulinkForkedRepoInfo(Base):
	'''
	model class for Simulink Repo Info
	'''
	__tablename__ = "Forked_Projects"

	id = Column('forked_project_id', Integer, primary_key=True)
	forked_from_id = Column('forked_from_id', Integer)
	
	repo_name = Column('repo_name', String)
	owner = Column('owner_name', String)
	owner_type = Column('owner_type', String)
	owner_id = Column('owner_id', String)
	is_private = Column('is_private', Boolean)
	html_github_url = Column('project_url', String)
	description = Column('description', String)
	is_forked = Column('is_forked', Boolean)
	api_url = Column('api_url', String)

	created_at = Column('created_at', DateTime)
	updated_at = Column('updated_at', DateTime)
	pushed_at = Column('pushed_at', DateTime)

	homepage = Column('homepage_url', String)

	size_in_kb = Column('size_in_kb', Integer)

	stargazers_count = Column('stargazers_count', Integer)  # Favorites
	watchers_count = Column('watchers_count', Integer)
	language = Column('languages', String)
	forks_count = Column('forks_count', Integer)  # Forks

	open_issues_count = Column('open_issues_count', Integer)
	master_branch = Column('master_branch', String)
	default_branch = Column('default_branch', String)
	topics = Column('topics', String)  # Domain


	license_type = Column('license', String)
	version_sha = Column('version_sha', String)

	def __init__(self, id, forked_from_id, repo_name, owner, owner_type, owner_id, is_private ,
				 html_github_url, description, is_forked, api_url,
				 created_at, updated_at, pushed_at,
				 homepage, size,
				 stargazers_count, watchers_count,language,forks_count,
				 open_issues_count , master_branch, default_branch,
				 topics,license_type,
			     version_sha):
		self.id = id
		self.forked_from_id = forked_from_id

		self.repo_name=repo_name
		self.owner = owner
		self.owner_id = owner_id
		self.owner_type = owner_type
		self.is_private = is_private
		self.html_github_url=html_github_url
		self.description = description


		self.is_forked = is_forked
		self.api_url = api_url
		self.created_at = created_at
		self.updated_at = updated_at
		self.pushed_at = pushed_at

		self.homepage = homepage
		self.size = size


		self.forks_count=forks_count
		self.stargazers_count=stargazers_count
		self.watchers_count=watchers_count

		self.open_issues_count = open_issues_count
		self.master_branch = master_branch
		self.default_branch = default_branch

		self.topics = topics



		self.language = language
		#self.has_license = has_license
		self.license_type = license_type
		self.version_sha = version_sha



class SimulinkForkedRepoInfoController(object):
	def __init__(self,db_name):
		# In memory SQlite database . URI : sqlite:///:memory:
		# URL = driver:///filename or memory
		self.engine = create_engine('sqlite:///'+db_name) # Hard coded Database Name . TODO : Make it user configurable/
		#Create Tables
		Base.metadata.create_all(bind=self.engine)
		
		self.Session = sessionmaker(bind=self.engine)

	def insert(self, id, forked_from_id, repo_name, owner,owner_type, owner_id,  is_private ,
				 html_github_url, description, is_forked, api_url,
				 created_at, updated_at, pushed_at,
				 homepage, size,
				 stargazers_count, watchers_count,language,forks_count,
				 open_issues_count , master_branch, default_branch,
				 topics,license_type,
			     version_sha):
		'''
		creates a session and object to insert the values
		need to implement error handling
		:param id:
		:param repo_name:
		:param owner:
		:param html_github_url:
		:param language:
		:param forks_count:
		:param stargazers_count:
		:param watchers_count:
		:param topics:
		:param created_at:
		:param updated_at:
		:param has_license:
		:param has_model_files:
		:param model_files:
		:return:
		'''
		session = self.Session()
		tmpSimulinkRepoInfo = SimulinkForkedRepoInfo( id, forked_from_id, repo_name, owner,owner_type, owner_id,  is_private ,
				 html_github_url, description, is_forked, api_url,
				 created_at, updated_at, pushed_at,
				 homepage, size,
				 stargazers_count, watchers_count,language,forks_count,
				 open_issues_count , master_branch, default_branch,
				 topics,license_type,
			     version_sha)
		session.add(tmpSimulinkRepoInfo)
		session.commit()
		session.close()

	def update(self,id,col_val): #TODO: Table is fixed , Change it to user configurable tables
		'''

		:param id:
		:param col_val: is the dictionary with {coln : updated_val }
		:return:
		'''
		session = self.Session()
		session.query(SimulinkForkedRepoInfo).filter_by(id=id).update(col_val) #{"name": u"Bob Marley"}

		session.commit()
		session.close()

	def delete(self, primary_key_id):
		session = self.Session()
		session.query(SimulinkForkedRepoInfo).filter(SimulinkForkedRepoInfo.id == primary_key_id).delete()

		session.commit()
		session.close()

	def delete_original_id(self, forked_from_id):
		session = self.Session()
		session.query(SimulinkForkedRepoInfo).filter(SimulinkForkedRepoInfo.forked_from_id == forked_from_id).delete()

		session.commit()
		session.close()
