import os
from flask import Flask, make_response, render_template, request, send_from_directory, safe_join
import json
from threading import Thread

class WebHandler(Thread):
    def __init__(self, lock):
        super().__init__()
        self.app = Flask(__name__)
        self.app.config['TEMPLATES_AUTO_RELOAD'] = True
        self.lock = lock

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/config')
        def get_config():
            with self.lock:
                with open('config.json', 'r') as file:
                    config = file.read()
            return config

        @self.app.route('/update', methods=['POST'])
        def update():
            try:
                with self.lock:
                    config = json.loads(request.form['config'])
                    with open('config.json', 'w') as file:
                        file.write(json.dumps(config))
                return 'Config updated successfully.'
            except:
                return 'Config update failed.'

        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            if 'file' not in request.files:
                return 'No file part'

            file = request.files['file']

            if file.filename == '':
                return 'No filename'

            if file.content_type != 'image/png':
                return 'Only PNG files are allowed'

            if len(file.read()) > 1 * 1024 * 1024:  # 1MB limit
                return 'File size exceeds 1MB limit'

            filename = safe_join('images', file.filename)
            file.seek(0)
            file.save(filename)
            return 'File uploaded successfully'

        @self.app.route('/images/<path:path>')
        def send_images(path):
            response = make_response(send_from_directory('images', path))
            response.headers['Cache-Control'] = 'no-store'
            return response

        @self.app.route('/default_images/<path:path>')
        def send_default_images(path):
            return send_from_directory('default_images', path)

    def run(self):
        self.app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
