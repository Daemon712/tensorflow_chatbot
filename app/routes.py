import sys
from datetime import datetime
from decimal import Decimal

from flask import render_template, request, redirect, url_for, jsonify

import sqlalchemy as sa

from app.models import Chat, Message, UserWord, BotWord, VocabularyWord
from app import app, db
from data_utils import basic_tokenizer
import execute


#############
# Routing
#
@app.route('/chat/<chat_id>/message', methods=['POST'])
def reply(chat_id):
    chat = Chat.query.filter_by(id=chat_id).first_or_404()
    request_text = request.form['msg']
    request_msg = Message(chat_id=chat_id, text=request_text, author=Message.AUTHOR_USER, order=chat.messages_count + 1)
    if app.config['NEURAL_LOGIC']:
        from app import sess, model, enc_vocab, rev_dec_vocab
        response_text = execute.decode_line(sess, model, enc_vocab, rev_dec_vocab, request_text)
    else:
        response_text = request.form['msg']

    response_msg = Message(chat_id=chat_id, text=response_text, author=Message.AUTHOR_BOT,
                           order=chat.messages_count + 2)
    for word in basic_tokenizer(request_text.encode()):
        db.session.add(UserWord(word=word))
    for word in basic_tokenizer(response_text.encode()):
        db.session.add(BotWord(word=word))

    chat.messages_count = chat.messages_count + 2

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
    messages = Message.query.filter_by(chat_id=chat_id).all()
    return render_template("feedback.html", chatId=chat_id, messages=messages)


@app.route("/chat/<chat_id>/feedback", methods=['POST'])
def save_feedback(chat_id):
    feedback = request.get_json()
    chat = Chat.query.filter_by(id=chat_id).first_or_404()
    chat.content_rate = feedback['content_rate']
    chat.organization_rate = feedback['organization_rate']
    chat.vocabulary_rate = feedback['vocabulary_rate']
    chat.grammar_rate = feedback['grammar_rate']
    chat.total_rate = feedback['total_rate']
    chat.comment = feedback['comment']
    chat.feedback_timestamp = datetime.now()
    for msg in chat.messages:
        msg_req = feedback['messages'][str(msg.id)]
        msg.rate = msg_req['rate']
        if msg_req['category'] in Message.LABELS_CATEGORY:
            msg.category = msg_req['category']
    db.session.add(chat)
    db.session.commit()
    return jsonify()


@app.route("/dashboard", methods=['GET'])
def dashboard():
    passive_vocabulary = db.session.query(db.func.count(VocabularyWord.word)).scalar()
    active_bot_vocabulary = db.session.query(BotWord.word).group_by(BotWord.word).count()
    active_user_vocabulary = db.session.query(UserWord.word).group_by(UserWord.word).count()
    known_user_vocabulary = db.session.query(UserWord.word) \
        .filter(UserWord.word == VocabularyWord.word) \
        .group_by(UserWord.word).count()

    return render_template("dashboard.html",
                           passive_vocabulary=passive_vocabulary,
                           active_bot_vocabulary=active_bot_vocabulary,
                           active_user_vocabulary=active_user_vocabulary,
                           known_user_vocabulary=known_user_vocabulary)


@app.route("/vocabulary_table", methods=['GET'])
def vocabulary_table():
    columns = ['word', 'total(f1)', 'total(f2)', 'total(f2)-total(f1)', 'total(f3)', 'total(f3)-total(f1)']
    params = {
        'search': request.args.get('search[value]', '') + '%',
        'offset': request.args.get('start', 0),
        'limit': request.args.get('length', 10)
    }
    script = sql_data_src.replace(':order_dir', request.args.get('order[0][dir]', 'desc')) \
        .replace(':order_column', columns[int(request.args.get('order[0][column]', 0))])
    results = list(db.engine.execute(script, params))
    return jsonify({
        'draw': request.args.get('draw'),
        'recordsTotal': db.engine.execute(sql_total_counter, params).scalar(),
        'recordsFiltered': db.engine.execute(sql_filtered_counter, params).scalar(),
        'data': [process_row(r) for r in results]
    })


sql_data_src = (
    'select word, total(f1), total(f2), total(f2)-total(f1), total(f3), total(f3)-total(f1) '
    'from ('
    '     select word, frequency f1, null f2, null f3'
    '     from vocabulary_word'
    '     union all'
    '     select word, null, 1000000 * count(word) / (select count(*) from bot_word), null'
    '    from bot_word group by word'
    '    union all'
    '    select word, null, null, 1000000 * count(word) / (select count(*) from user_word)'
    '    from user_word group by word'
    ') where word like :search '
    'group by word order by :order_column :order_dir limit :offset, :limit')

sql_total_counter = (
    'select count(word) '
    'from ('
    '     select word from vocabulary_word'
    '     union'
    '     select distinct word from bot_word'
    '     group by word'
    '     union'
    '     select distinct word from user_word'
    '     group by word'
    ')')
sql_filtered_counter = sql_total_counter + ' where word like :search'


@app.route("/feedback_table", methods=['GET'])
def feedback_table():
    columns = [Chat.feedback_timestamp, Chat.comment, Chat.total_rate]
    search = request.args.get('search[value]', '') + '%'
    offset = int(request.args.get('start', 0))
    limit = int(request.args.get('length', 10))
    order_dir = request.args.get('order[0][dir]', 'desc')
    order_column = columns[int(request.args.get('order[0][column]', 0))]

    record_query = db.session.query(Chat.feedback_timestamp, Chat.comment, Chat.total_rate) \
        .filter(sa.and_(Chat.comment.isnot(None), Chat.comment.like(search))) \
        .order_by(order_column.desc() if order_dir == 'desc' else order_column.asc()) \
        .paginate(offset / limit, limit, False)
    return jsonify({
        'draw': request.args.get('draw'),
        'recordsTotal': db.session.query(sa.func.count(Chat.id)).filter(Chat.comment.isnot(None)).scalar(),
        'recordsFiltered': record_query.total,
        'data': [process_row(r) for r in record_query.items]
    })


def process_row(row):
    return [process_cell(cell) for cell in row]


def process_cell(cell):
    if isinstance(cell, (bytes, bytearray)):
        return cell.decode("utf-8")
    if isinstance(cell, float):
        return round(cell, 2)
    if isinstance(cell, Decimal):
        return float(cell)
    if (isinstance(cell, datetime)):
        return cell.strftime("%d.%m.%Y")
    return cell
