'''budget program
	tracks expenses and incomes
	generates analysis of cashflow, credit amount and bank account
	additionally tracks debt amoutns and create graphs showing tracked data
'''

from budg_tables import Expense, Base

from sqlalchemy import create_engine,and_,or_
from sqlalchemy.orm import sessionmaker
import sys, string
from operator import ne,eq,lt,le,ge,gt
#make a new and simpler search ability, make an importable class?



#storage path for the database
path="C:\\Users\Charles\Dropbox\Programming\DataBases\budgetManager.db" #this will be used during devleopment
#path="/home/cmcfeaters/projects/idea_box/Idea_Box.db"	#eventually it will be moved to here when deployed to web server

def createAll():
	#create the engine, the base and the session
	engine=create_engine('sqlite:///'+path,echo=False)
	Session=sessionmaker(bind=engine)

	session=Session() #create the session object to comm with db
	Base.metadata.create_all(engine) #create our db with the tables
	return session


'''def usernameCheck(username):
	#checks a username for at least 3 characters no more than 10 and only letters and numbers
	#username is lowercase
	#returns 1 if good or the reason why if bad
	######JUST RETURN THE ERROR
	for character in username:
		if string.ascii_letters.count(character)==0 and string.digits.count(character)==0:
			return "%s is an invalid character, letters and numbers only please"%character
	if username=='admin':
		return username+" is a reserved username, please choose another"
	if not uniqueUsername(username):
		return username + " is already in use, please select another"
	if len(username)<3:
		return "At least 3 characters please"
	if len(username)>10:
		return "Maximum of 10 characters please"
	return 1

def uniqueUsername(username):
	#a search that returns 1 if username is unique, 0 if not
	session=createAll()
	if len(session.query(User).filter(User.username==username).all())>0:
		session.close()
		return 0
	else: 
		session.close()
		return 1
	
def uniqueTitle(username,title):
	#searches to determine if a title already exists for a given user
	session=createAll()
	user=session.query(User).filter(User.username==username).all()[0]
	if len(session.query(Idea).filter(and_(Idea.user_id==user.id,Idea.title==title)).all())>0:
		session.close()
		return 0
	else:
		session.close()
		return 1

def createUser(username,password,session=createAll()):
	#creates a new user, returns 1 if commited, 0 if not
	try:
		session.add(User(username.lower(),password))
		print "YES"
		session.commit()
		print "YES"
		session.close()
		return 1
	except:
		session.close()
		return 0

def changeUsername(oldUsername, newUsername, session=createAll()):
	#changes a username to another unique one, 1 if commited, returns error code if not
	#usernames are stored in lowercase
	if oldUsername==newUsername:
		session.close()
		return 1
	userCheck=usernameCheck(newUsername)
	if userCheck==1:
		user=session.query(User).filter(User.username==oldUsername).all()[0]
		user.username=newUsername
		session.commit()
		session.close()
		return 1
	else: 
		session.close()
		return userCheck
	
def changePassword(username,password,session=createAll()):
	#changes the password of a user as long as it's 10 characters, 1 if good 0 if not
	if len(password)>=10 and len(password)<=50:
		user=session.query(User).filter(User.username==username).all()[0]
		user.password=password
		session.commit()
		session.close()
		return 1
	else: 
		session.close()
		return 0
	
def deleteUser(username,session=createAll()):
	#deletes a user by username, 1 if good 0 if not
	try:
		user=session.query(User).filter(User.username==username).all()[0]
		session.delete(user)
		session.commit()
		session.close()
		return 1
	except: 
		session.close()
		return 0

def createIdea(username,title,body,tags,session=createAll()):
	#creates a new idea for a user as long as the title is unique, 1 if good 0 if not
	#body and tags can be empty
	user=session.query(User).filter(User.username==username).all()[0]
	if uniqueTitle(username,title):
		session.add(Idea(user.id,title,body,tags))
		session.commit()
		session.close()
		return 1
	else:
		session.close()
		return 0
	
def deleteIdea(username,title,session=createAll()):
	#deletes an idea
	user=session.query(User).filter(User.username==username).all()[0]
	try:
		idea=session.query(Idea).filter(and_(Idea.user_id==user.id,Idea.title==title)).all()[0]
		session.delete(idea)
		session.commit()
		session.close()
		return 1
	except: 
		session.close()
		return 0

def changeTitle(username,oldTitle,newTitle,session=createAll()):
	#changes a title to a unique new title
	user=session.query(User).filter(User.username==username).all()[0]
	if uniqueTitle(username,newTitle) and len(newTitle)>=3 and len(newTitle)<=15:
		idea=session.query(Idea).filter(and_(Idea.user_id==user.id,Idea.title==oldTitle)).all()[0]
		idea.title=newTitle
		session.commit()
		session.close()
		return 1
	elif newTitle==oldTitle:
		session.close()
		return 1
	else: 
		session.close()
		return 0

def changeIdea(username,title,newIdea,session=createAll()):
	#changes an idea, 1 if good 0 if not
	try:
		user=session.query(User).filter(User.username==username).all()[0]
		idea=session.query(Idea).filter(and_(Idea.user_id==user.id,Idea.title==title)).all()[0]
		idea.idea=newIdea
		session.commit()
		session.close()
		return 1
	except: 
		session.close()
		return 0
	
def deleteTag(username,title,tag,session=createAll()):
	#replaces a tag in the tag string with "", 1 if good 0 if not
	try:
		user=session.query(User).filter(User.username==username).all()[0]
		idea=session.query(Idea).filter(and_(Idea.user_id==user.id,Idea.title==title)).all()[0]
		idea.tags=idea.tags.replace(tag,"")
		idea.tags=idea.tags.replace(",,",",")#the tags are separated by commas, this deletes any double commas
		idea.tags=idea.tags.lstrip(',')
		idea.tags=idea.tags.rstrip(",")
		session.commit()
		session.close()
		return 1
	except: 
		session.close()
		return 0
	
def addTag(username,title,tag,session=createAll()):
	#adds a tag to the tag string, 1 if good 0 if not
	try:
		user=session.query(User).filter(User.username==username).all()[0]
		idea=session.query(Idea).filter(and_(Idea.user_id==user.id,Idea.title==title)).all()[0]
		idea.tags=idea.tags+","+tag
		session.commit()
		session.close()
		return 1
	except: 
		session.close()
		return 0

def editTag(username,title,oldTag,newTag):
	#edits oldTag to be newTag, 1 if good 0 if not
		if deleteTag(username,title,oldTag):
			if addTag(username,title,newTag):
				return 1
			else: return 0
		else: return 0

def changeTags(username,title,newTags,session=createAll()):
	#changes all tags, 1 if good 0 if not
	try:
		user=session.query(User).filter(User.username==username).all()[0]
		idea=session.query(Idea).filter(and_(Idea.user_id==user.id,Idea.title==title)).all()[0]
		idea.tags=newTags
		session.commit()
		session.close()
		return 1
	except: 
		session.close()
		return 0
	
def signInVerify(userName,password):
	#a function to check the username against it's password
	#given a username and password, returns 1 if correct or a string defining why
	session=createAll()
	result=session.query(User).filter(User.username==userName)
	if len(result.all())!=1:
		session.close()
		return "Username Not Found"
	elif result[0].password!=password:
		session.close()
		return "Password Incorrect"
	else:
		session.close()
		return 1
	session.close()
	'''
