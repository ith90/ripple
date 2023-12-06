from extensions import db
from datetime import datetime



class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    weather_id = db.Column(db.Integer, db.ForeignKey('weather.id'), nullable=False)
    emotion_id = db.Column(db.Integer, db.ForeignKey('emotions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    weather = db.relationship('Weather', back_populates='entry', primaryjoin='Entry.weather_id == Weather.id')
    users = db.relationship('Users', back_populates='entry', primaryjoin='Entry.user_id == Users.id')
    emotions = db.relationship('Emotions', back_populates='entry', primaryjoin='Entry.emotion_id == Emotions.id', uselist=True) # One to many relationship

    def __repr__(self):
        return f'<Entry {self.id}>'
    
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    hash = db.Column(db.String, nullable=False)

    entry = db.relationship('Entry', back_populates='users')
    
    def __repr__(self):
        return f'<User {self.id}>'

class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    temp = db.Column(db.Float, nullable=False)
    feels_like = db.Column(db.Float, nullable=False)
    clouds = db.Column(db.Integer, nullable=False)
    rain_1h = db.Column(db.Float, nullable=True)
    snow_1h = db.Column(db.Float, nullable=True)

    entry = db.relationship('Entry', back_populates='weather')

    def __repr__(self):
        return f'<Weather {self.id}>'
    
class Emotions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gratitude = db.Column(db.Float, nullable=True)
    admiration = db.Column(db.Float, nullable=True)
    joy = db.Column(db.Float, nullable=True)
    approval = db.Column(db.Float, nullable=True)
    caring = db.Column(db.Float, nullable=True)
    pride = db.Column(db.Float, nullable=True)
    excitement = db.Column(db.Float, nullable=True)
    neutral = db.Column(db.Float, nullable=True)
    relief = db.Column(db.Float, nullable=True)
    optimism = db.Column(db.Float, nullable=True)
    realization = db.Column(db.Float, nullable=True)
    love = db.Column(db.Float, nullable=True)
    annoyance = db.Column(db.Float, nullable=True)
    desire = db.Column(db.Float, nullable=True)
    disapproval = db.Column(db.Float, nullable=True)
    sadness = db.Column(db.Float, nullable=True)
    surprise = db.Column(db.Float, nullable=True)
    disappointment = db.Column(db.Float, nullable=True)
    remorse = db.Column(db.Float, nullable=True)
    grief = db.Column(db.Float, nullable=True)
    amusement = db.Column(db.Float, nullable=True)
    confusion = db.Column(db.Float, nullable=True)
    anger = db.Column(db.Float, nullable=True)
    curiosity = db.Column(db.Float, nullable=True)
    disgust = db.Column(db.Float, nullable=True)
    fear = db.Column(db.Float, nullable=True)
    embarrassment = db.Column(db.Float, nullable=True)
    nervousness = db.Column(db.Float, nullable=True)

    entry = db.relationship('Entry', back_populates='emotions')

    # CREATING TOP EMOTIONS FUNCTION
    def top_emotions(self):
    # Creating a list of tuples (emotion_name, score)
        emotions = [
            ('gratitude', self.gratitude),
            ('admiration', self.admiration),
            ('joy', self.joy),
            ('approval', self.approval),
            ('caring', self.caring),
            ('pride', self.pride),
            ('excitement', self.excitement),
            ('relief', self.relief),
            ('optimism', self.optimism),
            ('realization', self.realization),
            ('love', self.love),
            ('annoyance', self.annoyance),
            ('desire', self.desire),
            ('disapproval', self.disapproval),
            ('sadness', self.sadness),
            ('surprise', self.surprise),
            ('disappointment', self.disappointment),
            ('remorse', self.remorse),
            ('grief', self.grief),
            ('amusement', self.amusement),
            ('confusion', self.confusion),
            ('anger', self.anger),
            ('curiosity', self.curiosity),
            ('disgust', self.disgust),
            ('fear', self.fear),
            ('embarrassment', self.embarrassment),
            ('nervousness', self.nervousness)
        ]
        # Filter out emotions where score is None
        emotions = [emotion for emotion in emotions if emotion[1] is not None]

        # Sort the emotions based on scores in descending order and get the top 5
        top_emotions = sorted(emotions, key=lambda x: x[1], reverse=True)[:5]
        return top_emotions

    def __repr__(self):
        return f'<Emotions {self.id}>'
