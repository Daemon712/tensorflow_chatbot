from datetime import datetime
from app import db


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    content_rate = db.Column(db.Numeric)
    organization_rate = db.Column(db.Numeric)
    vocabulary_rate = db.Column(db.Numeric)
    grammar_rate = db.Column(db.Numeric)
    total_rate = db.Column(db.Numeric)
    comment = db.Column(db.String(4096))
    feedback_timestamp = db.Column(db.DateTime)
    messages_count = db.Column(db.Integer, default=0)
    messages = db.relationship('Message', backref='chat')

    def __repr__(self):
        return '<Chat {}>'.format(self.id)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer)
    text = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'))
    category = db.Column(db.String(16))
    rate = db.Column(db.Integer())
    order = db.Column(db.Integer)
    AUTHOR_USER = 0
    AUTHOR_BOT = -1
    CATEGORY_GREETING = "greeting"
    CATEGORY_NARRATIVE = "narrative"
    CATEGORY_QUESTION = "question"
    CATEGORY_ANSWER = "answer"
    CATEGORY_REQUEST = "request"
    CATEGORY_ABUSE = "abuse"
    CATEGORY_GOODBYE = "goodbye"
    LABELS_CATEGORY = {
        CATEGORY_GREETING: 'Приветствие',
        CATEGORY_NARRATIVE: 'Повествование',
        CATEGORY_QUESTION: 'Вопрос',
        CATEGORY_ANSWER: 'Ответ',
        CATEGORY_REQUEST: 'Просьба',
        CATEGORY_ABUSE: 'Оскорбление',
        CATEGORY_GOODBYE: 'Прощание',
        None: 'Нераспознано'
    }

    def __repr__(self):
        return '<Message {}>'.format(self.text)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
