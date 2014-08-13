'''Budget Page'''
#webpage
#uses flask to create working page

from budg_functions import delAccount, delCashFlow
from budg_tables import Account, CashFlow, Expense, Transfer, create_a_thing, Master, BudgetTag
import forms 
from appHolder import db, app
import datetime
from flask import Flask, render_template,redirect,url_for, flash, request, session

@app.route('/deleteCashFlow/<id>-<accID>_<name>',methods=['GET','POST'])
@app.route('/deleteAccount/<id>-<accID>_<name>',methods=['GET','POST'])
@app.route('/deleteTransfer/<id>-<accID>_<name>',methods=['GET','POST'])
@app.route('/deleteExpense/<id>-<accID>_<name>',methods=['GET','POST'])
@app.route('/deleteMaster/<id>-<accID>_<name>',methods=['GET','POST'])
def delete_a_thing(name,id,accID):
	'''
	universal delete
	'''
	dict={'cashflow':CashFlow,'expense':Expense,'transfer':Transfer,'account':Account,'master':Master,'budgettag':BudgetTag}
	db.session.delete(dict[name].query.filter_by(id=id).first())
	db.session.commit()
	
	if name=="account":
		return redirect(url_for('welcome'))
	else:
		return redirect(url_for('displayAccount',acData='None'))


def ed_a_thing(id,tblName):
	'''
	universal editer, takes in the table and Id, returns 
	'''
	tableDict={'cashflow':CashFlow,'expense':Expense,'transfer':Transfer,'account':Account,'master':Master}
	thing=tableDict[table].query.filter_by(id=id).first()
	formDict={'cashflow':forms.addCashFlowForm,'expense':forms.addExpenseForm,'transfer':forms.transferForm,'account':forms.addAccountForm,'master':forms.addBudgetForm}
	templateDict={'cashflow':'budg_Cashflow.html','expense':'budg_Expense.html','transfer':'budg_Transfer.html','account':'budg_Account.html','master':'budg_Master.html'}
	form=formDict[table]
	table=tableDict[tblName]

	if form.validate_on_submit():
		for key in thing.__dict__.keys():
			thing[key]=form[key]
			#need ot modify forms to match the tables
	
		return redirect(url_for('welcome'))
	
	return render_template(templateDict[table],accData=accData, form=form, edAdd='edit')
	
@app.route('/')
def welcome():
	#standard welcome, you're logged in or you're not
	results=Account.query
	return render_template("budg_welcome.html", results=results,tDate=datetime.date.today())
	
#***********ADD*********
@app.route('/adExpense',methods=['GET','POST'])
def adExpense():
	'''add a single expense to an account'''
	form=forms.addExpenseForm()	#set up theform
	form.account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title').all()]
	form.cashflow.choices=[(cf.id,cf.title) for cf in CashFlow.query.all()]
	form.budget.choices=[(budg.id,budg.title) for budg in Master.query.all()]
	form.cfOrBudg.data="none"
	if form.validate_on_submit(): 
		#if the form data is validated
		create_a_thing(Expense,[form.account.data,form.title.data,form.value.data,form.date.data,form.cashflow.data,form.budget.data])
		
		return redirect(url_for('welcome'))
	
	#send in the accounts to populate the dropdown menu
	
	return render_template('budg_Expense.html',form=form,edAdd="add")

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
	
@app.route('/adBudget',methods=['GET','POST'])
def adBudget():
	'''add a cashflow to an account'''
	form=forms.addBudget()
	form.account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	if form.validate_on_submit(): 
		create_a_thing(Master,[form.account.data,form.title.data,form.entVal.data,form.sDate.data,\
			form.rType.data,form.rRate.data,form.eDate.data])
		[master.createBudgetTags() for master in Master.query.all() if master.budgetTags==[]]
		#create all the budgettags
		return redirect(url_for('welcome'))
	
	return render_template('budg_Budget.html',form=form,edAdd="add")
	
#*******edits******

@app.route('/edExpense/<id>',methods=['GET','POST'])
def edExpense(id):
	'''
	only called with a url link
	'''
	expData=Expense.query.filter_by(id=id).first()
	#make form and assign default values
	
	form=forms.addExpenseForm(title=expData.title,value=expData.value,date=expData.date,account=expData.account_id,cashflow=expData.cf_id,budget=expData.budg_id)
	form.account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title').all()]
	form.cashflow.choices=[(cf.id,cf.title) for cf in CashFlow.query.filter_by(account_id=expData.id).all()]
	form.budget.choices=[(budg.id,budg.title) for budg in Master.query.filter_by(account_id=expData.id).all()]
	
	#set the radio to whatever the previous value was
	if expData.cf_id:
		form.cfOrBudg.data='cf'
	elif expData.budg_id:
		form.cfOrBudg.data='budg'
	else: form.cfOrBudg.data="none"
		
	#form submission info
	if form.validate_on_submit():

		db.session.delete(expData)
		db.session.commit()
		create_a_thing(Expense,[form.account.data,form.title.data,form.value.data,form.date.data,form.cashflow.data,form.budget.data])

		flash("Expense %s Edit Success!"%expData.title)

		return redirect(url_for('welcome'))
	
	return render_template('budg_Expense.html',expData=expData, form=form,expAdd="edit")


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
	
@app.route('/edCashFlow/<id>',methods=['GET','POST'])
def edCashFlow(id):
	'''
	only called with a url link
	'''
	cfData=CashFlow.query.filter_by(id=id).first()
	#make form and assign default values
	
	form=forms.addCashFlowForm(title=cfData.title,entVal=cfData.value,sDate=cfData.date,
	account=cfData.account_id, rType=cfData.recurType, rRate=cfData.recurRate, 
	eDate=cfData.recurEnd)
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

@app.route('/edBudget/<id>',methods=['GET','POST'])
def edBudget(id):
	'''
	only called with a url link
	'''
	budgData=Master.query.filter_by(id=id).first()
	#make form and assign default values
	
	form=forms.addBudget(title=budgData.title,entVal=budgData.value,sDate=budgData.date,
	account=budgData.account_id, rType=budgData.recurType, rRate=budgData.recurRate, 
	eDate=budgData.recurEnd)
	#add the account choices
	form.account.choices=[(acc.id,acc.title) for acc in Account.query.order_by('title')]
	
	if form.validate_on_submit():
	#	assign values and submit
		budgData.title=form.title.data
		budgData.value=form.entVal.data
		budgData.date=form.sDate.data
		budgData.account_id=form.account.data
		budgData.recurType=form.rType.data
		budgData.recurRate=form.rRate.data
		budgData.recurEnd=form.eDate.data
		
		db.session.add(budgData)
		db.session.commit()
		
		#create the new budget tags
		#need to fix this.  it will delete all expenses associated with the budget
		budgData.createBudgetTags()
				
		flash("Budget %s Edit Success!"%budgData.title)

		return redirect(url_for('welcome'))
	
	return render_template('budg_Budget.html',budgData=budgData, form=form,edAdd="edit")

	
@app.route('/cfBreakdown/<id>-<i>',methods=['GET','POST'])
def cfBreakdown(id,i):
	'''
	breaksdown a cashflow into expenses
	if the cashflow is an estimate allows addition of actual values
	'''
	cfData=CashFlow.query.filter_by(id=id).first() #get the cashflow data
	expData=Expense.query.filter_by(cf_id=id).order_by(Expense.date).all() #get all of the expenses for the cashflow
	form=[forms.expFlowForm(date=thing.date,value=thing.value) for thing in expData]	#create all of our forms for the page
	i=int(i)
	
	#check the submitted form
	if i>=0:
		if form[i].validate_on_submit():
			#find the expense and edit the expense data
			#exp=Expense.query.filter_by(id=expID).first()
			expData[i].date=form[i].date.data
			expData[i].value=form[i].value.data
			db.session.add(expData[i])
			db.session.commit()
			#return back to the template
			#the forms are not being sent properly
			return redirect(url_for('cfBreakdown',id=cfData.id,i=0))
			
	
	return render_template('budg_cfBreakdown.html',cfData=cfData, expData=expData,form=form)
	

@app.route('/budgBreakdown/<id>',methods=['GET','POST'])
def budgBreakdown(id):
	'''
	breaksdown a budget into budgetTags
	id is the master id
	'''
	budgData=BudgetTag.query.filter_by(master_id=id).all() #get the budgetTag data
	
	return render_template('budg_budgBreakdown.html',budgData=budgData)
		
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
	expData=acData.expenses.filter_by(cf_id=None, budg_id=None)
	budgData=acData.masters
	(tf_in,tf_out)=acData.getTransfers()	#[(tfIn,tfOut)]
	
	#otherwise we return with the option to select the accoutn data
	return render_template('budg_account_data.html',acData=acData,
		ddList=ddList,cfData=cfData,expData=expData,
		tf_in=tf_in, tf_out=tf_out,tDate=datetime.date.today(),budgData=budgData)

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

	for thing in value:
		for stuff in thing:
			print stuff
	return url_for(value[0][0],title=value[0][1])
app.jinja_env.filters['url_ext']=url_ext


#user defined functions
def getValue(budget,cr):
	#cr is determines if we are returning the cost or the remainder
	if cr=="cost":
		return budget.getValue()
	else: return abs(abs(budget.getValue())-abs(budget.value))

app.jinja_env.globals.update(getValue=getValue)

if __name__=='__main__':
	db.create_all()
	app.run()