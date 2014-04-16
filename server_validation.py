'''server_validation.py
this file contains all server side validation methods
	titleValidate
		-takes in a title and returns true if title is acceptable and false if not
	dateValidate
		-takes in a year, month and day as strings, returns true if acceptable, false if not
	amountValidate
		-takes in a string and validates it contains only digits, "-" returns True or false
	'''
from appHolder import db
from budg_tables import Account, CashFlow
#from budg_functions import delAccount
import datetime, unittest
import sys, string, os, random, re

def titleValidate(nTitle):
	'''this checks the title against are required parameters'''
	#1 3-20 characters
	#2 not a duplicate
	if (len(nTitle)>=3 and len(nTitle)<=20) and \
	len(Account.query.filter_by(title=nTitle.lower()).all())==0 and \
	len(re.findall("[a-zA-z0-9]",nTitle))==len(nTitle):
		return True
	else: return False 
	
def dateValidate(year,month,day):
	'''checks the year, month and day submitted to the following standards'''
	#1 month 2 digits (01-12)
	#2 day 2 digits (01-31)
	#3 year 4 digits (1900-2100)
	#4 date is valid (i.e. 2/31/14 = false)
	if re.search("0[1-9]|1[0-2]",month) and \
	re.search("0[1-9]|1[0-9]|2[0-9]|3[0-1]",day) and \
	re.search("19[0-9][0-9]|20[0-9][0-9]",year):
		try:
			datetime.datetime(int(year),int(month),int(day))
			return True
		except ValueError:
			#the date does not exist
			return False
	else: return False
			
def typeValidate(nType=""):
	'''validates type is "Year" "Month" "Day"'''
	#personal note: Does this need to be a separate function, it's like 1 line
	#i'm leaving it as a separate funcitont o keep my modules clean and dedicated
	return (nType=="Year" or nType=="Month" or nType=="Day")

def rateValidate(nRate):
	'''validates the rate is an integer'''
	return (len(re.findall("[0-9]",str(nRate)))==len(str(nRate))) and (type(int(nRate))==type(0))
			
def amountValidate(amt):
	'''takes in a cost amount and returns true if it passes the following standards, else returns false
	#1 contains only numbers -'s
	#2contains only 1 "-"
	'''
	nDig=len(re.findall("[0-9]",amt))
	nSin=len(re.findall("-",amt))
	if len(amt)==0:
		return False
	else:
		if (nDig+nSin)==len(amt): #only numbers and -'s
			if nSin>1 or (nSin==1 and amt[0]!="-"):	#if there is more than 1 - or it's not located at the front
				return False
			else: return True
		else:
			return False
	
class validationTests(unittest.TestCase):
	'''these tests will be to test the functionallity of the functions used in the budget program
	'''
	def deleteDB(self):
		path="C:\\Users\Charles\Dropbox\Programming\DataBases\\budget.db"
		if os.path.exists(path):
			os.remove(path)

	def test001_VerifyDuplicate(self):		
		#try to create a duplicate account
		acc=Account.query.all()[0]
		self.assertFalse(titleValidate(acc.title))
	
	def test002_tooLong(self):
		#try to create an accoun that's too long
		self.assertFalse(titleValidate("123123123123123123123123123123"))
	
	def test003_tooShort(self):
		#try to create an account that's too short
		self.assertFalse(titleValidate("12"))
	
	def test004_invalidChars(self):
		#try to create a title that's only letters and numbers
		self.assertFalse(titleValidate("asdf$%$%sdf"))
	
	def test005_justRight(self):
		#create an account that meets all of the requirements
		self.assertTrue("FuckYes")
		
	def test006_badMonth(self):
		#checks a month to verify it matches numeric format
		if not dateValidate("2014","abc","02") and \
		not dateValidate("2014","3","02") and \
		not dateValidate("2014","13","02") and \
		not dateValidate("2014","00","02"):
			self.assertTrue(True)
		else: self.assertTrue(False)
	
	def test007_badDay(self):
		#send an improper day
		if not dateValidate("2014","11","0") and \
		not dateValidate("2014","11","99") and \
		not dateValidate("2014","11","00") and \
		not dateValidate("2014","11","asd"):
			self.assertTrue(True)
		else: self.assertTrue(False)
	
	def test008_badYear(self):
		#send improper year
		if not dateValidate("1","11","02") and \
		not dateValidate("14","11","02") and \
		not dateValidate("2114","11","02") and \
		not dateValidate("114","11","02") and \
		not dateValidate("asbd","11","02") and \
		not dateValidate("1899","11","02"):
			self.assertTrue(True)
		else: self.assertTrue(False)
		
	def test009_badDate(self):
		#send a good date
		self.assertFalse(dateValidate("2014","02","31"))
		
	def test010_goodDate(self):
		#send a good date
		self.assertTrue(dateValidate("2014","02","28"))
		
	def test011_notNumber(self):
		#send a value that contains anything that isn't "-,." or a number
		if not amountValidate("asdf") and \
		not amountValidate("12345^") and \
		not amountValidate("123.,") and \
		not amountValidate("a123") and \
		not amountValidate("1a123") and \
		not amountValidate(";'';'asdfasf12") and \
		not amountValidate("1212..123"):
			self.assertTrue(True)
		else: self.assertFalse(True)
	
	def test012_aNumber(self):
		#send a number
		if amountValidate("-100") and \
		amountValidate("-0") and \
		amountValidate("0") and \
		amountValidate("1231230") and \
		amountValidate("-100123123"):
			self.assertTrue(True)
		else:
			self.assertTrue(False)
	
	def test013_badType(self):
		self.assertTrue(not typeValidate("Days") and not typeValidate() and not typeValidate("asdf"))
	
	def test014_goodType(self):
		self.assertTrue(typeValidate("Day") and typeValidate("Year") and typeValidate("Month"))
	
	def test015_badRate(self):
		self.assertTrue(not rateValidate("123123.4") and not rateValidate("asdf") and not rateValidate("-122"))
	
	def test016_goodRate(self):
		self.assertTrue(rateValidate("123123") and rateValidate(123))
	
	def test100_cleanUp(self):
		#delete the accountt that was just created
		pass
	
	
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
