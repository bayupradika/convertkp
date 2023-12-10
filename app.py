import threading
from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for, Response
import subprocess
import webbrowser
import os
from firebase_admin import credentials, storage, initialize_app

cred = credentials.Certificate("firebase-adminsdk.json")
initialize_app(cred, {'storageBucket': 'convert-f4bb1.appspot.com'})


app = Flask(__name__, static_url_path='/static', static_folder='static')

# Tentukan folder input dan output
input_folder = os.path.abspath("input")
output_folder = os.path.abspath("output")


# Pastikan folder output ada
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def get_unique_filename(file_path):
    base, extension = os.path.splitext(file_path)
    counter = 1
    while os.path.exists(file_path):
        file_path = f"{base}({counter}){extension}"
        counter += 1
    return file_path

@app.route('/upload_and_convert', methods=['POST'])
def upload_and_convert():
    if 'file' not in request.files:
        return "No file part"

    files = request.files.getlist('file')

    if not files or all(file.filename == '' for file in files):
        return "No selected file"

    # Simpan setiap file ke folder input
    for file in files:
        filename = file.filename
        file_path = os.path.join(input_folder, filename)

        # Tambahkan nomor jika file dengan nama yang sama sudah ada
        file_path = get_unique_filename(file_path)

        file.save(file_path)
        print(f"File {filename} uploaded to input folder as {os.path.basename(file_path)}")

    # Konversi file-file yang diupload
    convert()
    return redirect(url_for('index'))

    
@app.route('/')
def index():
    return render_template('index.html')

# Rute untuk menampilkan gambar
@app.route('/images/<path:filename>')
def images(filename):
    return send_from_directory('static/images', filename)

@app.route('/convert', methods=['GET'])
def convert():
    subprocess.run(['python', 'converter.py'], shell=True)
    return Response("Conversion initiated.<script>alert('File konversi selesai.');</script>", content_type='text/html')

def webbrowser_open(url):
    webbrowser.open(url)

if __name__ == '__main__':
    # Menggunakan threading untuk membuka browser
    thread = threading.Thread(target=webbrowser_open, args=('http://127.0.0.1:5000',))
    thread.start()
    app.run(debug=True, use_reloader=False)
