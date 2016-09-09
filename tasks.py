#!/usr/bin/python
from celery import Celery
import MySQLdb
import json
from MachineLearning.BuildClassifier import getDiscreetClassifier
from MachineLearning.Clean import cleanData
from MachineLearning.CrossValidate import doShuffleCrossValidation
from MachineLearning.GetDataPoints import getDataPoints
import pymongo
import gridfs
from bson.objectid import ObjectId


app = Celery('tasks', broker='amqp://guest@queue//')

def getDB():
  db = MySQLdb.connect("db","csynapse","MyMZhdiEvY33WbqqAsFnLkcoQqRbacxo", "csynapse")
  return db

def getMongoID(identifier):
  db = getDB()
  cursor = db.cursor()
  select_sql = "SELECT mongo_id FROM RequestInformation WHERE identifier='%s'" % (identifier)
  cursor.execute(select_sql)
  result = cursor.fetchone()
  if result != None:
    return result[0]
  else:
    return ""

# Returns path to training data on filesystem
def buildPath(identifier):
  mongo_id = getMongoID(identifier)
  
  if mongo_id == "":
    raise "MongoID is not in SQL Database"
  
  mdb = pymongo.MongoClient('mongo', 27017).csynapse_files
  fs = gridfs.GridFS(mdb)
  
  filename = '/tmp/'+identifier+'.csv'
  
  with open(filename, 'w') as f:
    f.write(fs.get(ObjectId(mongo_id)).read())
  
  return filename

@app.task
def runAlgorithm(identifier, algorithm):
  ret = {}
  if algorithm == "TEST":
    ret["status"] = 1
    ret["accuracy"] = 0.927
    ret["notes"] = "This is just a test algorithm"
  elif algorithm == 'graphData':
    data = cleanData(buildPath(identifier))
    ret = getDataPoints(data.data, data.target,2)
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
  #print update_sql
  cursor.execute(update_sql)
  db.commit()
  return