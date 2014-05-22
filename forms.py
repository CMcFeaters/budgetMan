#forms.py
'''this will store our forms'''
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, IntegerField, DateField, FormField, SelectField
from wtforms.validators import Required, ValidationError
from appHolder import db
from budg_tables import Account, CashFlow
import datetime

def unique_title(table):
	#check to verify the title is unique
	def _check(form,field):
		if len(table.query.filter_by(title=field.data.lower()).all())>0:
			raise ValidationError('Title already exists')
	return _check
	
def unique_cf_title(table):
	#checks a cashflow to the title is unique for the account it affects
	#this is a factory that creates "_check" functions.  when it's called in the class
	#as unique_cf_title(THETABLE) it returns _check(form,field), with table set to THETABLE
	#teh reason I couldn't send the account data was I was trying to do it during initiation
	#instead of dynamically during submission.  That's why changing it to "form.acc..." 
	#worked
	def _check(form,field):
		acc=[item for item in form.account.choices if item[0]==form.account.data][0]
		if len(table.query.filter_by(account_id=acc[0],title=field.data.lower()).all())>0:
			raise ValidationError('Title "%s" already exists for account "%s"'%(field.data.lower(),acc[1]))
	return _check

def before_date_check(form,field):
	#checks to make sure the endDate is after the start date
	if form.sDate.data>form.eDate.data:
		raise(ValidationError('Start Date (%s) occurs after the end date (%s)'%(form.sDate.data,form.eDate.data)))
	elif form.sDate.data==form.eDate.data:
		raise(ValidationError('Start Date = end date (%s). should be a single expense'%(form.sDate.data)))
	
	
class addAccountForm(Form):
	#a form for adding accounts
	title=TextField('title',validators=[Required(),unique_title(Account)])
	entVal=IntegerField('entVal',validators=[Required()])
	entDate=DateField('entDate',validators=[Required()])
	entLow=IntegerField('entLow', validators=[Required()])
	
class addCashFlowForm(Form):
	account=SelectField('account',coerce=int)
	title=TextField('title',validators=[Required(),unique_cf_title(CashFlow)])
	entVal=IntegerField('entVal',validators=[Required()])
	sDate=DateField('sDate',validators=[Required()])
	eDate=DateField('eDate',validators=[Required(),before_date_check])
	rType=SelectField('rType',choices=[('Day','Daily'),('Week','Weekly'),('Month','Monthly')],coerce=str)
	rRate=IntegerField('rRate',validators=[Required()])
	est=BooleanField('est')
	