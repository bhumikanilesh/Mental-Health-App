#Mood Tracker
A Flask web app for tracking emotions with sentiment analysis, user authentication, and personalized reports.
Features

Sentiment Analysis: Uses distilbert-base-uncased-finetuned-sst-2-english model for emotion analysis.
User Authentication: Secure login/register/logout with password hashing.
Emotion Tracking: Stores emotions in SQLite with timestamps and scores.
Critical Content Detection: Flags concerning inputs for safety.
Responsive Design: User-friendly interface with custom CSS.
Reports: View recent emotions for authenticated users.

Prerequisites

Python 3.8+
SQLite3
Internet for downloading the transformers model

Installation

Clone the repo:git clone https://github.com/your-username/mood-tracker.git
cd mood-tracker


Set up virtual environment:python -m venv env
source env/bin/activate  # macOS/Linux
env\Scripts\activate     # Windows


Install dependencies:pip install -r requirements.txt


Database initializes automatically on startup.

Usage

Run the app:python app.py


Visit http://localhost:5000 in your browser.
Register, log in, and submit feelings to track emotions.
View reports at /report.

Project Structure
mood-tracker/
├── app.py                # Main Flask app
├── mental-health.py      # Version without authentication
├── requirements.txt      # Dependencies
├── style.css             # Custom CSS
├── templates/
│   ├── index.html        # Main page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── layout.html       # Base template
│   └── report.html       # Report page
├── emotions.db           # SQLite database (auto-created)

Dependencies
Key packages (full list in requirements.txt):

Flask==3.1.1
flask-login==0.6.3
flask-bcrypt==1.0.1
transformers==4.52.4
torch==2.7.1

Configuration

Set a secure app.secret_key in app.py for production:app.secret_key = 'your-secure-secret-key'


Ensure emotions.db is writable.

Notes

Debug mode is enabled by default; disable in production.
transformers model requires sufficient memory.
Enhance critical content detection for production use.

Contributing

Fork the repo.
Create a branch (git checkout -b feature-name).
Commit changes (git commit -m "Add feature").
Push branch (git push origin feature-name).
Open a pull request.

