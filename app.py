from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
from gtts import gTTS
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration for database and session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/recipe'
app.config['SECRET_KEY'] = ' '
db = SQLAlchemy(app)

# Load recipe data from a CSV file into a DataFrame
recipe_df = pd.read_csv('recipes.csv')

# Vectorize ingredients using TF-IDF
vectorizer = TfidfVectorizer()
ingredients_matrix = vectorizer.fit_transform(
    recipe_df['ingredients'].apply(lambda x: ', '.join(x.split(', ')))
)

# User signup model for database interaction
class SignUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(12), nullable=True, unique=True)
    password = db.Column(db.String(20), nullable=False)

# Index route - redirects to signup if not logged in
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('signup'))
    return render_template('index.html')

# User signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        if SignUp.query.filter((SignUp.username == username) | (SignUp.email == email)).first():
            flash('Username or email already exists. Please choose a different one.', 'danger')
        else:
            new_user = SignUp(name=name, phone=phone, email=email, username=username, password=password)
            db.session.add(new_user)
            try:
                db.session.commit()
                flash('Registration successful!', 'success')
                session['user_id'] = new_user.id  # Log the user in after signup
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                flash('Error during registration. Please try again.', 'danger')

    return render_template('signup.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = SignUp.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

# Dashboard route for logged-in users
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        user = SignUp.query.get(user_id)
        if user:
            return render_template('dashboard.html', user=user)

    flash('User not found', 'danger')
    return redirect(url_for('login'))

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('signup'))

# Recommendation route
@app.route('/recommendation', methods=['GET'])
def get_recommendation():
    try:
        ingredients_input = request.args.get('ingredients', '').strip()

        # Validate input: Check if ingredients are provided
        if not ingredients_input:
            return jsonify({'error': 'Please provide a valid list of ingredients.'}), 400

        available_ingredients = [ingredient.strip() for ingredient in ingredients_input.split(',') if ingredient.strip()]

        if not available_ingredients:
            return jsonify({'error': 'No valid ingredients provided.'}), 400

        # Convert input ingredients to TF-IDF vector
        input_vector = vectorizer.transform([' '.join(available_ingredients)])

        # Compute cosine similarities
        cosine_similarities = linear_kernel(input_vector, ingredients_matrix).flatten()

        # Check if a matching recipe exists
        if cosine_similarities.max() == 0:
            return jsonify({'error': 'No matching recipe found for the given ingredients.'}), 404

        # Get the most similar recipe
        recommended_index = cosine_similarities.argmax()
        recommended_recipe = recipe_df.iloc[recommended_index]

        # Generate recommendation text
        recommendation_text = (
            f"The recommended recipe is {recommended_recipe['name']} with ingredients "
            f"{recommended_recipe['ingredients']} and steps: {recommended_recipe['steps']}."
        )

        # Convert recommendation text to speech
        tts = gTTS(text=recommendation_text, lang='en')
        tts.save('recommendation.mp3')

        # Play the audio file
        os.system('start recommendation.mp3')

        return render_template('recommendation.html', recommended_recipe=recommended_recipe)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# About route
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)
