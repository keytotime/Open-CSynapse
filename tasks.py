from celery import Celery
import MySQLdb
import json
from MachineLearning.BuildClassifier import getDiscreetClassifier
from MachineLearning.Clean import cleanData
from MachineLearning.CrossValidate import doShuffleCrossValidation
from MachineLearning.GetDataPoints import get2DPoints

app = Celery('tasks', broker='amqp://guest@localhost//')

def getDB():
  db = MySQLdb.connect("localhost","csynapse","MyMZhdiEvY33WbqqAsFnLkcoQqRbacxo", "csynapse")
  return db

# Returns path to training data on filesystem
def buildPath(identifier):
  return '/var/csynapse/uploads/' + identifier + '.csv'

@app.task
def runAlgorithm(identifier, algorithm):
  ret = {}
  if algorithm == "TEST":
    ret["status"] = 1
    ret["accuracy"] = 0.927
    ret["notes"] = "This is just a test algorithm"
  elif algorithm == 'graphData':
    data = cleanData(buildPath(identifier))
    ret = get2DPoints(data.data, data.target)
  else:
    # Instantiate Classifier
    alg = getDiscreetClassifier(algorithm)
    # Get data from file
    data = cleanData(buildPath(identifier))
    # Run Cross Validation
    meanScoreTime = doShuffleCrossValidation(alg, data.data, data.target)
    ret['score'] = meanScoreTime.meanScore
    ret['time'] = meanScoreTime.timeTaken

  db = getDB()
  cursor = db.cursor()
  update_sql = "UPDATE Requests SET complete=1, return_object='%s' WHERE identifier='%s' AND algorithm='%s'" % (json.dumps(ret), identifier, algorithm)
  print update_sql
  cursor.execute(update_sql)
  db.commit()
  return