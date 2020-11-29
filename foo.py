big_list = set()
big_list.add(1)
big_list.add(3)

class Test():

	def __init__(self):
		self.color = 'red'
		self.bdsm = 'kinky'

	def __and__(self, other):
		global big_list
		big_list.discard(other)


me = Test()
print(me.__getattribute__(self))