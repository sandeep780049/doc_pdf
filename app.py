from flask import Flask, render_template, request, send_file, session, redirect, url_for
import os
from werkzeug.utils import secure_filename
from fpdf import FPDF
from PIL import Image
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import uuid
import shutil

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'files' not in request.files:
        return "No file part"
    
    files = request.files.getlist('files')
    operation = request.form.get('operation')
    output_filename = str(uuid.uuid4()) + '.pdf'
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    if operation == 'img2pdf':
        images = []
        for file in files:
            img = Image.open(file.stream)
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
            img.save(img_path)
            images.append(Image.open(img_path).convert('RGB'))
        if images:
            images[0].save(output_path, save_all=True, append_images=images[1:])
    
    elif operation == 'pdf2img':
        # Save uploaded PDF
        file = files[0]
        pdf_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(pdf_path)
        return "PDF to Image conversion not implemented in this version."

    elif operation == 'merge':
        merger = PdfMerger()
        for file in files:
            file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
            file.save(file_path)
            merger.append(file_path)
        merger.write(output_path)
        merger.close()
    
    elif operation == 'split':
        file = files[0]
        pdf_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(pdf_path)
        reader = PdfReader(pdf_path)
        output_files = []
        for i in range(len(reader.pages)):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            split_filename = f"{uuid.uuid4()}_page_{i+1}.pdf"
            split_path = os.path.join(UPLOAD_FOLDER, split_filename)
            with open(split_path, 'wb') as f:
                writer.write(f)
            output_files.append(split_filename)
        session['history'] = session.get('history', []) + output_files
        return render_template('result.html', files=output_files)

    else:
        return "Unsupported operation."

    session['history'] = session.get('history', []) + [output_filename]
    return render_template('result.html', files=[output_filename])

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(path, as_attachment=True)

@app.route('/history')
def history():
    files = session.get('history', [])
    return render_template('history.html', files=files)

@app.route('/clear')
def clear():
    session.pop('history', None)
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)