import os
import json

from flask import Flask, render_template, request
from dotenv import load_dotenv
from google import genai

# --------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------

load_dotenv()

app = Flask(__name__)

# --------------------------------
# GEMINI API
# --------------------------------

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found. Check your .env file.")

client = genai.Client(api_key=api_key)


# --------------------------------
# HOME PAGE
# --------------------------------

@app.route("/")
def home():
    return render_template("editor.html")


# --------------------------------
# GENERATE PORTFOLIO
# --------------------------------

@app.route("/generate", methods=["POST"])
def generate():

    try:

        # --------------------------------
        # 1. GET RESUME FROM WEBSITE
        # --------------------------------

        resume = request.form.get("resume", "").strip()

        if not resume:
            return """
            <h2>Resume is empty.</h2>
            <p>Please go back and enter your resume.</p>
            """


        print("\n================================")
        print("Resume received from website.")
        print("================================")


        # --------------------------------
        # 2. SAVE RESUME TO resume.txt
        # --------------------------------

        with open("resume.txt", "w", encoding="utf-8") as file:
            file.write(resume)

        print("Resume saved to resume.txt")


        # --------------------------------
        # 3. READ RESUME FROM resume.txt
        # --------------------------------

        with open("resume.txt", "r", encoding="utf-8") as file:
            resume_from_file = file.read()

        print("Resume read from resume.txt")


        # --------------------------------
        # 4. CREATE GEMINI PROMPT
        # --------------------------------

        prompt = f"""
You are an expert resume analyzer and professional portfolio content generator.

Analyze the resume below and extract all useful information.

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add explanations before or after the JSON.

Use EXACTLY this structure:

{{
    "name": "",
    "title": "",
    "about": "",

    "contact": {{
        "email": "",
        "phone": "",
        "location": "",
        "github": "",
        "linkedin": ""
    }},

    "skills": [],

    "education": [
        {{
            "degree": "",
            "institution": "",
            "year": "",
            "details": ""
        }}
    ],

    "projects": [
        {{
            "name": "",
            "description": "",
            "technologies": []
        }}
    ],

    "experience": [
        {{
            "position": "",
            "company": "",
            "duration": "",
            "description": ""
        }}
    ],

    "achievements": [],

    "certifications": [],

    "interests": [],

    "languages": []
}}

IMPORTANT RULES:

1. Do not invent information.
2. Only use information that exists in the resume.
3. If information is missing, use an empty string or empty list.
4. Keep project descriptions accurate to the resume.
5. Extract technologies used in each project when available.
6. Extract company, position and duration for experience.
7. Extract degree, institution and year for education.
8. Extract GitHub and LinkedIn links if present.
9. Extract languages if they are mentioned.
10. Extract certifications if they are mentioned.
11. Extract achievements if they are mentioned.
12. Extract interests if they are mentioned.
13. Preserve the original meaning of the resume.
14. Return valid JSON only.

RESUME:

{resume_from_file}
"""


        # --------------------------------
        # 5. SEND DATA TO GEMINI
        # --------------------------------

        print("Sending resume.txt to Gemini...")

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        result = interaction.output_text

        print("Gemini response received.")


        # --------------------------------
        # 6. CLEAN GEMINI RESPONSE
        # --------------------------------

        result = result.strip()

        # Remove markdown code fences if Gemini adds them

        if result.startswith("```json"):
            result = result[7:]

        elif result.startswith("```"):
            result = result[3:]

        if result.endswith("```"):
            result = result[:-3]

        result = result.strip()


        # --------------------------------
        # 7. CONVERT RESPONSE TO JSON
        # --------------------------------

        try:

            portfolio_data = json.loads(result)

        except json.JSONDecodeError as error:

            print("\n================================")
            print("JSON ERROR")
            print("================================")

            print(error)

            print("\nGemini returned:")
            print(result)

            return """
            <html>

            <head>
                <title>JSON Error</title>
            </head>

            <body style="
                font-family: Arial;
                background: #111;
                color: white;
                padding: 40px;
            ">

                <h1>Gemini returned invalid JSON</h1>

                <p>
                    Please try generating the portfolio again.
                </p>

                <p>
                    Check the PowerShell window for details.
                </p>

            </body>

            </html>
            """


        print("Portfolio JSON created successfully.")


        # --------------------------------
        # 8. DISPLAY PORTFOLIO
        # --------------------------------

        return render_template(
            "portfolio.html",
            portfolio=portfolio_data
        )


    # --------------------------------
    # 9. HANDLE OTHER ERRORS
    # --------------------------------

    except Exception as error:

        print("\n================================")
        print("ERROR")
        print("================================")

        print(type(error).__name__)
        print(error)

        print("================================\n")

        return f"""
        <html>

        <head>
            <title>Portfolio Generation Error</title>
        </head>

        <body style="
            font-family: Arial;
            background: #111;
            color: white;
            padding: 40px;
        ">

            <h1>Something went wrong</h1>

            <p>
                Your portfolio could not be generated.
            </p>

            <p>
                Error type:
                <strong>{type(error).__name__}</strong>
            </p>

            <p>
                Error:
                {error}
            </p>

            <p>
                Check your PowerShell window for more details.
            </p>

        </body>

        </html>
        """


# --------------------------------
# START FLASK
# --------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )