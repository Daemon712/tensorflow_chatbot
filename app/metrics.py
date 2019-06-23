import decimal
import json

from flask import jsonify
from sqlalchemy.orm import aliased

from app.models import Chat, Message
from app import app, db
import sqlalchemy as sa


@app.route("/metrics/chats_count", methods=['GET'])
def chats_count():
    data = db.session.query(sa.func.date(Chat.timestamp), sa.func.count(Chat.id),
                            sa.func.count(Chat.feedback_timestamp)) \
        .group_by(sa.func.date(Chat.timestamp)) \
        .all()
    return jsonify(data)


@app.route("/metrics/feedback_ratio", methods=['GET'])
def feedback_ratio():
    all, feedback = db.session.query(sa.func.count(Chat.id), sa.func.count(Chat.feedback_timestamp)) \
        .one()
    data = [
        {'label': 'С отзывом', 'value': feedback},
        {'label': 'Без отзыва', 'value': all - feedback}
    ]
    return jsonify(data)


@app.route("/metrics/chat_lengths", methods=['GET'])
def chat_lengths():
    data = db.session.query(sa.func.date(Chat.timestamp), sa.func.max(Chat.messages_count), sa.func.avg(Chat.messages_count)) \
        .group_by(sa.func.date(Chat.timestamp)) \
        .all()

    return jsonify(data)


@app.route("/metrics/chat_length_ratio", methods=['GET'])
def chat_length_ratio():
    rows = db.session.query(Chat.messages_count, sa.func.count(Chat.id)) \
        .group_by(Chat.messages_count) \
        .all()
    data = [{'label': row[0], 'value': row[1]} for row in rows]
    return jsonify(data)


@app.route("/metrics/rate_trend/<rate>", methods=['GET'])
def rate_trend(rate):
    column = resolve_rate_column(rate)
    data = db.session.query(sa.func.date(Chat.timestamp),
                            sa.func.max(column), sa.func.avg(column), sa.func.min(column)) \
        .filter(column.isnot(None)) \
        .group_by(sa.func.date(Chat.timestamp)) \
        .all()
    return jsonify_fixed(data)


@app.route("/metrics/rate_ratio/<rate>", methods=['GET'])
def rate_ratio(rate):
    column = resolve_rate_column(rate)
    rows = db.session.query(sa.func.round(column), sa.func.count(Chat.id)) \
        .filter(column.isnot(None)) \
        .group_by(sa.func.round(column)) \
        .all()
    data = [{'label': 'Оценка: ' + str(int(row[0])), 'value': row[1]} for row in rows]
    return jsonify_fixed(data)


@app.route("/metrics/msg_ratio", methods=['GET'])
def msg_ratio_total():
    rows = db.session.query(Message.category, sa.func.count(Message.id)) \
        .group_by(Message.category) \
        .all()

    data = [{'label': Message.LABELS_CATEGORY[row[0]], 'value': row[1]} for row in rows]
    return jsonify(data)


@app.route("/metrics/msg_ratio/<author>", methods=['GET'])
def msg_ratio(author):
    rows = db.session.query(Message.category, sa.func.count(Message.id)) \
        .filter(sa.and_(Message.author == author, Message.category.isnot(None))) \
        .group_by(Message.category) \
        .all()

    data = [{'label': Message.LABELS_CATEGORY[row[0]], 'value': row[1]} for row in rows]
    return jsonify(data)


@app.route("/metrics/next_msg_ratio/<category>", methods=['GET'])
def next_msg_ratio(category):
    message = aliased(Message)
    message_next = aliased(Message)
    rows = db.session.query(message_next.category, sa.func.count(message_next.id)) \
        .filter(sa.and_(message.chat_id == message_next.chat_id,
                        message.category == category,
                        message_next.order == message.order + 1)) \
        .group_by(message_next.category) \
        .all()
    if len(rows):
        data = [{'label': Message.LABELS_CATEGORY[row[0]], 'value': row[1]} for row in rows]
    else:
        data = [{'label': 'Нет данных', 'value': 100}]
    return jsonify(data)


@app.route("/metrics/prev_msg_ratio/<category>", methods=['GET'])
def prev_msg_ratio(category):
    message = aliased(Message)
    message_prev = aliased(Message)
    rows = db.session.query(message_prev.category, sa.func.count(message_prev.id)) \
        .filter(sa.and_(message.chat_id == message_prev.chat_id,
                        message.category == category,
                        message_prev.order == message.order - 1)) \
        .group_by(message_prev.category) \
        .all()
    if len(rows):
        data = [{'label': Message.LABELS_CATEGORY[row[0]], 'value': row[1]} for row in rows]
    else:
        data = [{'label': 'Нет данных', 'value': 100}]
    return jsonify(data)


@app.route("/metrics/msg_rate_ratio/<category>", methods=['GET'])
def msg_rate_ratio(category):
    rows = db.session.query(Message.rate, sa.func.count(Message.id)) \
        .filter(Message.category == category) \
        .group_by(Message.rate) \
        .all()
    if len(rows):
        data = [{'label': 'Хорошо' if row[0] == 1 else 'Плохо', 'value': row[1]} for row in rows]
    else:
        data = [{'label': 'Нет данных', 'value': 100}]
    return jsonify(data)


@app.route("/metrics/msg_position/<category>", methods=['GET'])
def msg_position(category):
    rows = db.session.query(Message.order, sa.func.count(Message.id)) \
        .filter(Message.category == category) \
        .group_by(Message.order) \
        .all()

    max_index = max([row[0] for row in rows]) if len(rows) else 10
    items = (max_index if max_index > 10 else 10)
    data = []
    for index in range(items):
        data.append([index, 0])
    for row in rows:
        val = row[1]
        index = row[0] - 1
        holder = data[index]
        holder[1] = val
    return jsonify(data)


def resolve_rate_column(rate):
    if rate == 'content':
        return Chat.content_rate
    if rate == 'grammar':
        return Chat.grammar_rate
    if rate == 'vocabulary':
        return Chat.vocabulary_rate
    if rate == 'organization':
        return Chat.organization_rate
    if rate == 'total':
        return Chat.total_rate


def encoder(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    return obj


def jsonify_fixed(data):
    return app.response_class(
        json.dumps(data, indent=2, separators=(', ', ': '), default=encoder) + '\n',
        mimetype=app.config['JSONIFY_MIMETYPE']
    )