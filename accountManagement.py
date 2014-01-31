'''Account management module'''
#this will be responsible for all functions performed on accounts
import datetime

def getExpenses(account,startDate=False,endDate=datetime.date.today()):
	
	if not startDate: startDate=account.entDate
	expValue=0
	for cf in account.cashFlows:	#for each cashflow verify it is between the dates, add and append it
		for expense in cf.createSeries():
			if expense.date<=endDate and expense.date>=startDate: expValue+=expense.value
	
	return (account.title,expValue)

def getAllExpenses(account):
	'''returns all expenses listed to an account as a single array'''
	return [expense for cf in account.cf
	
def getDateValue(accounts,endDate=datetime.date.today()):
	'''given an array of accounts, returns an array containing the
	tuple values of account title and value on <date> day'''
	expenseArray=[getExpenses(account,False,endDate) for account in accounts]	#start date is assumed false so the entered value can be used
	valueArray=[(expenseArray[i][0],expenseArray[i][1]+accounts[i].entVal) for i in range(0,len(accounts))]
	return valueArray
			
def getRate(accounts,type,startDate,endDate):
	'''returns the cashflow <type> cashflow rate of each account between <startDate> and <endDate>, form of (title,rate)'''
	rates=[]
	expenseArray=[getExpenses(account,startDate,endDate) for account in accounts]	#get the expenses betwen two dates
	for expenseTotal in expenseArray:
		if type=="Day":		#daily expenses
			rates.append((expenseTotal[0],(expenseTotal[1]/(endDate-startDate).days)))
		elif type=="Week":	#weekly expenses
			rates.append((expenseTotal[0],(expenseTotal[1]/(endDate-startDate).days)*7))
		else:	#monthly expense
			rates.append((expenseTotal[0],expenseTotal[1]/((endDate.year-startDate.year)*12+endDate.month-startDate.month)))
	return rates
