'''Budget Page'''
#webpage
#uses flask to create working page

from budg_functions import delAccount, addAccount, accountCompile, addCashFlow, cfCompile,delCashFlow,dateCompile, editAccount
from budg_tables import Account, CashFlow
from appHolder import db, app
import datetime
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
	return redirect(url_for('displayAccount'))

	
@app.route('/edAccount/<id>',methods=['GET','POST'])
def edAccount(id):
	'''this should use add account template with filled in values'''
	accData=Account.query.filter_by(id=id).first()
	#print"****1****"
	if request.method=='POST': 
		#check to see what was changed
		if request.form['title']==accData.title: nTitle=""
		else: nTitle=request.form['title']
		print"****1****"
		#entered value
		
		if request.form['entVal']==accData.entVal: nVal=""
		else: nVal=request.form['entVal']
		print"****2****"
		
		#repeat compariosn 
		if request.form['entLow']==accData.lowVal: nLow=""
		else: nLow=request.form['entLow']
		print"****3****"
		
		#for the date, compile it first, then compare
		fDate=dateCompile(request.form['entY'], request.form['entM'],request.form['entD'])
		if fDate==False or fDate==accData.entDate: nDate=""
		else: nDate=fDate
		print"****4****"
		
		#run the edit, see what comes up false
		edRes=editAccount(accData.id,nTitle,nVal,nDate,nLow)
		print"****5****"
		
		if edRes[0]==False:
			flash(edRes[1])
		else:
			return redirect(url_for('welcome'))
	return render_template('budg_editAccount.html',accData=accData)

@app.route('/adAccount',methods=['GET','POST'])
def adAccount():
	'''adds an account'''
	if request.method=='POST': 
		#the form data has been posted
		acRes=accountCompile(request.form['title'],request.form['entVal'],request.form['entY'], request.form['entM'],request.form['entD'],request.form['entLow'])
		if acRes[0]==False:
			flash(acRes[1])
			
		else:
			addAccount(acRes[0],acRes[1],acRes[2],acRes[3])
			return redirect(url_for('welcome'))
	return render_template('budg_addAccount.html')

@app.route('/adExpense',methods=['GET','POST'])
def adExpense():
	'''add cashflow, but for a single expense'''
	if request.method=='POST': 
		#the form data has been posted
		#run the compile/validate procedure
		cfRes=cfCompile(request.form['account'],request.form['title'],request.form['entVal'],request.form['Y'],request.form['M'],request.form['D'])
		#error check and create
		if cfRes[0]==False:
			flash(cfRes[1])
		else:
			addCashFlow(cfRes[0],cfRes[1],cfRes[2],cfRes[3],cfRes[4],cfRes[5],cfRes[6],cfRes[7])
			return redirect(url_for('welcome'))
	
	#send in the accounts to populate the dropdown menu
	acData=Account.query.all()
	return render_template('budg_addExpense.html',acData=acData)

	
@app.route('/adCashFlow',methods=['GET','POST'])
def adCashFlow():
	'''add a cashflow to an account'''
	if request.method=='POST': 
		#get the estimating
		if request.form['estimate']=="known":
			est=False
		else:
			est=True
		#the form data has been posted
		#run the compile/validate procedure
		cfRes=cfCompile(request.form['account'],request.form['title'],request.form['entVal'],request.form['sY'],request.form['sM'],request.form['sD'], \
		request.form['nType'],request.form['nRate'],request.form['eY'],request.form['eM'],request.form['eD'],est)
		#error check and create
		if cfRes[0]==False:
			flash(cfRes[1])
		else:
			addCashFlow(cfRes[0],cfRes[1],cfRes[2],cfRes[3],cfRes[4],cfRes[5],cfRes[6],cfRes[7])
			return redirect(url_for('welcome'))
	
	#send in the accounts to populate the dropdown menu
	acData=Account.query.all()
	return render_template('budg_addCashFlow.html',acData=acData)

@app.route('/displayAccount', methods=['GET','POST'])
def displayAccount():
	#this will display an account and show the cashflows specific to it
	#eventually this will display future, past, etc options

	ddList=Account.query.all()
	if request.method=='POST':
		#post will perform the querying of the account and display the information
		#include: the account information
		#the cashflow informationd
		acData=Account.query.filter_by(id=request.form['account']).first()
		
		cfData=CashFlow.query.filter_by(account_id=request.form['account']).all()
		return render_template('budg_account_data.html',acData=acData,ddList=ddList,cfData=cfData,tDate=datetime.date.today())
	#otherwise we return with the option to select the accoutn data
	return render_template('budg_account_data.html',acData="None",ddList=ddList,cfData="",tDate=datetime.date.today())


#simple python scripts made part of jinja template
@app.template_test('less10')
def less10(value):
	'''takes in a value and dertmines if it is less than 10'''
	return (value<10)
app.jinja_env.tests['less10']=less10

if __name__=='__main__':
	db.create_all()
	app.run()