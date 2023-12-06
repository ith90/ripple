import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import speech_recognition as sr
import pyttsx3
from extensions import db
from models import Weather, Entry, Emotions, Users
from flask import redirect, render_template, session, request, jsonify
from functools import wraps
import pandas as pd

# HUGGINGFACE
from transformers import AutoTokenizer, pipeline, AutoModelForSequenceClassification
from scipy.special import softmax

# heatplot
from data_utils import get_extracted_data, get_all_text
    #transform_data_for_stacked_chart
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Circle

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

# FOR CIRCUMPLEX
import numpy as np

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

# def speech_to_text(audio_file_path):
#     """Convert speech from an audio file to text."""
#     recognizer = sr.Recognizer()

#     with sr.AudioFile(audio_file_path) as source:
#         audio_data = recognizer.record(source)
#         try:
#             text = recognizer.recognize_google(audio_data)
#             return text.lower()
#         except sr.UnknownValueError:
#             return "Google Speech Recognition could not understand audio"
#         except sr.RequestError as e:
#             return f"Could not request results from Google Speech Recognition service; {e}"
#         except Exception as e:
#             return f"An error occurred: {e}"




# def speech_to_text(speech):
#     """Speech to text"""
#     recognizer = speech_recognition.Recognizer()
    
#     while True:
        
#         try:

#             with speech_recognition.Microphone() as mic:
#                 recognizer.adjust_for_ambient_noise(mic, duration=0.2)
#                 audio = recognizer.listen(mic)

#                 text = recognizer.recognize_google(audio)
#                 text = text.lower()

#                 print(f"Reecognizeed {text}")

#         except speech_recognition.UnknownValueError():
            
#             recognizer = speech_recognition.Recognizer()
#             continue


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
    classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

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

# def plot_stacked_chart(extracted_data, title, xlabel, ylabel):
#     # Transform data
#     long_df = transform_data_for_stacked_chart(extracted_data)

#     # Plot
#     ax = plt.subplots(figsize=(15, 7))

#     # Initialize a dictionary to keep track of the 'bottom' for each bar stack
#     bottoms = dict.fromkeys(long_df['entry_identifier'].unique(), 0)

#     for emotion in long_df['Emotion'].unique():
#         emotion_data = long_df[long_df['Emotion'] == emotion]
#         ax.bar(emotion_data['entry_identifier'], emotion_data['Percentage'], 
#                bottom=[bottoms[identifier] for identifier in emotion_data['entry_identifier']], 
#                label=emotion)
        
#         # Update the bottoms
#         for identifier, percentage in zip(emotion_data['entry_identifier'], emotion_data['Percentage']):
#             bottoms[identifier] += percentage

#     ax.set_xlabel(xlabel)
#     ax.set_ylabel(ylabel)
#     ax.set_title(title)
#     ax.legend(title="Emotions", bbox_to_anchor=(1.05, 1), loc='upper left')
#     plt.xticks(rotation=45)
#     plt.tight_layout()

#     # Save to BytesIO object
#     img = io.BytesIO()
#     plt.savefig(img, format='png', bbox_inches='tight')
#     img.seek(0)
#     plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
    
#     # Close the figure
#     plt.close()

#     return plot_url

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

# def plot_circumplex():
#     #emotions_data = get_extracted_data()

#     # Sample data: Replace this with your actual emotion data retrieval logic
#     emotions_data = {
#         'Happiness': 0.8,
#         'Sadness': 0.5,
#         'Anger': 0.3,
#         # ... other emotions
#     }

#     # Define the positions of each emotion on the plot
#     # These should be normalized to the range [0, 1] if they represent percentages
#     # or appropriately scaled if they represent some other range of values
#     positions = {
#         'Happiness': (0.75, 0.75),
#         'Sadness': (0.25, 0.75),
#         'Anger': (0.25, 0.25)
#     }

#     colors = {
#         'Happiness': 'green',
#         'Sadness': 'blue',
#         'Anger': 'red',
#     }

#     # Create a plot
#     fig, ax = plt.subplots(figsize=(10,10))

#     # # Plot each emotion as a circle
#     # for emotion, intensity in emotions_data.items():
#     #     circle = Circle(positions[emotion], intensity / 2, alpha=0.5, label=emotion)
#     #     ax.add_patch(circle)

#     # Plot each emotion as a circle with a gradient effect
#     for emotion, intensity in emotions_data.items():
#         position = positions[emotion]
#         color = colors[emotion]
        
#         # Create gradient effect by overlaying multiple circles
#         for i in range(10, 0, -1):  # Decreasing range for overlay effect
#             alpha_value = (i / 10) ** 2  # Exponential decay for alpha value
#             radius = (intensity / 2) * (i / 10)  # Decreasing radius
#             circle = Circle(position, radius, alpha=alpha_value, color=color)
#             ax.add_patch(circle)

#     # Customizations
#     ax.set_xlim(0, 1)
#     ax.set_ylim(0, 1)
#     ax.set_xticks([])
#     ax.set_yticks([])
#     ax.set_aspect('equal')
#     ax.legend()

#     # Save to BytesIO object
#     img = io.BytesIO()
#     plt.savefig(img, format='png', bbox_inches='tight')
#     img.seek(0)
#     circumplex_url = base64.b64encode(img.getvalue()).decode('utf-8')

#     # Close the figure
#     plt.close()

#     return circumplex_url