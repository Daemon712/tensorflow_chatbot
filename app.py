from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
from uuid import uuid4

app = Flask(__name__,static_url_path="/static") 

#############
# Routing
#
@app.route('/message', methods=['POST'])
def reply():
    return jsonify( { 'text': execute.decode_line(sess, model, enc_vocab, rev_dec_vocab, request.form['msg'] ) } )

@app.route("/")
def index(): 
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def newChat():
    chatId  = str(uuid4())
    return redirect(url_for("getChat", chatId=chatId))

@app.route("/chat/<chatId>", methods=['GET'])
def getChat(chatId):
    return render_template("chat.html", chatId=chatId)
#############

'''
Init seq2seq model

    1. Call main from execute.py
    2. Create decode_line function that takes message as input
'''
#_________________________________________________________________
import tensorflow as tf
import execute

sess = tf.Session()
sess, model, enc_vocab, rev_dec_vocab = execute.init_session(sess, conf='seq2seq_serve.ini')
#_________________________________________________________________

# start app
if (__name__ == "__main__"): 
    app.run(port = 5000) 
