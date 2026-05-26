from flask import Flask, render_template, request, jsonify
import os
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename
from urllib.parse import urlparse

from utils.extractor import extract_from_file, extract_from_url
from utils.preprocess import clean_text
from utils.predictor import predict_news

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"

# CREATE UPLOAD FOLDER
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])




def init_db():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # HISTORY TABLE
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            input_type TEXT,
            content TEXT,
            result TEXT,
            confidence INTEGER,
            date TEXT,

            source TEXT,
            category TEXT
        )
    """)


    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            rating INTEGER,
            review TEXT,

            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()




@app.route("/")
def home():

    return render_template("home.html")




@app.route("/analyze", methods=["POST"])
def analyze():

    url = request.form.get("url")
    file = request.files.get("media")

    text = ""
    input_type = ""

    # DEFAULT VALUES
    source = "Unknown"
    category = "General"

    try:

      

        if url and url.strip() != "":

            text = extract_from_url(url)

            input_type = "URL"

         

            domain = urlparse(url).netloc.lower()

            if "bbc" in domain:
                source = "BBC"

            elif "cnn" in domain:
                source = "CNN"

            elif "ndtv" in domain:
                source = "NDTV"

            elif "reuters" in domain:
                source = "Reuters"

            elif "timesofindia" in domain:
                source = "Times of India"

            elif "hindustantimes" in domain:
                source = "Hindustan Times"

            else:
                source = domain

        

        elif file and file.filename != "":

            filename = secure_filename(file.filename)

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(filepath)

            text = extract_from_file(filepath)

            input_type = "File"

            source = "Uploaded File"

     

        else:

            return render_template(
                "result.html",
                result="No input provided",
                content="",
                confidence=0
            )

        if not text or len(text.strip()) == 0:

            return render_template(
                "result.html",
                result="Could not extract text",
                content="",
                confidence=0
            )

       

        cleaned_text = clean_text(text)


        lower_text = text.lower()

        if any(word in lower_text for word in
               ["election", "government", "minister", "politics", "president"]):

            category = "Politics"

        elif any(word in lower_text for word in
                 ["match", "cricket", "football", "sports", "ipl"]):

            category = "Sports"

        elif any(word in lower_text for word in
                 ["technology", "software", "computer", "ai", "mobile"]):

            category = "Technology"

        elif any(word in lower_text for word in
                 ["movie", "actor", "music", "entertainment", "bollywood"]):

            category = "Entertainment"

        elif any(word in lower_text for word in
                 ["health", "hospital", "doctor", "disease", "medicine"]):

            category = "Health"

        elif any(word in lower_text for word in
                 ["science", "space", "nasa", "research"]):

            category = "Science"

        else:
            category = "General"

        # .....prediction...........

        result, confidence = predict_news(cleaned_text)

        # ........database........

        conn = sqlite3.connect("database.db")

        c = conn.cursor()

        c.execute("""

            INSERT INTO history
            (
                input_type,
                content,
                result,
                confidence,
                date,
                source,
                category
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)

        """, (

            input_type,
            text[:500],
            result,
            confidence,

            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            source,
            category
        ))

        conn.commit()

        conn.close()

        #......result........

        return render_template(
            "result.html",
            result=result,
            confidence=confidence,
            content=text[:500]
        )

    except Exception as e:

        return render_template(
            "result.html",
            result="Error occurred",
            content=str(e),
            confidence=0
        )




@app.route("/history")
def history():

    try:

        conn = sqlite3.connect("database.db")

        c = conn.cursor()

        c.execute("""

            SELECT *
            FROM history
            ORDER BY id DESC

        """)

        data = c.fetchall()

        conn.close()

        return render_template(
            "history.html",
            data=data
        )

    except Exception as e:

        return f"Database Error: {e}"
 
@app.route("/reviews")
def reviews():

    conn = sqlite3.connect("database.db")

    c = conn.cursor()

    c.execute("""

        SELECT *
        FROM reviews
        ORDER BY id DESC

    """)

    data = c.fetchall()

    conn.close()

    return render_template(
        "reviews.html",
        data=data
    )
    # ......review api .....

@app.route("/submit_review", methods=["POST"])
def submit_review():

    data = request.get_json()

    rating = data.get("rating")
    review = data.get("review")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""

        INSERT INTO reviews
        (
            rating,
            review,
            created_at
        )

        VALUES (?, ?, ?)

    """, (

        rating,
        review,

        datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Review submitted successfully"
    })


@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database.db")

    c = conn.cursor()

    # TOTAL NEWS CHECKED
    c.execute("SELECT COUNT(*) FROM history")
    total_checked = c.fetchone()[0]

    # REAL NEWS COUNT
    c.execute("""

        SELECT COUNT(*)
        FROM history
        WHERE result='Real News'

    """)

    real_news = c.fetchone()[0]

    # FAKE NEWS COUNT
    c.execute("""

        SELECT COUNT(*)
        FROM history
        WHERE result='Fake News'

    """)

    fake_news = c.fetchone()[0]

    # AVERAGE ACCURACY
    c.execute("""

        SELECT AVG(confidence)
        FROM history

    """)

    accuracy = c.fetchone()[0]

    # AVERAGE RATING
    c.execute("""

        SELECT AVG(rating)
        FROM reviews

    """)

    avg_rating = c.fetchone()[0]

    # ALL REVIEWS
    c.execute("""

        SELECT rating, review
        FROM reviews
        ORDER BY id DESC
        LIMIT 5

    """)

    reviews = c.fetchall()

    conn.close()

    return render_template(

        "dashboard.html",

        total_checked=total_checked,
        real_news=real_news,
        fake_news=fake_news,

        accuracy=round(accuracy or 0, 2),

        avg_rating=round(avg_rating or 0, 1),

        reviews=reviews
    )





if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8001, debug=True)