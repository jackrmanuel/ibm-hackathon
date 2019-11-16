
from __future__ import print_function
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
import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2
import time

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
    webcam()
    return template('scancard.html',info,urlnext="/scancard",percent="10",message="Scan QR Code")  
  if option == 'ScanAccountNumber':
    webcam()
    return template('scancard.html',info,urlnext="/scancard",percent="10",message="Scan QR Code")      
  if option == 'FacialRecognition':
    webcam()
    return template('scancard.html',info,urlnext="/scancard",percent="10",message="Scan QR Code")      
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
    #conn = http.client.HTTPSConnection("service.us.apiconnect.ibmcloud.com")
    #headers = {
    #'x-ibm-client-id': "4ce73542-13ef-4ae1-bb25-26fe9c6f5164",
    #'accept': "application/json"
    #}
    #conn.request("GET", "/gws/apigateway/api/c0b78651e1904db457f52363cf9c26f7aa9723145f347166ca9885ac82cdb3c0/H2ncOL/customer/getCustomerBankInformation?debitcardNumber=38383", headers=headers)
    #res = conn.getresponse()
    #data = res.read()
    #print (data)    
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
    generate_pdf(accountnumber)      
    percent = 100
    log_array = []  
    log_array.append('PAD Form printed.')  
    info = {'accountnumber': accountnumber } 
    return template('pdfdisplay.html',info,percent=percent,message=log_array)
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
  can.drawString(470, 798, account_no)
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

def decode(im) : 
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)
    # Print results
    for obj in decodedObjects:
        print('Type : ', obj.type)
        print('Data : ', obj.data,'\n')     
    return decodedObjects

def webcam():
  # get the webcam:  
  cap = cv2.VideoCapture(0)

  cap.set(3,640)
  cap.set(4,480)
  #160.0 x 120.0
  #176.0 x 144.0
  #320.0 x 240.0
  #352.0 x 288.0
  #640.0 x 480.0
  #1024.0 x 768.0
  #1280.0 x 1024.0
  time.sleep(2)

  font = cv2.FONT_HERSHEY_SIMPLEX

  while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Our operations on the frame come here
    im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
         
    decodedObjects = decode(im)

    for decodedObject in decodedObjects: 
        points = decodedObject.polygon
     
        # If the points do not form a quad, find convex hull
        if len(points) > 4 : 
          hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
          hull = list(map(tuple, np.squeeze(hull)))
        else : 
          hull = points;
         
        # Number of points in the convex hull
        n = len(hull)     
        # Draw the convext hull
        for j in range(0,n):
          cv2.line(frame, hull[j], hull[ (j+1) % n], (255,0,0), 3)

        x = decodedObject.rect.left
        y = decodedObject.rect.top

        print(x, y)

        print('Type : ', decodedObject.type)
        print('Data : ', decodedObject.data,'\n')

        barCode = str(decodedObject.data)
        cv2.putText(frame, barCode, (x, y), font, 1, (0,255,255), 2, cv2.LINE_AA)
               
    # Display the resulting frame
    cv2.imshow('frame',frame)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('s'): # wait for 's' key to save 
        cv2.imwrite('Capture.png', frame)     

  # When everything done, release the capture
  cap.release()
  cv2.destroyAllWindows()


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

