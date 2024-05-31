import os

from flask import Flask, flash, redirect, render_template, request, session,  url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from helpers import login_required, apology, fetch_weather, emotions_hf, add_entry, plot_heatmap, get_frequent_words, get_today_emotions, get_week_emotions, get_all_emotions, get_top_emotions_agg, get_last_week_emotions, calculate_percent_change, emotion_names
    # plot_stacked_chart
from extensions import db
from datetime import datetime, timedelta

from models import Weather, Entry, Emotions, Users

# heatplot
from data_utils import get_extracted_data, transformed_data_daily, transformed_data_entry, transformed_data_weather
import seaborn as sns
import matplotlib
matplotlib.use('Agg') # Set a non-GUI backend

# row span
from collections import defaultdict
from itertools import groupby
from operator import attrgetter

# most emotions
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Configure session to use signed cookies
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # Configure the database URI for Heroku
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///entries.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app,db)	

    # Additional setup like registering blueprints

    return app

app = create_app()
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    
# Initialize database
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    app.logger.debug("Entering the index route")
    return render_template("index.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Enter Username")
        
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            return apology("Username already exists")

        if not password:
            return apology("Must provide password")

        if password != confirmation:
            return apology("Password and confirmation not the same")

        hash = generate_password_hash(password, method="pbkdf2", salt_length=16)

        new_user = Users(username=username, hash=hash)
        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id

        return render_template("record.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", 403)

        if not password:
            return apology("must provide password", 403)

        user = Users.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.hash, password):
            return apology("invalid username and/or password", 403)

        session["user_id"] = user.id
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



   

@app.route("/record", methods=["GET", "POST"])
@login_required
def record():

    if request.method == "GET":
        print("STARTING STARTING STARTING RECORDING")
        return render_template("record.html",  timestamp = datetime.now())

    if request.method == "POST":
        if 'user_id' in session:
            # Get user_id from session
            user_id = session['user_id']

            print("FORM DATA RECEIVED")

            # Get location data sent from JavaScript
            # location_data = request.get_json()
            # lat = location_data.get('latitude')
            # lon = location_data.get('longitude')

            lat=42.3825824
            lon=-71.1198

            # fetch user input
            user_entry = request.form.get('user_entry', '')  # Provide an empty string as the default value

            if user_entry:
                #  get weather and emotion ID as well as activate functions
                weather_id = fetch_weather(lat, lon)
                emotion_id = emotions_hf(user_entry)

                # ADD EMITION entry to database
                add_entry(user_entry, weather_id, emotion_id, user_id)
                
                new_entry = Entry.query.filter(Entry.user_id == user_id).order_by(Entry.id.desc()).first()


            else:
                
                print("empty user entry not adding to database.")
            # Redirect to the form page or a confirmation page
            return render_template('record.html', user_entry = user_entry, timestamp = datetime.now(), new_entry=new_entry) 
        
        return redirect(url_for('record'))
    else:
        return None


@app.route('/history')
@login_required
def history():
    if request.method == "GET":
        if session["user_id"]:
            user_id = session['user_id']
            entries = Entry.query.filter(Entry.user_id == user_id).order_by(Entry.id.desc()).all()  # This fetches all entries from the database

            # ROW SPAN
            # Assuming 'entries' is your list of entry objects
            entries_with_rowspan = []
            date_to_rowspan = defaultdict(int)

            # Group by date and count entries per date
            for date, group in groupby(entries, key=lambda x: x.timestamp.date()):
                date_to_rowspan[date] = sum(1 for _ in group)

            # Add rowspan information to entries
            for entry in entries:
                date = entry.timestamp.date()
                rowspan = date_to_rowspan.pop(date, None)
                entries_with_rowspan.append((entry, rowspan))

            return render_template('history.html', entries=entries_with_rowspan)

@app.route("/analyze", methods=["GET", "POST"])
@login_required
def analyze():    
    if request.method == "GET":
        if 'user_id' in session:
            
            user_id = session['user_id']
            # entries = Entry.query.filter(Entry.user_id == user_id).order_by(Entry.id.desc()).all()  # This fetches all entries from the database

            # get top emotions
            # Current datetime
            now = datetime.now()
            # Get times
            today = datetime.now().date() # Current date
            week_start = now - timedelta(days=now.weekday())  # Assuming week starts on Monday
            last_week_start = week_start - timedelta(days=7)
            last_week_end = week_start - timedelta(days=1)

            # get aggregated emotions
            today_emotions = get_today_emotions(db, user_id, today)
            week_emotions = get_week_emotions(db, user_id, week_start)
            overall_emotions = get_all_emotions(db, user_id)

            top_today_emotions = get_top_emotions_agg(today_emotions)
            top_week_emotions = get_top_emotions_agg(week_emotions)
            top_overall_emotions = get_top_emotions_agg(overall_emotions)

            # PERCENT CHANGE

            # Assuming you have functions to get last_week_start and last_week_end dates
            last_week_emotions = get_last_week_emotions(db, user_id, last_week_start, last_week_end)
            this_week_emotions = get_week_emotions(db, user_id, week_start)

            # Calculating percent changes for each emotion
            percent_changes = {}
            for emotion in emotion_names :
                old_value = getattr(last_week_emotions, emotion, 0)
                new_value = getattr(this_week_emotions, emotion, 0)
                percent_changes[emotion] = calculate_percent_change(old_value, new_value)


            # get frequent wordsF
            frequent_words= get_frequent_words() 

            #extract data
            extracted_data = get_extracted_data()

            # # stackplot here
            # stacked_data = transform_data_for_stacked_chart(extracted_data)
            # stacked_plot_url= plot_stacked_chart(stacked_data, title="Emotional Fluctuations", xlabel="Time", ylabel="Emotions")
            
            # heat map here
            heatmap_data_daily = transformed_data_daily(extracted_data) 
            heatmap_data_entry = transformed_data_entry(extracted_data) 
            heatmap_data_weather = transformed_data_weather(extracted_data) 

            # Initialize an empty list to store heatmap URLs
            heatmap_plot_urls = []

            # Append URLs for each heatmap to the list
            heatmap_plot_urls.append(plot_heatmap(heatmap_data_daily, title="Emotion Change - Daily", xlabel="Emotion", ylabel="Day"))
            heatmap_plot_urls.append(plot_heatmap(heatmap_data_entry, title="Emotion Change - Entry", xlabel="Emotion", ylabel="Entry"))
            heatmap_plot_urls.append(plot_heatmap(heatmap_data_weather, title="Emotion Change - Weather", xlabel="Emotion", ylabel="Weather"))

            # # data for d3js
            # emotion_data_json = get_emotion_data_json()

            return render_template("pattern.html", heatmap_plot_urls=heatmap_plot_urls, frequent_words=frequent_words, top_today_emotions=top_today_emotions, top_week_emotions=top_week_emotions, top_overall_emotions=top_overall_emotions, percent_changes=percent_changes)


