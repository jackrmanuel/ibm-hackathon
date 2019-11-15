
import bottle
from bottle import route, run, static_file, post, request, response, template
import bottle
import sys
import os
import socket
import gitlab
import shutil
import uuid
import re
import requests
import json
import time

############################################################################################################

DEBUG = 'YES'
TCP_PORT = 8080
rootdir = os.getcwd()+"/static/"
COOKIESECRET='ZvCXyOw4LlevVYlgEDwVPvjv42oqbHVIggzb'

# 0
@route('/')
def root():
    return static_file('initial.html', root=rootdir)

#1
@post('/initial')
def messaging():
  cardnumber = request.forms.get("form:cardnumber")
  # check for card swipe
  if cardnumber in ['1234','abcde']:
    response.set_cookie("account", cardnumber, secret=COOKIESECRET)
    # return "<meta http-equiv='refresh' content='2;url=/ambiente' /><p>Welcome! You are now logged in.</p>"
    info = {'cardnumber': cardnumber }
    return template('message.html',info,urlnext="/pinform",percent="10",message="Valid card swiped.")
  else:
    info = {'cardnumber': cardnumber }
    #return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid card. Please swipe a valid card</p>"
    return template('message.html',info,urlnext="/",percent=100,message="Invalid card. Please swipe a valid card.")

#2
@route('/pinform')
def restricted_area():
  cardnumber = request.get_cookie("account", secret=COOKIESECRET)
  if cardnumber:
    info = {'cardnumber': cardnumber } 
    return template('pinform.html',info)
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid card. Access denied.</p>"


@post('/printform')
def printform():
  cardnumber = request.get_cookie("account", secret=COOKIESECRET)
  if cardnumber:
    global percent, log_array, baseimage,appname,source,target,RancherProject,lob
    percent =70
    log_array = []    
    info = {'cardnumber': cardnumber } 
    pin = request.forms.get('form:pin')
    if pin in ['1234']:
      log_array.append('Printing PAD form')
      return template('messaginglog.html',info,urlnext="/displayform",percent=percent,message=log_array)
    else:
      return template('message.html',info,urlnext="/pinform",percent=percent,message="Incorrect pin number.")
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid card. Access denied..</p>"


@route('/displayform')
def displayform():
  cardnumber = request.get_cookie("account", secret=COOKIESECRET)
  if cardnumber:
    time.sleep(5) 
    percent = 100
    log_array = []  
    log_array.append('PAD Form printed.')  
    info = {'cardnumber': cardnumber } 
    return template('messaginglog.html',info,urlnext="/logout",percent=percent,message=log_array)
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid card. Access denied..</p>"    

#4
@route('/logout')
def logout():
  cardnumber = request.get_cookie("account", secret=COOKIESECRET)
  response.set_cookie("account", cardnumber, secret='')
  return '<meta http-equiv="refresh" content="2;url=/" />'

# ROUTE TO STATIC CONTENT - DONT DELETE!!!!
@route('/static/<filepath:path>')
def server_static(filepath):
  return static_file(filepath, root=rootdir)

def check_splcharacter(test): 
    string_check= re.compile('[@_!#$%^&*()<>?/\|}{~:]')       
    if(string_check.search(test) == None): 
        print("String does not contain Special Characters.")
        return False  
    else: 
        print("String contains Special Characters.") 
        return True

# FIX FOR LOAD BALANCER + BOTTLE
hostname=socket.gethostname()
#hostname='localhost'

def fix_environ_middleware(app):
  def fixed_app(environ, start_response):
    environ['wsgi.url_scheme'] = 'http'
    environ['HTTP_X_FORWARDED_HOST'] = hostname
    return app(environ, start_response)
  return fixed_app

app = bottle.default_app()
app.wsgi = fix_environ_middleware(app.wsgi)

if DEBUG == 'YES':
    bottledebug=True
else:
    bottledebug=False

run(host=hostname, port=TCP_PORT, debug=bottledebug, reloader=True)

