from celery import Celery
import MySQLdb
import json

app = Celery('tasks', broker='amqp://guest@localhost//')

def getDB():
  db = MySQLdb.connect("localhost","csynapse","MyMZhdiEvY33WbqqAsFnLkcoQqRbacxo", "csynapse")
  return db

@app.task
def runAlgorithm(identifier, algorithm):
  ret = {}
  if algorithm == "TEST":
    ret["status"] = 1
    ret["accuracy"] = 0.927
    ret["notes"] = "This is just a test algorithm"
  db = getDB()
  cursor = db.cursor()
  update_sql = "UPDATE Requests SET complete=1, return_object='%s' WHERE identifier='%s' AND algorithm='%s'" % (json.dumps(ret), identifier, algorithm)
  print update_sql
  cursor.execute(update_sql)
  db.commit()
  return