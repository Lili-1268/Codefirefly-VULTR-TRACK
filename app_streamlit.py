import streamlit as st
import requests
import json
import re
from config import GROQ_API_KEY, OPENCAGE_API_KEY, HUNTER_API_KEY

GROQ_MODEL = "llama3-8b-8192"

# === Groq: Get Companies by Sector ===
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

    match = re.search(r"\[.*\]", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            st.error(f"JSON decode error: {e}")
            return []
    else:
        st.error("No JSON array found in Groq response.")
        return []

# === Geocode ===
def geocode_location(location):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {"q": location, "key": OPENCAGE_API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json().get("results")
    if results:
        return results[0]["geometry"]
    return None

# === Hunter Email Search ===
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

# === Streamlit App ===
st.title("Client Finder App")

# --- Sector Search ---
st.header("🔍 Find Companies by Sector")
sector = st.text_input("Enter a sector")
if st.button("Search Sector"):
    companies = get_companies(sector)
    for company in companies:
        st.subheader(company["name"])
        st.write(company["description"])
        coords = geocode_location(company.get("location", ""))
        if coords:
            st.map([{"lat": coords["lat"], "lon": coords["lng"]}])
        else:
            st.warning("Location not found")

# --- Domain Search ---
st.header("📧 Find Contacts by Domain")
domain = st.text_input("Enter a domain (e.g., example.com)")
if st.button("Search Domain"):
    results = search_domain(domain)
    if isinstance(results, str):
        st.error(results)
    elif results:
        for email in results:
            st.write(f"**{email.get('first_name', '')} {email.get('last_name', '')}** — {email.get('value')}")
    else:
        st.info("No contacts found.")
