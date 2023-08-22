from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import numpy as np
import firebase_admin
import google.cloud 
from firebase_admin import credentials
from google.cloud import storage as gcs_storage
from firebase_admin import firestore, storage as fb_storage

app = Flask(__name__)

# Inicializar Firebase (usa tus propias credenciales descargadas desde Firebase Console)
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'gs://tesis-9d8c6.appspot.com'})


@app.route('/')
def home():
    return render_template('home.html', title='Welcome')

@app.route('/graphs')
def show_graphs():
    # Generar la gráfica de correlación aquí como lo hicimos antes...
    random_values = np.random.rand(10, 2)  # Ejemplo con 10 filas y 2 columnas
    plt.figure()
    plt.scatter(random_values[:, 0], random_values[:, 1])
    plt.title('Correlation Plot')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid()

    # Guardar la gráfica en un archivo
    graph_filename = 'static/correlation_plot.png'
    plt.savefig(graph_filename)
    plt.close()

    return render_template('graphs.html', title='Graphs', graph_filename=graph_filename)

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    uploaded_filename = None
    download_url = None 
    all_files_info = []
    db = firestore.client()
    available_files = db.collection('uploaded_files').stream()
    for file_doc in available_files:
        all_files_info.append(file_doc.to_dict())
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            # Subir archivo a Firebase Storage
            uploaded_filename = uploaded_file.filename
            storage_client = gcs_storage.Client.from_service_account_json("credentials.json")
            storage_bucket = storage_client.bucket('tesis-9d8c6.appspot.com')
            blob = storage_bucket.blob(uploaded_file.filename)
            blob.upload_from_string(uploaded_file.read(), content_type=uploaded_file.content_type)

            # Obtener información adicional del formulario
            name = request.form['name']
            description = request.form['description']

            # Guardar información en Firestore
            db = firestore.client()
            file_info = {
                'name': name,
                'description': description,
                'download_url': blob.public_url  # Obtén la URL pública del archivo
            }
            db.collection('uploaded_files').add(file_info)
            # Obtén la URL pública del archivo para la descarga
            download_url = blob.public_url
            
            # Obtener la información de archivos disponibles de la base de datos

            
    return render_template('upload.html', title='Upload Files',  uploaded_filename=uploaded_filename, download_url=download_url, all_files=all_files_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
