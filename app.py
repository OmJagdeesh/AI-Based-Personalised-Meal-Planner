from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

# Configure Gemini API
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-1.5-pro-002")


def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return weight_kg / (height_m**2)


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
        carbs = data["carbs"]
        protein = data["protein"]
        fat = data["fat"]
        meal_type = data["meal_type"]
        cuisine_type = data["cuisine_type"]
        dietary_restrictions = data["dietary_restrictions"]

        # Calculate BMI
        bmi = calculate_bmi(weight, height)

        prompt = f"""
        Create a personalized {meal_type} meal plan for:
        - {gender}, {age} years old
        - Height: {height} cm, Weight: {weight} kg (BMI: {bmi:.1f})
        - Activity level: {activity_level}
        - Dietary restrictions: {dietary_restrictions}
        
        Nutritional targets:
        - Carbohydrates: {carbs}g
        - Protein: {protein}g
        - Fat: {fat}g
        - Cuisine type: {cuisine_type}
        
        Include:
        1. Meal name and description
        2. Detailed ingredients list
        3. Step-by-step preparation
        4. Nutritional breakdown per serving
        5. Health benefits specific to this person's profile
        
        Also calculate daily caloric requirements and macronutrient distribution.
        Make it practical, delicious, and nutritionally balanced.
        """

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.7, top_p=0.8),
        )

        return jsonify(
            {
                "meal_plan": response.text,
                "bmi": f"{bmi:.1f}",
                "bmi_category": get_bmi_category(bmi),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True)

