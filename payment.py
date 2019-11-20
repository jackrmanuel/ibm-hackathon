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
import uuid

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
    #Get Account Number using CardNumber. Use API or get from Watson Data
    #url='https://service.us.apiconnect.ibmcloud.com/gws/apigateway/api/c0b78651e1904db457f52363cf9c26f7aa9723145f347166ca9885ac82cdb3c0/H2ncOL/customer/getCustomerBankInformation?debitcardNumber='+account_no'
    #resp=requests.get(url, headers=headers, params={'q': 'debitcardNumber='+account_no}).json()
    #print (resp['bankAccountNumber'])   
    accountnumber = cardnumber
    if accountnumber:
      response.set_cookie("account", accountnumber, secret=COOKIESECRET)
      info = {'accountnumber': accountnumber }     
      return template('message.html',info,urlnext="/pinform",percent="10",message="Valid card swiped.")
    else:
      info = {'accountnumber': accountnumber }
      #return "<meta http-equiv='refresh' content='2;url=/' /><p>Invalid card. Please swipe a valid card</p>"
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
    print (accountnumber)
    #Verify if it is a valid account number
    if accountnumber:
      response.set_cookie("account", accountnumber, secret=COOKIESECRET)
      info = {'accountnumber': accountnumber }     
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
    #Verify if it is a valid account number
    if accountnumber:
      response.set_cookie("account", accountnumber, secret=COOKIESECRET)
      info = {'accountnumber': accountnumber }     
      return template('message.html',info,urlnext="/pinform",percent="10",message="Account number "+accountnumber)
    else:
      info = {'accountnumber': accountnumber }
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
  accountnumber = request.get_cookie("account", secret=COOKIESECRET)
  if accountnumber:
    fileName = '/static/' + generate_pdf(accountnumber)      
    percent = 100
    log_array = []  
    log_array.append('PAD Form printed.')  
    info = {'accountnumber': accountnumber } 
    return template('pdfdisplay.html',info,percent=percent,fileName=fileName)
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

def generate_pdf(account_no):
  fileName = str(uuid.uuid4())+'.pdf'
  #Get Account Number using CardNumber. Use API or get from Watson Data
  print (account_no)
  headers = {
    'x-ibm-client-id': "4ce73542-13ef-4ae1-bb25-26fe9c6f5164",
    'accept': "application/json"
  }
  conn=http.client.HTTPSConnection('service.us.apiconnect.ibmcloud.com')
  conn.request('GET','/gws/apigateway/api/c0b78651e1904db457f52363cf9c26f7aa9723145f347166ca9885ac82cdb3c0/H2ncOL/customer/getCustomerBankInformation?debitcardNumber='+account_no,
                headers=headers)
  result=conn.getresponse().read()
  data=result.decode('utf+8')
  resp=json.loads(data)
  #resp = ''
  print (resp)
  if resp:
    AccountNumber = resp['bankAccountNumber']
    address = resp['address']
    name = resp['lastName'] + ', ' + resp['firstName']
  else:
    AccountNumber = account_no  
    address = "145 Generic St. Coquitlam, BC"
    name = "Jordan, Michael"   

  packet = io.BytesIO()
  # create a new PDF with Reportlab
  can = canvas.Canvas(packet, pagesize=letter)
  can.drawString(35, 848, name)
  can.drawString(470, 848, '604-777-7777')
  can.drawString(35, 822, address)
  can.drawString(470, 822, 'V4A5W7')
  can.drawString(35, 798, 'TD Canada')
  can.drawString(325, 798, '123')
  can.drawString(395, 798, '12345')
  can.drawString(460, 798, AccountNumber)
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
  completePathfileName='./static/'+fileName
  print (fileName)
  outputStream = open(completePathfileName, 'wb')
  output.write(outputStream)
  outputStream.close()    
  return fileName

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

