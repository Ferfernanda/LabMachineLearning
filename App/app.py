import time
import os
import cv2
import numpy as np
from PIL import Image
from flask import Flask, request, redirect, render_template
from tensorflow import keras
#from tensorflow.keras.models import load_model
#from tensorflow.keras.models import model_from_json

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route("/")
def index():
    return render_template('/select.html', )

@app.route('/predict', methods=['POST'])
def predict():
    chosen_model = request.form['select_model']
    model_dict = {'CNN'   :   'C:\\Users\\User\\MachineLearning\\CNN_skin_aug.h5',
                  'Transferlearning'     :   'C:\\Users\\User\\MachineLearning\\EfficientNetB3_skin_aug.h5',}
    if chosen_model in model_dict:
        model = keras.models.load_model(model_dict[chosen_model]) 
    else:
        model = keras.models.load_model(model_dict[0])
    file = request.files["file"]
    file.save(os.path.join('C:\\Users\\User\\MachineLearning\\App\\static\\temp.jpeg'))
    img = cv2.cvtColor(np.array(Image.open(file)), cv2.COLOR_BGR2RGB)
    img = np.expand_dims(cv2.resize(img,(100, 75)).astype('float32') / 255, axis=0)
    start = time.time()
    pred = model.predict(img)[0]
    labels = (pred > 0.5).astype(np.int)
    print(labels)
    runtimes = round(time.time()-start,4)
    respon_model = [round(elem * 100, 2) for elem in pred]
    return predict_result(chosen_model, runtimes, respon_model, 'temp.jpeg')

def predict_result(model, run_time, probs, img):
    class_list = {'Benign': 0, 'Malignant': 1}
    idx_pred = probs.index(max(probs))
    labels = list(class_list.keys())
    return render_template('/result_select.html', labels=labels, 
                            probs=probs, model=model, pred=idx_pred, 
                            run_time=run_time, img=img)

if __name__ == "__main__": 
        app.run(debug=True, host='0.0.0.0', port=2000)
