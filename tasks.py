#!/usr/bin/python
from celery import Celery
import json
from MachineLearning.BuildClassifier import getDiscreetClassifier
from MachineLearning.Clean import cleanData, cleanUntagged, getHeaders
from MachineLearning.CrossValidate import doShuffleCrossValidation
from MachineLearning.GetDataPoints import getDataPoints
from MachineLearning.ClassifyData import predict
import MachineLearning.RunExternal as runEx
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId


app = Celery('tasks', broker='amqp://guest@queue//')
mongoPort = 27017

def getMongoDB():
  mdb = MongoClient('mongo', mongoPort)
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
  result = None
  finalString = ''
  # special case for homegrown algorithms
  if(algorithm in ['adaline', 'hebbian', 'multiLayerPerceptronSig', 'multiLayerPerceptronTan']):
    # training data
    trainingPath = getDataFile(oldDataId)

    # get headers
    possibleHeaders = getHeaders(trainingPath)
    # new Data
    newDataPath = getDataFile(newDataId)
    resultsPath = trainingPath + 'results'

    runEx.execute('java -jar externalExecutables/{0}.jar {1} {2} {3}'.format(algorithm,trainingPath,newDataPath,resultsPath))

    # write header to file
    if(possibleHeaders != ''):
      with open(resultsPath, 'r') as f:
        content = f.read()
        finalString = possibleHeaders + content
  else:
    # Get old data 
    oldData = cleanData(getDataFile(oldDataId))
    # Instantiate Classifier
    alg = getDiscreetClassifier(algorithm)
    # Train on data
    alg.fit(oldData.data, oldData.target)

    # Get new data
    newData = cleanUntagged(getDataFile(newDataId))

    # Get headers from old file to save with results
    possibleHeaders = oldData.headers
    # Predict the new data
    result = predict(alg, newData.data)

    finalStringList = []
    if(possibleHeaders != ''):
      finalStringList.append(possibleHeaders)
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
  # Save data Id to cynapse
  users = getMongoDB().csynapse.users
  users.update_one({'_id':userName},\
    {'$set':{'csynapses.{0}.classified.{1}'.format(csynapseName,dataName):classifiedDataId}})
  return

@app.task
def runAlgoTest(dataId, algorithm, userName, csynapseName):
  ret = {}
  # special case for homegrown algos
  if(algorithm in ['adaline', 'hebbian', 'multiLayerPerceptronSig', 'multiLayerPerceptronTan']):
    # get file
    path = getDataFile(dataId)
    resultsPath = path + 'results'
    runEx.execute('java -jar externalExecutables/{0}.jar {1} {2}'.format(algorithm,path,resultsPath))
    # get results from file
    with open(resultsPath, 'r') as f:
      data = f.read()
      score, time = data.split(',')
      ret['score'] = float(score) / 100
      ret['time'] = float(time) / 1000
  else:
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

@app.task
def taskGetPoints(userName, csynapseName, mongoId):
  ret = {}
  # get Data points
  data = cleanData(getDataFile(mongoId))
  # find dimensionality of data
  d = len(data.data[0])
  dimensions = None
  if(d >= 3):
    dimensions = [3,2,1]
  elif(d == 2):
    dimensions = [2,1]
  else:
    dimensions = [1]

  for x in dimensions:
    points = getDataPoints(data.data,data.target,x)
    #save result in database
    mdb = getMongoDB().csynapse_files
    fs = gridfs.GridFS(mdb)
    pointsId = fs.put(str(points))
    userCollection = getMongoDB().csynapse.users
    userCollection.update_one({'_id':userName},\
      {'$set':{'csynapses.{0}.points.{1}'.format(csynapseName,x):pointsId}})