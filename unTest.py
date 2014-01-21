import unittest, datetime

#the expected datepattern
class DatePattern():
	
	def __init__(self,year, month, day, weekDay=0):
		self.year=year
		self.month=month
		self.day=day
		self.weekDay=weekDay
	
	#matches method
	def matches(self, date):
		return ((self.year and self.year==date.year or True) and
		(self.month and self.month==date.month or True) and
		(self.day and self.day==date.day or True) and
		(self.weekDay and self.weekDay==date.weekday() or True))

#tyhe unit tests
class FooTests(unittest.TestCase):
	def testFoo(self):
		self.failUnless(True)
		
	def testMatches(self):
		p=DatePattern(2004, 9, 28)
		d=datetime.date(2004, 9, 28)
		self.failUnless(p.matches(d))
		
	def testMatchesYearAsWildcard(self):
		p=DatePattern(0,9,28)
		d=datetime.date(2005,9,28)
		self.failUnless(p.matches(d))
	
	def testMatchesMonthYearAsWildcard(self):
		p=DatePattern(0,0,28)
		d=datetime.date(2005,9,28)
		self.failUnless(p.matches(d))
	
	def testMatchesWeekday(self):
		p=DatePattern(0,0,0,2)
		d=datetime.date(2004,9,29)
		self.failUnless(p.matches(d))
	
def main():
	unittest.main()
	
if __name__=='__main__':
	main()
