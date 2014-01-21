'''
budg_tables
this contains all of the setup data for the tables
'''
import unittest, datetime, inspect, types

from sqlalchemy import Column, Integer, String, Date, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine,and_,or_
from sqlalchemy.orm import sessionmaker
import sys, string, os
Base=declarative_base()

#need to create a date iterator

class dateRange():
	'''an array of all days between two dates'''
	def __init__(self,startDate=datetime.date.today(),endDate=datetime.date(datetime.date.today().year+1,datetime.date.today().month,datetime.date.today().day)):
		self.startDate=startDate
		self.endDate=endDate
	
	def __iter__(self):
		#returns the iterator
		return iter([(self.startDate+datetime.timedelta(day)) for day in range(0,(self.endDate-self.startDate).days)])

		
class CashFlow(Base):
	'''cashFlow class'''
	__tablename__="cashflows"
	
	id=Column(Integer,primary_key=True)
	account_id=Column(Integer,ForeignKey('accounts.id'))
	title=Column(String)
	value=Column(Integer)
	date=Column(Date)
	recurType=Column(String)
	recurRate=Column(Integer)
	recurEnd=Column(Date)
		
	def __init__(self,account_id,title,value,date=datetime.date.today(),recurType="False",recurRate=0, 
	recurEnd=datetime.date.today()):
		'''cash flow values'''
		self.account_id=account_id	#the account the cashflow affects
		self.title=title
		self.value=value
		self.date=date
		self.recurType=recurType	#can be false (none recurring), days, weeks, months
		self.recurRate=recurRate	#number or recurtypes between recurrence
		self.recurEnd=recurEnd		#date recurrence ends

	def createSeries(self):
		#converts a recurring payment into a series of paymnets
		#create entire array of cashflows
		#return an array of applicable entries
		
		#initial entry
		cfRange=dateRange(self.date,self.recurEnd)	#the date range for the cashflow
		#print self

		#generate remaining recurring entries in a similar fasion
		if self.recurType=="Day" and self.recurRate>0:
			series=[CashFlow(self.account_id,self.title,self.value,pDate,False) for pDate in cfRange if ((pDate-self.date).days)%self.recurRate==0]
		elif self.recurType=="Week":
			series=[CashFlow(self.account_id,self.title,self.value,pDate,False) for pDate in cfRange if ((pDate-self.date).days)%(self.recurRate*7)==0]
		elif self.recurType=="Month":
			series=[CashFlow(self.account_id,self.title,self.value,pDate,False) for pDate in cfRange if ((pDate.month-self.date.month))%(self.recurRate)==0 and pDate.day==self.date.day]
		else:
			series=[CashFlow(self.account_id,self.title,self.value,self.date,False)]
		return series
		
	def __repr__(self):
		disp=""
		for thing in self:
			disp=disp+thing+": "+str(getattr(self,thing))+"\n"
		return disp#"%s %s %s"%(self.title,self.value,self.date)

	def __iter__(self):
		#iterate the members of cashflow
		return iter([attr[0] for attr in inspect.getmembers(self,not inspect.ismethod) if type(attr[1])!=types.MethodType and not attr[0].startswith("_")])

class Account(Base):
	__tablename__="accounts"
	#values
	id=Column(Integer,primary_key=True)
	title=Column(String)
	entVal=Column(Integer)
	entDate=Column(Date)
	lowVal=Column(Integer)
	cashFlows=relationship("CashFlow",backref="accounts",cascade="all,delete-orphan")	#link to cashflow table
		
	'''account class'''
	def __init__(self,title,entVal,entDate=datetime.date.today(),lowVal=0):
		self.title=title
		self.entVal=entVal
		self.entDate=entDate
		self.lowVal=lowVal
	
	def dateValue(self,date=datetime.date.today()):
		'''calculate the current value based on cashflows up to a certain date'''
		#need to add the ability to evaluate series
		cVal=self.entVal
	#	cfArray=[]
		for cf in self.cashFlows:
			for expense in cf.createSeries():
				if expense.date<=date: cVal=cVal+expense.value
		return cVal
	
	def getRate(self,type,startDate,endDate):
		'''returns the cashflow rate on a <type> basis between the start and end date'''
		cVal=0
		for cf in self.cashFlows:
			for expense in cf.createSeries():
				if expense.date<=endDate and expense.date>=startDate: cVal=cVal+expense.value
				
		if type=="Day":
			return cVal/(endDate-startDate).days
		elif type=="Week":
			return (cVal/(endDate-startDate).days)*7
		else:
			return cVal/((endDate.year-startDate.year)*12+endDate.month-startDate.month)
	
	def valueDate(self,value,startDate=0,endDate=0):
		if startDate==0:startDate=self.entDate
		if endDate==0:endDate=datetime.date(startDate.year+1,startDate.month,startDate.day)
		'''return the date a given value will be reached, given the cashflow rate over a year starting from teh entry date'''
		if self.dateValue(startDate)<value and self.getRate("Day",startDate,endDate)>0:#positive rate
			return startDate+datetime.timedelta((value-self.dateValue(startDate))/self.getRate("Day",startDate,endDate))
		elif self.dateValue(startDate)>value and self.getRate("Day",startDate,endDate)<0:#negative rate
			return startDate+datetime.timedelta((value-self.dateValue(startDate))/self.getRate("Day",startDate,endDate))
		else:	#else we will never cross this threshold
			return False


	def upcomingExpenses(self,endDate,startDate=datetime.date.today()):
		'''returns a list of upcoming cashflows from today up till <date>'''
		return [expense for cf in self.cashFlows for expense in cf.createSeries() if expense.date<=endDate and expense.date>=startDate]
		
	def lowWarn(self,date=datetime.date.today()):
		'''summarizes all cashflows upto a given date and determines if they meet the low account warning criteria'''
		return (self.dateVal(date)<=self.lowVal)

	def __repr__(self):
		disp=""
		for thing in self:
			disp=disp+thing+": "+str(getattr(self,thing))+"\n"

		return disp

	def __iter__(self):
		return iter([attr[0] for attr in inspect.getmembers(self,not inspect.ismethod) if type(attr[1])!=types.MethodType and not attr[0].startswith("_")])

class AccountTests(unittest.TestCase):
	#x=Account("Test",10,goalVal=100,goalDate=datetime.date(2014,1,28))
	#create tests for engine/db based development
	
	
	def createDB(self):
		path="C:\\Users\Charles\Dropbox\Programming\DataBases\\budget.db"
		engine=create_engine('sqlite:///'+path,echo=False)
		Session=sessionmaker(bind=engine)
		session=Session()#instance of a session to communicate with the DB
		
		Base.metadata.create_all(engine)	#create the DB with tables
		return session
	
	def deleteDB(self):
		path="C:\\Users\Charles\Dropbox\Programming\DataBases\\budget.db"
		if os.path.exists(path):
			os.remove(path)
		
	
	def test001_AddAccount(self):		
		#create an account
		acc=Account("Checking", 100, datetime.date.today(),5)
		session=self.createDB()
		session.add(acc)
		session.commit()	#add the entry to the db
		session.close()
		self.assertTrue(True)
		
	def test002_AddCashFlows(self):
		#add a cashflow
		session=self.createDB()
		acc=session.query(Account).filter(Account.title=="Checking").all()[0]
		rent=CashFlow(acc.id,"Rent",-1550,datetime.date(2014,02,01),"Month",1,datetime.date(2015,01,20))
		income=CashFlow(acc.id,"Payroll",2048,datetime.date(2014,01,23),"Week",2,datetime.date(2015,01,20))
		session.add(rent)
		session.add(income)
		session.commit()
		session.close()
		self.assertTrue(True)
		
	def test003_AccountBalance(self):
		#check the account balance of the account
		session=self.createDB()
		result=session.query(Account)
		acc=result.all()[0]
		print "Value: "+str(acc.dateValue(datetime.date(2014,02,22)))
		session.close()

		self.assertTrue(True)
	
	def test004_CashFlowRate(self):
		#check the cashflow rate between two given dates
		session=self.createDB()
		result=session.query(Account)
		acc=result.all()[0]
		print "Daily: "+str(acc.getRate("Day",datetime.date(2014, 1,21),datetime.date(2014,2,23)))
		print "Weekly: "+str(acc.getRate("Week",datetime.date(2014, 1,21),datetime.date(2014,2,23)))
		print "Monthly: "+str(acc.getRate("Month",datetime.date(2014, 1,21),datetime.date(2014,2,23)))
		session.close()
		self.assertTrue(True)
	
	def test005_upcomingExpenses(self):
		#return a list of upcoming expenses from today till X
		session=self.createDB()
		result=session.query(Account)
		acc=result.all()[0]
		
		for bill in acc.upcomingExpenses(datetime.date(2014,3,24)):
			print "Title: "+bill.title+" Date: "+str(bill.date)+" - Amount: "+str(bill.value)
		
		session.close()
		self.assertTrue(True)
	
	def test006_goalActual(self):
		#return the date the goal will be made, return false if won't hit goal
		session=self.createDB()
		acc=session.query(Account).all()[0]
		print acc.valueDate(10000)
		session.close()
		self.deleteDB()
		
	def printAccounts(self):
		session=self.createDB()
		results=session.query(Account)
		
		for thing in results:
			print "_____******______"
			print thing
			print "_____******______"
		
		session.close()
		
	
	'''def testFoo(self):
		self.failUnless(True)
		
	def testLowAlert(self):
		x=Account("Test",10,datetime.date(2014,01,10))
		e=cashFlow("A fuckload of whores",-10,datetime.date(2014,1,11))
		self.assertTrue(x.lowWarn([e]),x.dateVal([e]))
	
	def testLowAlertPass(self):
		x=Account("Test",100,lowVal=4)
		e=cashFlow("A modest amount of whores",-5,datetime.date.today(),"Week",3,datetime.date(datetime.date.today().year,datetime.date.today().month+10,datetime.date.today().day))
		print str(len(e.createSeries()))
		self.assertFalse(x.lowWarn(e.createSeries(),datetime.date(datetime.date.today().year,datetime.date.today().month+10,datetime.date.today().day)),x.dateVal(e.createSeries(),datetime.date(datetime.date.today().year,datetime.date.today().month+10,datetime.date.today().day)))
		
	
	def testGoalMeet(self):
		x=Account("Test",10,goalVal=100,goalDate=datetime.date(2014,1,28))
		e=cashFlow("A modest amount of whores",100,datetime.date.today())
		self.assertFalse(x.meetGoal([e]),x)
	
	def testAcctPrint(self):
		x=Account("Test",10,goalVal=100,goalDate=datetime.date(2014,1,28))
		print x
		self.assertTrue(True)
	
	def testPrintCF(self):
		x=Account("Test",10,goalVal=100,goalDate=datetime.date(2014,1,28))
		e=cashFlow("Down payment on an IRON",10,datetime.date.today(),False)
		print e
		self.assertTrue(True)
	
	def testSingleCashFlow(self):
		e=cashFlow("Down payment on an IRON",10,datetime.date.today(),False)
		e.createSeries()
		self.assertTrue(True)
	
	def testDailyCashflow(self):
		e=cashFlow("Down payment on 2 IRONs",10,datetime.date.today(),"Day",30,datetime.date(datetime.date.today().year+1,datetime.date.today().month,datetime.date.today().day))
		#print e
		print "#Daily payments: "+str(len(e.createSeries()))
		self.assertTrue(True)
	def testWeekCashflow(self):
		e=cashFlow("Down payment on 2 IRONs",10,datetime.date.today(),"Week",10,datetime.date(datetime.date.today().year+1,datetime.date.today().month,datetime.date.today().day))
		#print e
		print "#weekly payments: "+str(len(e.createSeries()))
		self.assertTrue(True)
	
	def testMonthCashflow(self):
		e=cashFlow("Down payment on 2 IRONs",10,datetime.date.today(),"Month",2,datetime.date(datetime.date.today().year+1,datetime.date.today().month,datetime.date.today().day))
		#print e
		print "#Monthly payments: "+ str(len(e.createSeries()))
		self.assertTrue(True)
	def testCreateSeries(self):

		e=cashFlow("saving for blow",10,recurType="Day",recurRate=3,recurEnd=datetime.date(datetime.date.today().year+1, 
		datetime.date.today().month,datetime.date.today().day))
		
		self.assertTrue(length(e.createSeries)>3)'''

def main():
	unittest.main()
	
if __name__=="__main__":
	main()