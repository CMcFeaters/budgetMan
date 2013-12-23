#test code
#this code will test our database project

#test 1
#create an entry
try:
	print "Attempting Importing"
	import sys, string, random, os, budg_main
	
	from budg_tables import Expense
	
	from budg_main import path as impPath
	sys.path.append("C:\\Users\Charles\Dropbox\Programming\py\general_use")
	from error_classes import stdException
	from conversion import timeConv
	from random_tools import id_generator
	from sqlalchemy import and_,or_
	from datetime import date
	
except:
	print "Importing Failed"
	raise 
else:
	print "Importing Complete"

#This section is only used if we make changes to our database
#delete the existing database for now till it is setup the way we want it
def deleteDB():
	try:
		print "Attempting Database Deletion"
		if os.path.exists(impPath) and os.path.isfile(impPath):
			print "file found"
			print "Last accessed: "+timeConv(os.path.getatime(impPath))
			os.remove(impPath)
			print "Deleted: %s"%impPath
	except:
		print "Database deletion Failed"
	else:
		print "Database deletion Complete"
	print "----------------------"
		
def createDB():
	#create the new database and session
	try:
		print "Attempting Database Creation"
		session=budg_main.createAll()
		session.close()
	except:
		print "Database creation Failed"
	else:
		print "Database create Complete"

def testEntries_Expense():
	#a function to quickly fill out a DB in case of deletion, used for testing
	#creates multiple test entries
	session=budg_main.createAll()	#create a session to edit the expense table with
	#create basic entries
	session.add(Expense("car",True,date(2013,12,14),"",True,311,"",False))
	#commit the entries
	session.commit()
	#search for all results
	result=session.query(Expense)
	for thing in result:
		print thing
	session.close()
'''
def outputUser(username):
	#prints out a user's data
	session=idea_box.createAll()
	print session.query(User).filter(User.username==username).all()
	
def outputIdea(username,title):
	#prints out a specific idea
	session=idea_box.createAll()
	user=session.query(User).filter(User.username==username).all()[0]
	print session.query(Idea).filter(and_(Idea.user_id==user.id,Idea.title==title)).all()
	
def newUser():
	#this function creats a new user
	try:
		#create a new use with a randomly generated username
		print "Attempting New User Creation"
		session=idea_box.createAll()
		username="New User 1"
		password="THISSHOULDBEACCEPTABLE"
		if idea_box.createUser(username,password,session):
			print "User Created"
		else: print "User not Created"
		session.close()
	except:
		print "User Creation Error"
		raise
	else:
		print "User Creation Error Free"
		outputUser(username.lower())
		
def newIdea():
	#create a new idea for a user with no existing ideas
	try:
		#add an idea to a user with no existing ideas, if one does not exist, create a new user
		print "Attempting First Idea Addition"
		username="New User 1"
		title="A stupid Title"
		#find a user with no ideas
		session=idea_box.createAll()		
		#the test user has no ideas, we will add a new one
		if idea_box.createIdea(username.lower(),title.lower(),"BODY","tag1,tag2",session):
			print "Idea Created"
		else: print "IDea not created"
		session.close()
		
	except:
		print "Idea Creation Failed"
		raise
	else:
		print "Idea Creation Successful"
		outputIdea(username.lower(),title.lower())
		
def changePW():
	#this function changes the password
	try:
		#create a new use with a randomly generated username
		print "Attempting Password change"
		session=idea_box.createAll()
		username="New User 1".lower()
		password="fuckmeisthis10?E"
		if idea_box.changePassword(username,password,session):
			print "Password Changed"
		else: print "Password not changed"
		session.close()
	except:
		print "Password change error"
		raise
	else:
		print "Passowrd Change complete"
		outputUser(username.lower())
		
def changeUname():
	#this ufnction changes the password
	try:
		#create a new use with a randomly generated username
		print "Attempting Username change"
		session=idea_box.createAll()
		username="New User 1".lower()
		newUsername="fuckYes".lower()
		if idea_box.changeUsername(username,newUsername,session):
			print "Username changed"
		else: print "Username not changed"
		session.close()
	except:
		print "Username change error"
		raise
	else:
		print "Username change error free"
		outputUser(newUsername.lower())
		
def changeIdeaTitle():
	#changes an idea's title
	try:
		print "Attempting title change"
		session=idea_box.createAll()
		username="fuckyes".lower()
		title="A stupid Title".lower()
		newTitle="A great title".lower()
		if idea_box.changeTitle(username,title,newTitle,session):
			print "Title Changed"
		else: print "Title not changed"
		session.close()
	except:
		print "Title Chjange error"
		raise
	else:
		print "title change error free"
		outputIdea(username.lower(),newTitle.lower())
		
def changeBody():
	#changes an idea's body
	try:
		#create a new use with a randomly generated username
		print "Attempting body change"
		session=idea_box.createAll()
		username="fuckyes".lower()
		title="A great title".lower()
		if idea_box.changeIdea(username,title,"THIS IS A FUCKING BODY",session):
			print "Body Changed"
		else: print "Body not changed"
		session.close()
	except:
		print "Body Change error"
		raise
	else:
		print "Body change error free"
		outputIdea(username.lower(),title.lower())
		
def tagWork():
	#changes an idea's tags, delete one, add one, edit one
	try:
		#create a new use with a randomly generated username
		print "Attempting body change"
		session=idea_box.createAll()
		username="fuckyes".lower()
		title="A great title".lower()
		tagtoAdd="NEWTAG"
		tagtoDelete="tag1"
		tagtoEdit="tag2"
		tagtoEditTo="supertag2"
		if idea_box.deleteTag(username,title,tagtoDelete,session):
			print "Tag %s deleted"%tagtoDelete
		else: print "Tag  not deleted"%tagtoDelete
		
		if idea_box.addTag(username,title,tagtoAdd,session):
			print "Tag %s added"%tagtoAdd
		else: print "Tag  not added"%tagtoAdd
		
		if (idea_box.deleteTag(username,title,tagtoEdit,session) and idea_box.addTag(username,title,tagtoEditTo,session)):
			print "Tag %s edited to %s"%(tagtoEdit,tagtoEditTo)
		else: print "Tag  not edited to %s"%(tagtoEdit,tagtoEditTo)
		session.close()
	except:
		print "Tags edited with error"
		raise
	else:
		print "Tag edits error free"
		outputIdea(username.lower(),title.lower())

def deleteIdea():
#deletes the idea
	try:
		#create a new use with a randomly generated username
		print "Attempting idea deletion"
		session=idea_box.createAll()
		username="fuckyes".lower()
		title="A great title".lower()
		if idea_box.deleteIdea(username,title,session):
			print "Idea Deleted"
		else: print "Idea not deleted"
		session.close()
	except:
		print "Body Change error"
		raise
	else:
		print "Body change error free"
		outputIdea(username.lower(),title.lower())
		
def deleteUser():
#deletes the user
	try:
		#create a new use with a randomly generated username
		print "Attempting user deletion"
		session=idea_box.createAll()
		username="fuckyes".lower()
		if idea_box.deleteUser(username,session):
			print "User Deleted"
		else: print "User not deleted"
		session.close()
	except:
		print "User deletion error"
		raise
	else:
		print "User Deletion error free"
		outputUser(username.lower())
		
def changeToLowerIdeas():
	#a function that changes all idea titles to lowercase
	session=idea_box.createAll()
	results=session.query(User).all()
	
	for user in results:
		for idea in user.ideas:
			idea.title=idea.title.lower()
			idea.tags=idea.tags.lower()
			
	session.commit()
	session.close
	
def changeToLowerUsers():
	#change all aspects of ideas to lower case
	session=idea_box.createAll()
	results=session.query(User).all()
	lNames=[thing.username.lower() for thing in results]
	for i in range(len(results)):
		results[i].username=lNames[i]
		session.add(results[i])
	session.commit()
	session.close
'''

		
deleteDB()
createDB()
testEntries_Expense()
print "----------------------"	
'''
newUser()
print "----------------------"	
newIdea()
print "----------------------"	
changePW()
print "----------------------"	
changeUname()
print "----------------------"	
changeIdeaTitle()
print "----------------------"	
changeBody()
print "----------------------"	
tagWork()
print "----------------------"	
deleteIdea()
print "----------------------"	
deleteUser()
print "----------------------"
'''
