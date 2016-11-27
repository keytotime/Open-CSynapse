#!/usr/bin/python

from bottle import *
from Demo import classifyForDemo
from MachineLearning.BuildClassifier import getDiscreetClassifier
from MachineLearning.ParseImage import vectorizeToAdd
from MachineLearning.Constants import Constants
from MachineLearning.ParseImage import getPixels
from tasks import runAlgoTest, classify, taskGetPoints, regression, process_photos, classifyImages, taskGetRegressionPoints
import json
from database import db
from beaker.middleware import SessionMiddleware
import hashlib
import os
import base64
from bson.objectid import ObjectId
import zipfile
import uuid
from os import listdir
from os.path import isfile, isdir, join
from PIL import Image
from tempfile import TemporaryFile

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

def check_request_for_params(params, fail_status=400):
  for param in params:
    param_obj = request.params.getall(param)
    if param_obj == [] or param_obj == None:
      raise HTTPResponse(status=fail_status, body=json.dumps({"status":"error",'error':'param {} is required but not provided'.format(param), "error_type":"missing_param", "missing_param":param}))

def check_request_for_files(files, fail_status=400):
  for file in files:
    files_obj = request.files.getall(file)
    if files_obj == [] or files_obj == None:
      raise HTTPResponse(status=fail_status, body=json.dumps({"status":"error",'error':'file param {} is required but not provided'.format(file), "error_type":"missing_param", "missing_param":file}))

def re_space(param):
  if param is not None:
    return param.replace("%20", " ")

@get('/healthcheck')
def healthCheck():
	return HTTPResponse(status=200, body=json.dumps({"status":'ok'}))

# Get list of available algorithms from db 
@get('/algorithms')
def getAlgorithms():
  algoCollection = db.algorithms
  algos = algoCollection.find_one({'_id':'algorithms'})
  algorithms = [{'algoId':x,'description':algos[x][u'description'], \
    'name':algos[x][u'name'],'type':algos[x][u'type'], 'paramInfo':algos[x][u'paramInfo']} for x in algos if(x != u'_id')]
  return HTTPResponse(status=200, body=json.dumps({"status":"ok", "algorithms":algorithms}))

# Get list of all csynapses owned by a user
# params user=UserName
@get('/csynapses')
def getCsynapses():
  userName = getUsername()
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})
  if(doc is not None and 'csynapses' in doc):
    return HTTPResponse(status=200, body=json.dumps({"status":"ok",'csynapses':doc['csynapses'].keys()}))
  else:
    return HTTPResponse(status=200, body=json.dumps({"status":"ok",'csynapses':[]}))

# Creates a new csynapse for the user
# @params (body or query) user=userName, name=csynapseName to create
@post('/create')
def createCsynapse():
  # get username and csynapse
  userName = getUsername()
  check_request_for_params(["name"])
  csynapseName = re_space(request.params.get('name'))
  userCollection = db.users

  ret = ''
  # update only if the csynapse doesn't already exist
  r = userCollection.update_one({'_id':userName,'csynapses.{0}'.format(csynapseName):{'$exists':False}}, \
  {'$set':{'csynapses.{0}'.format(csynapseName):{}}})
  
  if(r.matched_count == 1):
    return HTTPResponse(status=200, body=json.dumps({"status":"ok"}))
  else:
    if (r.matched_count == 0):
      return HTTPResponse(status=422, body=json.dumps({"status":"error","error":'csynapse was not created'}))
    else:
      return HTTPResponse(status=422, body=json.dumps({"status":"error","error":"csynapse already exists"}))

# Saves data associated with a cynapse
# @params user=userName, name=csynapseName, dataName=dataset name,
# image=true flag indicating image data
@post('/data')
def saveData():
  userName = getUsername()
  check_request_for_params(["name"])
  check_request_for_files(["upload"])

  csynapseName = re_space(request.params.get('name'))
  if "zipped" in request.POST and (request.params.get("zipped") in ["true", "True", "TRUE"]):
    zipped = True
  else:
    zipped = False

  forDemo = request.params.get('forDemo')
 
  # Check if csynapse already has data
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})
  if(doc is not None and 'csynapses' in doc):
    if csynapseName not in doc['csynapses'].keys():
      return HTTPResponse(status=422, body=json.dumps({"status":"error","error":'csynapse {} does not exist'.format(csynapseName)}))
  if(doc is not None and doc['csynapses'] is not None):
    if(csynapseName in doc['csynapses'].keys() and 'data_id' in doc['csynapses'][csynapseName].keys()):
      return HTTPResponse(status=422, body=json.dumps({"status": "error","error":"csynapse already has data"}))
  
  # check to see if we have image data
  uploads = request.files.getall('upload')
  
  fs = db.files
  files_list = []
  tag_map = {}
  datasetId = ''
  for upload in uploads:
    if zipped == False:
      datasetId = fs.put(upload.file.read().replace('\r\n','\n'))
      files_list.append(datasetId)
    else:
      try:
        unique_tmp_file = uuid.uuid4()
        unique_tmp_folder = uuid.uuid4()
        unique_extract_folder = uuid.uuid4()
        #http://stackoverflow.com/questions/15050064/how-to-upload-and-save-a-file-using-bottle-framework
        save_path = "/tmp/{}".format(unique_tmp_folder)
        if not os.path.exists(save_path):
          os.makedirs(save_path)
        file_path = "{path}/{file}.zip".format(path=save_path, file=unique_tmp_file)#upload.filename)
        upload.save(file_path)
        extract_path = "/tmp/{}".format(unique_extract_folder)
        zip_ref = zipfile.ZipFile(file_path, "r")
        zip_ref.extractall(extract_path)
        zip_ref.close()
        #http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
        tags = [f for f in listdir(extract_path) if isdir(join(extract_path, f))]
        if "__MACOSX" in tags:
          tags.remove("__MACOSX")
        if len(tags) == 1:
          extract_path = extract_path+"/"+tags[0]
          tags = [f for f in listdir(extract_path) if isdir(join(extract_path, f))]
        for tag in tags:
          tag_map[tag] = []
          tag_folder = "{}/{}".format(extract_path, tag)
          unzipped_files = [f for f in listdir(tag_folder) if isfile(join(tag_folder, f))]
          for ufile in unzipped_files:
            f = open("{}/{}".format(tag_folder, ufile), "r")
            datasetId = fs.put(f)
            f.close()
            files_list.append(datasetId)
            tag_map[tag].append(datasetId)
      except (zipfile.BadZipFile, zipfile.LargeZipFile), e:
        return HTTPResponse(status=422, body=json.dumps({"status":"error", "error":"zip file is not valid"}))
  # store dataset name and mon
  if zipped == False:
    userCollection.update_one({'_id':userName}, \
    {'$set':{'csynapses.{0}.data_id'.format(csynapseName):files_list[0]}})
    # queue up regression tasks
    regression.delay(userName, csynapseName, datasetId)
    # queue up regression points task
    taskGetRegressionPoints.delay(userName, csynapseName, files_list[0])
    # queue up points task
    taskGetPoints.delay(userName, csynapseName, files_list[0])
    
  elif len(files_list) > 1 or zipped:
    userCollection.update_one({'_id':userName}, \
    {'$set':{'csynapses.{0}.multipart_data'.format(csynapseName):files_list}})
    userCollection.update_one({'_id':userName}, \
    {'$set':{'csynapses.{0}.multipart_data_tagmap'.format(csynapseName):tag_map}})
    
    process_photos.delay(userName, csynapseName, forDemo)

  return HTTPResponse(status=200, body=json.dumps({"status":"ok", "message":"data added successfully"}))

@get('/getData')
def getData():
  check_request_for_params(["name"])
  userName = getUsername()
  csynapseName = re_space(request.params.get('name'))
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})
  if(doc is not None and 'csynapses' in doc):
    if csynapseName not in doc['csynapses'].keys():
      return HTTPResponse(status=422, body=json.dumps({"status":"error","error":'csynapse {} does not exist'.format(csynapseName)}))
  if(doc is not None and doc['csynapses'] is not None):
    if(csynapseName in doc['csynapses'].keys() and 'data_id' not in doc['csynapses'][csynapseName].keys()):
      return HTTPResponse(status=422, body=json.dumps({"status": "error","error":"csynapse has no data"}))

  mongoId = doc['csynapses'][csynapseName]['data_id']
  fs = db.files
  theData = fs.get(ObjectId(mongoId)).read()
  return HTTPResponse(status=200, body=json.dumps({"status":"ok","data":theData}))

# Begins obtaining the cross-validation score on an algorithm
# @params (body or query) user=userName, name=csynapseName,
# algorithms=list of algorithms to cross validate
@post('/test')
def testAlgorithm():
  userName = getUsername()
  check_request_for_params(["name", "algorithm"])
  csynapseName = re_space(request.params.get('name'))
  algos = request.params.getall('algorithm')
  failedAlgos = []
  successAlgos = []
  for j in algos:
    # Try and load the algorithm and return errors with information about the algorithms that failed
    algoData = ''
    try:
      algoData = json.loads(j)
      successAlgos.append(algoData)
    except Exception as e:
      failedAlgos.append({'error':'json data {0} is invalid'.format(j),\
      "error_type":"invalid_json", "exception_message":str(e)})
      continue
    try:
      if('params' in algoData):
        paramsData = algoData['params']
        for key, val in paramsData.iteritems():
          try:
            if(key == u'n_estimators'):
              paramsData[key] = int(val)
            else:
              paramsData[key] = float(val)
          except Exception:
            continue
        getDiscreetClassifier(algoData['algorithm'], algoData['params'])
    except Exception as e:
      failedAlgos.append({'error':'algo params {0} is invalid'.format(j),\
      "error_type":"invalid_params", "exception_message":str(e)})
    runAlgoTest.delay(algoData, userName, csynapseName)
    
  if(len(failedAlgos) > 0):
    raise HTTPResponse(status=500, body=json.dumps({"status":"error",'failedAlgorithms':failedAlgos,\
      "error_type":"failedAlgorithms"}))
  else:
    return HTTPResponse(status=200, body=json.dumps({"status":"ok","message":"submitted for testing", "csynapse":csynapseName, "algorithms":successAlgos}))

# Gets the test results for all the algos run on the given csynapse
# @params (body or query) user=userName, name=csynapseName
# @returns {results:{algoId:svm,description:SVM classifier, score:score, time:time}}
@get('/testResults')
def getTestResults():
  userName = getUsername()
  check_request_for_params(["name"])
  csynapseName = re_space(request.params.get('name'))

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
        val['name'] = algorithms[x]['name']
        val['id'] = key
  return HTTPResponse(status=200, body=json.dumps({"status":"ok","name":csynapseName, "testResults":[x for x in algos.itervalues()]}))

  
# Runs algorithms on new data
#params (body or query) user=userName, name=csynapseName
#upload:fileOfNewData
@post('/run')
def runAlgos():
  userName = getUsername()
  check_request_for_params(["name", "dataName", "algorithm"])
  check_request_for_files(["upload"])
  csynapseName = re_space(request.params.get('name'))
  dataName = re_space(request.params.get('dataName'))
  algo = request.params.get('algorithm')
  upload = request.files.get('upload')

  fs = db.files
  # get mongoId of old data
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})
  oldDataId = doc['csynapses'][csynapseName]['data_id']
  # get algo type
  algoType = doc['csynapses'][csynapseName]['algorithms'][algo]['algoId']
  params = doc['csynapses'][csynapseName]['algorithms'][algo]['params']
  # save new data
  if "zipped" in request.POST and (request.params.get("zipped") in ["true", "True", "TRUE"]):
    unique_tmp_file = uuid.uuid4()
    unique_tmp_folder = uuid.uuid4()
    #http://stackoverflow.com/questions/15050064/how-to-upload-and-save-a-file-using-bottle-framework
    save_path = "/tmp/{}".format(unique_tmp_file)
    if not os.path.exists(save_path):
      os.makedirs(save_path)
    
    file_path = "{path}/{file}".format(path=save_path, file=upload.filename)
    upload.save(file_path)
    tmp_path = "/tmp/{}".format(unique_tmp_folder)
    zip_ref = zipfile.ZipFile(file_path, "r")
    zip_ref.extractall(tmp_path)
    zip_ref.close()
    #http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
    zipDir = [f for f in listdir(tmp_path) if isdir(join(tmp_path, f))][0]
    # get list of file paths
    zipDirPath = '{0}/{1}'.format(tmp_path,zipDir)
    filepaths = [f for f in listdir(zipDirPath)]
    filenamesAndIds = []
    for x in filepaths:
      filename = '{0}/{1}'.format(zipDirPath,x)
      with open(filename,'r') as f:
        dataId = fs.put(f)
        filenamesAndIds.append((x,dataId))

    # get list of data ids
    classifyImages.delay(filenamesAndIds, oldDataId, algoType, params, userName, csynapseName, dataName)
  else:
    newDatasetId = fs.put(upload.file)
    classify.delay(newDatasetId, oldDataId, algoType, params, userName, csynapseName, dataName)

  return HTTPResponse(status=200, body=json.dumps({"status":"ok"}))

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
  return HTTPResponse(status=200, body=json.dumps({"status":"ok","all_classified":finalList}))

# Gets classified data for the given mongoId
# @params mongoId=mongoId of classifiedData
@get('/getClassified')
def getClassified():
  check_request_for_params(["mongoId"])
  mongoId = request.params.get('mongoId')
  fs = db.files
  theData = fs.get(ObjectId(mongoId)).read()
  return HTTPResponse(status=200, body=json.dumps({"status":"ok","classified_data":theData}))
 
# Gets regression data for a csynapse
# @params name=csynapseName
@get('/regressionData')
def getRegressionData():
  userName = getUsername()
  check_request_for_params(['name'])
  csynapseName = re_space(request.params.get('name'))
  limit = request.params.get('limit')
  pValue = re_space(request.params.get('p'))
  # Get data Id
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})
  try:
    dataId = doc['csynapses'][csynapseName]['regression']
    regData = json.loads(db.files.get(ObjectId(dataId)).read())
    if(pValue is not None):
      regData = [x for x in regData if(x['p'] <= float(pValue) and x['r'] > .8)]
    regData.sort(key=lambda obj:obj['rSquared'], reverse=True)
    if(limit is not None):
      regData = regData[:int(limit)]
    return json.dumps({'status':'ok', 'regressionData':regData})
  except Exception as e:
    return HTTPResponse(status=500, body=json.dumps({"status":"error","message":"no regression data available"}))

# Returns the datapoints if they have already been calc'd and saved
# @params name=csynapseName
# @returns {'1':{label:[listOf 1 d points],otherLabel:[]...}, '2':{label:[list of 2 d points]}}}
@get('/getPoints')
def getPoints():
  userName = getUsername()
  check_request_for_params(["name"])
  csynapseName = re_space(request.params.get('name'))

  # get dataset Id
  userCollection = db.users
  doc = userCollection.find_one({'_id':userName})

  # see if data points already exist
  if('points' in doc['csynapses'][csynapseName].keys()):
    final = {}
    ids = doc['csynapses'][csynapseName]['points']
    ret = {}
    final['status'] = 'ok'
    for key, val in ids.items():
      theData = json.loads(db.files.get(ObjectId(val)).read())
      ret[key] = theData
    final['points'] = ret
    if('headerPoints' in doc['csynapses'][csynapseName].keys()):
      headerInfo = doc['csynapses'][csynapseName]['headerPoints']
      final['headerPoints'] = headerInfo['headerPoints']
      final['labels'] = headerInfo['labels']
    return HTTPResponse(status=200, body=json.dumps(final))
  else: # inform the user the points are being generated
    return HTTPResponse(status=200, body=json.dumps({"status":"ok","message":"points are being generated"}))

# Logs in the user, returning a session cookie with the relevant information
# @params username, password
# returns a cookie as well as a status 
@post('/login')
def postLogin():
  check_request_for_params(["username", "password"], fail_status=401)
  username = re_space(request.params.get('username'))
  password = re_space(request.params.get('password'))
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
        return HTTPResponse(status=200, body=json.dumps({"status":"ok","message":"logged in {}".format(username)}))
      else:
        return HTTPResponse(status=401, body=json.dumps({"status":"error","error":"Username/Password Combination was not valid - Type 1"}))
    else:
      return HTTPResponse(status=401, body=json.dumps({"status":"error","error":"Username/Password Combination was not valid - Type 2"}))
  else:
    return HTTPResponse(status=400, body=json.dumps({"status":"error","error":"Already Logged In"}))
    
# registers a user
# @params username, password
@post('/register')
def postRegister():
  check_request_for_params(["username", "password"], fail_status=401)
  username = re_space(request.params.get('username'))
  password = re_space(request.params.get('password'))
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
    return HTTPResponse(status=200, body=json.dumps({"status":"ok", "registered":username}))
  else:
    raise HTTPResponse(status=401, body=json.dumps({"status":"error","error":"Username already exists"}))

def getUsername():
  session = getBeakerSession()
  if "username" in session:
    return session['username']
  else:
    raise HTTPResponse(status=401, body=json.dumps({"status":"error","error":"not logged in"}))

@get('/getUsername')
def getHTTPUsername():
  username = getUsername()
  if username != None:
    return HTTPResponse(status=200, body=json.dumps({"status":"ok","username":username}))
  else:
    raise HTTPResponse(status=401, body=json.dumps({"status":"error","error":"not logged in"}))

@route('/logout')
def postLogout():
  session = getBeakerSession()
  session.delete()
  return HTTPResponse(status=200, body=json.dumps({"status":"ok","message":"logged out"}))

@post('/demoDataAdd')
def addDemoData():
  dataFiles = request.files.getall('upload')
  label = request.params.get('label')
  name = request.params.get('name')
  doc = db.custom.find_one({'name':name})
  if(dataFiles is None or label is None or name is None):
    raise HTTPResponse(status=500, body=json.dumps({"status":"error","error":"check params need:upload,label,name"}))

  # Convert each image into data
  toAdd = vectorizeToAdd([x.file for x in dataFiles], label)

  if(doc is None):
    newMongoId = db.files.put(toAdd)
    db.custom.insert({'name':name, 'trainingData':newMongoId})
  elif('trainingData' not in doc):
    newMongoId = db.files.put(toAdd)
    db.custom.update_one({'name':name},
    {'$set':{'trainingData':newMongoId}})
  else:
    oldMongoId = doc['trainingData']
    # Get the file
    oldFile = db.files.get(ObjectId(oldMongoId))
    # add the data
    newMongoId = db.files.put(oldFile.read() + '\n' + toAdd)
    # remove the old file
    db.files.delete(oldMongoId)
    # update the doc with the new file
    db.custom.update_one({'name':name},
      {'$set':{'trainingData':newMongoId}})
  # get the data, add the new row(s) to it, save the data
  res = HTTPResponse(status=200, body=json.dumps({"status":"ok","message":"added data","datasetId":str(newMongoId)}))

  res.set_header('Access-Control-Allow-Origin', '*')

  return res

@post('/demoDataToClassify')
def demoClassifyImage():
  dataFiles = request.files.getall('upload')
  name = request.params.get('name')
  doc = db.custom.find_one({'name':name})

  newMongoIds = []
  # Convert each file to jpg and save them into mongo
  for x in dataFiles:
    with TemporaryFile() as f:
      img = Image.open(x.file).convert('RGB').resize((Constants.DEMO_SIZE,Constants.DEMO_SIZE))
      img.save(f, 'JPEG')
      f.flush()
      f.seek(0)
      newMongoIds.append(db.files.put(f.read()))

  # If to classify doesn't exist add it, otherwise update it
  doc = db.custom.find_one({'name':name})

  if(doc is not None):
    if('toClassify' in doc):
      newMongoIds.extend(doc['toClassify'])

  # Create new list
  db.custom.update_one({'name':name},
    {'$set':{'toClassify':newMongoIds}})

  res = HTTPResponse(status=200, body=json.dumps({"status":"ok","message":"added pictures"}))
  res.set_header('Access-Control-Allow-Origin', '*')

  return res

@get('/demoImagesToClassify')
def getImages():
  name = request.params.get('name')
  index = int(request.params.get('index'))
  doc = db.custom.find_one({'name':name})

  imageList = doc['toClassify']

  nextIndex = index + 1
  if(nextIndex >= len(imageList)):
    nextIndex = 'none'

  imageData = db.files.get(imageList[index]).read()
  
  res = HTTPResponse(body=imageData,status=200)
  res.set_header('content_type', 'image/jpeg')
  res.set_header('Access-Control-Allow-Origin', '*')
  return res

@get('/demoNumberToClassify')
def getNumber():
  name = request.params.get('name')
  doc = db.custom.find_one({'name':name})

  imageListLen = len(doc['toClassify'])
  res = HTTPResponse(status=200, body=json.dumps({"status":"ok","number":imageListLen}))
  res.set_header('Access-Control-Allow-Origin', '*')
  return res

@get('/demoClassifyImage')
def demoClassify():
  name = request.params.get('name')
  i = int(request.params.get('index'))
  doc = db.custom.find_one({'name':name})

  result = classifyForDemo(db.files.get(doc['trainingData']),db.files.get(doc['toClassify'][i]))

  res = HTTPResponse(status=200, body=json.dumps({"status":"ok","result":result}))
  res.set_header('Access-Control-Allow-Origin', '*')
  return res

if __name__ == '__main__':
  run(host='', port=8888, debug=True, reloader=True, app=app)
