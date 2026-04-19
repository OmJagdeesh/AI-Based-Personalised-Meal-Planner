from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from model import MealRecommender

load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

# Initialize PyTorch-based Meal Recommender
print("Loading PyTorch model and dataset...")
recommender = MealRecommender()
print("Model loaded successfully.")


def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return weight_kg / (height_m**2)


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_meal():
    try:
        data = request.get_json()

        # Personal info
        weight = float(data["weight"])
        height = float(data["height"])
        age = int(data["age"])
        gender = data["gender"]
        activity_level = data["activity_level"]

        # Meal preferences
        carbs = float(data["carbs"])
        protein = float(data["protein"])
        fat = float(data["fat"])
        meal_type = data["meal_type"]
        cuisine_type = data["cuisine_type"]
        dietary_restrictions = data["dietary_restrictions"]

        # Calculate BMI
        bmi = calculate_bmi(weight, height)
        
        # Calculate target calories based on macros (4 kcal per g for carbs/protein, 9 for fat)
        target_calories = (carbs * 4) + (protein * 4) + (fat * 9)

        # Build user profile for the model
        user_profile = {
            "calories": target_calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "meal_type": meal_type,
            "cuisine_type": cuisine_type,
            "dietary_restrictions": dietary_restrictions
        }

        # Query the PyTorch recommendation model
        top_meals = recommender.recommend_meals(user_profile, top_k=3)

        # Format the response as HTML
        meal_plan_html = f"<h3>Top Recommendations for your Profile</h3>"
        meal_plan_html += f"<p>Target Calories: {target_calories:.0f} kcal</p><hr>"

        for idx, meal in enumerate(top_meals, 1):
            meal_plan_html += f"<h4>{idx}. {meal['recipe_name']}</h4>"
            meal_plan_html += f"<p><strong>Match Score:</strong> <span class='badge bg-success'>{meal['match_score']}%</span></p>"
            meal_plan_html += f"<p><em>{meal['description']}</em></p>"
            meal_plan_html += f"<ul>"
            meal_plan_html += f"<li><strong>Cuisine:</strong> {meal['cuisine']}</li>"
            meal_plan_html += f"<li><strong>Calories:</strong> {meal['calories']} kcal</li>"
            meal_plan_html += f"<li><strong>Protein:</strong> {meal['protein_g']}g</li>"
            meal_plan_html += f"<li><strong>Carbs:</strong> {meal['carbs_g']}g</li>"
            meal_plan_html += f"<li><strong>Fat:</strong> {meal['fat_g']}g</li>"
            meal_plan_html += f"</ul>"
            meal_plan_html += f"<h5>Ingredients:</h5><p>{meal['ingredients']}</p>"
            meal_plan_html += f"<h5>Instructions:</h5><p>{meal['instructions']}</p>"
            meal_plan_html += "<hr>"

        return jsonify(
            {
                "meal_plan": meal_plan_html,
                "bmi": f"{bmi:.1f}",
                "bmi_category": get_bmi_category(bmi),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True, use_reloader=False) # disabled reloader so model doesn't load twice
