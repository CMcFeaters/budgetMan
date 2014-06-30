'''Budget Page'''
#webpage
#uses flask to create working page

from budg_functions import delAccount, addAccount, addCashFlow, delCashFlow
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
	delAccount(title)
	return redirect(url_for('welcome'))

@app.route('/deleteCashFlow/<id><accID>')
def deleteCashFlow(id,accID):
	#deletes the selected cashflow
	delCashFlow(id)
	#print Account.query.filter_by(id=accID).first()
	
	
	return redirect(url_for('displayAccount',acData=Account.query.filter_by(id=accID).all()[0].id))
	
@app.route('/edAccount/<id>',methods=['GET','POST'])
def edAccount(id):
	'''this should use add account template with filled in values'''
	accData=Account.query.filter_by(id=id).first()

	if request.method=='POST': 
		#check to see what was changed
		if request.form['title']==accData.title: nTitle=""
		else: nTitle=request.form['title']
		#entered value
		
		if request.form['entVal']==accData.entVal: nVal=""
		else: nVal=request.form['entVal']
		
		#repeat compariosn 
		if request.form['entLow']==accData.lowVal: nLow=""
		else: nLow=request.form['entLow']
		
		#for the date, compile it first, then compare
		fDate=dateCompile(request.form['entY'], request.form['entM'],request.form['entD'])
		if fDate==False or fDate==accData.entDate: nDate=""
		else: nDate=fDate
		
		#run the edit, see what comes up false
		edRes=editAccount(accData.id,nTitle,nVal,nDate,nLow)
		
		if edRes[0]==False:
			flash(edRes[1])
		else:
			return redirect(url_for('welcome'))
	return render_template('budg_editAccount.html',accData=accData)

@app.route('/adAccount',methods=['GET','POST'])
def adAccount():
	'''adds an account'''
	form=forms.addAccountForm()
	
	#if request.method=='POST': 
		#the form data has been posted
	if form.validate_on_submit():
		addAccount(form.title.data.lower(),form.entVal.data,form.entDate.data,form.entLow.data)
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
		create_a_thing(####RIGHT HERE####
		
		
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
		cfData=CashFlow.query.filter_by(account_id=request.form['account']).all()
	else:
		cfData=CashFlow.query.filter_by(account_id=acData.id).all()
		
	#otherwise we return with the option to select the accoutn data
	return render_template('budg_account_data.html',acData=acData,ddList=ddList,cfData=cfData,tDate=datetime.date.today())


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