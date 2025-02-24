from flask import Flask, request, render_template
from textblob import TextBlob
import sqlite3
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Function to analyze sentiment and recommend tasks
def analyze_mood(text):
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity  # Score between -1 to 1

    if sentiment_score > 0:
        return "Positive 😊", ["Creative Work", "Team Meetings", "Brainstorming"]
    elif sentiment_score < 0:
        return "Negative 😞", ["Break Time", "Meditation", "Light Tasks"]
    else:
        return "Neutral 😐", ["Routine Work", "Email Responses", "Documentation"]

# Function to store employee mood in database
def save_mood(employee_name, mood):
    conn = sqlite3.connect('employee_moods.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS mood_history
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, mood TEXT)''')
    cursor.execute("INSERT INTO mood_history (name, mood) VALUES (?, ?)", (employee_name, mood))
    conn.commit()
    conn.close()

# Function to get team mood analytics
def get_team_mood():
    conn = sqlite3.connect('employee_moods.db')
    df = pd.read_sql_query("SELECT mood FROM mood_history", conn)
    conn.close()
    return df['mood'].value_counts().to_dict()  # Return mood counts

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        employee_name = request.form["name"]
        user_input = request.form["text"]
        
        # Analyze sentiment and get tasks
        mood, recommended_tasks = analyze_mood(user_input)
        
        # Save mood to database
        save_mood(employee_name, mood)
        
        # Get overall team mood
        team_mood = get_team_mood()

        return render_template("index.html", mood=mood, tasks=recommended_tasks, team_mood=team_mood)

    return render_template("index.html", mood=None, tasks=None, team_mood=None)

if __name__ == "__main__":
    app.run(debug=True)
