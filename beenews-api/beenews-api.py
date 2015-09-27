# -*- coding: utf-8 -*-
"""
GeoData API Flask application
"""
import logging
from app.mongo import mongo
from flask import Flask
from config import get_app_conf
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)


def configure_app():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s %(name)s] %(message)s')
    app.config.from_object(get_app_conf())

    app.register_blueprint(mongo)


configure_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
