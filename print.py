from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


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


