from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os
from docx import Document
from pdf2docx import Converter
from docx2pdf import convert

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    if filename.endswith('.docx'):
        output_path = os.path.join(UPLOAD_FOLDER, filename.replace('.docx', '.pdf'))
        convert(filepath, output_path)
    elif filename.endswith('.pdf'):
        output_path = os.path.join(UPLOAD_FOLDER, filename.replace('.pdf', '.docx'))
        cv = Converter(filepath)
        cv.convert(output_path)
        cv.close()
    else:
        return "Unsupported file format"

    return send_file(output_path, as_attachment=True)


    app =  app