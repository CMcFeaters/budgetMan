'''
budg_tables
this contains all of the setup data for the tables
'''
from appHolder import db
import datetime, inspect, types
import sys, string, os

'''remove these lines when done with debugging
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
path="Users/Charles/Dropbox/Programming/DataBases/budget.db"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+path
db = SQLAlchemy(app)
db.create_all()
'''

def create_a_thing(table,args):
	'''a function that will create a "thing"
	the thing will be an Account, Expense or any other budget related object
	the args will be the parameters required
	assume the user knows what the hell he is doing'''
	thing=table(*args)
	db.session.add(thing)
	db.session.commit()
	if table==CashFlow:
		thing.createExpenses()
		
class dateRange():
	'''an array of all days between two dates'''
	def __init__(self,startDate=datetime.datetime.today(),endDate=datetime.date(datetime.datetime.today().year+1,datetime.datetime.today().month,datetime.datetime.today().day)):
		self.startDate=startDate
		self.endDate=endDate
	
	def __iter__(self):
		#returns the iterator
		return iter([(self.startDate+datetime.timedelta(day)) for day in range(0,(self.endDate-self.startDate).days)])

class Account(db.Model):
	'''primary account class.  the account is setup with a title, a starting value, a starting date and a low value (used to execute warnings)
	additionally cashflows can be linked to the account (separate table) and will be accessed by the account to display output values
	functions:
	getPayments-
		takes in a end date, and start date.  returns an array of the expenses (cashflows) impacting teh account between the two dates
	getPaymentValues
		takes in a start and end date, returns the cash value of expenditures between the two dates
	getRate-
		give a type, a start date and an end date, returns the rate of expense/savings for the account on a type basis (day, month, week)
	getDateValue-
		given an end date, returns the value of the account on that date
	getEstimates-
		given an end date, returns all expenses on an account that are estimates
	'''
	__tablename__="accounts"
	#values
	id=db.Column(db.Integer,primary_key=True)
	title=db.Column(db.String)	#this will have to be a unique value for search purposes
	entVal=db.Column(db.Integer)
	entDate=db.Column(db.DateTime)
	lowVal=db.Column(db.Integer)
	cashFlows=db.relationship("CashFlow",backref=db.backref("accounts",lazy="joined"), cascade='all, delete',lazy="dynamic")	#link to cashflow table
	expenses=db.relationship("Expense",backref=db.backref("accounts",lazy="joined"),cascade='all, delete',lazy="dynamic")	#link to Expense table
	budgets=db.relationship("BudgetTag",backref=db.backref("accounts",lazy="joined"),cascade='all, delete',lazy="dynamic")	#link to Expense table
	masters=db.relationship("Master",backref=db.backref("accounts",lazy="joined"),cascade='all, delete',lazy="dynamic")	#link to Expense table
		
	'''account class'''
	def __init__(self,title,entVal,entDate=datetime.datetime.today(),lowVal=0):
		self.title=title
		self.entVal=entVal
		self.entDate=entDate
		self.lowVal=lowVal
	
	def getBudgets(self,endDate=datetime.datetime.today(),startDate=entDate):
		'''
		returns a list of budgets associated with this account
		'''
		return [budg for budg in self.budgets.all() if budg.eDate.date()<=endDate.date() and budg.sDate.date()>=startDate.date()]
	
	def getBudgetValues(self,endDate=datetime.datetime.today(),startDate=False):
		'''
		gets the value all of the expenses between the two dates given
		defaults to entDate if startdate isn't given
		'''
		if not startDate: startDate=self.entDate
		budgValue=0
		print endDate
		print startDate
		print self.getBudgets(endDate,startDate)
		#not returning all of the linked budgets
		for budget in self.getBudgets(endDate,startDate):
			if budget.expenses.all()==[]:
				budgValue+=budget.value	#only count budgets that do not have expenses associated with them, expenses are picked up in get expenses
		return budgValue
	
	def getExpenses(self,endDate=datetime.datetime.today(),startDate=entDate):
		'''
		returns a list of expenses associated with this account
		'''
		return [exp for exp in self.expenses if exp.date.date()<=endDate.date() and exp.date.date()>=startDate.date()]
	
	def getExpenseValues(self,endDate=datetime.datetime.today(),startDate=False):
		'''
		gets the value all of the expenses between the two dates given
		defaults to entDate if startdate isn't given
		'''
		if not startDate: startDate=self.entDate
		expValue=0
		
		for expense in self.getExpenses(endDate,startDate):
			expValue+=expense.value
		return expValue
	
	def getTransfers(self,endDate=datetime.datetime.today(),startDate=False):
		
		'''
		this finds all of the transfers related to this acocunt
		returns ([transfers_in],[transfers_out]) in the form of (transfer in,transfer out)
		'''
		if not startDate: startDate=self.entDate
		
		tf_in=db.session.query(Transfer).\
		filter(Transfer.t_account_id==self.id).all()
			
		tf_out=db.session.query(Transfer).\
		filter(Transfer.f_account_id==self.id).all()
		
		#this is a workaround for filtering out the dates associated with the transfers
		for thing in tf_out:
			if thing.date.date()<startDate.date() or thing.date.date()>endDate.date() :
				tf_out.remove(thing)
		#this is a workaround for filtering out the dates associated with the transfers
		for thing in tf_in:
			if thing.date.date()<startDate.date() or thing.date.date()>endDate.date() :
				tf_in.remove(thing)
				
		return (tf_in,tf_out)
	
	def getTransferValues(self,endDate=datetime.datetime.today(),startDate=False, inOut="none"):
		'''
		a function which returns the values of all transfers in teh form of (in,-out)
		'''
		(tfs_in,tfs_out)=self.getTransfers(endDate,startDate)
		incoming=0
		outgoing=0
		
		for tf_in in tfs_in:
			incoming+=tf_in.value
		for tf_out in tfs_out:
			outgoing-=tf_out.value
			
		if inOut=="in":
			return incoming
		elif inOut=="out":
			return outgoing
		else: return (incoming,outgoing)
		
	def getDateValue(self,endDate=datetime.datetime.today()):
		'''returns a value containing the $ value of an account including all expenses up to endDate from entDate'''
		return self.entVal+self.getExpenseValues(endDate)+self.getTransferValues()[0]+self.getTransferValues()[1]+self.getBudgetValues()
		
	def __repr__(self):
		return "Title: %s \nValue: %s \nDate: %s\n Current Value: %s"%(self.title,self.entVal,self.entDate, self.getDateValue())

	def __iter__(self):
		return iter([attr[0] for attr in inspect.getmembers(self,not inspect.ismethod) if type(attr[1])!=types.MethodType and not attr[0].startswith("_") and not len(attr[0])<=1])
	
class CashFlow(db.Model):
	'''cashFlow class
		This class/table is to capture all cashflow data related to an account.
		this is a constant thing like rent
	'''
	__tablename__="cashflows"
	id=db.Column(db.Integer,primary_key=True)
	account_id=db.Column(db.Integer,db.ForeignKey('accounts.id'))
	title=db.Column(db.String)	
	value=db.Column(db.Integer)
	date=db.Column(db.DateTime)
	recurType=db.Column(db.String) #Day, Month, Week
	recurRate=db.Column(db.Integer)
	recurEnd=db.Column(db.DateTime)
	expenses=db.relationship("Expense",backref=db.backref("cashflows",lazy="joined"),\
		cascade="all, delete",lazy="dynamic")	#link to expenses table
		
	def __init__(self,account_id,title,value,date=datetime.datetime.today(),recurType="Day",recurRate=1,
	recurEnd=datetime.datetime.today()):
		'''cash flow values'''
		self.account_id=account_id	#the account the cashflow affects
		self.title=title
		self.value=value
		self.date=date
		self.recurType=recurType	#can be false (non-recurring), Day, Month, Week
		self.recurRate=recurRate	#number or recurtypes between recurrence
		self.recurEnd=recurEnd		#date recurrence ends

	def createExpenses(self):
		#generates the expense tables
		
		#delete the existing items
		[db.session.delete(thing) for thing in Expense.query.filter_by(cf_id=self.id).all()]
		db.session.commit()
		
		#creates all new expenses which are linked to the cashflow
		cfRange=dateRange(self.date,self.recurEnd)
		
		#fill in the expenses
		if self.recurType=="Day" and self.recurRate>0:
			series=[create_a_thing(Expense,[self.account_id,self.title,self.value,pDate,self.id])
			for pDate in cfRange if ((pDate-self.date).days)%self.recurRate==0]
		elif self.recurType=="Week":
			series=[create_a_thing(Expense,[self.account_id,self.title,self.value,pDate,self.id])
			for pDate in cfRange if ((pDate-self.date).days)%(self.recurRate*7)==0]
		elif self.recurType=="Month":
			series=[create_a_thing(Expense,[self.account_id,self.title,self.value,pDate,self.id])
			for pDate in cfRange if ((pDate.month-self.date.month))%(self.recurRate)==0 and pDate.day==self.date.day]
	
	def getFlow(self):
		'''
		get's the daily value of the cashflow
		'''
		val=0
		for thing in self.expenses:
			val+=thing.value
		return int(val/int((self.recurEnd-self.date).days))
		
	def __repr__(self):
		return "Title: %s \nValue: %s \nRate: %s %s"%(self.title,self.value, self.recurRate,self.recurType)

	def __iter__(self):
		#iterate the members of cashflow
		return iter([attr[0] for attr in inspect.getmembers(self,not inspect.ismethod) if type(attr[1])!=types.MethodType and not attr[0].startswith("_")])

		
class Expense(db.Model):
	'''Single expense class
		Contains the following properties-
		id: primary key
		account_id: foreign_key (one account to many expenses)
		value: integer, the cost of the expense (+/-)
		date: datetime, the datetime of the expense
	'''
	__tablename__="expenses"
	
	id=db.Column(db.Integer,primary_key=True)
	account_id=db.Column(db.Integer,db.ForeignKey('accounts.id'))
	cf_id=db.Column(db.Integer,db.ForeignKey('cashflows.id'))	#link to a cashflow if appropriate
	title=db.Column(db.String)
	value=db.Column(db.Integer)
	date=db.Column(db.DateTime)
	budg_id=db.Column(db.Integer,db.ForeignKey('budgets.id'))
	#actuals=db.relationship("Actual",backref=db.backref("expenses",lazy="joined"),lazy="dynamic")	#link to actuals table
	
	def __init__(self,account_id,title,value,date=datetime.datetime.today(),cf_id=False,budg_id=False):
		self.account_id=account_id
		self.title=title
		self.value=value
		self.date=date
		if cf_id:
			self.cf_id=cf_id
		
		if budg_id:
			self.budg_id=budg_id
		
	def __repr__(self):
		return "Title: %s \nValue: %s \nDate: %s"%(self.title,self.value,self.date)

		
	def __iter__(self):
		#iterate the members of cashflow
		return iter([attr[0] for attr in inspect.getmembers(self,not inspect.ismethod) if type(attr[1])!=types.MethodType and not attr[0].startswith("_")])

class Master(db.Model):
	'''cashFlow class
		This class/table is to capture all cashflow data related to an account.
		this is a constant thing like rent
	'''
	__tablename__="masters"
	id=db.Column(db.Integer,primary_key=True)
	account_id=db.Column(db.Integer,db.ForeignKey('accounts.id'))
	title=db.Column(db.String)	
	value=db.Column(db.Integer)
	date=db.Column(db.DateTime)
	recurType=db.Column(db.String) #Day, Month, Week
	recurRate=db.Column(db.Integer)
	recurEnd=db.Column(db.DateTime)
	budgetTags=db.relationship("BudgetTag",backref=db.backref("masters",lazy="joined"),\
		cascade="all, delete",lazy="dynamic")	#link to expenses table
		
	def __init__(self,account_id,title,value,date=datetime.datetime.today(),recurType="Day",recurRate=1,
	recurEnd=datetime.datetime.today()):
		'''cash flow values'''
		self.account_id=account_id	#the account the cashflow affects
		self.title=title
		self.value=value
		self.date=date
		self.recurType=recurType	#can be false (non-recurring), Day, Month, Week
		self.recurRate=recurRate	#number or recurtypes between recurrence
		self.recurEnd=recurEnd		#date recurrence ends

	def createBudgetTags(self):
		#generates the expense tables
		
		#delete the existing budgetTags
		[db.session.delete(thing) for thing in BudgetTag.query.filter_by(master_id=self.id).all()]
		db.session.commit()
		
		#creates all new expenses which are linked to the cashflow
		budgRange=dateRange(self.date,self.recurEnd)
		
		#create a list of start dates depending on the recurRate
		if self.recurType=="Day" and self.recurRate>0:
			sDates=[pDate for pDate in budgRange if ((pDate-self.date).days)%self.recurRate==0]
		elif self.recurType=="Week":
			sDates=[pDate for pDate in budgRange if ((pDate-self.date).days)%(self.recurRate*7)==0]
		elif self.recurType=="Month":
			sDates=[pDate for pDate in budgRange if ((pDate.month-self.date.month))%(self.recurRate)==0 and pDate.day==self.date.day]
		
		#use the start dates to create the budget dates useing the
		budgDates=[]
		for i in range(0,len(sDates)-1):
			budgDates.append((sDates[i],sDates[i+1]-datetime.timedelta(1)))
		
		#create all of the budgetTags
		[create_a_thing(BudgetTag,[self.account_id,self.id,self.title,self.value,sDate[0],sDate[1]]) for sDate in budgDates]

	
class BudgetTag(db.Model):
	'''A container/label for expenses
		this is used for individual budgets and is generated by the master budget table
		expenses are assigned to this budget
	'''
	__tablename__="budgets"
	
	id=db.Column(db.Integer,primary_key=True)
	account_id=db.Column(db.Integer,db.ForeignKey('accounts.id'))
	master_id=db.Column(db.Integer, db.ForeignKey('masters.id'))
	title=db.Column(db.String)
	value=db.Column(db.Integer)
	sDate=db.Column(db.DateTime)
	eDate=db.Column(db.DateTime)
	expenses=db.relationship("Expense",backref=db.backref("budgets",lazy="joined"),lazy="dynamic")	#link to expenses table
	
	def __init__(self,account_id,master_id,title,value,sDate,eDate):
		self.account_id=account_id
		self.master_id=master_id
		self.title=title
		self.value=value
		self.sDate=sDate
		self.eDate=eDate
		
	def getValue():
		#returns the total value of all expenses listed under the budget
		val=0
		for exp in self.expenses:
			val+=exp.value
		return val
		

class Transfer(db.Model):
	'''transfer is an expense from one account to another
	ex: paying your credit card bill, cc account decreases, debit account decreases
		f_account_id is the from account
		t_account_id is the to account
		value will be relative to the from account, e.g. if -500 is the value
		f_account will have entVal+value
		t_account_id will have entVal-val
		'''
	__tablename__="transfers"
	
	id=db.Column(db.Integer,primary_key=True)
	title=db.Column(db.String)
	value=db.Column(db.Integer)
	date=db.Column(db.DateTime)
	f_account_id=db.Column(db.Integer, db.ForeignKey("accounts.id"))
	t_account_id=db.Column(db.Integer, db.ForeignKey("accounts.id"))
	
	f_account=db.relationship("Account",foreign_keys=f_account_id,
		primaryjoin=("Transfer.f_account_id==Account.id"))
	t_account=db.relationship("Account", foreign_keys=t_account_id,
		primaryjoin=("Transfer.t_account_id==Account.id"))
	
	def __init__(self,title,value,f_account_id,t_account_id,date=datetime.datetime.today()):
		self.f_account_id=f_account_id
		self.t_account_id=t_account_id
		self.title=title
		self.value=value
		self.date=date
	
	def __repr__(self):
		return "Title: %s \nValue: %s \nDate: %s\n to Acc: %s\n from Acc: %s"%(self.title,self.value,self.date, self.t_account_id,self.f_account_id)


	
