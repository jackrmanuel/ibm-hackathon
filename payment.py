
import bottle
from bottle import route, run, static_file, post, request, response, template
import bottle
#import sys
import os
import socket
#import requests
#import json
import time
import http.client

############################################################################################################

DEBUG = 'YES'
TCP_PORT = 8080
rootdir = os.getcwd()+"/static/"
COOKIESECRET='VvCXyOw4LlevVYlgEDwVPvjv42oqbHVIggzb'

# 0
@route('/')
def root():
    return static_file('initial.html', root=rootdir)

#1
@post('/initial')
def initial():
  print ('INITIAL')
  option = request.forms.get("form:option")
  info = {'option': option }
  print (option)
  response.set_cookie("account", option, secret=COOKIESECRET)
  return template('scancard.html',info,urlnext="/scancard",percent="10",message="continue")
  

#2
@post('/scancard')
def scancard():
  print('SCAN')
  option = request.get_cookie("account", secret=COOKIESECRET)
  if option:
    info = {'option': 'option' } 
    cardnumber = request.forms.get("form:cardnumber")
    if cardnumber in ['1234','abcde']:
      response.set_cookie("account", cardnumber, secret=COOKIESECRET)
      # return "<meta http-equiv='refresh' content='2;url=/ambiente' /><p>Welcome! You are now logged in.</p>"
      info = {'cardnumber': cardnumber }
      #conn = http.client.HTTPSConnection("service.us.apiconnect.ibmcloud.com")
      #headers = {
      #'x-ibm-client-id': "4ce73542-13ef-4ae1-bb25-26fe9c6f5164",
      #'accept': "application/json"
      #}
      #conn.request("GET", "/gws/apigateway/api/c0b78651e1904db457f52363cf9c26f7aa9723145f347166ca9885ac82cdb3c0/H2ncOL/customer/getCustomerBankInformation?debitcardNumber=38383", headers=headers)
      #res = conn.getresponse()
      #data = res.read()
      #print (data)

      return template('message.html',info,urlnext="/pinform",percent="10",message="Valid card swiped.")
    else:
      info = {'cardnumber': cardnumber }
      #return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid card. Please swipe a valid card</p>"
      return template('message.html',info,urlnext="/",percent=100,message="Invalid card. Please swipe a valid card.")    
      response.set_cookie("account", cardnumber, secret=COOKIESECRET)
      return template('pinform.html',info,urlnext="/pinform",percent="10",message="Valid card swiped.")
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid card. Access denied.</p>"  

  #return template('scancard.html',info)
  return template('pinform.html',info,urlnext="/pinform",percent="10",message="Valid card swiped.")
  print ('RETURN')
  cardnumber = request.forms.get("form:cardnumber")
  print (cardnumber)
  print ('WHY')
  # check for card swipe


@route('/pinform')
def pinform():
  print ('PIN')
  cardnumber = request.get_cookie("account", secret=COOKIESECRET)
  if cardnumber:
    info = {'cardnumber': cardnumber } 
    return template('pinform.html',info)
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid card. Access denied.</p>"


@post('/printform')
def printform():
  print ('PRINT FORM')
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

