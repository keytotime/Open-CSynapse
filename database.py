from pymongo import MongoClient
import gridfs

class db:
	def __init__(self, name, port):
		self.client = MongoClient(name, port)
		self.algorithms = self.client.csynapse.algorithms
		self.users = self.client.csynapse.users
		self.files = gridfs.GridFS(self.client.csynapse_files)
		self.userAuth = self.client.cysnapse.csynapse_users