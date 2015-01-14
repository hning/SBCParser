import json


print "test"

class Config:
	def __init__(self, _setup_path):
		self.setup_path = _setup_path
		print self.setup_path
		self.parse_json()

	def parse_json(self):
		with open(self.setup_path) as data_file:    
   			self.data = json.load(data_file)

   	def __getitem__(self, key):
   		return self.data[key]
