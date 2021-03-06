import os
import sys
import os.path
import time


from flask import Flask, request, send_from_directory, redirect, url_for
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from VideoToImages import getVideo

app = Flask(__name__, static_url_path='', static_folder='public')
UPLOAD_FOLDER = '../tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Check if request has file
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        print file
        # If user didn't select a file, submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        else:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return file.filename
    return ''

@app.route('/<filename>')
def uploaded_file(filename):
   return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/VideoToImages', methods=['POST'])
def send_to_video_to_images():
    if request.method == 'POST':
        start_time = time.time()
        result = getVideo(request.get_data())
        print("--- %s seconds ---" % (time.time() - start_time))
        return result
    return ''

if __name__ == "__main__":
    app.run(threaded=True)
