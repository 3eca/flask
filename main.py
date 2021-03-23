from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://telegramBot:xxxxxxxx@xxx.xxx.xxx:xxxx" \
                                        "/subscribers?driver=SQLDriverConnect"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)
ma = Marshmallow(app)


class Subscriber(db.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hustlecastle'
    id = db.Column(db.Integer(), primary_key=True)
    telegram = db.Column(db.Integer(), nullable=False)
    sub = db.Column(db.Boolean(), default=False, nullable=False)
    trial = db.Column(db.Integer(), default=10, nullable=False)
    end_sub = db.Column(db.String(10), default='', nullable=False)
    payment_code = db.Column(db.String(10), default='', nullable=False)
    re_sub = db.Column(db.Integer(), default=0, nullable=False)
    date_reg = db.Column(db.String(10), default='', nullable=False)

    def __init__(self, telegram, sub, trial, end_sub, payment_code, re_sub, date_reg):
        self.telegram = telegram
        self.sub = sub
        self.trial = trial
        self.end_sub = end_sub
        self.payment_code = payment_code
        self.re_sub = re_sub
        self.date_reg = date_reg


class SubscriberSchema(ma.Schema):
    class Meta:
        fields = ('telegram', 'sub', 'trial', 'end_sub', 'payment_code', 're_sub', 'date_reg')


class SubscriberClientSide(db.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hustlecastle'
    telegram = db.Column(db.Integer(), nullable=False)
    sub = db.Column(db.Boolean(), default=False, nullable=False)
    trial = db.Column(db.Integer(), default=10, nullable=False)
    end_sub = db.Column(db.String(10), default='', nullable=False)

    def __init__(self, telegram, sub, trial, end_sub):
        self.telegram = telegram
        self.sub = sub
        self.trial = trial
        self.end_sub = end_sub


class SubscriberClientSideSchema(ma.Schema):
    class Meta:
        fields = ('telegram', 'sub', 'trial', 'end_sub')


sub_schema = SubscriberSchema()
subs_schema = SubscriberSchema(many=True)
sub_cs_schema = SubscriberClientSideSchema()


@app.route('/registration', methods=['POST'])
def reg_subscriber():
    telegram = request.json['telegram']
    sub = request.json['sub']
    trial = request.json['trial']
    end_sub = request.json['end_sub']
    payment_code = request.json['payment_code']
    re_sub = request.json['re_sub']
    date_reg = request.json['date_reg']

    new_subscriber = Subscriber(telegram, sub, trial, end_sub, payment_code, re_sub, date_reg)
    db.session.add(new_subscriber)
    db.session.commit()
    return sub_schema.jsonify(new_subscriber)


@app.route('/subscribers', methods=['GET'])
def get_subscribers():
    subscribers = Subscriber.query.all()
    result = subs_schema.dump(subscribers)
    return jsonify(result)


@app.route('/subscriber_cs/:<telegram>', methods=['GET'])
def find_subscriber_for_client_side(telegram):
    subscriber = SubscriberClientSide.query.filter(SubscriberClientSide.telegram == telegram).first()
    return sub_cs_schema.jsonify(subscriber)


@app.route('/subscriber/:<telegram>', methods=['GET'])
def find_subscriber(telegram):
    subscriber = Subscriber.query.filter(Subscriber.telegram == telegram).first()
    return sub_schema.jsonify(subscriber)


@app.route('/subscriber/:<telegram>', methods=['PUT'])
def update_subscriber(telegram):
    subscriber = Subscriber.query.filter(Subscriber.telegram == telegram).first()

    telegram = request.json['telegram']
    sub = request.json['sub']
    trial = request.json['trial']
    end_sub = request.json['end_sub']
    payment_code = request.json['payment_code']
    re_sub = request.json['re_sub']
    date_reg = request.json['date_reg']

    subscriber.telegram = telegram
    subscriber.sub = sub
    subscriber.trial = trial
    subscriber.end_sub = end_sub
    subscriber.payment_code = payment_code
    subscriber.re_sub = re_sub
    subscriber.date_reg = date_reg

    db.session.commit()
    return sub_schema.jsonify(subscriber)


@app.route('/subscriber_cs/:<telegram>', methods=['PUT'])
def update_subscriber_for_client_side(telegram):
    subscriber = SubscriberClientSide.query.filter(SubscriberClientSide.telegram == telegram).first()

    telegram = request.json['telegram']
    sub = request.json['sub']
    trial = request.json['trial']
    end_sub = request.json['end_sub']

    subscriber.telegram = telegram
    subscriber.sub = sub
    subscriber.trial = trial
    subscriber.end_sub = end_sub

    db.session.commit()
    return sub_schema.jsonify(subscriber)


if __name__ == '__main__':
    app.run(debug=True)
