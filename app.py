from flask import Flask, render_template, request
import requests
import json
import re
from config import GROQ_API_KEY, OPENCAGE_API_KEY, HUNTER_API_KEY
import os

GROQ_MODEL = "llama3-8b-8192"

app = Flask(__name__)

# === Groq: Get Companies by Sector (returns JSON-formatted) ===
def get_companies(sector):
    prompt = (
        f"I'm researching the \"{sector}\" sector.\n"
        "List 3 innovative companies in this space in JSON format like:\n"
        "[{\"name\": \"Company Name\", \"description\": \"What they do\", \"location\": \"Headquarters City, Country\"}]"
    )
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()



    content = response.json()["choices"][0]["message"]["content"]

    # Extract first JSON array from the response text
    match = re.search(r"\[.*\]", content, re.DOTALL)
    if match:
       try:
           return json.loads(match.group(0))
       except json.JSONDecodeError as e:
           raise Exception(f"JSON decode error: {e}\nExtracted content:\n{match.group(0)}")
    else:
       raise Exception("Could not find a valid JSON array in the response:\n" + content)


# === Geocode with OpenCage ===
def geocode_location(location):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {"q": location, "key": OPENCAGE_API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json().get("results")
    if results:
        return results[0]["geometry"]  # {'lat': ..., 'lng': ...}
    return None


def search_domain(domain):
    url = "https://api.hunter.io/v2/domain-search"
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("data", {}).get("emails", [])
    except Exception as e:
        return f"Error: {str(e)}"


# === Home Page Route ===
@app.route("/", methods=["GET", "POST"])
def index():
    companies_with_coords = []
    sector_error = None
    domain_error = None
    emails = None

    if request.method == "POST":
        if "sector_submit" in request.form:
            sector = request.form.get("sector")
            try:
                companies = get_companies(sector)
                for company in companies:
                    coords = geocode_location(company.get("location", ""))
                    if coords:
                        companies_with_coords.append({
                            "name": company["name"],
                            "description": company["description"],
                            "lat": coords["lat"],
                            "lng": coords["lng"]
                        })
            except Exception as e:
                sector_error = str(e)

        elif "domain_submit" in request.form:
            domain = request.form.get("domain")
            result = search_domain(domain)
            if isinstance(result, str):
                domain_error = result
            else:
                emails = result

    return render_template("index.html",
                           companies=companies_with_coords,
                           sector_error=sector_error,
                           emails=emails,
                           domain_error=domain_error)

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)

    