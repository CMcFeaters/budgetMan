'''Budget Page'''
#webpage
#uses flask to create working page

from budg_functions import delAccount, addAccount, accountCompile, addCashFlow, cfCompile
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

@app.route('/editAccount/<title>',methods=['GET','POST'])
def edAccount(title):
	'''this should use add account template with filled in values'''
	pass

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

@app.route('/adCashFlow',methods=['GET','POST'])
def adCashFlow():
	'''add a cashflow to an account'''
	if request.method=='POST': 
		#get the estimating
		if request.form['estimate']=="Checked":
			est=True
		else:
			est=False
		#current problem***********************
			#the cashflow's aren't affecting the totals on the welcome page
			#maybe something with the account id's, etc
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

@app.route('/displayAccount', methods=['GET'])
def displayAccount():
	#this will display an account and show the cashflows specific to it
	pass

if __name__=='__main__':
		app.run()