#!/usr/bin/python

from bottle import *
# from tasks import runAlgorithm
import json
from pymongo import MongoClient
import gridfs
from beaker.middleware import SessionMiddleware
import hashlib
import os
import base64

#prefix = "/app"
prefix = ""

session_opts = {
    'beaker.session.type': 'ext:memcached',
    'session.url': 'memcached:11211',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}

app = SessionMiddleware(app(), session_opts)
mongoPort = 27017

def getDB():
  db = MySQLdb.connect("db","csynapse","MyMZhdiEvY33WbqqAsFnLkcoQqRbacxo", "csynapse")
  return db

def getMongoDB():
  mdb = pymongo.MongoClient('mongo', mongoPort)
  return mdb

def getBeakerSession():
  s = request.environ.get('beaker.session')
  return s

def getDescription(identifier):
  db = getDB()
  cursor = db.cursor()
  select_sql = "SELECT description FROM RequestInformation WHERE identifier='%s'" % (identifier)
  cursor.execute(select_sql)
  result = cursor.fetchone()
  if result != None:
    return result[0]
  else:
    return ""

@get('/healthcheck')
def healthCheck():
	return json.dumps({200:'ok'})

# Get list of available algorithms from db 
@get('/algorithms')
def getAlgorithms():
  algoCollection = getMongoDB().csynapse.algorithms
  algos = algoCollection.find()
  return json.dumps([d for d in algos])

# Get list of all csynapses owned by a user
# params user=UserName
@get('/csynapses')
def getCsynapses():
  userName = request.params.get('user')
  userCollection = getMongoDB().csynapse.users

  doc = userCollection.find_one({'_id':userName})

  return json.dumps({'csynapses':doc['csynapses'].keys()})

# Creates a new csynapse for the user
# @params (body or query) user=userName, name=csynapseName to create
@post('/create')
def createCsynapse():
  # get username and csynapse
  userName = request.params.get('user')
  csynapseName = request.params.get('name')
  userCollection = getMongoDB().csynapse.users

  ret = ''
  # update only if the csynapse doesn't already exist
  r = userCollection.update_one({'_id':userName,'csynapses.{0}'.format(csynapseName):{'$exists':False}}, \
  {'$set':{'csynapses.{0}'.format(csynapseName):{}}})
  
  if(r.matched_count == 1):
    ret = {'status':200,'body':'ok'}
  else:
    ret = {'status':422,'body':'csynapse already exists'}

  return HTTPResponse(status=ret['status'], body=json.dumps({'message':ret['body']}))

# Saves data associated with a cynapse
# @params user=userName, name=csynapseName, dataName=dataset name
@post('/data')
def saveData():
  userName = request.params.get('user')
  csynapseName = request.params.get('name')
  upload = request.files.get('upload')

  # TODO Check if cynapse name and dataset Name already exists
  # return failed status if so

  # Save file in grid fs
  mdb = getMongoDB().csynapse_files
  fs = gridfs.GridFS(mdb)
  datasetId = fs.put(upload.file)

  # store dataset name and mon
  userCollection = getMongoDB().csynapse.users
  userCollection.update_one({'_id':userName}, \
    {'$set':{'csynapses.{0}.data_id'.format(csynapseName):datasetId}})

  return HTTPResponse(status=200)


# Begins obtaining the cross-validation score on an algorithm
# @params (body or query) user=userName, name=csynapseName to create,
# algorithms=list of algorithms to cross validate
@post('/test')
def testAlgorithm():
  userName = request.params.get('user')
  csynapseName = request.params.get('name')
  algos = request.params.getall('algorithms')
  # Get dataId
  userCollection = getMongoDB().csynapse.users

  doc = userCollection.find_one({'_id':userName})

  dataId = doc['csynapses'][csynapseName]['data_id']

  print(dataId)
  print(algos)
  # pass dataId and algorithms to task
  runAlgoTest(dataId, algos)
  # return 200
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
    mdb = getMongoDB().csynapse
    users = mdb.csynapse_users
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
        abort(401, "Username/Password Combination was not valid")
    else:
      abort(401, "Username/Password Combination was not valid")
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
  mdb = getMongoDB().csynpase
  users = mdb.csynapse_users
  if users.find_one({"username":username}) == None:
    salt = os.urandom(16)
    user_obj = {}
    user_obj['username'] = username
    user_obj['password'] = base64.b64encode(hashlib.pbkdf2_hmac('sha256', password, salt, 200000))
    user_obj['salt'] = base64.b64encode(salt)
    users.insert_one(user_obj)
    return "registered {}".format(username)
  else:
    abort(400, "Username already exists")

@post('/logout')
def postLogout():
  session = getBeakerSession()
  session.delete()
  return "logged out"

# Trains algorithm(s) on given dataset name and then saves the data
# @params user=userName, name=csynapse, algos=list of algorithm names

# Fetches all the cross validation information for the csynapse
# @params (query) user=userName, name=csynapseName
@get('/testResults')
def getTestResults():
  pass

# Trains then saves the given algorithm(s) in their trained state.
# Params in JSON Body
# {csynapseID:[{algoName:algoName,score:score}, ...]}
# 
@post('/save')
def saveAlgo():
  pass

# @get('/active_algorithms')
# def getActiveAlgorithms():
#   db = getDB()
#   cursor = db.cursor()
#   select_sql = "SELECT identifier, description FROM Algorithms WHERE active = 1"
#   cursor.execute(select_sql)
#   ret = ""
#   ret_list = []
#   results = cursor.fetchall()
#   for result in results:
#     res = {}
#     res["identifier"] = result[0]
#     res["description"] = result[1]
#     ret_list.append(res)
#   return json.dumps(ret_list)

@route("/")
def index():
  links = """
  <a href=\""""+prefix+"""/all?human_readable=1">All Available Requests</a><br />
  <a href=\""""+prefix+"""/new">Submit new Request</a><br />
  """
  return links

@get('/new')
def getNew():
  
  algorithms = json.loads(getActiveAlgorithms())
  algorithms_text = ""
  for algorithm in algorithms:
    algorithms_text += "<input type=\"checkbox\" name=\"algorithm\" value=\"%s\" /> %s<br />\n" % (algorithm["identifier"], algorithm["description"])
  
  ret = """
  <form action="new" method="POST" enctype="multipart/form-data">
  description <input type="text" name="description" /><br />
  Algorithms: <br />"""+algorithms_text+"""
  Test File: <input type="file" name="upload" /><br />
  <input type="hidden" name="redirect" value=\""""+prefix+"""/check" />
  <input type="submit" value="Submit">
  
  </form>
  
  """
  return ret


@post('/new')
def postNew():
  db = getDB()
  cursor = db.cursor()
  cursor.execute("SELECT MD5(UUID())")
  data = cursor.fetchone()
  #cursor.execute("use csynapse")
  newID = data[0]
  upload = request.files.get('upload')
  mdb = pymongo.MongoClient('mongo', 27017).csynapse_files
  fs = gridfs.GridFS(mdb)
  #print dir(upload)
  mongo_id = fs.put(upload.file)
  #savePath = "/var/csynapse/uploads/%s.csv" % (newID)
  #upload.save(savePath)
  # Get data points from training data
  runAlgorithm.delay(newID, 'graphData')
  # Put this into data base
  insertSQL = "INSERT INTO Requests (identifier, algorithm) VALUES (\"%s\", \"%s\")" % (newID, 'graphData')
  cursor.execute(insertSQL)

  for algorithm in request.params.getall('algorithm'):
    insertSQL = "INSERT INTO Requests (identifier, algorithm) VALUES (\"%s\", \"%s\")" % (newID, algorithm)
    #print insertSQL
    cursor.execute(insertSQL)
    runAlgorithm.delay(newID, algorithm)
  description = request.params.get('description')
  #print mongo_id
  insertSQL = "INSERT INTO RequestInformation (identifier, description, mongo_id) VALUES ('%s', '%s', '%s')" % (newID, description, mongo_id)
  cursor.execute(insertSQL)
  db.commit()
  db.close()
  if request.params.get("redirect") != None and request.params.get("redirect") != "":
    redirect(request.params.get("redirect")+"?id=%s" %(newID))
  else:
    return "New ID: <a href=\""+prefix+"/check?id=%s\">%s</a>" % (newID, newID)

# @route('/check')
# def check():
#   db = getDB()
#   cursor = db.cursor()
#   ret = ""
#   for check_id in request.params.getall('id'):
#     select_sql = "SELECT identifier, algorithm, complete, return_object FROM Requests WHERE identifier=\"%s\"" % (check_id)
#     cursor.execute(select_sql)
#     results = cursor.fetchall()
#     human_readable = request.params.get('human_readable')
#     if human_readable == "1":
#       for result in results:
#         ret += "ID: %s, Algorithm %s, Return Object: %s, Status: " % (result[0], result[1], result[3])
#         if result[2]==1:
#           ret += "Complete"
#         else:
#           ret += "Not Complete"
#         ret += "<br />\n"
#     else:
#       retlist = []
#       for result in results:
#         result_obj = {}
#         result_obj["id"] = result[0]
#         result_obj["algorithm"] = result[1]
#         result_obj["status"] = result[2]
#         result_obj["return_object"] = result[3]
#         result_obj["description"] = getDescription(result_obj["id"])
#         retlist.append(result_obj)
#       ret = json.dumps(retlist)
#   return ret

# @get('/all')
# def getAll():
#   db = getDB()
#   cursor = db.cursor()
#   select_sql = "SELECT DISTINCT(identifier) FROM Requests"
#   cursor.execute(select_sql)
#   ret = ""
#   results = cursor.fetchall()
#   if request.params.get('human_readable') == "1":
#     for result in results:
#       ret += "<a href=\""+prefix+"/check?id=%s\">%s</a><br />" % (result[0], result[0])
#   else:
#     res = []
#     for result in results:
#       #print result[0]
#       res.append(result[0])
#     ret_obj = {}
#     ret_obj["ids"] = res
#     ret = json.dumps(ret_obj)
#   return ret


if __name__ == '__main__':
  run(host='', port=8888, debug=True, reloader=True, app=app)
