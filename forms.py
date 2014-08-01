#forms.py
'''this will store our forms'''
from flask_wtf import Form
from wtforms import TextField, BooleanField, IntegerField, DateField, FormField, SelectField, RadioField
from wtforms.validators import Required, ValidationError, Optional
from budg_tables import Account, CashFlow, Master
import datetime

def unique_title(table):
	#check to verify the title is unique
	def _check(form,field):
		if len(table.query.filter_by(title=field.data.lower()).all())>0:
			raise ValidationError('Title already exists')
			
	return _check

def unique_title_edit(table):
	#check to verify the title is actually changed
	def _sameCheck(form,field):
		if field.data.lower()!=field.default.lower():
			if len(table.query.filter_by(title=field.data.lower()).all())>0:
				raise ValidationError('Title already exists')
	return _sameCheck
	
def before_date_check(form,field):
	#checks to make sure the endDate is after the start date
	if form.sDate.data>form.eDate.data:
		raise(ValidationError('Start Date (%s) occurs after the end date (%s)'%(form.sDate.data,form.eDate.data)))
	elif form.sDate.data==form.eDate.data:
		raise(ValidationError('Start Date = end date (%s). should be a single expense'%(form.sDate.data)))

def titleLengthCheck(min=0,max=0):
	#checks to verify the title is the appropriate length
	message="Must be between %d and %d characters long."%(min,max)
	
	def _lenCheck(form,field):
		t=form.data and len(form.data) or 0
		if t<min or max!=-1 and t>max:
			raise ValidationError(message)
	
	return _lenCheck

def notDuplicate(form, field):
	'''
	verifies that a transfer can't be to and from the same account
	'''
	if form.t_account.data==form.f_account.data:
		raise (ValidationError('FROM and TO accounts cannot be the same'))
		
def withinSelectedAccount(table):
	'''
	verifies the selected cashflow is contained within the selected account
	'''
	print '0'
	def _accountCheck(form,field):
		print '1'
		if (form.cfOrBudg.data=='cf'and table==CashFlow) or (form.cfOrBudg.data=='budg' and table==Master):
			print '2'
			if (table.query.filter_by(id=field.data).first().account_id)!=(form.account.data):
				print '3'
				raise (ValidationError('Not in Account %s'%(Account.query.filter_by(id=form.account.data).first().title)))
	return _accountCheck
				
class transferForm(Form):
	#a form for adding accounts
	title=TextField('title',validators=[Required()])
	value=IntegerField('value',validators=[Required()])
	date=DateField('date',validators=[Required()])
	f_account=SelectField('account',coerce=int)
	t_account=SelectField('account',coerce=int, validators=[notDuplicate])
	
class addAccountForm(Form):
	#a form for adding accounts
	title=TextField('title',validators=[Required(),unique_title(Account)])
	entVal=IntegerField('entVal',validators=[Required()])
	entDate=DateField('entDate',validators=[Required()])
	entLow=IntegerField('entLow',validators=[Optional()])
	
class addExpenseForm(Form):
	'''adds an expense form'''
	account=SelectField('account',coerce=int)
	title=TextField('title',validators=[Required(),titleLengthCheck(min=3,max=15)])
	date=DateField('date',validators=[Required()])
	value=IntegerField('val',validators=[Required()])
	cfOrBudg=RadioField('cfOrBudg', choices=[('none','None'),('cf','CashFlow'),('budg','Budget')])
	cashflow=SelectField('cashflow',coerce=int,validators=[withinSelectedAccount(CashFlow)])
	budget=SelectField('budget',coerce=int,validators=[withinSelectedAccount(Master)])
	
class addCashFlowForm(Form):
	account=SelectField('account',coerce=int)
	title=TextField('title',validators=[Required()])
	entVal=IntegerField('entVal',validators=[Required()])
	sDate=DateField('sDate',validators=[Required()])
	eDate=DateField('eDate',validators=[Required(),before_date_check])
	rType=SelectField('rType',choices=[('Day','Daily'),('Week','Weekly'),('Month','Monthly')],coerce=str)
	rRate=IntegerField('rRate',validators=[Required()])
	
class expFlowForm(Form):
	#a form used to modify the expenses shown in a cashflow breakdown
	date=DateField('date',validators=[Required()])
	value=IntegerField('val',validators=[Required()])
	
class addBudget(Form):
	account=SelectField('account',coerce=int)
	title=TextField('title',validators=[Required()])
	entVal=IntegerField('entVal',validators=[Required()])
	sDate=DateField('sDate',validators=[Required()])
	eDate=DateField('eDate',validators=[Required(),before_date_check])
	rType=SelectField('rType',choices=[('Day','Daily'),('Week','Weekly'),('Month','Monthly')],coerce=str)
	rRate=IntegerField('rRate',validators=[Required()])

