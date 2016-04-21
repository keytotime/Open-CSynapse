#!/usr/bin/python

from bottle import *
import MySQLdb

def getDB():
  db = MySQLdb.connect("localhost","csynapse","MyMZhdiEvY33WbqqAsFnLkcoQqRbacxo", "csynapse")
  return db

@get('/test')
def getTest():
  ret = """
  <form action="test" method="POST" enctype="multipart/form-data">
  description <input type="text" name="description" /><br />
  Algorithms: <input type="checkbox" name="algorithm" value="TEST" />TEST<br />
  Test File: <input type="file" name="upload" /><br />
  <input type="submit" value="Submit">
  </form>
  
  """
  return ret

@post('/test')
def postTest():
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
  db.commit()
  upload = request.files.get('upload')
  savePath = "/var/csynapse/uploads/%s.csv" % (newID)
  upload.save(savePath)
  db.close()
  return "New ID: <a href=\"/app/check?id=%s\">%s</a>" % (newID, newID)

@route('/check')
def check():
  db = getDB()
  cursor = db.cursor()
  ret = ""
  for check_id in request.params.getall('id'):
    select_sql = "SELECT identifier, algorithm, complete FROM Requests WHERE identifier=\"%s\"" % (check_id)
    cursor.execute(select_sql)
    results = cursor.fetchall()
    for result in results:
      ret += "ID: %s, Algorithm %s, Status: " % (result[0], result[1])
      if result[2]==1:
        ret += "Complete"
      else:
        ret += "Not Complete"
      ret += "<br />\n"
  return ret

@get('/all')
def getAll():
  db = getDB()
  cursor = db.cursor()
  select_sql = "SELECT DISTINCT(identifier) FROM Requests"
  cursor.execute(select_sql)
  ret = ""
  results = cursor.fetchall()
  for result in results:
    ret += "<a href=\"/app/check?id=%s\">%s</a><br />" % (result[0], result[0])
  return ret

@route("/")
def index():
  links = """
  <a href="/app/all">All Available Requests</a><br />
  <a href="/app/test">Submit new Request</a><br />
  """
  return links

run(host='', port=8888, debug=True, reloader=True)