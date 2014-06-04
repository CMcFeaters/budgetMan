from appHolder import db
import unittest, datetime, sys
from budg_tables import Account, Expense, CashFlow, Transfer

'''this file runs some tests on the budget tables created
'''

class expenseTests(unittest.TestCase):
	
	def deleteDB(self):
		path="C:\\Users\Charles\Dropbox\Programming\DataBases\\budget.db"
		if os.path.exists(path):
			os.remove(path)
	
	def _test001_addExpense(self):		
		#create an account
		acc=db.session.query(Account).all()[0]
		exp=Expense(acc.id, "TestExpense",5,datetime.datetime.today())
		#session=self.createDB()
		db.session.add(exp)
		db.session.commit()	#add the entry to the db
		self.assertTrue(True)
	
	def _test002_displayExpenses(self):
		acc=db.session.query(Account).all()[0]
		exp=db.session.query(Expense).all()[0]
		print '--------------------'
		print exp
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

class transferTests(unittest.TestCase):
	
	def deleteDB(self):
		path="C:\\Users\Charles\Dropbox\Programming\DataBases\\budget.db"
		if os.path.exists(path):
			os.remove(path)
	
	def test001_addTransfer(self):		
		#create an account
		acc1=db.session.query(Account).all()[0]
		acc2=db.session.query(Account).all()[1]
		budg_tables.create_a_thing(Transfer,['TestTransfer',50,acc1.id,add2.id,datetime.datetime.today()])

		self.assertTrue(True)
	
	def test002_displayTransfer(self):
		#acc=db.session.query(Account).all()[0]
		tf=db.session.query(Transfer).all()[0]
		print '--------------------'
		print tf
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

			
			
class accountTests(unittest.TestCase):
	'''tests run on the account to verify random things are working
	'''

		
	def test001_displayAccounts(self):
		'''test to display available accounts and their expense data
		'''
		accs=db.session.query(Account)
		for acc in accs:
			print "----Account----"
			print ">"+acc.title
			
			exps=db.session.query(Expense).filter_by(account_id=acc.id)
			print "----Expenses----"
			for exp in exps:
				print ">"+exp.title

			cfs=db.session.query(CashFlow).filter_by(account_id=acc.id)
			print "----CashFlows----"
			for cf in cfs:
				print ">"+cf.title
		
		self.assertTrue(True)
			
	def test002_verifyExpense(self):
		'''gives account total based on expenses using getDateValue
		'''
		if db.session.query(Account).filter_by(title="TESTACCOUNT").all()==[]:
			budg_tables.create_a_thing(Account,["TESTACCOUNT",100])
		acc=db.session.query(Account).filter_by(title="TESTACCOUNT").all()[0]
		
		if db.session.query(Expense).filter_by(title="TESTEXPENSE",account_id=acc.id).all()==[]:
			db.session.add(Expense(acc.id,"TESTEXPENSE",-50))
			db.session.commit()
		
		exp=db.session.query(Expense).filter_by(title="TESTEXPENSE",account_id=acc.id).all()[0]
		
		self.assertTrue(acc.getDateValue()==50)
		
	
def main():
	'''from flask import Flask
	from flask.ext.sqlalchemy import SQLAlchemy
	path="Users/Charles/Dropbox/Programming/DataBases/budget.db"
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+path
	db = SQLAlchemy(app)'''
	db.create_all()
	unittest.main()
	
if __name__=="__main__":
	main()