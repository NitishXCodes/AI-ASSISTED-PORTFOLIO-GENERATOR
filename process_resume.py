import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: Gemini API key not found.")
    exit()

client = genai.Client(api_key=api_key)

# Read resume.txt
with open("resume.txt", "r", encoding="utf-8") as file:
    resume = file.read()

if not resume.strip():
    print("ERROR: resume.txt is empty.")
    exit()

print("Resume loaded successfully!")
print("Sending resume to Gemini...\n")

prompt = f"""
You are a professional resume analyzer.

Read the resume below and extract the information.

Return ONLY valid JSON.
Do not use markdown.
Do not add ```json.
Do not add explanations.

Use exactly this structure:

{{
    "name": "",
    "about": "",
    "skills": [],
    "education": [],
    "projects": [],
    "experience": [],
    "achievements": [],
    "contact": {{
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": ""
    }}
}}

Rules:
- Do not invent information.
- If information is missing, use an empty string or empty list.
- Keep the information accurate to the resume.

Resume:
{resume}
"""

print("Waiting for Gemini...")

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input=prompt
)

result = interaction.output_text

print("\nGemini response:")
print(result)

# Try to convert response into Python JSON
try:
    portfolio_data = json.loads(result)

    print("\nJSON successfully created!")

except json.JSONDecodeError:
    print("\nERROR: Gemini did not return valid JSON.")