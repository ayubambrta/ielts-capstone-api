import os
import io
import requests
import keras
import librosa
import numpy as np
import cloudinary
import cloudinary.uploader
import cloudinary.api
import logging
import pydub
from keras.models import load_model
from pathlib import Path
from flask import Flask
from flask_cors import CORS, cross_origin
from flask import jsonify
from flask import Flask, render_template, request
from cloudinary.utils import cloudinary_url
from urllib.request import urlopen
# from google.cloud import storage

# Cloudinary API
CLOUD_NAME='dntqqcuci'
API_KEY='182168662843965'
API_SECRET='3M7PhAHGCMOOr5EcImPt1g-bxvw'

app = Flask(__name__)

CORS(app)
logging.basicConfig(level=logging.DEBUG)

# Konfigurasi Cloudinary
cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET
)

# Check model availabilty folder "MODEL"
def download(url: str, dest_folder: str):
    if not os.path.exists(dest_folder):
        os.makedirs('./model1/')  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))

pathh = "./model/model_ielts_fluency_real_data.h5"

my_file = Path(pathh)
if not my_file.is_file():
    # file exists
    download("https://storage.googleapis.com/ielts-capstone/model_ielts_fluency_real_data.h5", dest_folder="./model/")

loaded_model_h5 = load_model(pathh)

# Load Model
def feature_extraction(file_name):
    wav = io.BytesIO()

    with urlopen(file_name) as r:
        r.seek = lambda *args: None  # allow pydub to call seek(0)
        pydub.AudioSegment.from_file(r).export(wav, "wav")

    wav.seek(0)
    X , sample_rate = librosa.load(wav)

    if X.ndim > 1:
        X = X[:,0]
    X = X.T
            
    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=30).T, axis=0)
    rmse = np.mean(librosa.feature.rms(y=X).T, axis=0)
    spectral_flux = np.mean(librosa.onset.onset_strength(y=X, sr=sample_rate).T, axis=0)
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=X).T, axis=0)

    return mfccs, rmse, spectral_flux, zcr

# Upload File Fluency
@app.route("/fluency", methods=['POST'])
def fluency():
    cloudinary.config()
    upload_result = None

    if request.method == 'POST':
        file_to_upload = request.files['file']
        app.logger.info('%s file_to_upload', file_to_upload)

    if file_to_upload:
        upload_result = cloudinary.uploader.upload(file_to_upload, resource_type="video")
        app.logger.info(upload_result)
        app.logger.info(type(upload_result))
        print(upload_result['secure_url'])
        
        # Using data from Cloudinary with (secure_url)
        mfccs, rmse, spectral_flux, zcr = feature_extraction(upload_result['secure_url']) 
        number_of_features = 3 + 30
        datasetcheck = np.empty((0,number_of_features))
        extracted_features = np.hstack([mfccs, rmse, spectral_flux, zcr])
        datasetcheck = np.vstack([datasetcheck, extracted_features])
        datasetcheck = np.expand_dims(datasetcheck, axis=1)
        pred = loaded_model_h5.predict(datasetcheck)
        classes = np.argmax(pred, axis = 1).tolist()
        print(classes)
        return jsonify({"Fluency Class": classes[0]})
