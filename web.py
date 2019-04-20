import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename

from scan import document_scan
app = Flask(__name__, template_folder='templates')

UPLOAD_FOLDER = 'uploadfile'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# check if the file provided is elligible for scanning
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# show the details of the uploaded image
@app.route("/uploaded_file/<filename>/<scanned_path>", methods=['GET'])
def uploaded_file(filename, scanned_path):
    print("Filename: {}".format(filename))
    orig_path   = filename
    
    scanned_filename = scanned_path.rsplit(os.path.sep,1)[1]
    return render_template('uploaded.html', filename=filename, orig_filename=filename, scanned_filename=scanned_filename)

# upload the file and scan it    
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            orig_filename, scanned_path = document_scan(filepath)
            return redirect(url_for('uploaded_file',
                                    filename=filename, scanned_path=scanned_path))
    
    return render_template('web.html')
    
# send the uploaded image to the calling function
@app.route('/uploads/<path:path>')
def send_upload(path):
    
    return send_from_directory('uploadfile', path)

# download or view the scanned image    
@app.route('/scanned/<path:path>', defaults={'download':False})
@app.route('/scanned/<path:path>/<download>')
def send_scanned(path, download):
    if download:
        return send_from_directory('temp', path, as_attachment=True)
    return send_from_directory('temp', path)