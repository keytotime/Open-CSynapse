#!/usr/bin/python
from celery import Celery
import json
from MachineLearning.BuildClassifier import getDiscreetClassifier
from MachineLearning.Clean import cleanData, cleanUntagged, getHeaders, regressionData
from MachineLearning.CrossValidate import doShuffleCrossValidation
from MachineLearning.GetDataPoints import getDataPoints
from MachineLearning.ClassifyData import predict
from MachineLearning.Regression import reg
from MachineLearning.ParseImage import vectorizeImages,vectorizeForClassify
import MachineLearning.RunExternal as runEx
from database import db
from bson.objectid import ObjectId
import os
import itertools
from numpy import transpose
from time import sleep
import uuid

app = Celery('tasks', broker='amqp://guest@queue//')
mongoPort = 27017
db = db('mongo', mongoPort, connect=False)

# Returns path to file of data
def getDataFile(mongoId):
  filename = '/tmp/{0}.csv'.format(mongoId)
  with open(filename, 'w') as f:
    f.write(db.files.get(ObjectId(mongoId)).read())
  return filename

def getMultiPartDataFiles(userName, csynapseName):
  obj = db.users.find_one({"_id":userName}, {"csynapses.{}.multipart_data".format(csynapseName):1})
  ids = obj["csynapses"]["{}".format(csynapseName)]["multipart_data"]
  files = []
  for file in ids:
    files.append(getDataFile(file))
  return files

@app.task
def process_photos(userName, csynapseName):
  fileNames = getMultiPartDataFiles(userName,csynapseName)
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})

  labelMap = doc['csynapses'][csynapseName]['multipart_data_tagmap']

  # make dictionary mapping labels to lists of filenames
  mappedFiles = {}
  for key, value in labelMap.iteritems():
    mappedFiles[key] = [getDataFile(mongoId) for mongoId in value]  

  stringData = vectorizeImages(mappedFiles)
  
  dataId = db.files.put(stringData)
  
  userCollection.update_one({'_id':userName},\
      {'$set':{'csynapses.{0}.data_id'.format(csynapseName):dataId}})
  userCollection.update_one({'_id':userName},\
      {'$set':{'csynapses.{0}.multipart_reduced'.format(csynapseName):1}})
 
  taskGetPoints(userName, csynapseName, dataId)

@app.task
def classify(newDataId, oldDataId, algorithm, params, userName, csynapseName, dataName):
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

    # Get params of algorithm 
    # Instantiate Classifier
    alg = getDiscreetClassifier(algorithm, params)
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
      for v in x[1][:-1]:
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
def classifyImages(dataIds, oldDataId, algorithm, params, userName, csynapseName, dataName):
  fileNames = getMultiPartDataFiles(userName,csynapseName)
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})

  labelMap = doc['csynapses'][csynapseName]['multipart_data_tagmap']

  # make dictionary mapping labels to lists of filenames
  mappedFiles = {}
  for key, value in labelMap.iteritems():
    mappedFiles[key] = [getDataFile(mongoId) for mongoId in value]

  unlabeledFiles = []
  for x in dataIds:
    filename, dataId = x
    unlabeledFiles.append((filename,getDataFile(dataId)))

  finalString = ''

  # special case for homegrown algorithms
  if(algorithm in ['adaline', 'hebbian', 'multiLayerPerceptronSig', 'multiLayerPerceptronTan']):
    # Get file paths for old and new data
    unique = str(uuid.uuid4())
    trainingPath = 'train' + unique
    newDataPath = 'classify' + unique
    resultsPath = 'results' + unique

    script_dir = os.path.dirname(os.path.realpath(__file__))
    imageNames = vectorizeForClassify(mappedFiles, unlabeledFiles, trainingPath, newDataPath)
    
    runEx.execute('java -jar {4}/externalExecutables/{0}.jar {1} {2} {3}'.format(algorithm,trainingPath,newDataPath,resultsPath,script_dir))

    stringBuilder = []
    with open(resultsPath, 'r') as f:
      for i, line in enumerate(f):
        stringBuilder.append(line.split(',')[0] + ',' + imageNames[i])
    finalString = '\n'.join(stringBuilder)
  else:
    trainingData, toClassify = vectorizeForClassify(mappedFiles, unlabeledFiles)
    # Instantiate Classifier
    alg = getDiscreetClassifier(algorithm, params)
    # Train on data
    alg.fit(trainingData.data, trainingData.target)

    predictResult = predict(alg, toClassify.data)

    classifiedData = []
    # add file names back
    for index, label in enumerate(toClassify.names):
      classifiedData.append((predictResult[index][0], label))

    commaStringList = [','.join(x) for x in classifiedData]
    finalString = '\n'.join(commaStringList)

  classifiedDataId = db.files.put(finalString.encode("UTF-8"))
  # Save data Id to cynapse
  users = db.users
  users.update_one({'_id':userName},\
    {'$set':{'csynapses.{0}.classified.{1}'.format(csynapseName,dataName):classifiedDataId}})


@app.task
def runAlgoTest(algoData, userName, csynapseName):
  
  algorithm = algoData['algorithm']
  params = {}
  if('params' in algoData):
    params = algoData['params']

  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})
  #the following is ATROCIOUS code, but should work for now.
  #need better reporting tools to do better
  if "data_id" not in (doc['csynapses'][csynapseName]).keys() and "multipart_data" not in (doc['csynapses'][csynapseName]).keys():
    raise DataException("Data Not Available")
  found = False
  if "data_id" in (doc['csynapses'][csynapseName]).keys():
    found = True
  cycles_to_wait = 20
  cycles = 0
  if not found:
    while not found:
      doc = userCollection.find_one({'_id':userName})
      if ("multipart_data" in (doc['csynapses'][csynapseName]).keys() and "multipart_reduced" in (doc['csynapses'][csynapseName]).keys()):
        found = True
      else:
        cycles = cycles + 1
      if cycles == cycles_to_wait:
        raise WaitException("Took Too Long to Generate Data")
      sleep(1)
    sleep(3)
    
  dataId = doc['csynapses'][csynapseName]['data_id']
  
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
    alg = getDiscreetClassifier(algorithm, params)
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
    'time':ret['time'], 'algoId':algorithm, 'params':params}}})
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

  # yields list of [(index,value),...]
  indexedHeaders = [indexed for indexed in enumerate(data.headers)]

  # yields list of [((index,value),(index,value))...]
  combinations = [combo for combo in itertools.combinations(indexedHeaders,2)]

  # Get data into list of columns
  transposedData = transpose(data.data)
  # Do regressions. Yields (headerOne, HeaderTwo, (rValue_strength, pValue_))
  finalList = []
  for x in combinations:
    d = {}
    d['h1'] = x[0][1]
    d['h2'] =  x[1][1]
    regResults = reg(transposedData[x[0][0]], transposedData[x[1][0]])
    d['r'] = regResults.r
    d['p'] = regResults.p
    d['rSquared'] = regResults.r * regResults.r
    finalList.append(d)

  regressionId = db.files.put(json.dumps(finalList))
  userCollection = db.users
  userCollection.update_one({'_id':userName},\
    {'$set':{'csynapses.{0}.regression'.format(csynapseName):regressionId}})

class WaitException(Exception):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

class DataException(Exception):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message