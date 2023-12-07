# Emotion Tracker

## Project Overview
The Emotion Tracker is a web-based application designed to help users track and understand their emotional fluctuations. It allows users to record their thoughts, analyzes these thoughts for emotional content, correlates them with current weather conditions, and visualizes emotional trends.

## Key Features
- Thought recording with emotional analysis
- Weather data integration
- Emotional trend visualization
- User authentication for personalized tracking

## Technical Requirements
This project is built using Flask, Django, HTML, CSS, Bootstrap, SQLAlchemy, Python, HuggingFace, and other Python libraries as specified in the requirements document.

## Installation Instructions
1. Clone the repository.
2. Ensure Python is installed on your system.
3. Install the required Python packages:

pip install -r requirements.txt


## Setting Up the Database
1. The project uses SQLAlchemy for database interactions. Ensure the database configuration is set in `app.py`.
2. Initialize the database within the Flask application context:

(in scss)
with app.app_context():
 db.create_all()


## Configuring the Application
1. The Flask application is configured to use environment variables for sensitive information like database URIs.
2. Flask sessions are configured to use the filesystem.

## Running the Application
1. Start the application with:

python app.py
(Or if running in VScode flask run)


2. Access the application at `http://localhost:5000`.

## Application Structure
- **app.py**: Contains the Flask application setup and routes.
- **models.py**: Defines the database models for SQLAlchemy.
- **helpers.py**: Contains helper functions for the application, including user authentication, weather data fetching, and emotion analysis.
- **data_utils.py**: Includes functions for data transformation and analysis.
- **extensions.py**: Sets up extensions like SQLAlchemy.

## Usage Guide
- **Registration and Login**: Users can register and log in to access personalized emotion tracking.
- **Recording Thoughts**: Users can record their thoughts, which are then analyzed for emotional content and correlated with current weather data.
- **Visualization**: The application provides various visualizations of emotional trends based on user entries.

## Troubleshooting
- Check if all required environment variables are set correctly.
- Ensure that all dependencies listed in `requirements.txt` are installed.

## Contribution Guidelines
Contributions to the project are welcome. Please follow standard practices for submitting pull requests.