'''Budget Page'''
#webpage
#uses flask to create working page

from budg_functions import delAccount, delCashFlow
from budg_tables import Account, CashFlow, Expense, Transfer, create_a_thing
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


	
@app.route('/deleteExpense/<id><accID>')
def deleteExpense(id,accID):
	#deletes the selected cashflow
	db.session.delete(Expense.query.filter_by(id=id).first())
	db.session.commit()
	#print Account.query.filter_by(id=accID).first()

	return redirect(url_for('displayAccount',acData=Account.query.filter_by(id=accID).all()[0].id))

@app.route('/edExpense/<id>',methods=['GET','POST'])
def edExpense(id):
	'''
	only called with a url link
	'''
	expData=Expense.query.filter_by(id=id).first()
	#make form and assign default values
	
	form=forms.addExpenseForm(title=expData.title,value=expData.value,date=expData.date,account=expData.account_id)
	form.account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	
	if form.validate_on_submit():

		expData.title=form.title.data
		expData.value=form.value.data
		expData.entDate=form.date.data
		expData.account_id=form.account.data
		
		db.session.add(expData)
		db.session.commit()

		flash("Expense %s Edit Success!"%expData.title)

		return redirect(url_for('welcome'))
	
	return render_template('budg_Expense.html',expData=expData, form=form,expAdd="edit")

@app.route('/adExpense',methods=['GET','POST'])
def adExpense():
	'''add a single expense to an account'''
	form=forms.addExpenseForm()	#set up theform
	form.account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	if form.validate_on_submit(): 
		#if the form data is validated
		create_a_thing(Expense,[form.account.data,form.title.data,form.value.data,form.date.data])
		return redirect(url_for('welcome'))
	
	#send in the accounts to populate the dropdown menu
	
	return render_template('budg_Expense.html',form=form,edAdd="add")

		
	
@app.route('/edAccount/<id>',methods=['GET','POST'])
def edAccount(id):
	'''this should use add account template with filled in values'''
	accData=Account.query.filter_by(id=id).first()
	#make form and assign default values
	
	form=forms.addAccountForm(title=accData.title.lower(),entVal=accData.entVal,entDate=accData.entDate,
	entLow=accData.lowVal)
	
	form.title.default=accData.title.lower()
	form.title.validators=[forms.Required(),forms.unique_title_edit(Account)]
	
	if form.validate_on_submit():

		accData.title=form.title.data
		accData.entVal=form.entVal.data
		accData.entDate=form.entDate.data
		accData.lowVal=form.entLow.data
		
		db.session.add(accData)
		db.session.commit()

		flash("Account Edit Success!")

		return redirect(url_for('welcome'))
	
	return render_template('budg_Account.html',accData=accData, form=form, edAdd='edit')


@app.route('/adAccount',methods=['GET','POST'])
def adAccount():
	'''adds an account'''
	form=forms.addAccountForm()

	#if request.method=='POST': 
		#the form data has been posted
	if form.validate_on_submit():
		create_a_thing(Account,[form.title.data.lower(),form.entVal.data,form.entDate.data,form.entLow.data])
		return redirect(url_for('welcome'))
	return render_template('budg_Account.html',form=form, edAdd='add')


@app.route('/adTransfer',methods=['GET','POST'])
def adTransfer():
	'''add a transfer to two accounts'''
	
	form=forms.transferForm()
	form.f_account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	form.t_account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	if form.validate_on_submit(): 
		create_a_thing(Transfer,[form.title.data,form.value.data,
			form.f_account.data,form.t_account.data,form.date.data])
			
		return redirect(url_for('welcome'))
	
	return render_template('budg_Transfer.html',form=form,edAdd="add")
	


@app.route('/deleteTransfer/<id><accID>')
def deleteTransfer(id,accID):
	#deletes the selected transfer
	
	db.session.delete(Transfer.query.filter_by(id=id).first())
	db.session.commit()
	
	return redirect(url_for('displayAccount',acData=Account.query.filter_by(id=accID).all()[0].id))
	
@app.route('/edTransfer/<id>',methods=['GET','POST'])
def edTransfer(id):
	'''this should use add account template with filled in values'''
	
	#pick up the transferwe're editing
	tfData=Transfer.query.filter_by(id=id).first()
	
	form=forms.transferForm(title=tfData.title, value=tfData.value, f_account=tfData.f_account.id,
		t_account=tfData.t_account.id, date=tfData.date)
	#assign the drop downs
	form.f_account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	form.t_account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	
	if form.validate_on_submit(): 
		#assign the values
		tfData.title=form.title.data
		tfData.value=form.value.data
		tfData.t_account=Account.query.filter_by(id=form.t_account.data).first()
		tfData.f_account=Account.query.filter_by(id=form.f_account.data).first()
		tfData.date=form.date.data
		db.session.add(tfData)
		db.session.commit()
		flash("Transfer edit complete")
			
		return redirect(url_for('welcome'))
	
	return render_template('budg_Transfer.html',form=form,edAdd="edit", tfData=tfData)


@app.route('/adCashFlow',methods=['GET','POST'])
def adCashFlow():
	'''add a cashflow to an account'''
	form=forms.addCashFlowForm()
	form.account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	if form.validate_on_submit(): 
		create_a_thing(CashFlow,[form.account.data,form.title.data,form.entVal.data,form.sDate.data,\
			form.rType.data,form.rRate.data,form.eDate.data])
		return redirect(url_for('welcome'))
	
	return render_template('budg_CashFlow.html',form=form,edAdd="add")

@app.route('/deleteCashFlow/<id><accID>')
def deleteCashFlow(id,accID):
	#deletes the selected cashflow
	db.session.delete(CashFlow.query.filter_by(id=id).first())
	db.session.commit()
	
	return redirect(url_for('displayAccount',acData=Account.query.filter_by(id=accID).all()[0].id))
	
@app.route('/edCashFlow/<id>',methods=['GET','POST'])
def edCashFlow(id):
	'''
	only called with a url link
	'''
	cfData=CashFlow.query.filter_by(id=id).first()
	#make form and assign default values
	
	form=forms.addCashFlowForm(title=cfData.title,entVal=cfData.value,sDate=cfData.date,
	account=cfData.account_id, rType=cfData.recurType, rRate=cfData.recurRate, 
	eDate=cfData.recurEnd, est=cfData.estimate)
	#add the account choices
	form.account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	
	if form.validate_on_submit():
	#	assign values and submit
		cfData.title=form.title.data
		cfData.value=form.entVal.data
		cfData.date=form.sDate.data
		cfData.account_id=form.account.data
		cfData.recurType=form.rType.data
		cfData.recurRate=form.rRate.data
		cfData.recurEnd=form.eDate.data
		
		db.session.add(cfData)
		db.session.commit()
		
		#create the new expenses
		cfData.createExpenses()
				
		flash("CashFlow %s Edit Success!"%cfData.title)

		return redirect(url_for('welcome'))
	
	return render_template('budg_CashFlow.html',cfData=cfData, form=form,edAdd="edit")


@app.route('/adActual/<cfID>',methods=['POST'])
def adActual(cfID):
	'''
	an internal method to create an actual value
	creates the actual and returns to the list
	'''
	cfData=CashFlow.query.filter_by(id=cfID).first()
	#here is where we will make the new or edit the existing actual data
	
	return redirect(url_for('cfBreakdown',id=cfData.id, accID=cfData.account_id))
	
@app.route('/cfBreakdown/<id><expID>',methods=['GET','POST'])
def cfBreakdown(id,expID):
	'''
	breaksdown a cashflow into expenses
	if the cashflow is an estimate allows addition of actual values
	'''
	cfData=CashFlow.query.filter_by(id=id).first() #get the cashflow data
	expData=Expense.query.filter_by(cf_id=id).all() #get all of the expenses for the cashflow
	form={thing.id:forms.addExpenseForm(date=thing.date,value=thing.value) for thing in expData}	#create all of our forms for the page
	#
	for key in form.keys():
		if form[key].validate_on_submit():
			#find the expense and edit the expense data
			exp=Expense.query.filter_by(id=expID).first()
			exp.date=cfForm.date
			exp.value=cfForm.value
			db.session.add(exp)
			db.session.commit()
			#return back to the template
			#the forms are not being sent properly
			return redirect(url_for('cfBreakdown',id=cfData.id, expID=exp.id))
	
	return render_template('budg_cfBreakdown.html',cfData=cfData, expData=expData,form=form)
	
@app.route('/displayAccount/<acData>', methods=['GET','POST'])
@app.route('/displayAccount', methods=['GET','POST'])
def displayAccount(acData):
	#this will display an account and show the cashflows specific to it
	#eventually this will display future, past, etc options

	ddList=Account.query.all()
	if acData=='None':
		#sent an empty 
		acData=ddList[0]
	else:
		acData=Account.query.filter_by(id=acData).first()
		
	if request.method=='POST':
		#something was posted
		acData=Account.query.filter_by(id=request.form['account']).first()		
		
	cfData=acData.cashFlows
	expData=acData.expenses.filter_by(cf_id=None)
	(tf_in,tf_out)=acData.getTransfers()	#[(tfIn,tfOut)]
	
	#otherwise we return with the option to select the accoutn data
	return render_template('budg_account_data.html',acData=acData,
		ddList=ddList,cfData=cfData,expData=expData,
		tf_in=tf_in, tf_out=tf_out,tDate=datetime.date.today())


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