'''Budget Page'''
#webpage
#uses flask to create working page

from budg_functions import delAccount, addAccount, accountCompile
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
	print "1"
	if request.method=='POST': 
		#the form data has been posted
		print "2"
		acRes=accountCompile(request.form['title'],request.form['entVal'],request.form['entY'], request.form['entM'],request.form['entD'],request.form['entLow'])
		print "3"
		if acRes[0]==False:
			flash(acRes[1])
		else:
			addAccount(acRes[0],acRes[1],acRes[2],acRes[3])
			return redirect(url_for('welcome'))
	return render_template('budg_addAccount.html')
		

if __name__=='__main__':
		app.run()