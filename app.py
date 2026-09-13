from flask import Flask, render_template, request
import pandas as pd
import os
from dotenv import load_dotenv
from agent.decision_agent import DecisionAgent

load_dotenv()

app = Flask(__name__)

decision_agent = DecisionAgent()

# -----------------------------
# Load College Dataset
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "colleges.csv")

try:
    colleges = pd.read_csv(DATA_FILE)
    print("College dataset loaded successfully.")
except FileNotFoundError:
    colleges = pd.DataFrame()
    print("ERROR: colleges.csv not found.")


# -----------------------------
# Recommendation Engine
# -----------------------------

def find_recommendations(student):

    if colleges.empty:
        return []

    results = colleges.copy()

    # --------------------------------
    # 1. Stream Filtering
    # --------------------------------

    if student["stream"]:

        stream = student["stream"].strip().lower()

        results = results[
            results["stream"]
            .astype(str)
            .str.lower()
            .str.contains(stream, na=False)
        ]

    # --------------------------------
    # 2. Location Filtering
    # --------------------------------

    if student["location"] and not results.empty:

        location = student["location"].strip().lower()

        location_results = results[
            results["location"]
            .astype(str)
            .str.lower()
            .str.contains(location, na=False)
        ]

        # Only apply location filter when matches exist
        if not location_results.empty:
            results = location_results

    # --------------------------------
    # 3. Budget / Fee Filtering
    # --------------------------------

    try:

        budget = float(student["budget"])

        results["annual_fee"] = pd.to_numeric(
            results["annual_fee"],
            errors="coerce"
        )

        results = results[
            results["annual_fee"] <= budget
        ]

    except (ValueError, TypeError):

        pass

    # --------------------------------
    # 4. Career + Interest Matching
    # --------------------------------

    if not results.empty:

        interest = str(student["interest"]).lower()
        career_goal = str(student["career_goal"]).lower()

        search_text = interest + " " + career_goal

        search_words = search_text.split()

        def calculate_score(row):

            score = 0

            # Important fields
            career = str(row.get("career", "")).lower()
            course = str(row.get("course", "")).lower()
            specialization = str(
                row.get("specialization", "")
            ).lower()
            description = str(
                row.get("description", "")
            ).lower()

            # Career match gets higher weight
            for word in search_words:

                if len(word) > 2:

                    if word in career:
                        score += 5

                    if word in specialization:
                        score += 3

                    if word in course:
                        score += 2

                    if word in description:
                        score += 1

            return score

        results = results.copy()

        results["match_score"] = results.apply(
            calculate_score,
            axis=1
        )

        # Highest match first
        results = results.sort_values(
            by="match_score",
            ascending=False
        )

    # Return top 5
    return results.head(5).to_dict(orient="records")


# -----------------------------
# Home Page
# -----------------------------

@app.route("/")
def home():

    return render_template("index.html")


# -----------------------------
# Analyze Student
# -----------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    student = {

        "class_level": request.form.get(
            "class_level",
            ""
        ),

        "stream": request.form.get(
            "stream",
            ""
        ),

        "interest": request.form.get(
            "interest",
            ""
        ),

        "location": request.form.get(
            "location",
            ""
        ),

        "budget": request.form.get(
            "budget",
            ""
        ),

        "career_goal": request.form.get(
            "career_goal",
            ""
        )
    }

    recommendations = find_recommendations(
        student
    )

    return render_template(
        "result.html",
        student=student,
        recommendations=recommendations
    )


# -----------------------------
# Run Flask
# -----------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )