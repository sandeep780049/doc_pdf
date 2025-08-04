import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from docx import Document
from fpdf import FPDF
import uuid

app = Flask(__name__)
app.secret_key = "pdfconvertersecret"
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    uploaded_file.save(file_path)

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + '.pdf')

    if filename.endswith('.docx'):
        doc = Document(file_path)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for para in doc.paragraphs:
            pdf.multi_cell(0, 10, para.text)
        pdf.output(output_path)
    else:
        return "Only .docx to .pdf supported for now."

    session['last_file'] = output_path
    return render_template('result.html', file_url=url_for('download_file'))

@app.route('/download')
def download_file():
    return send_file(session.get('last_file'), as_attachment=True)

@app.route('/merge', methods=['GET', 'POST'])
def merge():
    if request.method == 'POST':
        files = request.files.getlist('files')
        merger = PdfMerger()
        paths = []

        for file in files:
            path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(path)
            merger.append(path)
            paths.append(path)

        merged_path = os.path.join(app.config['UPLOAD_FOLDER'], 'merged_' + str(uuid.uuid4()) + '.pdf')
        merger.write(merged_path)
        merger.close()
        session['last_file'] = merged_path
        return render_template('result.html', file_url=url_for('download_file'))

    return render_template('merge.html')

@app.route('/split', methods=['GET', 'POST'])
def split():
    if request.method == 'POST':
        file = request.files['file']
        page_num = int(request.form['page'])
        path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(path)

        reader = PdfReader(path)
        writer = PdfWriter()
        writer.add_page(reader.pages[page_num - 1])

        split_path = os.path.join(app.config['UPLOAD_FOLDER'], 'split_' + str(uuid.uuid4()) + '.pdf')
        with open(split_path, 'wb') as f:
            writer.write(f)

        session['last_file'] = split_path
        return render_template('result.html', file_url=url_for('download_file'))

    return render_template('split.html')

@app.route('/history')
def history():
    return render_template('history.html')