import os
import win32com.client as win32
import subprocess
from firebase_admin import credentials, storage, initialize_app

# Inisialisasi Firebase Admin SDK
cred = credentials.Certificate("firebase-adminsdk.json")
initialize_app(cred, {'storageBucket': 'convert-f4bb1.appspot.com'})

def upload_to_firebase_storage(file_path):
    # Upload file ke Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(os.path.basename(file_path))
    blob.upload_from_filename(file_path)
    print(f"File {os.path.basename(file_path)} uploaded to Firebase Storage")

def get_unique_output_filename(output_folder, base_filename, extension):
    file_path = os.path.join(output_folder, f"{base_filename}{extension}")
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join(output_folder, f"{base_filename}({counter}){extension}")
        counter += 1
    return file_path

def excel_to_pdf(input_folder, output_folder):
    excel = win32.Dispatch("Excel.Application")
    for filename in os.listdir(input_folder):
        if filename.endswith((".xlsx", ".xls", ".xla")):
            excel_path = os.path.join(input_folder, filename)
            
            # Ambil nama dasar file tanpa ekstensi
            base_filename, _ = os.path.splitext(filename)
            
            # Tentukan path output yang unik
            pdf_path = get_unique_output_filename(output_folder, base_filename, ".pdf")

            wb = excel.Workbooks.Open(excel_path)
            wb.ExportAsFixedFormat(0, pdf_path, Quality=0, IncludeDocProperties=True, IgnorePrintAreas=False)
            wb.Close()

            # Upload ke Firebase Storage
            upload_to_firebase_storage(pdf_path)

    excel.Quit()
    close_command_prompt()

def ppt_to_pdf(input_folder, output_folder):
    powerpoint = win32.Dispatch("Powerpoint.Application")
    for filename in os.listdir(input_folder):
        if filename.endswith((".ppt", ".pptx")):
            ppt_path = os.path.join(input_folder, filename)
            
            # Ambil nama dasar file tanpa ekstensi
            base_filename, _ = os.path.splitext(filename)
            
            # Tentukan path output yang unik
            pdf_path = get_unique_output_filename(output_folder, base_filename, ".pdf")

            presentation = powerpoint.Presentations.Open(ppt_path)
            presentation.SaveAs(pdf_path, 32)
            presentation.Close()

            # Upload ke Firebase Storage
            upload_to_firebase_storage(pdf_path)

    powerpoint.Quit()
    close_command_prompt()


def word_to_pdf(input_folder, output_folder):
    word = win32.Dispatch("Word.Application")
    for filename in os.listdir(input_folder):
        if filename.endswith((".doc", ".docx", ".rtf")):
            doc_path = os.path.join(input_folder, filename)
            print(f"Converting: {doc_path}")
            if not os.path.exists(doc_path):
                print(f"File not found: {doc_path}")
                continue

            # Ambil nama dasar file tanpa ekstensi
            base_filename, _ = os.path.splitext(filename)
            
            # Tentukan path output yang unik
            pdf_path = get_unique_output_filename(output_folder, base_filename, ".pdf")

            doc = word.Documents.Open(doc_path)
            print(f"Saving as PDF: {pdf_path}")
            doc.SaveAs(pdf_path, FileFormat=17)
            doc.Close()

            # Upload ke Firebase Storage
            upload_to_firebase_storage(pdf_path)

    # Tambahkan try-except block untuk menangani kesalahan
    try:
        word.Quit()
    except Exception as e:
        print(f"Error quitting Word application. Reason: {e}")

    close_command_prompt()



def close_command_prompt():
    subprocess.run('TASKKILL /F /IM cmd.exe', shell=True)

def delete_files_in_input_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting: {file_path}. Reason: {e}")


# Path direktori untuk file-file Office
input_folder = os.path.abspath("input")
output_folder = os.path.abspath("output")

# Pastikan folder output sudah ada, jika belum, maka buat folder tersebut
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Konversi berbagai jenis file ke PDF
excel_to_pdf(input_folder, output_folder)
word_to_pdf(input_folder, output_folder)
ppt_to_pdf(input_folder, output_folder)

# Hapus file di dalam folder input setelah konversi selesai
delete_files_in_input_folder(input_folder)

close_command_prompt()

# Pastikan file ini tidak dijalankan saat `converter.py` dieksekusi secara langsung
if __name__ == "__main__":
    pass
