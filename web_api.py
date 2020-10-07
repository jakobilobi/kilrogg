from flask import Flask, request, flash, redirect, url_for, send_from_directory
from flask_cors import CORS
import uuid
import os
from interfaces import ModelInterface as MI
from PIL import Image

UPLOAD_FOLDER = 'uploads'
TRANSFORMATION_FOLDER = 'test_data/u2net_results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["TRANSFORMATION_FOLDER"] = TRANSFORMATION_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    return str(uuid.uuid4()) + filename

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/test_data/u2net_results/<filename>')
def transformed_file(filename):
    return send_from_directory(app.config['TRANSFORMATION_FOLDER'],filename)


@app.route('/', methods=['POST'])
def cut():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        mi = MI()
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            img = Image.open(filepath) # open the image file
            img.verify() # verify that it is, in fact an image
        except (IOError, SyntaxError) as e:
            print('Bad file:', filename)
            #os.remove(base_dir+"\\"+filename) (Maybe)
        model_file_path = os.path.join(os.getcwd(), filepath)
        cropped_image_filename =  mi.run_inference([model_file_path])
        
        print(cropped_image_filename)
        return redirect(url_for('transformed_file', filename=os.path.basename(cropped_image_filename[0])))
    # Cut logic here
    return "this is cut"