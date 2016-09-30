#!/usr/bin/python

from bottle import *
from tasks import runAlgoTest, classify, taskGetPoints
import json
from database import db
from beaker.middleware import SessionMiddleware
import hashlib
import os
import base64
from bson.objectid import ObjectId

#prefix = "/app"
prefix = ""

session_opts = {
    'beaker.session.type': 'ext:memcached',
    'session.url': 'memcached:11211',
    'session.cookie_expires': 86400,
    'session.data_dir': './data',
    'session.auto': True
}

app = SessionMiddleware(app(), session_opts)
mongoPort = 27017
db = db('mongo', mongoPort)


def getBeakerSession():
  s = request.environ.get('beaker.session')
  return s

@get('/healthcheck')
def healthCheck():
	return json.dumps({200:'ok'})

# Get list of available algorithms from db 
@get('/algorithms')
def getAlgorithms():
  algoCollection = db.algorithms
  algos = algoCollection.find_one({'_id':'algorithms'})
  print(algos)
  return json.dumps([{'algoId':x,'description':algos[x][u'description'], 'name':algos[x][u'name']} for x in algos if(x != u'_id')])

# Get list of all csynapses owned by a user
# params user=UserName
@get('/csynapses')
def getCsynapses():
  userName = getUsername()
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})
  return json.dumps({'csynapses':doc['csynapses'].keys()})

# Creates a new csynapse for the user
# @params (body or query) user=userName, name=csynapseName to create
@post('/create')
def createCsynapse():
  # get username and csynapse
  userName = getUsername()
  csynapseName = request.params.get('name')
  userCollection = db.users

  ret = ''
  # update only if the csynapse doesn't already exist
  r = userCollection.update_one({'_id':userName,'csynapses.{0}'.format(csynapseName):{'$exists':False}}, \
  {'$set':{'csynapses.{0}'.format(csynapseName):{}}})
  
  if(r.matched_count == 1):
    ret = {'status':200,'body':'ok'}
  else:
    if (r.matched_count == 0):
      ret = {'status':422,'body':'csynapse was not created'}
    else:
      ret = {'status':422,'body':'csynapse already exists'}

  return HTTPResponse(status=ret['status'], body=json.dumps({'message':ret['body']}))

# Saves data associated with a cynapse
# @params user=userName, name=csynapseName, dataName=dataset name
@post('/data')
def saveData():
  userName = getUsername()
  csynapseName = request.params.get('name')
  upload = request.files.get('upload')

  # TODO Check if cynapse name and dataset Name already exists
  # return failed status if so
  # Save file in grid fs

  fs = db.files
  datasetId = fs.put(upload.file)

  # store dataset name and mon
  userCollection = db.users
  userCollection.update_one({'_id':userName}, \
    {'$set':{'csynapses.{0}.data_id'.format(csynapseName):datasetId}})

  return HTTPResponse(status=200)

# Begins obtaining the cross-validation score on an algorithm
# @params (body or query) user=userName, name=csynapseName,
# algorithms=list of algorithms to cross validate
@post('/test')
def testAlgorithm():
  userName = getUsername()
  csynapseName = request.params.get('name')
  algos = request.params.getall('algorithm')
  # Get dataId
  userCollection = db.users

  doc = userCollection.find_one({'_id':userName})
  dataId = doc['csynapses'][csynapseName]['data_id']

  # pass dataId and algorithms to task
  for algo in algos:
    runAlgoTest(dataId, algo, userName, csynapseName)
  # return 200
  return HTTPResponse(status=200)

# Gets the test results for all the algos run on the given csynapse
# @params (body or query) user=userName, name=csynapseName
# @returns {results:{algoId:svm,description:SVM classifier, score:score, time:time}}
@get('/testResults')
def getTestResults():
  userName = getUsername()
  csynapseName = request.params.get('name')

  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})
  algos = doc['csynapses'][csynapseName]['algorithms']
  # get descriptions
  algoCollection = db.algorithms
  
  algorithms = algoCollection.find_one({'_id':'algorithms'})
  for x in algorithms:
    for key,val in algos.items():
      if(x == val['algoId']):
        val['description'] = algorithms[x]['description']
        val['id'] = key
  return json.dumps([x for x in algos.itervalues()])

  
# Runs algorithms on new data
#params (body or query) user=userName, name=csynapseName
#upload:fileOfNewData
@post('/run')
def runAlgos():
  userName = getUsername()
  csynapseName = request.params.get('name')
  dataName = request.params.get('dataName')
  algo = request.params.get('algorithm')
  upload = request.files.get('upload')

  # save new data
  fs = db.files
  newDatasetId = fs.put(upload.file)

  # get mongoId of old data
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})
  oldDataId = doc['csynapses'][csynapseName]['data_id']
  # get algo type
  algoType = doc['csynapses'][csynapseName]['algorithms'][algo]['algoId']

  classify(newDatasetId, oldDataId, algoType, userName, csynapseName, dataName)

# Gets all available classified data
# @returns {cynapseName:[{datasetname:name, mongoId:id},...]}
@get('/getAllAvailableClassified')
def getClassified():
  userName = getUsername()
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})
  csynapses = doc['csynapses']

  finalList = []
  for key, val in csynapses.items():
    if('classified' in val.keys()):
      available = []
      toAdd = {key:available}
      for aKey, aVal in val['classified'].items():
        available.append({'datasetName':aKey,'mongoId':str(aVal)})
      finalList.append(toAdd)
  return json.dumps(finalList)

# Gets classified data for the given mongoId
# @params mongoId=mongoId of classifiedData
@get('/getClassified')
def getClassified():
  mongoId = request.params.get('mongoId')
  fs = db.files
  theData = fs.get(ObjectId(mongoId)).read()
  return theData
 
# Returns the datapoints if they have already been calc'd and saved
# otherwise queues them up to be saved
# @params user=userName, name=csynapseName
# @returns {'1':{label:[listOf 1 d points],otherLabel:[]...}, '2':{label:[list of 2 d points]}}}
@get('/getPoints')
def getPoints():
  userName = getUsername()
  csynapseName = request.params.get('name')

  # get dataset Id
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})

  # see if data points already exist
  if('points' in doc['csynapses'][csynapseName].keys()):
    ids = doc['csynapses'][csynapseName]['points']
    finalList = []
    for key, val in ids.items():
      mdb = getMongoDB().csynapse_files
      fs = gridfs.GridFS(mdb)
      theData = fs.get(ObjectId(val)).read()
      finalList.append({key:theData})
    return json.dumps(finalList)
  else: # process the dataset and save the points
    mongoId = str(doc['csynapses'][csynapseName]['data_id'])
    taskGetPoints(userName, csynapseName, mongoId)
    return HTTPResponse(status=200)

@post('/login')
def postLogin():
  username = request.params.get('username')
  password = request.params.get('password')
  if username == "" or username == None:
    abort(401, "Username is Required")
  if password == "" or password == None:
    abort(401, "Password is Required")
  session = getBeakerSession()
  if not 'logged_in' in session or session['logged_in'] == False:
    users = db.userAuth
    user = users.find_one({"username":username})
    if user != None:
      db_pass = user['password']
      salt = base64.b64decode(user['salt'])
      check_pass = base64.b64encode(hashlib.pbkdf2_hmac('sha256', password, salt, 200000))
      if check_pass == db_pass:
        session['logged_in'] = True
        session['username'] = username
        return "logged in {}".format(username)
      else:
        abort(401, "Username/Password Combination was not valid - Type 1")
    else:
      abort(401, "Username/Password Combination was not valid - Type 2")
  else:
    return "Already Logged In"
    
@post('/register')
def postRegister():
  username = request.params.get('username')
  password = request.params.get('password')
  if username == "" or username == None:
    abort(401, "Username is Required")
  if password == "" or password == None:
    abort(401, "Password is Required")
  usersAuth = db.userAuth
  if usersAuth.find_one({"username":username}) == None:
    salt = os.urandom(16)
    user_obj = {}
    user_obj['username'] = username
    user_obj['_id'] = username
    user_obj['password'] = base64.b64encode(hashlib.pbkdf2_hmac('sha256', password, salt, 200000))
    user_obj['salt'] = base64.b64encode(salt)
    usersAuth.insert_one(user_obj)
    users = db.users
    users.insert_one({"_id":username})
    return "registered {}".format(username)
  else:
    abort(401, "Username already exists")

@get('/getUsername')
def getUsername():
  session = getBeakerSession()
  if "username" in session:
    return session['username']
  else:
    abort(401, "Not Logged In")

@route('/logout')
def postLogout():
  session = getBeakerSession()
  session.delete()
  return "logged out"

if __name__ == '__main__':
  run(host='', port=8888, debug=True, reloader=True, app=app)
