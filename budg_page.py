'''Budget Page'''
#webpage
#uses flask to create working page

from budg_functions import delAccount, addAccount
from budg_tables import Account, CashFlow
from appHolder import db, app
import datetime





@app.route('/')
def welcome():
	#standard welcome, you're logged in or you're not
	results=budg_tables.Account.query
	return render_template("budg_welcome.html", results=results,tDate=datetime.date.today())
	
@app.route('/deleteAccount/<title>')
def deleteAccount(title):
	#standard welcome, you're logged in or you're not
	budg_functions.delAccount(title)
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
		return redirect(url_for('welcome')
		
	else:
		#just display the page so the user can enter the data
		

if __name__=='__main__':
		app.run()