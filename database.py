from pymongo import MongoClient
import gridfs

class db:
	def __init__(self, name, port, connect=True):
		self.client = MongoClient(name, port, connect=connect)
		self.algorithms = self.client.csynapse.algorithms
		self.users = self.client.csynapse.users
		self.files = gridfs.GridFS(self.client.csynapse_files)
		self.userAuth = self.client.auth.csynapse_users
		self.custom = self.client.custom.data