from extensions import db  # Import the SQLAlchemy database instance from your Flask app
from models import Entry, Emotions, Weather, Users  # Import your model classes
import pandas as pd
from flask_session import Session
from flask import session, current_app
from sqlalchemy.orm import  aliased


def get_all_text():
    # Check if user_id is in session
    if 'user_id' in session:
        user_id = session['user_id']
        # Query to retrieve all text entries
        text_entries = db.session.query(Entry.text).filter(Entry.user_id == user_id).all()

        # This will give you a list of tuples, so you need to extract the text from each tuple
        text_entries = [entry[0] for entry in text_entries]

        # Join all text entries into a single string
        all_text = ' '.join(text_entries)
        return all_text
    else:
        return None
    
    


def get_extracted_data():
    # # Check if user_id is in session
    # if 'user_id' in session:
    #     user_id = session['user_id']
        
    #     try:
    #         # Use SQLAlchemy to query data
    #         emotion_columns = [col for col in Emotions.__table__.columns if col.key not in ('id', 'neutral')]

    #         query = db.session.query(
    #             Entry, Weather,
    #             *emotion_columns  # Expands to all columns in the Emotions table except 'id'
    #         ).join(Emotions, Entry.emotion_id == Emotions.id)\
    #         .join(Weather, Entry.weather_id == Weather.id)\
    #         .filter(Entry.user_id == user_id) 

    #         current_app.logger.info("Query: %s", query)
    #         statement = query.statement
    #         current_app.logger.info("Statement: %s", statement)

    #         # Execute the query and convert to DataFrame
    #         extracted_data = pd.read_sql_query(statement, db.session.bind)
    #         current_app.logger.info('Extracted Data Columns: %s', extracted_data.columns)

    #         return extracted_data

    #     except Exception as e:
    #         current_app.logger.error(f"Error in get_extracted_data: {e}")
    #         raise
    # else:
    #     current_app.logger.warning("No user_id in session")
    #     return None

    
    # Check if user_id is in session
    if 'user_id' in session:
        user_id = session['user_id']
            
        # Use SQLAlchemy to query data
        emotion_columns = [col for col in Emotions.__table__.columns if col.key not in ('id', 'neutral')]
        # emotion_columns = [col for col in Emotions.__table__.columns if col.key != 'id']
        
        query = db.session.query(
            Entry, Weather,
            *emotion_columns  # Expands to all columns in the Emotions table except 'id'
        ).join(Emotions, Entry.emotion_id == Emotions.id)\
        .join(Weather, Entry.weather_id == Weather.id)\
        .filter(Entry.user_id == user_id) 

        print ("Query:" , query)
        statement = query.statement
        print ("Statement:" , statement)
        # Execute the query and convert to DataFrame
        extracted_data = pd.read_sql_query(statement, db.session.connection())
        print('EXATRACTED DATA COLUMNS:', extracted_data.columns)

        return extracted_data
    else:
        return None

def transform_data_for_d3(extracted_data):
    # Convert 'timestamp' to just the date part if it includes time
    extracted_data['date'] = pd.to_datetime(extracted_data['timestamp']).dt.date

    # Select only emotion-related columns and the date
    emotion_columns = ['gratitude', 'admiration', 'joy', 'approval', 'caring',
                       'pride', 'excitement', 'relief', 'optimism', 'realization', 'love',
                       'annoyance', 'desire', 'disapproval', 'sadness', 'surprise',
                       'disappointment', 'remorse', 'grief', 'amusement', 'confusion', 'anger',
                       'curiosity', 'disgust', 'fear', 'embarrassment', 'nervousness']
    emotion_data = extracted_data[['date'] + emotion_columns]

    # Pivot data to have dates as rows and emotions as columns
    # This assumes that there is only one entry per emotion per day
    pivoted_data = emotion_data.pivot(index='date', columns=emotion_columns)

    # Reset index to make 'date' a column again
    pivoted_data.reset_index(inplace=True)

    return pivoted_data

def get_emotion_data_json():
    extracted_data = get_extracted_data()
    if extracted_data is not None:
        transformed_data = transform_data_for_d3(extracted_data)
        return transformed_data.to_json(orient='records')
    return jsonify([])
    
def transformed_data_daily(extracted_data):
    # Ensure timestamps are in the right format
    extracted_data['timestamp'] = pd.to_datetime(extracted_data['timestamp']).dt.date

    # Pivot the DataFrame to get timestamps as rows and emotions as columns
    heatmap_data = extracted_data.pivot_table(index='timestamp', 
                                  values=[
                                      'gratitude', 'admiration', 'joy', 
                                      'approval', 'caring', 'pride', 
                                      'excitement', 'relief', 
                                      'optimism', 'realization', 'love', 
                                      'annoyance', 'desire', 'disapproval', 
                                      'sadness', 'surprise', 'disappointment', 
                                      'remorse', 'grief', 'amusement', 
                                      'confusion', 'anger', 'curiosity', 
                                      'disgust', 'fear', 'embarrassment', 
                                      'nervousness'
                                  ],
                                  aggfunc='mean')  # You can change the aggregation function as needed

    return heatmap_data

def transformed_data_entry(extracted_data):
    # Assuming 'entry_id' is the unique identifier for each entry and 'timestamp' is the timestamp

    # Convert 'timestamp' column to datetime format if it's not already
    extracted_data['timestamp'] = pd.to_datetime(extracted_data['timestamp'])
    
    # Create a combined identifier
    extracted_data['entry_identifier'] = extracted_data['id'].astype(str) + ' - ' + extracted_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Pivot the DataFrame to get timestamps as rows and emotions as columns
    heatmap_data = extracted_data.pivot_table(index='entry_identifier', 
                                  values=[
                                      'gratitude', 'admiration', 'joy', 
                                      'approval', 'caring', 'pride', 
                                      'excitement', 'relief', 
                                      'optimism', 'realization', 'love', 
                                      'annoyance', 'desire', 'disapproval', 
                                      'sadness', 'surprise', 'disappointment', 
                                      'remorse', 'grief', 'amusement', 
                                      'confusion', 'anger', 'curiosity', 
                                      'disgust', 'fear', 'embarrassment', 
                                      'nervousness'
                                  ],
                                  aggfunc='mean') 

    return heatmap_data

def transformed_data_weather(extracted_data):


    # Pivot the DataFrame to get timestamps as rows and emotions as columns
    heatmap_data = extracted_data.pivot_table(index='description', 
                                  values=[
                                      'gratitude', 'admiration', 'joy', 
                                      'approval', 'caring', 'pride', 
                                      'excitement', 'relief', 
                                      'optimism', 'realization', 'love', 
                                      'annoyance', 'desire', 'disapproval', 
                                      'sadness', 'surprise', 'disappointment', 
                                      'remorse', 'grief', 'amusement', 
                                      'confusion', 'anger', 'curiosity', 
                                      'disgust', 'fear', 'embarrassment', 
                                      'nervousness'
                                  ],
                                  aggfunc='mean') 

    return heatmap_data


# def transform_data_for_stacked_chart(extracted_data):
#     print("Inside function: ", extracted_data.columns)

#     # Ensure 'timestamp' column is present
#     if 'timestamp' not in extracted_data.columns:
#         raise KeyError("timestamp column not found in extracted_data")

#     # Convert 'timestamp' column to datetime format if it's not already
#     extracted_data['timestamp'] = pd.to_datetime(extracted_data['timestamp'])

#     # Create a combined identifier
#     extracted_data['entry_identifier'] = extracted_data['id'].astype(str) + ' - ' + extracted_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

#     # Select the emotion columns
#     emotion_columns = [
#         # ... your emotion columns ...
#         'gratitude', 'admiration', 'joy', 
#         'approval', 'caring', 'pride', 
#         'excitement', 'relief', 
#         'optimism', 'realization', 'love', 
#         'annoyance', 'desire', 'disapproval', 
#         'sadness', 'surprise', 'disappointment', 
#         'remorse', 'grief', 'amusement', 
#         'confusion', 'anger', 'curiosity', 
#         'disgust', 'fear', 'embarrassment', 
#         'nervousness'
#     ]

#     # Calculate the sum of emotion scores for each row
#     total_emotions = extracted_data[emotion_columns].sum(axis=1)
    
#     # Normalize the emotion scores to percentages, handle zero division
#     extracted_data[emotion_columns] = extracted_data[emotion_columns].div(total_emotions.replace(0, 1), axis=0)

#     # Replace NaN with 0
#     extracted_data[emotion_columns] = extracted_data[emotion_columns].fillna(0)

#     # Melt the DataFrame to long format
#     long_df = extracted_data.melt(id_vars=['entry_identifier'], value_vars=emotion_columns, var_name='Emotion', value_name='Percentage')

#     return long_df