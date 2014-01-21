Budget program
Front End
User interface: Browser
Templates: HTML
"Server": Flask
Back End
Database: SQL Lite
Database interface: Sqlalchemy

The program will be used to track expenses.  Users will be able to 
set recurring expenses/incomes, input miscallaneous expenses/incomes and
all other monitoring of cash flow.

Account values will be calculated.  There are two types of account: Cash and debt.  Cash accounts
are used to store income and cash on hand after expenses.  
Debsts will be interest incurring.  The debt amount will be either fixed value (student loans) or 
fluxuating (credit card).  Users can experiment with payment plans to see the amount of money lost to interest,
pay off dates, etc.

In addition to storing this data, the program will calculate account values on given dates, notify of upcoming payments and 
monitor account values to preset conditions.  Finally graphs visually displaying long term trends will be added.


Functionality to Add:
	Account
	-time to goal
	-


The database will have the following tables

CashFlow
	-This will be used to keep track of cash movement in and out of accounts.  Values can either be recurring or instantaneous, positive or negative
Accounts
	-This will keep a total for each account and account for interest

Cashflow Table
-Title
-Value
-Estimated (optional)
-From 
-To (optional)
-Date
-Recurring rate (optional)

Accounts Table
-Title
-Current Value
-Entered Value
-Entered Date
-Interest Rate