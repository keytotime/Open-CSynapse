#!/usr/bin/python
from celery import Celery
import json
from MachineLearning.BuildClassifier import getDiscreetClassifier
from MachineLearning.Clean import cleanData, cleanUntagged
from MachineLearning.CrossValidate import doShuffleCrossValidation
from MachineLearning.GetDataPoints import getDataPoints
from MachineLearning.ClassifyData import predict
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId


app = Celery('tasks', broker='amqp://guest@queue//')
mongoPort = 5000

def getMongoDB():
  mdb = MongoClient('localhost', mongoPort)
  return mdb

# Returns path to file of data
def getDataFile(mongoId):
  mdb = getMongoDB().csynapse_files
  fs = gridfs.GridFS(mdb)

  filename = '/tmp/{0}.csv'.format(mongoId)
  with open(filename, 'w') as f:
    f.write(fs.get(ObjectId(mongoId)).read())
  return filename
   

@app.task
def classify(newDataId, oldDataId, algorithm, userName, csynapseName, dataName):
  ret = {}

  # Get old data 
  oldData = cleanData(getDataFile(oldDataId))
  # Instantiate Classifier
  alg = getDiscreetClassifier(algorithm)
  # Train on data
  alg.fit(oldData.data, oldData.target)

  # Get new data
  newData = cleanUntagged(getDataFile(newDataId))

  # Predict the new data
  result = predict(alg, newData)

  finalStringList = []
  # Put data into string to save
  for x in result:
    finalStringList.append(str(x[0]) + ',')
    for v in x[1]:
      finalStringList.append(str(v))
      finalStringList.append(',')
    finalStringList[-1] = '\n'

  finalString = ''.join(finalStringList)
  # Put classified data file into the database
  mdb = getMongoDB().csynapse_files
  fs = gridfs.GridFS(mdb)
  classifiedDataId = fs.put(finalString)
  print(finalString)
  # Save data Id to cynapse
  users = getMongoDB().csynapse.users
  users.update_one({'_id':userName},\
    {'$set':{'csynapses.{0}.classified.{1}'.format(csynapseName,dataName):classifiedDataId}})
  return

@app.task
def runAlgoTest(dataId, algorithm, userName, csynapseName):
  ret = {}
  # Instantiate Classifier
  alg = getDiscreetClassifier(algorithm)
  # Get data from file
  data = cleanData(getDataFile(dataId))
  # Run Cross Validation
  meanScoreTime = doShuffleCrossValidation(alg, data.data, data.target)
  ret['score'] = meanScoreTime.meanScore
  ret['time'] = meanScoreTime.timeTaken

  newObjectId = str(ObjectId())
  # save result in db
  userCollection = getMongoDB().csynapse.users
  userCollection.update_one({'_id':userName}, \
    {'$set':{'csynapses.{0}.algorithms.{1}'.format(csynapseName,newObjectId):{'score':ret['score'],\
    'time':ret['time'], 'algoId':algorithm}}})
  return