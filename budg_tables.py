'''
budg_tables
this contains all of the setup data for the tables
'''
from sqlalchemy import Column, Integer, String, Date, Boolean, Float
#from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
Base=declarative_base()

class Expense(Base):
	'''expenses class'''
	
	__tablename__='expenses'
	
	id=Column(Integer,primary_key=True)
	name=Column(String)			#name of the payment
	recurring=Column(Boolean)	#is this a recurring payment or 1 time
	due=Column(Date)			#the due date of the (first) payment
	cycle=Column(String)		#change to somethign else.  This is used to pickup this payment every occurence
	fixed=Column(Boolean)		#is the amount being paid fixed
	amount=Column(Float)			#this is the amount paid
	estimated=Column(Float)		#this is the amount estimated (for varible payments)
	credit=Column(Boolean)		#true added to card, false subtracted from bank account
	
	def __init__(self,name,recurring,due,cycle,fixed,amount,estimated,credit):
		'''creates the expense'''
		self.name=name
		self.recurring=recurring
		
		if self.recurring:	#recurring schedule
			self.cycle=cycle
		else:
			self.cycle="N/A"
		
		self.due=due
		self.fixed=fixed
		self.amount=amount
		if self.fixed:
			self.estimated=amount
		else:
			self.estimated=estimated

		self.credit=credit
		
	def __repr__(self):
		return "Name: %s \n Due: %s \n Recurring: %s \n Cycle: %s \n Fixed: %s \n Amount: %s \
		\n Estimated: %s \n Credit: %s"%(self.name, self.due,self.recurring,self.cycle,self.fixed, 
		self.amount, self.estimated, self.credit)
		