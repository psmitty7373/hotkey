import os
from flask import Flask, render_template, request, send_file, send_from_directory
import json

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/config')
def get_config():
    with open('config.json', 'r') as file:
        config = file.read()
    return config

@app.route('/update', methods=['POST'])
def update():
    try:
        config = json.loads(request.form['config'])
        with open('config.json', 'w') as file:
            file.write(json.dumps(config))
        return 'Config updated successfully.'
    except:
        return 'Config update failed.'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file and file.filename.endswith('.png'):
        filename = os.path.join('images', file.filename)
        file.save(filename)
        return 'File uploaded successfully'
    else:
        return 'Only PNG files are allowed'

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('images', path)

def init_web_interface():
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

if __name__ == '__main__':
    init_web_interface()
