#!/usr/bin/python

from bottle import *

@get('/hello')
def index():
  name = request.params.getall('name')
  print name
  return template('<b>Hello {{name}}</b>!', name=name)

run(host='localhost', port=8080, debug=True, reloader=True)