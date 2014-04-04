'''Budget Page'''
#webpage
#uses flask to create working page
from flask import Flask, render_template,redirect,url_for, flash, request, session
from flask.ext.sqlalchemy import SQLAlchemy
import budg_tables
import datetime

path="Users/Charles/Dropbox/Programming/DataBases/budget.db"

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+path
db = SQLAlchemy(app)
#app.config.from_envvar('FLASKR_SETTINGS',silent=True)
app.debug=True
app.secret_key = 'development key'

@app.route('/')
def welcome():
	#standard welcome, you're logged in or you're not
	results=budg_tables.Account.query
	return render_template("budg_welcome.html", results=results,tDate=datetime.date.today())
	
if __name__=='__main__':
		app.run()