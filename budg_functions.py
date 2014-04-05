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
		
	addExpenses-
		
	removeExpense-
		
	editExpense-
		
	
'''

from budg_tables import CashFlow, Account
from budg_page import db
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import unittest, datetime, inspect, types
import sys, string, os, random

import sys, string
from operator import ne,eq,lt,le,ge,gt

class functionTests(unittest.TestCase):
	'''these tests will be to test the functionallity of the functions used in the budget program
	'''
	def deleteDB(self):
		path="C:\\Users\Charles\Dropbox\Programming\DataBases\\budget.db"
		if os.path.exists(path):
			os.remove(path)

	def test001_AddAccount(self):		
		#create an account
		name="Checking"+str(random.randrange(100))
		amount=random.randrange(100)
		date=datetime.datetime(2014,01,01)
		addAccount(name,amount,date)
		#session=self.createDB()
		res=Account.query.filter_by(title=name.lower()).first()
		if res.entVal==amount and res.entDate==date:
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
	
	def test004_addCashflow(self):
		'''adds a cash flow to a given account'''
		res=Account.query
		acc=res[random.randrange(len(res.all()))]
		nTitle="CashFlow%s"%random.randrange(100)
		value=random.randrange(100)
		date=datetime.datetime(2014,01,01)#.today()-datetime.timedelta(days=random.randrange(100))
		recurType="Day"
		recurRate=10
		recurEnd=datetime.datetime.today()+datetime.timedelta(days=365)
		addCashFlow(acc,nTitle,value,date,recurType,recurRate,recurEnd)
		if len(CashFlow.query.filter_by(title=nTitle).all())==1:
			self.assertTrue(True)
		else:
			self.assertTure(False)
		
	
	def test099_displayAccountsFinal(self):
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

def addAccount(nTitle,entVal,entDate,lowVal=0):
	'''creates and commits a new account, must first verify the name doesn't already exist'''
	if len(Account.query.filter_by(title=nTitle.lower()).all())==0:
		acc=Account(nTitle.lower(),entVal,entDate,lowVal)
		db.session.add(acc)
		db.session.commit()
	else:
		return "Account: %s already exists, please rename the new account"%nTitle
	
def delAccount(nTitle):
	'''deletes an account with matching title to nTitle'''
	acc=Account.query.filter_by(title=nTitle).all()
	if len(acc)==1:
		db.session.delete(acc[0])
		db.session.commit()

def addCashFlow(account,nTitle,nValue,nDate,nRType,nRRate,nREnd,nEstimate=False):
	'''adds a cashflow to a given account'''
	if len(CashFlow.query.filter_by(title=nTitle.lower()).all())==0:
		cf=CashFlow(account.id,nTitle,nValue,nDate,nRType,nRRate,nREnd,nEstimate)
		db.session.add(cf)
		db.session.commit()
	else:
		return "Cashflor: %s already exists, please rename the new cashflow"%nTitle
		
	
def main():
	path="Users/Charles/Dropbox/Programming/DataBases/budget.db"
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+path
	db = SQLAlchemy(app)
	db.create_all()
	unittest.main()
			
if __name__=="__main__":
	main()
