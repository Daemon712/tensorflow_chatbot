import sys
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


if app.config['NEURAL_LOGIC']:
    import tensorflow as tf
    import execute

    sess = tf.Session()
    sess, model, enc_vocab, rev_dec_vocab = execute.init_session(sess, conf='seq2seq_serve.ini')

from app import routes, metrics, models