import sys

from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
from uuid import uuid4

app = Flask(__name__, static_url_path="/static")

#############
# Routing
#
@app.route('/message', methods=['POST'])
def reply():
    if sys.argv[1] == 'mock':
        return jsonify({'text': request.form['msg']})
    else:
        return jsonify({'text': execute.decode_line(sess, model, enc_vocab, rev_dec_vocab, request.form['msg'])})


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def new_chat():
    chat_id = str(uuid4())
    return redirect(url_for("get_chat", chatId=chat_id))


@app.route("/chat/<chat_id>", methods=['GET'])
def get_chat(chat_id):
    return render_template("chat.html", chatId=chat_id)


@app.route("/chat/<chat_id>/feedback", methods=['GET'])
def get_feedback(chat_id):
    return render_template("feedback.html", chatId=chat_id)


#############

'''
Init seq2seq model

    1. Call main from execute.py
    2. Create decode_line function that takes message as input
'''
# _________________________________________________________________
if sys.argv[1] != 'mock':
    import tensorflow as tf
    import execute

    sess = tf.Session()
    sess, model, enc_vocab, rev_dec_vocab = execute.init_session(sess, conf='seq2seq_serve.ini')
# _________________________________________________________________

# start app
if __name__ == "__main__":
    app.run(port=5000)
