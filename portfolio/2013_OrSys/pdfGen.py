import cStringIO
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph,\
        Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch


PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
styles = getSampleStyleSheet()
Title = "Purchase Order Table"
pageinfo = "OrSys purchase order"


def myFirstPage(canvas, doc):
    """First page style"""
    canvas.saveState()
    canvas.setFont('Times-Bold', 16)
    canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 54, Title)
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo)
    canvas.restoreState()


def myLaterPages(canvas, doc):
    """General page style"""
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))
    canvas.restoreState()


def composePDF_PO(poData, prSet):
    """Yields PDF purchase order as stream"""
    buffer = cStringIO.StringIO()
    doc = SimpleDocTemplate(buffer)
    Story = [Spacer(1, 1 * inch)]
    style = styles["Normal"]
    style_H = styles["Heading3"]
    table_data = []
    for i in prSet:
        q = i['No'], i['sku'], i['name'][:55], i['price'], i['qty']
        table_data.append(q)
    bogustext1 = "This is #%s order." % poData['No']
    bogustext2 = 'You should contact your designated Buyer.'
    bogustext3 = "Your designated Buyer is <b>%s</b>," % poData['buyer']
    bogustext4 = "Phone: <b>%s</b>" % poData['phoneNo']
    bogustext5 = "Email: <b>%s</b>" % poData['email']
    p1 = Paragraph(bogustext1, style_H)
    p2 = Paragraph(bogustext2, style)
    p3 = Paragraph(bogustext3, style)
    p4 = Paragraph(bogustext4, style)
    p5 = Paragraph(bogustext5, style)
    product_table = Table(
        table_data, colWidths=[
            doc.width / 20.0,
            doc.width / 10.0,
            doc.width * 7.0 / 10.0,
            doc.width / 10.0,
            doc.width / 20.0])
    #
    product_table.setStyle(
        TableStyle([(
            'INNERGRID', (0, 0), (-1, -1), 0.25, colors.black
        ), ('BOX', (0, 0), (-1, -1), 1.0, colors.black)]))
    Story.append(p1)
    Story.append(p2)
    Story.append(p3)
    Story.append(p4)
    Story.append(p5)
    Story.append(Spacer(1, 0.2 * inch))
    Story.append(product_table)
    Story.append(Spacer(1, 0.2 * inch))

    doc.build(
        Story, onFirstPage=myFirstPage,
        onLaterPages=myLaterPages)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
