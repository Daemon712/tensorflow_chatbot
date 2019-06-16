import sys
from flask import render_template, request, redirect, url_for, jsonify
from app.models import Chat, Message
from app import app, db
import execute

#############
# Routing
#
@app.route('/chat/<chat_id>/message', methods=['POST'])
def reply(chat_id):
    request_text = request.form['msg']
    request_msg = Message(chat_id=chat_id, text=request_text, author=Message.AUTHOR_USER)

    if sys.argv[1] == 'tf':
        from app import sess, model, enc_vocab, rev_dec_vocab
        response_text = execute.decode_line(sess, model, enc_vocab, rev_dec_vocab, request_text)
    else:
        response_text = request.form['msg']

    response_msg = Message(chat_id=chat_id, text=response_text, author=Message.AUTHOR_BOT)

    db.session.add(request_msg)
    db.session.add(response_msg)
    db.session.commit()
    return jsonify(response_msg.as_dict())

@app.route('/chat/<chat_id>/message', methods=['GET'])
def get_messages(chat_id):
    messages = Message.query.filter_by(chat_id=chat_id).all()
    return jsonify([message.as_dict() for message in messages])


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def new_chat():
    chat = Chat()
    db.session.add(chat)
    db.session.commit()
    return redirect(url_for("get_chat", chat_id=chat.id))


@app.route("/chat/<chat_id>", methods=['GET'])
def get_chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id).first_or_404()
    return render_template("chat.html", chat=chat)


@app.route("/chat/<chat_id>/feedback", methods=['GET'])
def get_feedback(chat_id):
    return render_template("feedback.html", chatId=chat_id)