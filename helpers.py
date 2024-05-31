
import requests
from extensions import db
from models import Weather, Entry, Emotions, Users
from flask import redirect, render_template, session, request, jsonify
from functools import wraps
import pandas as pd

# HUGGINGFACE
from transformers import pipeline

# heatplot
from data_utils import get_all_text
    #transform_data_for_stacked_chart
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import io
import base64

# COMMON WORDS
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from collections import Counter

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

# for top emotions
from sqlalchemy import func

classifier = None

def load_model():
    global classifier
    if classifier is None:
        classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

load_model()

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_weather_data(lat, lon):

    # API Key and URL
    api_key = "641441002b2d913f06a4f91d4e4dab72"
   
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"

    response = requests.get(url)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        print("Success!")
        data = response.json()

        # check if API is returning data
        print("Raw Response:", response.text)  # Raw text of the response
        print("JSON Data:", response.json())   # JSON content of the response

        weather = Weather(
            description=data['weather'][0]['description'],
            temp=data['main']['temp'],
            feels_like=data['main']['feels_like'],
            clouds=data['clouds']['all'],
            rain_1h=data['rain'].get('1h', 0) if 'rain' in data else 0,
            snow_1h=data['snow'].get('1h', 0) if 'snow' in data else 0
        )

        print("COMMITTING WEATHER DATA")

        db.session.add(weather)
        db.session.commit()

        print (weather)
        return weather
    else:
        print("Failed to fetch data from API")
        return None
    

def fetch_weather(lat, lon):

    weather = get_weather_data(lat, lon) 

    if weather:
        return weather.id
    else:
        return None


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ("\"", "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


# List of all emotion attributes in the Emotions model

emotion_names = [
    'gratitude', 'admiration', 'joy', 'approval', 'caring', 
    'pride', 'excitement', 'relief', 'optimism', 'realization', 
    'love', 'annoyance', 'desire', 'disapproval', 'sadness', 
    'surprise', 'disappointment', 'remorse', 'grief', 'amusement', 
    'confusion', 'anger', 'curiosity', 'disgust', 'fear', 
    'embarrassment', 'nervousness'
]

# Roberta Hugging face
def emotions_hf(entry):

    global classifier
    if classifier is None:
        load_model()

    # data output as lists
    data = classifier(entry)

   #  print(data[:2])  # Print the first two elements (or fewer if there are not many)

    emotions_list = data[0]
    emotions_dict = {emotion['label']: emotion['score'] for emotion in emotions_list}

    emotions = Emotions(
        neutral=emotions_dict.get('neutral', 0),
        approval=emotions_dict.get('approval', 0),
        anger=emotions_dict.get('anger', 0),
        curiosity=emotions_dict.get('curiosity', 0),
        realization=emotions_dict.get('realization', 0),
        confusion=emotions_dict.get('confusion', 0),
        optimism=emotions_dict.get('optimism', 0),
        caring=emotions_dict.get('caring', 0),
        annoyance=emotions_dict.get('annoyance', 0),
        disappointment=emotions_dict.get('disappointment', 0),
        admiration=emotions_dict.get('admiration', 0),
        joy=emotions_dict.get('joy', 0),
        disapproval=emotions_dict.get('disapproval', 0),
        relief=emotions_dict.get('relief', 0),
        desire=emotions_dict.get('desire', 0),
        sadness=emotions_dict.get('sadness', 0),
        nervousness=emotions_dict.get('nervousness', 0),
        excitement=emotions_dict.get('excitement', 0),
        surprise=emotions_dict.get('surprise', 0),
        fear=emotions_dict.get('fear', 0),
        pride=emotions_dict.get('pride', 0),
        love=emotions_dict.get('love', 0),
        embarrassment=emotions_dict.get('embarrassment', 0),
        grief=emotions_dict.get('grief', 0),
        remorse=emotions_dict.get('remorse', 0),
        disgust=emotions_dict.get('disgust', 0),
        amusement=emotions_dict.get('amusement', 0),
        gratitude=emotions_dict.get('gratitude', 0)
    )

    print("COMMITTING EMOTION DATA")
    db.session.add(emotions)
    db.session.commit()

    print("SUCCESS commiting emotions")

    # print(emotions)
    return  emotions.id


def add_entry(text, weather_id, emotion_id, user_id):
  

    print("Adding entry:", text)

    # Create a new Entry object with weather_id and emotion_id
    new_entry = Entry(text=text, weather_id=weather_id, emotion_id=emotion_id, user_id=user_id)

    # Debug: Print new_entry to see if it's created correctly
    print("New Entry:", new_entry)

    print("COMMITTING ENTRY DATA")

    # Add the new entry to the session
    db.session.add(new_entry)
    db.session.commit()

    # return new_entry
    return new_entry

# order by emotional valence and arousal
def desired_order(data):
    df = pd.DataFrame(data)
    desired_order =[
        'excitement', 'amusement', 'joy', 'optimism', 'love', 'caring', 'gratitude', 'relief',
        'curiosity', 'surprise', 'desire', 'confusion', 'realization', 'approval', 'admiration', 'pride',
        'disgust', 'sadness', 'grief', 'disappointment', 'remorse', 'embarrassment', 'fear', 'nervousness', 'annoyance', 'anger'
    ]
    ordered_data_by_emotion = df[desired_order]
    return ordered_data_by_emotion

def plot_heatmap(heatmap_data, title, xlabel, ylabel):

    ordered_heatmap_data = desired_order(heatmap_data)

    plt.figure(figsize=(12, 6))
    sns.heatmap(ordered_heatmap_data, annot=False, cmap='RdPu', norm=LogNorm())
    plt.title(title, fontsize = 20, pad=20)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

    

    # Save to BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf-8')

    # Close the figure
    plt.close()

    return plot_url


def get_frequent_words(num_words =20):
    all_text= get_all_text()
    tokens = word_tokenize(all_text)
    tokens = [word.lower() for word in tokens if word.isalpha()] # Keep all text lower

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    # Perform POS tagging
    tagged = pos_tag(tokens)

    # Filter words based on POS tags
    filtered_words = [word for word, tag in tagged]
    print("FILTERED WORDS:", filtered_words)

    # Get the frequency distribution of the filtered words
    word_freq = Counter(filtered_words)

    # Get the most common words
    most_frequent_words = word_freq.most_common(num_words)[:10]

    print("MOST COMMON WORDS:", most_frequent_words)
    return most_frequent_words


#  list of emotions for top emotions
emotion_fields = [
    func.sum(Emotions.gratitude),
    func.sum(Emotions.admiration),
    func.sum(Emotions.joy),
    func.sum(Emotions.approval),
    func.sum(Emotions.caring),
    func.sum(Emotions.pride),
    func.sum(Emotions.excitement),
    func.sum(Emotions.relief),
    func.sum(Emotions.optimism),
    func.sum(Emotions.realization),
    func.sum(Emotions.love),
    func.sum(Emotions.annoyance),
    func.sum(Emotions.desire),
    func.sum(Emotions.disapproval),
    func.sum(Emotions.sadness),
    func.sum(Emotions.surprise),
    func.sum(Emotions.disappointment),
    func.sum(Emotions.remorse),
    func.sum(Emotions.grief),
    func.sum(Emotions.amusement),
    func.sum(Emotions.confusion),
    func.sum(Emotions.anger),
    func.sum(Emotions.curiosity),
    func.sum(Emotions.disgust),
    func.sum(Emotions.fear),
    func.sum(Emotions.embarrassment),
    func.sum(Emotions.nervousness)
]

def get_today_emotions(db, user_id, today):
    return db.session.query(
        *emotion_fields
    ).join(Entry, Entry.emotion_id == Emotions.id).filter(
        Entry.user_id == user_id,
        func.strftime('%Y-%m-%d', Entry.timestamp) == func.strftime('%Y-%m-%d', today)
    ).group_by(func.strftime('%Y-%m-%d', Entry.timestamp)).first()

def get_week_emotions(db, user_id, week_start):
    result = db.session.query(
        *emotion_fields
    ).join(Entry, Entry.emotion_id == Emotions.id).filter(
        Entry.user_id == user_id,
        func.strftime('%Y-%W', Entry.timestamp) == func.strftime('%Y-%W', week_start)
    ).group_by(func.strftime('%Y-%W', Entry.timestamp)).first()
    return result

def get_all_emotions(db, user_id):
    return db.session.query(
        *emotion_fields
    ).join(Entry, Entry.emotion_id == Emotions.id).filter(
        Entry.user_id == user_id
    ).first()

def get_top_emotions_agg(aggregated_emotions_instance):
    if aggregated_emotions_instance is None:
        return []
    
    print("Aggregated Emotions Instance:", aggregated_emotions_instance)

    # Pair each emotion name with its corresponding value
    emotions = list(zip(emotion_names, aggregated_emotions_instance))

    # Filter out emotions with zero score and sort by score
    top_emotions = sorted([emotion for emotion in emotions if emotion[1]], key=lambda x: x[1], reverse=True)

    # You may choose to return top 3, top 5, etc., based on your requirement
    return top_emotions[:3]

def calculate_percent_change(old, new):
    if old == 0:
        return float('inf')  # or handle division by zero differently
    return ((new - old) / old) * 100

def get_last_week_emotions(db, user_id, last_week_start, last_week_end):
    return db.session.query(
        *emotion_fields
    ).join(Entry, Entry.emotion_id == Emotions.id).filter(
        Entry.user_id == user_id,
        Entry.timestamp >= last_week_start,
        Entry.timestamp <= last_week_end
    ).group_by(func.strftime('%Y-%W', Entry.timestamp)).first()

