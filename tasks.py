#!/usr/bin/python
from celery import Celery
import json
from MachineLearning.BuildClassifier import getDiscreetClassifier
from MachineLearning.Clean import cleanData, cleanUntagged, getHeaders, regressionData
from MachineLearning.CrossValidate import doShuffleCrossValidation
from MachineLearning.GetDataPoints import getDataPoints
from MachineLearning.ClassifyData import predict
from MachineLearning.Regression import reg
import MachineLearning.RunExternal as runEx
from database import db
from bson.objectid import ObjectId
import os
import itertools
from numpy import transpose

app = Celery('tasks', broker='amqp://guest@queue//')
mongoPort = 27017
db = db('mongo', mongoPort, connect=False)

# Returns path to file of data
def getDataFile(mongoId):
  filename = '/tmp/{0}.csv'.format(mongoId)
  with open(filename, 'w') as f:
    f.write(db.files.get(ObjectId(mongoId)).read())
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
  classifiedDataId = db.files.put(finalString)
  # Save data Id to cynapse
  users = db.users
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
    script_dir = os.path.dirname(os.path.realpath(__file__))
    runEx.execute('java -jar {3}/externalExecutables/{0}.jar {1} {2}'.format(algorithm,path,resultsPath,script_dir))
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
  userCollection = db.users
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
    pointsId = db.files.put(json.dumps(points))
    userCollection = db.users
    userCollection.update_one({'_id':userName},\
      {'$set':{'csynapses.{0}.points.{1}'.format(csynapseName,x):pointsId}})

@app.task
def regression(userName, csynapseName, mongoId):
  data = ''

  data = regressionData(getDataFile(mongoId))

  print(data)
  # yields list of [(index,value),...]
  indexedHeaders = [indexed for indexed in enumerate(data.headers)]

  # yields list of [((index,value),(index,value))...]
  combinations = [combo for combo in itertools.combinations(indexedHeaders,2)]

  # Get data into list of columns
  transposedData = transpose(data.data)
  # Do regressions. Yields (headerOne, HeaderTwo, (rValue_strength, pValue_))
  finalList = []
  for x in combinations:
    print(x)
    print('hello\n\n\n')
    d = {}
    d['h1'] = x[0][1]
    d['h2'] =  x[1][1]
    regResults = reg(transposedData[x[0][0]], transposedData[x[1][0]])
    d['r'] = regResults.r
    d['p'] = regResults.p
    finalList.append(d)

  regressionId = db.files.put(json.dumps(finalList))
  userCollection = db.users
  userCollection.update_one({'_id':userName},\
    {'$set':{'csynapses.{0}.regression'.format(csynapseName):regressionId}})
  
