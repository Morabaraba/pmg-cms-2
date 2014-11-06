import logging
import logging.config
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import sys
import os

env = os.environ.get('FLASK_ENV', 'development')

app = Flask(__name__, instance_relative_config=True, static_folder="static")
app.config.from_pyfile('config.py', silent=True)

db = SQLAlchemy(app)

# setup logging
with open('config/%s/logging.yaml' % env) as f:
    import yaml
    logging.config.dictConfig(yaml.load(f))

import views
