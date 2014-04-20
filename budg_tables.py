'''
budg_tables
this contains all of the setup data for the tables
'''
from appHolder import db
import unittest, datetime, inspect, types
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


class dateRange():
	'''an array of all days between two dates'''
	def __init__(self,startDate=datetime.datetime.today(),endDate=datetime.date(datetime.datetime.today().year+1,datetime.datetime.today().month,datetime.datetime.today().day)):
		self.startDate=startDate
		self.endDate=endDate
	
	def __iter__(self):
		#returns the iterator
		return iter([(self.startDate+datetime.timedelta(day)) for day in range(0,(self.endDate-self.startDate).days)])
		
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
	
		
	def __init__(self,account_id,title,value,date=datetime.datetime.today(),recurType="False",recurRate=0, 
	recurEnd=datetime.datetime.today(),estimate=False):
		'''cash flow values'''
		self.account_id=account_id	#the account the cashflow affects
		self.title=title
		self.value=value
		self.date=date
		self.recurType=recurType	#can be false (none recurring), days, weeks, months
		self.recurRate=recurRate	#number or recurtypes between recurrence
		self.recurEnd=recurEnd		#date recurrence ends
		self.estimate=estimate		#used to determine if the cashflow is an estimate or a known value

	def createSeries(self):
		#converts a recurring payment into a series of paymnets
		#create entire array of cashflows
		#return an array of applicable entries
		
		#initial entry
		cfRange=dateRange(self.date,self.recurEnd)	#the date range for the cashflow
		#print self

		#generate remaining recurring entries in a similar fasion
		if self.recurType=="Day" and self.recurRate>0:
			series=[CashFlow(self.account_id,self.title,self.value,pDate,False,estimate=self.estimate) for pDate in cfRange if ((pDate-self.date).days)%self.recurRate==0]
		elif self.recurType=="Week":
			series=[CashFlow(self.account_id,self.title,self.value,pDate,False,estimate=self.estimate) for pDate in cfRange if ((pDate-self.date).days)%(self.recurRate*7)==0]
		elif self.recurType=="Month":
			series=[CashFlow(self.account_id,self.title,self.value,pDate,False,estimate=self.estimate) for pDate in cfRange if ((pDate.month-self.date.month))%(self.recurRate)==0 and pDate.day==self.date.day]
		else:
			series=[CashFlow(self.account_id,self.title,self.value,self.date,False,estimate=self.estimate)]
		return series
	
	def popSeries(self,payDate=False,payAmount=False):
		'''Removes the most recent event from a series.  returns a tuple containing the most recent member of the series and the remainder of the series'''
		#update the date and create a new cashflowSeries
		if self.recurType=="Day" and self.recurRate>0:
			#update to teh next day
			nDate=self.date+datetime.timedelta(self.recurRate)
			newSeries=CashFlow(self.account_id,self.title,self.value,nDate,self.recurType,self.recurRate,self.recurEnd,self.estimate)
		elif self.recurType=="Week":
			#update to the next week cyce
			nDate=self.date+datetime.timedelta(self.recurRate*7)
			newSeries=CashFlow(self.account_id,self.title,self.value,nDate,self.recurType,self.recurRate,self.recurEnd,self.estimate)
		elif self.recurType=="Month":
			#update to the next month cycle
			nMonth=self.date.month+self.recurRate
			nYear=self.date.year
			while nMonth>12:
				nMonth-=12
				nYear+=1
			#what if it's the 31st, or february?
			nDate=datetime.date(nYear,nMonth,self.date.day)
			newSeries=CashFlow(self.account_id,self.title,self.value,nDate,self.recurType,self.recurRate,self.recurEnd,self.estimate)
		else:
			#else it's not recurring and we can delete the whole fucking thing
			newSeries=False
		
		#create a new single cashflow with newDate and newAmount
		temp=self.createSeries().pop(0)
		#update the sent in values
		if not payDate: payDate=temp.date
		if not payAmount: payAmount=temp.value
		
		newCashFlow=CashFlow(temp.account_id,temp.title,payAmount,payDate,False,estimate=False)
		return (newCashFlow,newSeries)
		
	def __repr__(self):
		disp=""
		for thing in self:
			disp=disp+thing+": "+str(getattr(self,thing))+"\n"
		return disp#"%s %s %s"%(self.title,self.value,self.date)

	def __iter__(self):
		#iterate the members of cashflow
		return iter([attr[0] for attr in inspect.getmembers(self,not inspect.ismethod) if type(attr[1])!=types.MethodType and not attr[0].startswith("_")])

class Account(db.Model):
	'''primary account class.  the account is setup with a title, a starting value, a starting date and a low value (used to execute warnings)
	additionally cashflows can be linked to the account (separate table) and will be accessed by the account to display output values
	functions:
	getExpenses-
		takes in a end date, and start date.  returns an array of the expenses (cashflows) impacting teh account between the two dates
	getExpenseValues
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
		
	'''account class'''
	def __init__(self,title,entVal,entDate=datetime.datetime.today(),lowVal=0):
		self.title=title
		self.entVal=entVal
		self.entDate=entDate
		self.lowVal=lowVal
	
	def getExpenses(self,endDate=datetime.datetime.today(),startDate=False):
		'''returns a list continaing all of the epenses that will occur over a given period'''
		if not startDate: startDate=self.entDate	#if a start date is not given, assume it's the account entered date
		return [expense for cf in self.cashFlows for expense in cf.createSeries() if expense.date<=endDate and expense.date>=startDate]
	
	def getExpenseValues(self,endDate=datetime.datetime.today(),startDate=False):
		'''given an accounts, start date and an end date, returns the total expenditure
		s for the account between the two dates'''
		if not startDate: startDate=self.entDate
		expValue=0
		for expense in self.getExpenses(endDate,startDate):
			if expense.date<=endDate and expense.date>=startDate: expValue+=expense.value
		return expValue
	
	def getRate(self,type,startDate,endDate):
		'''determines your <type> cashflow rate between <startDate> and <endDate>'''
		if type=="Day":		#daily expenses
			return (self.getExpenseValues(endDate,startDate)/(endDate-startDate).days)
		elif type=="Week":	#weekly expenses
			return (self.getExpenseValues(endDate,startDate)/(endDate-startDate).days)*7
		else:	#monthly expense
			return self.getExpenseValues(endDate,startDate)/((endDate.year-startDate.year)*12+endDate.month-startDate.month)
	
	def getDateValue(self,endDate=datetime.datetime.today()):
		'''returns a value containing the $ value of an account including all expenses up to endDate from entDate'''
		return self.entVal+self.getExpenseValues(endDate)
	
	def getEstimates(self,endDate,startDate=False):
		#'''if startdate is false, account entered date is assumed'''
		'''returns a list of all estimated cashflows between <startDate> and <endDate>'''
		return [expense for expense in self.getExpenses(endDate,startDate) if expense.estimate]
		
	def __repr__(self):
		disp=""
		for thing in self:
			disp=disp+thing+": "+str(getattr(self,thing))+"\n"

		return disp

	def __iter__(self):
		return iter([attr[0] for attr in inspect.getmembers(self,not inspect.ismethod) if type(attr[1])!=types.MethodType and not attr[0].startswith("_") and not len(attr[0])<=1])
		
class AccountTests(unittest.TestCase):
	#x=Account("Test",10,goalVal=100,goalDate=datetime.date(2014,1,28))
	#create tests for engine/db based development

	
	#def createDB(self):

	
	#db.create_all()
	#engine=create_engine('sqlite:///'+path,echo=False)
	#Session=sessionmaker(bind=engine)
	#session=Session()#instance of a session to communicate with the DB
	#Base.metadata.create_all(engine)	#create the DB with tables
	#	return session
	
	def deleteDB(self):
		path="C:\\Users\Charles\Dropbox\Programming\DataBases\\budget.db"
		if os.path.exists(path):
			os.remove(path)
	
	def test001_AddAccount(self):		
		#create an account
		acc=Account("Checking", 100, datetime.datetime(2014,01,01),5)
		#session=self.createDB()
		db.session.add(acc)
		db.session.commit()	#add the entry to the db
		self.assertTrue(True)
		
	def test002_AddCashFlows(self):
		#add a cashflow
		#session=self.createDB()
		acc=db.session.query(Account).filter(Account.title=="Checking").all()[0]
		rent=CashFlow(acc.id,"Rent",-10,datetime.datetime(2014,02,01),"Month",1,datetime.datetime(2015,01,20))
		income=CashFlow(acc.id,"Payroll",2048,datetime.datetime(2014,01,23),"Week",2,datetime.datetime(2015,01,20))
		#expense2=CashFlow(acc.id,"Drug Sales",-100,datetime.date(2014,01,23),estimate=True)#,"Day",1,datetime.date(2014,1,30))
		db.session.add(rent)
		db.session.add(income)
		#db.session.add(expense2)
		db.session.commit()
		#session.close()
		self.assertTrue(True)
		
	def test003_AccountBalance(self):
		#check the account balance of the account
		#session=self.createDB()
		result=Account.query
		acc=result.all()[0]
		print "Value: "+str(acc.getDateValue())
		#session.close()

		self.assertTrue(True)
	
	def test004_CashFlowRate(self):
		#check the cashflow rate between two given dates
		#session=self.createDB()
		result=db.session.query(Account)
		acc=result.all()[0]
		print "Daily: "+str(acc.getRate("Day",datetime.datetime(2014, 1,21),datetime.datetime(2014,2,23)))
		print "Weekly: "+str(acc.getRate("Week",datetime.datetime(2014, 1,21),datetime.datetime(2014,2,23)))
		print "Monthly: "+str(acc.getRate("Month",datetime.datetime(2014, 1,21),datetime.datetime(2014,2,23)))
		#session.close()
		self.assertTrue(True)
	
	def test005_upcomingExpenses(self):
		#return a list of upcoming expenses from today till X
		#session=self.createDB()
		result=db.session.query(Account)
		acc=result.all()[0]
		
		for bill in acc.getExpenses(datetime.datetime(2014,3,24)):
			print "Title: "+bill.title+" Date: "+str(bill.date)+" - Amount: "+str(bill.value)
		
		#session.close()
		self.assertTrue(True)
	
	def test006_AccountDetectManualMiss(self):
		#given an estimated cashflow, an account needs to be able to check if the cashflow has been updated
		#an updated cashflow will have estimate moved to false
		#this should just be updating bits
		acc=db.session.query(Account).all()[0]
		#add the income to be estimated
		print acc.getEstimates(datetime.datetime.today())
		
	def _test007_popTest(self):
		#tests the pop function of cashflow
		
		acc=db.session.query(Account).all()[0]
		print acc.cashFlows[0].popSeries()
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
