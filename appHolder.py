'''this file will hold our app.  all other files will reference this
when they need to access the db'''

from flask import Flask, render_template,redirect,url_for, flash, request, session
from flask.ext.sqlalchemy import SQLAlchemy

path="Users/Charles/Dropbox/Programming/DataBases/budget.db"

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+path
db = SQLAlchemy(app)
#app.config.from_envvar('FLASKR_SETTINGS',silent=True)
app.debug=True
app.secret_key = 'development key'