'''
idea_tables
this contains all of the setup data for the tables
'''
from sqlalchemy import ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
Base=declarative_base()

class User(Base):
	'''the user class'''
	__tablename__='users'
	
	id=Column(Integer,primary_key=True)
	username=Column(String)
	password=Column(String)
	ideas=relationship("Idea", backref="users", cascade="all, delete-orphan") #this is the link to the idea table
	
	def __init__(self,username,password):
		self.username=username.lower()
		self.password=password#this is something you could do some security work with
	
	def __repr__(self):
		#print portion
		return "User Id: %s \n UserName: %s \n Password: %s"%(self.id, self.username,self.password)
		
	

class Idea(Base):
	'''the ideas table'''
	#each idea in the tableis linked back to a specific user using their ID as a foreign key
	__tablename__='ideas'
	
	id=Column(Integer,primary_key=True)
	
	user_id=Column(Integer,ForeignKey('users.id'))
	title=Column(String(20))
	idea=Column(String)
	tags=Column(String)
	
	def __init__(self,user_id,title,idea,tags):
		self.user_id=user_id
		self.title=title.lower()
		self.idea=idea
		self.tags=tags
	
	def addTag(self,tag):
		#adds a tag to the self.tag string, separated with a comma
		if self.tags=="":
			self.tags=tag
		else:
			self.tags=str(self.tags)+" , "+tag
		
	def __repr__(self):
		return "Title: %s\nIdea:\n%s\nTags: %s"%(self.title,self.idea,self.tags)
		