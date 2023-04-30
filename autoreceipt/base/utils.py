from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
import pandas as pd
import os

def generate_pdf(data):
    # Set up the canvas
    pdf = canvas.Canvas('receipt.pdf', pagesize=letter)
    pdf.setTitle('Transaction Receipt')
    pdf.setLineWidth(0.5)
    pdf.setFont('Helvetica', 12)
    
    # Add header
    pdf.drawString(inch, 10 * inch, "Transaction Receipt")
    
    # Add table
    table_data = [['Name', 'Transaction Type', 'Amount']]
    for row in data:
        table_data.append([row['name'], row['transaction_type'], row['amount']])
    table = pd.DataFrame(table_data)
    table_style = [('GRID', (0,0), (-1,-1), 1, (0,0,0)), ('BACKGROUND', (0,0), (-1,0), (220/255,220/255,220/255))]
    table_width = sum(table.style._compute_column_widths()) + table.style._compute_index_width() + 20
    table_height = len(table.index) * 25 + 25
    table.wrapOn(pdf, inch, 8.5 * inch)
    table.drawOn(pdf, inch, 8.5 * inch - table_height)
    pdf.line(inch, 8.5 * inch - table_height - 20, inch + table_width, 8.5 * inch - table_height - 20)
    
    # Add footer
    pdf.drawString(inch, inch, "Thank you for your business!")
    
    # Save the PDF
    pdf.save()
    
    return 'receipt.pdf'

def send_email(email, data):
    # Generate the PDF
    pdf_filename = generate_pdf(data)
    
    # Send the email
    subject = 'Transaction Receipt'
    body = 'Thank you for your business!'
    from_email = 'noreply@example.com'
    to_email = [email]
    attachment = open(pdf_filename, 'rb')
    email = EmailMessage(subject, body, from_email, to_email)
    email.attach('receipt.pdf', attachment.read(), 'application/pdf')
    email.send()
    
    # Clean up the PDF file
    attachment.close()
    os.remove(pdf_filename)
