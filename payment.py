
import bottle
from bottle import route, run, static_file, post, request, response, template
import bottle
#import sys
import os
import socket
#import requests
#import json
#import http.client
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

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
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid card. Access denied.</p>"  



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
      packet = io.BytesIO()
      # create a new PDF with Reportlab
      can = canvas.Canvas(packet, pagesize=letter)
      can.drawString(35, 848, 'Jordan, Michael')
      can.drawString(470, 848, '604-777-7777')
      can.drawString(35, 822, '777 Ottawa St. Surrey, BC')
      can.drawString(470, 822, 'V4A5W7')
      can.drawString(35, 798, 'TD Canada')
      can.drawString(325, 798, '123')
      can.drawString(395, 798, '12345')
      can.drawString(470, 798, '1234567890')
      can.drawString(35, 754, 'Insurance Corporation of British Columbia')
      can.drawString(35, 730, '151 Esplanade W, North Vancouver, BC ')
      can.drawString(325, 730, 'V7M1A2')
      can.drawString(470, 730, '604-888-8888')
      can.drawString(290, 667, 'x')
      can.drawString(37, 620, 'x')
      can.drawString(122, 620, '125.00')
      can.drawString(145, 586, 'x')
      can.save()
      #move to the beginning of the StringIO buffer
      packet.seek(0)
      new_pdf = PdfFileReader(packet)
      # read your existing PDF
      existing_pdf = PdfFileReader(open("PAD_template.pdf", "rb"))
      output = PdfFileWriter()
      # add the "watermark" (which is the new pdf) on the existing page
      page = existing_pdf.getPage(0)
      page.mergePage(new_pdf.getPage(0))
      output.addPage(page)
      # finally, write "output" to a real file
      outputStream = open('./static/PAD_target.pdf', 'wb')
      output.write(outputStream)
      outputStream.close()      
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
    percent = 100
    log_array = []  
    log_array.append('PAD Form printed.')  
    info = {'cardnumber': cardnumber } 
    return template('pdfdisplay.html',info,percent=percent,message=log_array)
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

