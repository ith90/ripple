# Design Document for Emotion Tracker

## Overview
The Emotion Tracker is a web-based application designed for tracking and analyzing users' emotions over time. The application combines user-submitted text entries, weather data integration, and advanced emotion analysis to provide insights into how emotional states correlate with external factors like weather.

## Architecture

### Backend
The backend is structured around the Flask framework, chosen for its lightweight nature and flexibility. Flask is ideal for small to medium-sized web applications due to its simplicity for running simple apps on python, and its ability to create apps that have database interactions. *Flask sessions* were used to manage user sessions, so that different users can log in, and have acess to their own thought entries and emotional analysis. *Flask SQLAlchemy* was used because of its ability for schema migrations.

### Frontend
The frontend employs HTML, CSS, Djanga, and Bootstrap. This stack was chosen for its efficiency in creating responsive and visually appealing user interfaces. *Bootstrap* was used for its ability to develop responsive design, and an simple solution for controlling the aesthetics and style of the site. *CSS* was used for minimal tweeks in style. *Jinja2* was used as a templating engine for flask, and was used to render templates, with template inheritance, and its ability to dynamically render content while passing through variables.

### Database
SQLite, via SQLAlchemy was used as a light weight database especially considering the ease of setup and low maintenance requirements. In the current database Entries.db, `models.py` defines the structure of the database, containing models for `Weather`, `Entry`, `Emotions`, and `Users`. This modular approach allows for clear separation of concerns and ease of data management. The `Entry`table is the main table that connects  `Weather`, `Emotions`, and `Users` this is because the most imporant entry into the database that sets off all other functions is the add_entry function, which is triggered when the user submits an entry.

## Core Functionalities

The core functionalities of this web app include: Entry logging, Emotion Analysis, Weather Data Integration, and Data Visualization. This is because the app should ultimately be able to help users understand their emotions through time and seasons.

- **Emotion Analysis** For emotion analysis, the application leverages HuggingFace's transformer models. These models provide Natural Language Processing capabilities, which are crucial for accurately discerning emotions from text. This particular model used called Roberta-base-go_emotions by SamLowe (https://huggingface.co/SamLowe/roberta-base-go_emotions) is trained with a large reddit entry database.

- **Weather Data Integration** Real-time weather data is fetched using the OpenWeatherMap API. This integration was chosen to investigate the potential correlation between weather conditions and emotional states. 

- **Data Visualization** Data visualization is implemented using Seaborn and Matplotlib with heatmap plots. These Python libraries were selected for their extensive functionality and ease of integration with Flask. They are good for representing emotional trends and patterns in an easily digestible format. Another useful chart would be the stacked chart. Interactive visualizations would have also been nice from D3.js.

## Code Organization

The application's codebase is divided into several modules:
- **app.py**: Serves as the entry point of the Flask application, defining routes and the core app logic.
- **helpers.py**: Contains utility functions that help app.py including user authentication, API interactions for weather data fetching, and emotion analysis.
- **data_utils.py**: Dedicated to data processing and transformation tasks, particularly for preparing data for visualizations.
- **extensions.py**: Initializes Flask extensions like SQLAlchemy.

## Security and User Authentication

Security considerations are central to the application's design, particularly because it handles personal user data:
- **Werkzeug Security** was employed for hashing and verifying user passwords. 
- **Flask Session Management** was used to manage user sessions, a critical feature for maintaining security and user-specific data access throughout the application.

## Challenges and Solutions

1. One of the main challenges was to analyze and provide insight and visualizations to the emotional analysis in a meaningful way. This may have to be a Phase 2 of this project. 
2. I would have liked to taken advantage of Bootstrap's more to design a more responsive environment, especially if accessed by a phone.
3. It was challenging to get a recording as user input and analyzing audio for emotions. It would be a great next step, along with emotion recognition for faces.

## Future Enhancements
- Better data visualization, possibly interactive dashboard.
- Face and voice analysis for emotion.
- A way to text this web app, instead of having to log on.