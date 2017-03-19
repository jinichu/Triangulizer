import os
from flask import Flask, request, send_from_directory

app = Flask(__name__, static_url_path='', static_folder='public')
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/')
def root():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run()
