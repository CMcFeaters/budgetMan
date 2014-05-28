'''test code
'''

def func(x,y):
	z=x+y
	print z
	
def tableMaker(**kwargs):
	for name,value in kwargs.items():
		return '{0} = {1}'.format(name,value)
		
func(*[7,2])