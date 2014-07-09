'''Budget Page'''
#webpage
#uses flask to create working page

from budg_functions import delAccount, delCashFlow
from budg_tables import Account, CashFlow, Expense, Actual, Transfer, create_a_thing
import forms 
from appHolder import db, app
import datetime
import re
from flask import Flask, render_template,redirect,url_for, flash, request, session


@app.route('/')
def welcome():
	#standard welcome, you're logged in or you're not
	results=Account.query
	return render_template("budg_welcome.html", results=results,tDate=datetime.date.today())
	
@app.route('/deleteAccount/<title>')
def deleteAccount(title):
	#standard welcome, you're logged in or you're not
	db.session.delete(Account.query.filter_by(title=nTitle).first())
	db.session.commit()
	return redirect(url_for('welcome'))

@app.route('/deleteCashFlow/<id><accID>')
def deleteCashFlow(id,accID):
	#deletes the selected cashflow
	db.session.delete(CashFlow.query.filter_by(id=nID).first())
	db.session.commit()
	#print Account.query.filter_by(id=accID).first()
	
	
	return redirect(url_for('displayAccount',acData=Account.query.filter_by(id=accID).all()[0].id))
	
@app.route('/edAccount/<id>',methods=['GET','POST'])
def edAccount(id):
	'''this should use add account template with filled in values'''
	accData=Account.query.filter_by(id=id).first()
	#make form and assign default values
	
	form=forms.editAccount(title=accData.title.lower(),entVal=accData.entVal,entDate=accData.entDate,
	entLow=accData.lowVal)
	
	form.title.default=accData.title.lower()
	
	if form.validate_on_submit():

		accData.title=form.title.data
		accData.entVal=form.entVal.data
		accData.entDate=form.entDate.data
		accData.lowVal=form.entLow.data
		
		db.session.add(accData)
		db.session.commit()

		flash("Account Edit Success!")

		return redirect(url_for('welcome'))
	
	return render_template('budg_editAccount.html',accData=accData, form=form)


@app.route('/adAccount',methods=['GET','POST'])
def adAccount():
	'''adds an account'''
	form=forms.addAccountForm()

	#if request.method=='POST': 
		#the form data has been posted
	if form.validate_on_submit():
		create_a_thing(Account,[form.title.data.lower(),form.entVal.data,form.entDate.data,form.entLow.data])
		return redirect(url_for('welcome'))
	return render_template('budg_addAccount.html',form=form)

@app.route('/adExpense',methods=['GET','POST'])
def adExpense():
	'''add a single expense to an account'''
	form=forms.addExpenseForm()	#set up theform
	form.account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	if form.validate_on_submit(): 
		#if the form data is validated
		create_a_thing(Expense,[form.account.data,form.title.data,form.entVal.data,form.eDate.data])
		return redirect(url_for('welcome'))
	
	#send in the accounts to populate the dropdown menu
	
	return render_template('budg_addExpense.html',form=form)

	
@app.route('/adCashFlow',methods=['GET','POST'])
def adCashFlow():
	'''add a cashflow to an account'''
	form=forms.addCashFlowForm()
	form.account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	if form.validate_on_submit(): 
		create_a_thing(CashFlow,[form.account.data,form.title.data,form.entVal.data,form.sDate.data,\
			form.rType.data,form.rRate.data,form.eDate.data,form.est.data])
			
		return redirect(url_for('welcome'))
	
	return render_template('budg_addCashFlow.html',form=form)

@app.route('/displayAccount/<acData>', methods=['GET','POST'])
@app.route('/displayAccount', methods=['GET','POST'])
def displayAccount(acData):
	#this will display an account and show the cashflows specific to it
	#eventually this will display future, past, etc options

	ddList=Account.query.all()
	if acData=='None':
		#sent an empty list
		acData=ddList[0]
	else:
		acData=Account.query.filter_by(id=acData).first()
	
	if request.method=='POST':
		#something was posted
		acData=Account.query.filter_by(id=request.form['account']).first()		
		cfData=acData.cashFlows
		expData=acData.expenses
		tfData=acData.getTransfers()	#[(tfIn,tfOut)]
	else:
		cfData=acData.cashFlows
		expData=acData.expenses
		tfData=acData.getTransfers()	#[(tfIn,tfOut)]
		
	#otherwise we return with the option to select the accoutn data
	return render_template('budg_account_data.html',acData=acData,\
		ddList=ddList,cfData=cfData,expData=expData,\
		trfData=tfData,tDate=datetime.date.today())


#simple python scripts made part of jinja template
@app.template_test('less10')
def less10(value):
	'''takes in a value and dertmines if it is less than 10'''
	return (value<10)
app.jinja_env.tests['less10']=less10

#simple python scripts made part of jinja template
@app.template_filter('url_ext')
def url_ext(*value):
	'''takes in a value and dertmines if it is less than 10'''
	print value
	print type(value)
	for thing in value:
		for stuff in thing:
			print stuff
	return url_for(value[0][0],title=value[0][1])
app.jinja_env.filters['url_ext']=url_ext

if __name__=='__main__':
	db.create_all()
	app.run()