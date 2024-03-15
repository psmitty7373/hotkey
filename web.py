import fcntl, json, os, syslog
from flask import Flask, make_response, render_template, request, send_from_directory, safe_join
from jsonschema import validate, ValidationError
from config_schema import config_schema
from threading import Thread

class WebHandler(Thread):
    def __init__(self):
        super().__init__()
        self.app = Flask(__name__)

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/config')
        def get_config():
            try:
                with open('config.json', 'r') as file:
                    fcntl.flock(file.fileno(), fcntl.LOCK_EX)
                    config = file.read()
                    fcntl.flock(file.fileno(), fcntl.LOCK_UN)
                return config
            except Exception as e:
                syslog.syslog(syslog.LOG_INFO, f'Error opening config: {e}')
                return ''

        @self.app.route('/update', methods=['POST'])
        def update():
            try:
                config = json.loads(request.form['config'])
                validate(instance=config, schema=config_schema)
                with open('config.json', 'w') as file:
                    fcntl.flock(file.fileno(), fcntl.LOCK_EX)                    
                    file.write(json.dumps(config))
                    fcntl.flock(file.fileno(), fcntl.LOCK_UN)
                return 'Config updated successfully.'

            except Exception as e:
                syslog.syslog(syslog.LOG_INFO, f'Error opening config: {e}')
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
