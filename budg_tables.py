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
	cashFlows=db.relationship("CashFlow",backref=db.backref("accounts",lazy="joined"),lazy="dynamic")	#link to cashflow table
	expenses=db.relationship("Expense",backref=db.backref("accounts",lazy="joined"),lazy="dynamic")	#link to Expense table
	
		
	'''account class'''
	def __init__(self,title,entVal,entDate=datetime.datetime.today(),lowVal=0):
		self.title=title
		self.entVal=entVal
		self.entDate=entDate
		self.lowVal=lowVal
	
	def getPayments(self,endDate=datetime.datetime.today(),startDate=False):
		'''returns a list continaing all of the payments that will occur over a given period for cashflows associated 
		with this account and daterange
		'''
		if not startDate: startDate=self.entDate	#if a start date is not given, assume it's the account entered date
		return [payment for cf in self.cashFlows for payment in cf.createSeries() if payment.date.date()<=endDate.date() and payment.date.date()>=startDate.date()]
	
	def getPaymentValues(self,endDate=datetime.datetime.today(),startDate=False):
		'''given an accounts, start date and an end date, returns the total expenditure
		s for the account between the two dates'''
		if not startDate: startDate=self.entDate
		paymentValue=0
		for payment in self.getPayments(endDate,startDate):
			if payment.date<=endDate and payment.date>=startDate: paymentValue+=payment.value
		return paymentValue
	
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
		return self.entVal+self.getPaymentValues(endDate)+self.getExpenseValues(endDate)+self.getTransferValues()[0]+self.getTransferValues()[1]
	
	def getRate(self,type,startDate,endDate):
		'''determines your <type> cashflow rate between <startDate> and <endDate>'''
		if type=="Day":		#daily expenses
			return (self.getPaymentValues(endDate,startDate)/(endDate-startDate).days)
		elif type=="Week":	#weekly expenses
			return (self.getPaymentValues(endDate,startDate)/(endDate-startDate).days)*7
		else:	#monthly expense
			return self.getPaymentValues(endDate,startDate)/((endDate.year-startDate.year)*12+endDate.month-startDate.month)

	def getEstimates(self,endDate,startDate=False):
		#'''if startdate is false, account entered date is assumed'''
		'''returns a list of all estimated cashflows between <startDate> and <endDate>'''
		return [expense for expense in self.getPayments(endDate,startDate) if expense.estimate]
		
	def __repr__(self):
		return "Title: %s \nValue: %s \nDate: %s\n Current Value: %s"%(self.title,self.entVal,self.entDate, self.getDateValue())

	def __iter__(self):
		return iter([attr[0] for attr in inspect.getmembers(self,not inspect.ismethod) if type(attr[1])!=types.MethodType and not attr[0].startswith("_") and not len(attr[0])<=1])
	
class CashFlow(db.Model):
	'''cashFlow class
		This class/table is to capture all cashflow data related to an account.
		*Note: because some cashflows will affect multiple accoutns (paying a credit card account), a 
				the process for creating the cashflow should include the option to create 2 identical cashflows
				affecting the different accoutns
		Cashflows can be recurring (they happen on a periodic basis) or single.  they have a value, an entry date and
		can be estimates if total is not known (ex: grocery budget)
		functions:
		createSeries-
			this expands a recurring payment into a series of individual paymnets based on type.  output is an array
		popSeries-
			this function takes in a cashflow and returns a tuple containing the first amount of the series and the remainder of teh series.
			this is designed to be used to convert estimated values to real values
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
	estimate=db.Column(db.Boolean)	#is the cashflow an estimate or known value
	expenses=db.relationship("Expense",backref=db.backref("cashflows",lazy="joined"),lazy="dynamic")	#link to expenses table
		
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
		if self.expenses==[]:
			#create all new expenses
			'''
			***********this isnt working.  it's making an transfer accoutn appear
			'''
			if self.recurType=="Day" and self.recurRate>0:
				series=[create_a_thing(Expense,[self.account_id,self.title,self.value,pDate])
				for pDate in cfRange if ((pDate-self.date).days)%self.recurRate==0]
			elif self.recurType=="Week":
				series=[create_a_thing(Expense,[self.account_id,self.title,self.value,pDate])
				for pDate in cfRange if ((pDate-self.date).days)%(self.recurRate*7)==0]
			elif self.recurType=="Month":
				series=[create_a_thing(Expense,[self.account_id,self.title,self.value,pDate])
				for pDate in cfRange if ((pDate.month-self.date.month))%(self.recurRate)==0 and pDate.day==self.date.day]
			
			for exp in series:
				#assign the cf_id for each newly created expense
				exp.cf_id=self.id 
		else:
			#update expenses
			#delete then recreate?
			pass
	
	'''def createSeries(self):
		#converts a recurring payment into a series of paymnets
		#create entire array of cashflows
		#return an array of applicable entries
		
		#initial entry
		cfRange=dateRange(self.date,self.recurEnd)	#the date range for the cashflow

		#generate remaining recurring entries in a similar fasion
		#>>>insert estima6+te links here
		if self.recurType=="Day" and self.recurRate>0:
			series=[CashFlow(self.account_id,self.title,self.value,pDate,False,estimate=self.estimate)
			for pDate in cfRange if ((pDate-self.date).days)%self.recurRate==0]
		elif self.recurType=="Week":
			series=[CashFlow(self.account_id,self.title,self.value,pDate,False,estimate=self.estimate)
			for pDate in cfRange if ((pDate-self.date).days)%(self.recurRate*7)==0]
		elif self.recurType=="Month":
			series=[CashFlow(self.account_id,self.title,self.value,pDate,False,estimate=self.estimate)
			for pDate in cfRange if ((pDate.month-self.date.month))%(self.recurRate)==0 and pDate.day==self.date.day]
		else:
			series=[CashFlow(self.account_id,self.title,self.value,self.date,False,estimate=self.estimate)]
			
		if self.estimate:
			for cf in series:
				#replace all of the estimated values with actual values
				for actual in self.actuals:
					#compare the dates, replace if necessary
					if actual.cf_date==cf.date:
						series[series.index(cf)].date=actual.date
						series[series.index(cf)].value=actual.value
				
			
		return series
		'''
		
	def __repr__(self):
		return "Title: %s \nValue: %s \nRate: %s %s"%(self.title,self.value, self.recurRate,self.recurType)

	def __iter__(self):
		#iterate the members of cashflow
		return iter([attr[0] for attr in inspect.getmembers(self,not inspect.ismethod) if type(attr[1])!=types.MethodType and not attr[0].startswith("_")])

class Actual(db.Model):
	#may be able to remove this completely
	'''
		actual class
			this class will be the actual values aassocited with expenses generated in a cashflow
			cf_id will be th elink to the cashflow
			title will be the cf title+"_{date}"
			value will be the actual value
			date will be the date of the cashflow
			cf_date will be the date of the cashflow it replaces/supercedes
	'''
	__tablename__="actuals"
	
	id=db.Column(db.Integer,primary_key=True)
	#exp_id=db.Column(db.Integer,db.ForeignKey('expenses.id'))	#the expense it's replacing
	title=db.Column(db.String)
	value=db.Column(db.Integer)
	date=db.Column(db.DateTime)
	exp_date=db.Column(db.DateTime)
	
	def __init__(self,cf_id,title,value,exp_date,date=datetime.datetime.today()):
		self.cf_id=cf_id
		self.title=title
		self.value=value
		self.exp_date=exp_date
		self.date=date
	
	def __repr__(self):
		return "Title: %s \nValue: %s \nDate: %s\nCf_Date: %s"%(self.title,self.value, self.date, self.exp_date)
	
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
	#actuals=db.relationship("Actual",backref=db.backref("expenses",lazy="joined"),lazy="dynamic")	#link to actuals table
	
	def __init__(self,account_id,title,value,date=datetime.datetime.today()):
		self.account_id=account_id
		self.title=title
		self.value=value
		self.date=date

		
	def __repr__(self):
		return "Title: %s \nValue: %s \nDate: %s"%(self.title,self.value,self.date)

		
	def __iter__(self):
		#iterate the members of cashflow
		return iter([attr[0] for attr in inspect.getmembers(self,not inspect.ismethod) if type(attr[1])!=types.MethodType and not attr[0].startswith("_")])

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


	
