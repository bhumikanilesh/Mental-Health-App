from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)


sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)


def init_db():
    conn = sqlite3.connect('emotions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emotions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME,
                  text TEXT,
                  sentiment TEXT,
                  score FLOAT)''')
    conn.commit()
    conn.close()

init_db()

CRITICAL_WORDS = ['suicide', 'kill myself', 'self harm', 'end it all', 
                 'want to die', 'harm myself', 'no reason to live']

def check_critical(text):
    text_lower = text.lower()
    return any(word in text_lower for word in CRITICAL_WORDS)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'feeling' not in data:
        return jsonify({"error": "No feeling provided."}), 400

    text = data['feeling']
    sentiment_result = analyze_sentiment(text)
    
    if isinstance(sentiment_result, tuple):
        sentiment, score = sentiment_result
    else:
        return jsonify({"error": sentiment_result}), 500
    
    is_critical = check_critical(text)
    
    # Store in database
    conn = sqlite3.connect('emotions.db')
    c = conn.cursor()
    c.execute("INSERT INTO emotions (timestamp, text, sentiment, score) VALUES (?, ?, ?, ?)",
              (datetime.now(), text, sentiment, score))
    conn.commit()
    conn.close()
    
    suggestion = generate_suggestion(sentiment)
    
    return jsonify({
        "sentiment": sentiment,
        "score": score,
        "suggestion": suggestion,
        "is_critical": is_critical,
        "model": "distilbert-base"
    })

@app.route('/report', methods=['GET'])
def generate_report():
    conn = sqlite3.connect('emotions.db')
    c = conn.cursor()
    
    # Get today's entries
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT sentiment, score FROM emotions WHERE date(timestamp) = ?", (today,))
    results = c.fetchall()
    
    # Get historical data (last 30 days)
    c.execute("""
        SELECT date(timestamp) as day, 
               AVG(CASE WHEN sentiment = 'POSITIVE' THEN 1 ELSE 0 END) as positive_pct,
               COUNT(*) as total_entries
        FROM emotions
        WHERE date(timestamp) >= date('now', '-30 days')
        GROUP BY date(timestamp)
        ORDER BY day DESC
    """)
    history = c.fetchall()
    
    conn.close()
    
    # Process today's data
    total = len(results)
    sentiment_count = {
        "POSITIVE": 0,
        "NEGATIVE": 0,
        "NEUTRAL": 0
    }
    avg_score = 0
    
    for sentiment, score in results:
        sentiment_count[sentiment] += 1
        avg_score += score
    
    if total > 0:
        avg_score = avg_score / total
        positive_pct = (sentiment_count["POSITIVE"] / total) * 100
        negative_pct = (sentiment_count["NEGATIVE"] / total) * 100
        neutral_pct = (sentiment_count["NEUTRAL"] / total) * 100
    else:
        positive_pct = negative_pct = neutral_pct = avg_score = 0
    
    # Process historical data
    history_data = [{
        "date": row[0],
        "positive_pct": row[1] * 100,
        "total_entries": row[2]
    } for row in history]
    
    # Generate recommendations
    recommendations = []
    if sentiment_count["NEGATIVE"] >= 2:
        recommendations.extend([
            "Consider speaking with a therapist or counselor",
            "Physical exercise can help improve mood - try a short walk",
            "Practice mindfulness or meditation exercises"
        ])
    elif sentiment_count["POSITIVE"] >= 2:
        recommendations.append("Great job! Keep doing activities that make you happy")
    else:
        recommendations.append("Your mood seems balanced. Try journaling to identify patterns")
    
    if any(check_critical(entry[1]) for entry in results if len(results) > 0):
        recommendations.insert(0, "⚠️ We detected concerning content. Please seek professional help if needed")
    
    return jsonify({
        "today": {
            "total_entries": total,
            "positive_pct": positive_pct,
            "negative_pct": negative_pct,
            "neutral_pct": neutral_pct,
            "avg_score": avg_score,
            "sentiment_distribution": sentiment_count
        },
        "history": history_data,
        "recommendations": recommendations
    })

def analyze_sentiment(text):
    try:
        if not text.strip():
            return "Empty text provided"
            
        result = sentiment_analyzer(text[:512])[:1]  # Truncate long texts
        return result[0]['label'].upper(), result[0]['score']
    except Exception as e:
        return f"Error analyzing sentiment: {str(e)}"

def generate_suggestion(emotion):
    suggestions = {
        "NEGATIVE": "It seems you're having a tough time. Remember that difficult emotions are temporary.",
        "POSITIVE": "That's wonderful! Savor these positive feelings.",
        "NEUTRAL": "It's okay to feel neutral. Pay attention to subtle emotions."
    }
    return suggestions.get(emotion, "Thanks for sharing how you feel.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)