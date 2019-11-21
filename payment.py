import bottle
from bottle import route, run, static_file, post, request, response, template
import bottle
#import sys
import os
import socket
import requests
import json
import http.client
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
#import uuid
import webbrowser
import re

############################################################################################################

DEBUG = 'YES'
TCP_PORT = 8080
rootdir = os.getcwd()+"/static/"
COOKIESECRET='VvCXyOw4LlevVYlgEDwVPvjv42oqbHVIggzb'
#global AccountNumber, address, name, bankName, primaryPhone, institutionNo, transitNo, monthPayment, postalCode
AccountNumber = ''
address = ''
name = ''
name = ''
bankName = ''
primaryPhone = ''
institutionNo = ''
transitNo = ''
monthPayment = ''
postalCode = ''
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
  if option == 'DebitCard':
    return template('scancard.html',info,urlnext="/scancard",percent="10",message="Swipe/Tap Debit Card")
  if option == 'QRCode':
    return template('qrcode.html',info,urlnext="/qrcode",percent="10",message="Scan QR Code")  
  if option == 'ScanAccountNumber':
    return template('qrcode.html',info,urlnext="/qrcode",percent="10",message="ScanAccountNumber")      
  if option == 'FacialRecognition':
    return template('qrcode.html',info,urlnext="/pinform",percent="10",message="FacialRecognition")      
  if option == 'TypeAccountNumber':
    return template('accountnumber.html',info,urlnext="/accountnumber",percent="10",message="Type Account Number")   
  
@post('/scancard')
def scancard():
  print('SCAN')
  option = request.get_cookie("account", secret=COOKIESECRET)
  if option:
    info = {'option': 'option' } 
    cardnumber = request.forms.get("form:cardnumber")
    cardnumber = str.split(cardnumber,'=')[0]
    cardnumber = re.sub('[^A-Za-z0-9]+', '', cardnumber)
    accountnumber = cardnumber
    print (accountnumber+':'+cardnumber)

    if ApiCardCall(accountnumber):
      response.set_cookie("account", accountnumber, secret=COOKIESECRET)
      info = {'accountnumber': accountnumber }     
      return template('message.html',info,urlnext="/pinform",percent="10",message="Valid card swiped.")
    else:
      info = {'accountnumber': accountnumber }
      webbrowser.open('https://assistant-chat-us-south.watsonplatform.net/web/public/1c9e40a5-9fdb-43f1-b776-10462cfa5012', new=2)
      return template('message.html',info,urlnext="/",percent=100,message="Invalid card. Please swipe a valid card.")          
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid card. Access denied.</p>"  

@post('/qrcode')
def qrcode():
  print('QRCode')
  option = request.get_cookie("account", secret=COOKIESECRET)
  if option:
    info = {'option': 'option' } 
    accountnumber = request.forms.get("form:accountnumber")
    #Remove Special Characters
    accountnumber = re.sub('[^A-Za-z0-9]+', '', accountnumber)    
    print (accountnumber)
    #For simplicity just used card number in QRcode and search
    if ApiCardCall(accountnumber):
      response.set_cookie("account", accountnumber, secret=COOKIESECRET)
      info = {'accountnumber': accountnumber }  
      webbrowser.open('https://assistant-chat-us-south.watsonplatform.net/web/public/df4179f7-6baa-41ff-8060-e5aa5536970f', new=2)   
      return template('message.html',info,urlnext="/pinform",percent="10",message="Account number "+accountnumber)
    else:
      info = {'accountnumber': accountnumber }
      print ('No account number')
      #return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid Account number.</p>"
      return template('message.html',info,urlnext="/",percent=100,message="Invalid account.")    
  else:
    print ('no option')
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid account. Access denied.</p>"  


@post('/accountnumber')
def accountnumber():
  print('Account Number')
  option = request.get_cookie("account", secret=COOKIESECRET)
  if option:
    info = {'option': 'option' } 
    accountnumber = request.forms.get("form:accountnumber")
    instNo = request.forms.get("form:InstitutionNo")
    TransNo = request.forms.get("form:TransitNo")
    #Remove Special Characters
    accountnumber = re.sub('[^A-Za-z0-9]+', '', accountnumber)
    #Verify if it is a valid account number
    if ApiAccountCall(accountnumber,instNo,TransNo):
      response.set_cookie("account", accountnumber, secret=COOKIESECRET)
      info = {'accountnumber': accountnumber }     
      return template('message.html',info,urlnext="/pinform",percent="10",message="Account number "+accountnumber)
    else:
      info = {'accountnumber': accountnumber }
      webbrowser.open('https://assistant-chat-us-south.watsonplatform.net/web/public/df4179f7-6baa-41ff-8060-e5aa5536970f', new=2)
      #return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid Account number.</p>"
      return template('message.html',info,urlnext="/",percent=100,message="Invalid account.")    
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid account. Access denied.</p>"  


@route('/pinform')
def pinform():
  print ('PIN')
  accountnumber = request.get_cookie("account", secret=COOKIESECRET)
  if accountnumber:
    info = {'accountnumber': accountnumber }   
    return template('pinform.html',info,urlnext="/printform")
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid account. Access denied.</p>"

@post('/printform')
def printform():
  print ('PRINT FORM')
  accountnumber = request.get_cookie("account", secret=COOKIESECRET)
  #print (accountnumber)
  if accountnumber:
    global log_array, percent
    percent =70
    log_array = []    
    info = {'accountnumber': accountnumber } 
    pin = request.forms.get('form:pin')
    print (pin)
    if pin:   
      log_array.append('Generating PAD form')
      return template('messaginglog.html',info,urlnext="/displayform",percent=percent,message=log_array)     
    else:
      return template('message.html',info,urlnext="/pinform",percent=percent,message="Incorrect pin number.")
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid account. Access denied..</p>"

@route('/displayform')
def displayform():
  print ('Display form')
  accountnumber = request.get_cookie("account", secret=COOKIESECRET)
  if accountnumber:
    print ('PAD_unsign')
    fileName = '/static/_PAD_unsign.pdf'      
    generate_pdf(accountnumber)
    percent = 100
    log_array = []  
    log_array.append('PAD Form printed.')  
    info = {'accountnumber': accountnumber } 
    return template('pdfdisplay.html',info,percent=percent,fileName=fileName)
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid account. Access denied..</p>"    

@route('/PADsign')
def PADsign():
  accountnumber = request.get_cookie("account", secret=COOKIESECRET)
  if accountnumber:
    fileName = '/static/PAD_unsign.pdf'     
    percent = 100
    log_array = []  
    log_array.append('PAD Form signed.')  
    info = {'accountnumber': accountnumber } 
    return template('pdfsign.html',info,percent=percent,fileName=fileName)
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid account. Access denied..</p>"        

@post('/displaysignform')
def displaysignform():
  print ('Display Signed form')
  accountnumber = request.get_cookie("account", secret=COOKIESECRET)
  #displaysignform
  if accountnumber:
    print ('PAD_sign')
    fileName = '/static/_PAD_unsign.pdf'      
    sign = request.forms.get("form:sign")
    print (sign)
    if sign == 'sign':
      print ('Signed')
      sign_pdf()
      percent = 100
      log_array = []  
      log_array.append('PAD Form printed.')  
      info = {'accountnumber': accountnumber } 
      return template('signeddisplay.html',info,percent=percent,fileName=fileName)
      #displaysignform
    else:
      print ('Cancel')     
      return "<meta http-equiv='refresh' content='2;url=/' /><p>Cancelled..</p>"    
  else:
    return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid account. Access denied..</p>"    

#4
@route('/logout')
def logout():
  accountnumber = request.get_cookie("account", secret=COOKIESECRET)
  response.set_cookie("account", accountnumber, secret='')
  return '<meta http-equiv="refresh" content="2;url=/" />'

# ROUTE TO STATIC CONTENT - DONT DELETE!!!!
@route('/static/<filepath:path>')
def server_static(filepath):
  return static_file(filepath, root=rootdir)

# FIX FOR LOAD BALANCER + BOTTLE
hostname=socket.gethostname()
#hostname='localhost'

def generate_pdf(card_no):
  global AccountNumber, address, name, bankName, primaryPhone, institutionNo, transitNo, monthPayment, postalCode
  #fileName = str(uuid.uuid4())+'.pdf'
  fileName = 'PAD_unsign.pdf'
  #Get Account Number using CardNumber. Use API or get from Watson Data
  print (card_no)
  print ('GENERATE PDF')
  #APICall(account_no)

  packet = io.BytesIO()
  # create a new PDF with Reportlab
  can = canvas.Canvas(packet, pagesize=letter)
  can.drawString(35, 848, name)
  can.drawString(470, 848, primaryPhone)
  can.drawString(35, 822, address)
  can.drawString(470, 822, postalCode)
  can.drawString(35, 798, bankName)
  can.drawString(325, 798, institutionNo)
  can.drawString(395, 798, transitNo)
  can.drawString(460, 798, AccountNumber)
  can.drawString(35, 754, 'Insurance Corporation of British Columbia')
  can.drawString(35, 730, '151 Esplanade W, North Vancouver, BC ')
  can.drawString(325, 730, 'V7M1A2')
  can.drawString(470, 730, '604-888-8888')
  can.drawString(290, 667, 'x')
  can.drawString(37, 620, 'x')
  can.drawString(122, 620, monthPayment)
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
  completePathfileName='./static/PAD_unsign.pdf'
  print (fileName)
  outputStream = open(completePathfileName, 'wb')
  output.write(outputStream)
  outputStream.close()    
  return fileName

def ApiCardCall(card_no):
  global AccountNumber, address, name, bankName, primaryPhone, institutionNo, transitNo, monthPayment, postalCode
  headers = { 'x-ibm-client-id': "d00ed2e3-a4b8-4abf-84dd-9821603ba6f2", 'accept': "application/json" } 
  url="/gws/apigateway/api/52a97357d94f73eb250a91be334dc75ba12f265192661af5af426d7b3cd54a7a/OXaNVx/CustomerBankInfo/"+card_no
  server='service.us.apiconnect.ibmcloud.com'
  conn=http.client.HTTPSConnection(server)
  conn.request("GET", url, headers=headers) 
  #conn.request('GET','/gws/apigateway/api/c0b78651e1904db457f52363cf9c26f7aa9723145f347166ca9885ac82cdb3c0/H2ncOL/customer/getCustomerBankInformation?debitcardNumber='+account_no,
  #              headers=headers)

  print(url)
  print(server)
  result=conn.getresponse().read()
  data=result.decode('utf+8')
  resp=json.loads(data)
  #resp = ''
  
  print (resp)
  if resp['bankAccountNumber']:
    AccountNumber = resp['bankAccountNumber']
    address = resp['address']
    name = resp['lastName'] + ', ' + resp['firstName']
    bankName = resp['bankName']
    primaryPhone = resp['primaryPhone']
    institutionNo = resp['institutionNo']
    transitNo = resp['transitNo']
    monthPayment = resp['monthPayment']
    postalCode = resp['postalCode']
    print ('Printing Name')
    print (name)
    return True
  else:
    #AccountNumber = account_no  
    #address = '145 Generic St. Coquitlam, BC'
    #name = 'Jordan, Michael'   
    #bankName = 'Toronto-Dominion Bank (TD Canada Trust)'
    #primaryPhone = '604-874-1432'
    #institutionNo = '0004'
    #transitNo = '94480'
    #monthPayment = '150.00'
    #postalCode = 'V9H4G2'  
    return False

def ApiAccountCall(account_no, instNo, transNo):
  global AccountNumber, address, name, bankName, primaryPhone, institutionNo, transitNo, monthPayment, postalCode
  headers = { 'x-ibm-client-id': "d00ed2e3-a4b8-4abf-84dd-9821603ba6f2", 'accept': "application/json" } 
  url='/gws/apigateway/api/52a97357d94f73eb250a91be334dc75ba12f265192661af5af426d7b3cd54a7a/OXaNVx/CustomerBankInfo/GetCustomerBankInfo?bankAccountNumber='+account_no+'&institutionNo='+instNo+'&transitNo='+transNo
  server='service.us.apiconnect.ibmcloud.com'
  conn=http.client.HTTPSConnection(server)
  conn.request("GET", url, headers=headers) 
  
  print(url)
  print(server)
  result=conn.getresponse().read()
  data=result.decode('utf+8')
  resp=json.loads(data)
  #resp = ''
  
  print (resp)
  if resp['bankAccountNumber']:
    AccountNumber = resp['bankAccountNumber']
    address = resp['address']
    name = resp['lastName'] + ', ' + resp['firstName']
    bankName = resp['bankName']
    primaryPhone = resp['primaryPhone']
    institutionNo = resp['institutionNo']
    transitNo = resp['transitNo']
    monthPayment = resp['monthPayment']
    postalCode = resp['postalCode']
    print ('Printing Name')
    print (name)
    return True
  else:
    #AccountNumber = account_no  
    #address = '145 Generic St. Coquitlam, BC'
    #name = 'Jordan, Michael'   
    #bankName = 'Toronto-Dominion Bank (TD Canada Trust)'
    #primaryPhone = '604-874-1432'
    #institutionNo = '0004'
    #transitNo = '94480'
    #monthPayment = '150.00'
    #postalCode = 'V9H4G2'  
    return False    

def sign_pdf():
  print ('SIGNING')

  packet = io.BytesIO()
  # create a new PDF with Reportlab
  can = canvas.Canvas(packet, pagesize=letter)
  can.drawString(370, 306, 'Digitally Signed')
  can.drawString(515, 306, '19-11-19')
  can.save()
  #move to the beginning of the StringIO buffer
  packet.seek(0)
  new_pdf = PdfFileReader(packet)
  # read your existing PDF
  existing_pdf = PdfFileReader(open("./static/PAD_unsign.pdf", "rb"))
  output = PdfFileWriter()
  # add the "watermark" (which is the new pdf) on the existing page
  page = existing_pdf.getPage(0)
  page.mergePage(new_pdf.getPage(0))
  output.addPage(page)
  # finally, write "output" to a real file
  completePathfileName='./static/PAD_sign.pdf'
  outputStream = open(completePathfileName, 'wb')
  output.write(outputStream)
  outputStream.close()    

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
#run(host='localhost', port=TCP_PORT, debug=bottledebug, reloader=True)

