import sys, signal, syslog
from web import WebHandler

web_handler = WebHandler()
flask_app = web_handler.app