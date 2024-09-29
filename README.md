# Recipe Recommender System

This is a Flask-based Recipe Recommender system that suggests recipes based on the ingredients you have. It includes features such as user authentication (signup/login), recipe liking, and text-to-speech functionality to speak the recommended recipe aloud.

# Features

- **User Registration and Login**: Users can sign up and log in to the platform using their credentials.
- **Recipe Recommendation**: Suggests a recipe based on the user's input ingredients.
- **Like Recipe**: Users can like recipes and view them on their dashboard.
- **Text-to-Speech**: The recommended recipe's name, ingredients, and steps are read aloud using Google's `gTTS` API.
- **MySQL Database Integration**: User and liked recipe data are stored in a MySQL database using SQLAlchemy ORM.

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **Machine Learning**: TF-IDF Vectorizer, Cosine Similarity
- **Text-to-Speech**: Google Text-to-Speech (`gTTS`)
- **Front-end**: HTML, CSS, Jinja2 templating

## Prerequisites

Make sure you have the following installed:

- Python 3.x
- MySQL
- Flask

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/SumitC962/recipe-recommender.git
   cd recipe-recommender
