#!/usr/bin/python

from bottle import *
import MySQLdb
from tasks import runAlgorithm
import json

def getDB():
  db = MySQLdb.connect("localhost","csynapse","MyMZhdiEvY33WbqqAsFnLkcoQqRbacxo", "csynapse")
  return db

def getDescription(identifier):
  db = getDB()
  cursor = db.cursor()
  select_sql = "SELECT description FROM RequestDescription WHERE identifier='%s'" % (identifier)
  cursor.execute(select_sql)
  result = cursor.fetchone()
  if result != None:
    return result[0]
  else:
    return ""

@get('/algorithms')
def getAlgorithms():
  db = getDB()
  cursor = db.cursor()
  select_sql = "SELECT identifier, description FROM Algorithms"
  cursor.execute(select_sql)
  ret = ""
  ret_list = []
  results = cursor.fetchall()
  for result in results:
    res = {}
    res["identifier"] = result[0]
    res["description"] = result[1]
    ret_list.append(res)
  return json.dumps(ret_list)

@get('/active_algorithms')
def getActiveAlgorithms():
  db = getDB()
  cursor = db.cursor()
  select_sql = "SELECT identifier, description FROM Algorithms WHERE active = 1"
  cursor.execute(select_sql)
  ret = ""
  ret_list = []
  results = cursor.fetchall()
  for result in results:
    res = {}
    res["identifier"] = result[0]
    res["description"] = result[1]
    ret_list.append(res)
  return json.dumps(ret_list)


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
  <input type="hidden" name="redirect" value="/app/check" />
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
  for algorithm in request.params.getall('algorithm'):
    insertSQL = "INSERT INTO Requests (identifier, algorithm) VALUES (\"%s\", \"%s\")" % (newID, algorithm)
    print insertSQL
    cursor.execute(insertSQL)
  description = request.params.get('description')
  insertSQL = "INSERT INTO RequestDescription (identifier, description) VALUES ('%s', '%s')" % (newID, description)
  cursor.execute(insertSQL)
  db.commit()
  upload = request.files.get('upload')
  savePath = "/var/csynapse/uploads/%s.csv" % (newID)
  upload.save(savePath)
  db.close()
  runAlgorithm.delay(newID, algorithm)
  if request.params.get("redirect") != None and request.params.get("redirect") != "":
    redirect(request.params.get("redirect")+"?id=%s" %(newID))
  else:
    return "New ID: <a href=\"/app/check?id=%s\">%s</a>" % (newID, newID)

@route('/check')
def check():
  db = getDB()
  cursor = db.cursor()
  ret = ""
  for check_id in request.params.getall('id'):
    select_sql = "SELECT identifier, algorithm, complete, return_object FROM Requests WHERE identifier=\"%s\"" % (check_id)
    cursor.execute(select_sql)
    results = cursor.fetchall()
    human_readable = request.params.get('human_readable')
    if human_readable == "1":
      for result in results:
        ret += "ID: %s, Algorithm %s, Return Object: %s, Status: " % (result[0], result[1], result[3])
        if result[2]==1:
          ret += "Complete"
        else:
          ret += "Not Complete"
        ret += "<br />\n"
    else:
      retlist = []
      for result in results:
        result_obj = {}
        result_obj["id"] = result[0]
        result_obj["algorithm"] = result[1]
        result_obj["status"] = result[2]
        result_obj["return_object"] = result[3]
        result_obj["description"] = getDescription(result_obj["id"])
        retlist.append(result_obj)
      ret = json.dumps(retlist)
  return ret

@get('/all')
def getAll():
  db = getDB()
  cursor = db.cursor()
  select_sql = "SELECT DISTINCT(identifier) FROM Requests"
  cursor.execute(select_sql)
  ret = ""
  results = cursor.fetchall()
  if request.params.get('human_readable') == "1":
    for result in results:
      ret += "<a href=\"/app/check?id=%s\">%s</a><br />" % (result[0], result[0])
  else:
    res = []
    for result in results:
      print result[0]
      res.append(result[0])
    ret_obj = {}
    ret_obj["ids"] = res
    ret = json.dumps(ret_obj)
  return ret

@route("/")
def index():
  links = """
  <a href="/app/all?human_readable=1">All Available Requests</a><br />
  <a href="/app/new">Submit new Request</a><br />
  """
  return links

run(host='', port=8888, debug=True, reloader=True)