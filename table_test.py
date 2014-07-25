from appHolder import db
import unittest, datetime, sys, os
from random import randint
from budg_tables import create_a_thing,Account, CashFlow, Expense, Transfer, Budget

'''this file runs some tests on the budget tables created
'''


class test1_accountTests(unittest.TestCase):
	'''tests run on the account to verify random things are working
	'''

	def test001_addAccount(self):
		'''adds an account
		'''
		name="TESTACCOUNT"+str(randint(0,100))
		create_a_thing(Account,[name,100])
			
		self.assertTrue(db.session.query(Account).filter_by(title=name).all()!=[])

	
	def test002_displayAccounts(self):
		'''test to display available accounts and their expense data
		'''
		accs=db.session.query(Account)
		'''for acc in accs:
			print '--------------------'
			print acc
		'''	
		
		self.assertTrue(True)
			
class test2_expenseTests(unittest.TestCase):
	
	def test001_addExpense(self):		
		#create an account
		name="TestExpense"+str(randint(0,100))
		acc=db.session.query(Account).all()[0]
		create_a_thing(Expense,[acc.id,name,5,datetime.datetime.today()])
		self.assertTrue(db.session.query(Expense).filter_by(title=name).all()!=[])
	
	def test002_displayExpenses(self):
		#acc=db.session.query(Account).all()[0]
		exps=db.session.query(Expense).all()
		#for exp in exps:
		#	print '--------------------'
		#	print exp
		self.assertTrue(True)

class test3_transferTests(unittest.TestCase):

	def test001_addTransfer(self):		
		#create an account
		acc=db.session.query(Account).all()
		if len(acc)<2:
			create_a_thing(Account,["TESTACCOUNT"+str(randint(0,100)),100])
			acc=db.session.query(Account).all()
		acc1=acc[0]
		acc2=acc[1]
		create_a_thing(Transfer,['TestTransfer'+str(randint(0,100)),50,acc1.id,acc2.id,datetime.datetime.today()])

		self.assertTrue(True)


class test4_cashFlowTests(unittest.TestCase):
	'''
	tests run to verify the cashflows are working
	'''
	def test001_addCashFlow(self):		
		#create an account
		name="TestCashFlow"+str(randint(0,100))
		acc=db.session.query(Account).all()[0]
		oneYear=datetime.datetime.today()+datetime.timedelta(365)
		create_a_thing(CashFlow,[acc.id,name,500,datetime.datetime.today(),"Day",10,oneYear])
		self.assertTrue(db.session.query(CashFlow).filter_by(title=name).all()!=[])
	
	def test002_displayCashFlow(self):
		#acc=db.session.query(Account).all()[0]
		cfs=db.session.query(CashFlow).all()
		for cf in cfs:
			print '---------*----------'
			print cf
			print  '---------*----------'
		self.assertTrue(True)
		
	def test003_createExpense(self):
		cf=db.session.query(CashFlow).all()[0]
		for thing in Expense.query.filter_by(cf_id=cf.id).all():
			print thing
		self.assertTrue(True)
			

class test7_checkBudgets(unittest.TestCase):
	'''tests the budget functionality'''
	def test001_make_budgets(self):
		testBudg=create_a_thing(Budget,['Snacks'])
		self.assertTrue(True)
	
	def test002_assign_budgets(self):
		testBudg=Budget.query.first()
		expData=Expense.query.first()
		expData.budg_id=testBudg.id
		db.session.add(expData)
		db.session.commit()
		self.assertTrue(expData.value==Expense.query.filter_by(budg_id=testBudg.id).first().value)
		
		
	
class test6_checkSum(unittest.TestCase):
	'''tests run on the account to verify random things are working
	'''
	tomorrow=datetime.datetime.today()+datetime.timedelta(365)	#a date for summing purposes
	
	def test001_checkExpenses(self):
		'''this function will validate the expense values are totaled in the getExpense function
		'''
		accs=db.session.query(Account).all()
		exps=db.session.query(Expense)
		for acc in accs:
			total=0
			exps_a=exps.filter_by(account_id=acc.id).all() #all expenses associated with acc
			for exp in exps_a:
				total+=exp.value
			if total!=acc.getExpenseValues(self.tomorrow): 
				print "Manual total: %s"%total
				print "Automat total: %s"%acc.getExpenseValues(self.tomorrow)
				self.assertTrue(False)
		
		self.assertTrue(True)
	
	def test002_checkTransfers(self):
		'''
		test to validate the transfers are effecting the accounts as they should be
		'''
		tfs=db.session.query(Transfer).all()
		accs=db.session.query(Account).all()
		#db.session.query(Transfer).filter_by(f_account_id=accs[0].id).all() 
		'''for thing in accs:
			print "*************"
			print "Account: %s"%thing.id
			print thing.getTransfers()
			print thing.getTransferValues()'''
		self.assertTrue(True)

	def test003_checkAll(self):
		'''
		this function checks to verify all of the items affecting an account are tallied up in 
		the account datevalue function
		'''
		exps=db.session.query(Expense).all()
		tfs=db.session.query(Transfer).all()
		accs=db.session.query(Account).all()
		oneYear=datetime.datetime.today()+datetime.timedelta(365)
		for acc in accs:
			transTotal=acc.getTransferValues(oneYear)[0]+acc.getTransferValues(oneYear)[1]

			expsTotal=acc.getExpenseValues(oneYear)
			
			if acc.getDateValue(oneYear)!=acc.entVal+expsTotal+transTotal:
				print acc.title
				self.assertTrue(False)
			else: 
				print "****12345******"
				print "Account: %s"%acc.title
				print "Value: %s"%acc.getDateValue(oneYear)
				print "Start Amount: %s"%acc.entVal
				print "Total transfered: %s"%transTotal
				print "Total Expense: %s"%expsTotal
		
		self.assertTrue(True)
		
			
def clear_test_db():
	path="C:\\Users\Charles\Dropbox\Programming\DataBases\\budget.db"
	if os.path.exists(path):
		os.remove(path)
	db.create_all()
			
def main():
	'''from flask import Flask
	from flask.ext.sqlalchemy import SQLAlchemy
	path="Users/Charles/Dropbox/Programming/DataBases/budget.db"
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+path
	db = SQLAlchemy(app)'''
	clear_test_db()
	unittest.main()
	
if __name__=="__main__":
	main()