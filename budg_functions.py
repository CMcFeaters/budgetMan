'''budget program
	these are individual functions called by the budg_page module
	these functions will handle all of the back end procedures used int he program
	functions include:
	
	addAccount-
		given a title, value, date and lowvalue(optional) creates and commits an account to the db
	queryAccounts-
		given a filter, returns an array containing all accounts		
	
	removeAccount-
		
	editAccount-
		takes in values and edits an account accordingly.
		
	dateCompile-
		takes in a year, month and day strings, validates and returns either a datetime object of false
	amountCompile-
		takes in a string as a number, validates and returns an int
	
	accountCompile-
		given entry data, validates all requirements, compiles data into database format and calls
		addAccount
	
	addExpenses-
		
	removeExpense-
		
	editExpense-
		
	
'''

from budg_tables import CashFlow, Account
from appHolder import db
from server_validation import titleValidate, dateValidate, amountValidate
import unittest, datetime, inspect, types
import sys, string, os, random

from operator import ne,eq,lt,le,ge,gt

class functionTests(unittest.TestCase):
	'''these tests will be to test the functionallity of the functions used in the budget program
	'''
	def deleteDB(self):
		path="C:\\Users\Charles\Dropbox\Programming\DataBases\\budget.db"
		if os.path.exists(path):
			os.remove(path)

	def _test001_AddAccount(self):		
		#create an account
		name="Checking"+str(random.randrange(100))
		amount=str(random.randrange(100))
		x=accountCompile(name,amount,"2013","12","25","500")
		if x[0]!=False:
			addAccount(x[0],x[1],x[2],x[3])
		res=len(Account.query.filter_by(title=name.lower()).all())
		if res==1:
			self.assertTrue(True)
		else:
			self.assertTrue(False)
	
	def _test002_displayAccounts(self):
		res=Account.query
		print"******************************************************"
		for thing in res:
			print "ID: %s\nTitle: %s\n Amount: %s\n Date: %s\n"%(thing.id,thing.title,thing.entVal,thing.entDate.date())
		print"******************************************************"
		self.assertTrue(True)	
	
	def _test003_deleteAccount(self):
		res=Account.query.all()
		acc=res[random.randrange(len(res))]
		delAccount(acc.title)
		if len(Account.query.filter_by(title=acc.title).all())==0:
			self.assertTrue(True)
		else:
			self.assertTrue(False)
	
	def _test004_addCashflow(self):
		'''adds a cash flow to a given account'''
		res=Account.query
		acc=res[random.randrange(len(res.all()))]
		nTitle="CashFlow%s"%random.randrange(100)
		value=random.randrange(100)
		sY="2014"
		sM="01"
		sD="01"
		eY="2015"
		eM="01"
		eD="01"
		recurType="Day"
		recurRate=10
		recurEnd=datetime.datetime.today()+datetime.timedelta(days=365)
		x=cfCompile(acc.id,nTitle,value,sY,sM,sD,recurType,recurRate,eY,eM,eD)
		if x[0]!=False:
			addCashFlow(x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8])
			self.assertTrue(True)
		else:
			self.assertTrue(False)
	
	def _test005_editAccount(self):
		'''a funciton to modify certain account aspects'''
		res=Account.query
		acc=res[random.randrange(len(res.all()))]
		nTitle=str(random.randrange(100))+"abcd"+str(random.randrange(100))
		nValue=acc.entVal*10
		nDate=acc.entDate+datetime.timedelta(365)
		editAccount(acc.id,nTitle,nValue,nDate)
		if len(Account.query.filter_by(title=nTitle).all())>0:
			self.assertTrue(True)
		else:
			self.assertTrue(False)
			
	
	def _test099_displayAccountsFinal(self):
		res=Account.query
		print"******************************************************"
		for thing in res:
			print "\nID: %s\nTitle: %s\n Start Amount: %s - End Amount: %s\n Start Date: %s - End Date: %s"% \
			(thing.id,thing.title,thing.entVal,thing.getDateValue(),thing.entDate.date(),datetime.date.today())
			for flow in thing.cashFlows:
				for cf in flow.createSeries():
					print "    %s - %s - %s - %s - %s - %s"%(cf.title,cf.value,cf.date.date(),cf.recurType,cf.recurRate,cf.recurEnd.date())
				
		print"******************************************************"
		self.assertTrue(True)	
		
	def _test999_deleteDB(self):
		db.session.close()
		self.deleteDB()
		print "deleted"
		self.assertTrue(True)
		
	def printAccounts(self):
		results=db.session.query(Account)
		
		for thing in results:
			print "_____******______"
			print thing
			print "_____******______"



def editAccount(aId,nTitle="",nVal="",nDate="",nLow=""):
	'''edits an existing account to match the new values sent in'''
	#this needs to be variable so that you can edit the name and/or value and/or date, etc
	#check to make sure the title isn't being used
	acc=Account.query.filter_by(id=aId).all()[0]
	if nTitle<>"":
		if titleValidate(nTitle):
			acc.title=nTitle.lower()
		else:
			print nTitle
			return False
	if nVal<>"":
		acc.entVal=nVal
	if nDate<>"":
		acc.entDate=nDate
	if nLow<>"":
		acc.lowVal=nLow
	db.session.commit()
		
def dateCompile(year,month,day):
	'''takes in strings for year, month and day.  if they pass datevalidate returns
	a datetime object, else returns false'''
	if dateValidate(year,month,day):
		return datetime.datetime(int(year),int(month),int(day))
	else:
		return False

def amountCompile(amt):
	if amountValidate(amt):
		return int(amt)
	else:
		return "False"

def accountCompile(nTitle,entVal,entY,entM,entD,lowVal=0):
	'''#check all of the entered values, return a multi element tuple with the 
	#compiled values if correct'''
	entVal=amountCompile(entVal)
	entDate=dateCompile(entY,entM,entD)
	lowVal=amountCompile(lowVal)
	if titleValidate(nTitle):
		if entVal!="False":
			if entDate!=False:
				if lowVal!="False":
					return (nTitle,entVal,entDate,lowVal)
				else:
					return (False,"LowVal is not a value")
			else:	
				return (False,"Entered date is a proper date in MM/DD/YYYY format")
		else:
			return (False,"Entered Value is not a value")
	else:
		return (False,"Title already exists or is not letters/numbers")
		
def addAccount(nTitle,entVal,entDate,lowVal=0):
	'''creates and commits a new account, must first verify the name doesn't already exist'''
	acc=Account(nTitle.lower(),entVal,entDate,lowVal)
	db.session.add(acc)
	db.session.commit()

def delAccount(nTitle):
	'''deletes an account with matching title to nTitle'''
	acc=Account.query.filter_by(title=nTitle).all()
	if len(acc)==1:
		db.session.delete(acc[0])
		db.session.commit()

	
def cfCompile(account,nTitle,nValue,sY,sM,sD,nRType,nRRate,eY,eM,eD,nEstimate=False):
	'''a compilation function.  takes in all teh cashflow variables, validates they are in range and returns
	a tuple containing True and the modified variables or False and the reason for failure'''
	#title check (will take in accunt id and newTitle
	#need a type check
	#need a ratecheck
	#need an estimate check
	entVal=amountCompile(nValue)
	sDate=dateCompile(sY,sM,sD)
	eDate=dateCompile(eY,eM,eD)
	#typeValidate-returns true or false, use to validate only
	#rate validate
	estimate=estCompile(nEstimate)#i don't think i actually need this one.
	return False
	
		
def addCashFlow(account,nTitle,nValue,nDate,nRType,nRRate,nREnd,nEstimate=False):
	'''adds a cashflow to a given account'''
	cf=CashFlow(account.id,nTitle,nValue,nDate,nRType,nRRate,nREnd,nEstimate)
	db.session.add(cf)
	db.session.commit()
	
	
def main():
	from flask import Flask
	from flask.ext.sqlalchemy import SQLAlchemy
	path="Users/Charles/Dropbox/Programming/DataBases/budget.db"
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+path
	db = SQLAlchemy(app)
	db.create_all()
	unittest.main()
			
if __name__=="__main__":
	main()
	
