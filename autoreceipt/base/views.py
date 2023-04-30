from django.shortcuts import render
from django.core.mail import EmailMessage
import pandas as pd
import os
from io import BytesIO
from django.conf import settings
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from bs4 import BeautifulSoup
import os
import pdfplumber
from django.http import HttpResponse, HttpResponseBadRequest
import os
import shutil
import tempfile
import zipfile
from tkinter import Tk, filedialog
import io
import PyPDF2
from django.urls import reverse
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        df = pd.read_excel(uploaded_file)

        transactions = df.to_dict('records')
        request.session['transactions'] = transactions
        return render(request, 'preview.html', {'transactions': transactions})

    return render(request, 'home.html')
 
@login_required
def template(request):
    return render(request, 'receipt_template.html')

@login_required
def generate_pdf(transaction):
    # Define the context for the template
    context = {
        'house_number': transaction['house_number'],
        'name': transaction['name'],
        'date': transaction['date'],
        'phone': transaction['phone'],
        'description': transaction['description'],
        'amount': transaction['amount'],
        'email': transaction['email'],
    }

    # Set the path and name for the output file
    date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    phone_number = str(transaction['phone']).zfill(10)
    file_name = f"0{phone_number}_{transaction['name']}_{date_str}.pdf"
    pdf_path = os.path.join(settings.STATIC_ROOT, 'receipts', file_name)

    # Load the template
    template = get_template('receipt_template.html')

    # Render the template with the context
    html = template.render(context)

    # Modify the contents of the page
    soup = BeautifulSoup(html, 'html.parser')
    soup.find(id='house_number').string = transaction['house_number']
    soup.find(id='name').string = transaction['name']
    soup.find(id='date').string = transaction['date']
    soup.find(id='phone').string = str(transaction['phone'])
    soup.find(id='description').string = transaction['description']
    soup.find(id='amount').string = str(transaction['amount'])
    soup.find(id='email').string = transaction['email']
    html = str(soup)

    # Create a PDF file
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=result)

    # Check if the PDF was successfully created
    if not pdf.err:
        # Save the PDF file
        with open(pdf_path, 'wb') as file:
            file.write(result.getvalue())
        # Return the PDF file as a BytesIO object
        result.seek(0)
        return result
    
    error_message = f"Error creating PDF: {pdf.err}"
    error_bytes = BytesIO(error_message.encode('utf-8'))
    return error_bytes

@login_required
def send_emails(request):
    transactions = request.session.get('transactions', [])
    num_emails_sent = 0
    for transaction in transactions:
        new_pdf = generate_pdf(transaction)
        email = EmailMessage(
            'Transaction Receipt',
            'Please find attached your transaction receipt.',
            'noreply@example.com',
            [transaction['email']]
        )
        email.attach('receipt.pdf', new_pdf.read(), 'application/pdf')
        num_emails_sent += email.send()
    return render(request, 'success.html', {'num_emails_sent': num_emails_sent})

@login_required
def download_receipt(request):
    transactions = request.session.get('transactions', [])
    receipts_dir = 'receipts'
    receipts_path = os.path.join(settings.STATIC_ROOT, receipts_dir)

    # Create the receipts directory if it doesn't exist
    if not os.path.exists(receipts_path):
        os.mkdir(receipts_path)

    # Create a temporary directory to hold the receipts
    temp_dir = tempfile.mkdtemp()

    # Generate and save receipts for each transaction
    for transaction in transactions:
        # Generate the PDF for the transaction
        pdf_file = generate_pdf(transaction)

        # Save the PDF file
        date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        phone_number = str(transaction['phone']).zfill(10)
        file_name = f"{phone_number}_{transaction['name']}_{date_str}.pdf"
        file_path = os.path.join(temp_dir, file_name)
        with open(file_path, 'wb') as file:
            file.write(pdf_file.getbuffer())

        # Remove the processed transaction from the session
        request.session['transactions'] = [t for t in transactions if t != transaction]

    # Create a zip file containing the receipts
    zip_path = os.path.join(settings.STATIC_ROOT, f"{receipts_dir}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for file_name in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file_name)
            zip_file.write(file_path, file_name)

    # Return a response to the user
    with open(zip_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename="{receipts_dir}.zip"'
        return response

    # Remove the temporary directory and its contents
    shutil.rmtree(temp_dir)

#Data Cleaning
ACCEPTED_FILE_FORMATS = ['csv', 'xlsx', 'xls', 'qfx', 'ofx', 'pdf']

@login_required
def cleanup(request):
    # Check if file was uploaded
    if request.method == 'POST' and request.FILES:
        # Get the uploaded file
        uploaded_file = request.FILES['file']

        # Get the file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        # Process the file based on its extension
        if file_extension == '.csv':
            # Read CSV file
            df = pd.read_csv(uploaded_file)

        elif file_extension in ('.xlsx', '.xls'):
            # Read Excel file
            df = pd.read_excel(uploaded_file)

        elif file_extension == '.qfx':
            # Read QFX file
            df = pd.read_xml(uploaded_file)

        elif file_extension == '.ofx':
            # Read OFX file
            df = pd.read_xml(uploaded_file)

        elif file_extension == '.pdf':
            # Read PDF file
            memory_file = io.BytesIO(uploaded_file.read())
            pdf_reader = PyPDF2.PdfReader(memory_file)
            tables = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                table = pd.read_csv(io.StringIO(page.extract_text()))
                tables.append(table)
            df = pd.concat(tables)

        else:
            # Invalid file format
            return HttpResponse(f"Invalid file format: {file_extension}. Accepted formats are: .csv, .xlsx, .xls, .qfx, .ofx, .pdf")

        # Preview the extracted data
        preview = df.head().to_html()

        # Get the output path from the user using a file explorer dialog
        root = Tk()
        root.withdraw()
        root.call('wm', 'attributes', '.', '-topmost', True)
        output_path = filedialog.asksaveasfilename(parent=root, defaultextension='.xlsx', filetypes=[('Excel files', '*.xlsx')])
        root.destroy()

        # Save the extracted data to the output path
        if output_path:
            df.to_excel(output_path, index=False)

        # Render the cleanup template with the preview and output path
        return render(request, 'preview2.html', {'preview': preview, 'output_path': output_path})

    else:
        # Render the cleanup template without any data
        return render(request, 'cleanup.html')

@login_required   
def preview_data(request, data):
    # Render the preview template with the extracted data
    return render(request, 'preview2.html', {'data': data})