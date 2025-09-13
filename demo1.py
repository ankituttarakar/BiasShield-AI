from flask import Flask, render_template_string, request, url_for
import time
import re
from transformers import pipeline

app = Flask(__name__)

# Load zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Bias-sensitive categories
bias_categories = [
    "gender", "age", "race", "religion", "disability",
    "sexual orientation", "nationality", "socioeconomic status", "political affiliation"
]

LOGO_FILENAME = "logo.png"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Bias-Free Firewall</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Orbitron', sans-serif;
      background: radial-gradient(circle at top, #000000 0%, #050d1a 100%);
      color: #e0f7ff;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }
    .container {
      background: rgba(0, 0, 0, 0.85);
      border: 2px solid #00f0ff;
      border-radius: 1rem;
      box-shadow: 0 0 25px #00f0ff;
      padding: 2rem;
      max-width: 700px;
      width: 100%;
      text-align: center;
      backdrop-filter: blur(10px);
    }
    .logo-wrapper {
      display: flex;
      justify-content: center;
      margin-bottom: 1rem;
    }
    .logo-wrapper img {
      max-width: 120px;
      height: auto;
      filter: drop-shadow(0 0 15px #00f0ff);
    }
    h1 {
      font-size: 2rem;
      font-weight: bold;
      color: #00f0ff;
      text-shadow: 0 0 10px #00f0ff;
      margin-bottom: 0.5rem;
    }
    p {
      color: #b0c7d1;
      margin-bottom: 1.5rem;
    }
    label {
      display: block;
      text-align: left;
      margin-bottom: 0.5rem;
      font-weight: bold;
      color: #00f0ff;
    }
    input, select, textarea {
      width: 100%;
      margin-bottom: 1rem;
      padding: 0.75rem;
      background: rgba(0, 0, 0, 0.6);
      border: 1px solid #00f0ff;
      border-radius: 0.5rem;
      color: #e0f7ff;
      outline: none;
      transition: all 0.3s ease;
    }
    input:focus, select:focus, textarea:focus {
      box-shadow: 0 0 10px #00f0ff;
    }
    button {
      width: 100%;
      padding: 0.75rem;
      background: #00f0ff;
      color: #000;
      font-weight: bold;
      border-radius: 0.5rem;
      transition: all 0.3s ease;
    }
    button:hover {
      background: #00c4cc;
      box-shadow: 0 0 15px #00f0ff;
      transform: translateY(-2px);
    }
    #results {
      margin-top: 2rem;
      padding: 1rem;
      background: rgba(0, 0, 0, 0.6);
      border-radius: 0.5rem;
      border: 1px solid #00f0ff;
      box-shadow: 0 0 15px #00f0ff;
      text-align: left;
    }
    .bias-indicator { color: #ff4d4d; font-weight: bold; text-shadow: 0 0 5px #ff4d4d; }
    .fair-indicator { color: #00ff99; font-weight: bold; text-shadow: 0 0 5px #00ff99; }
    .loading {
      display: none;
      margin-top: 1rem;
      font-size: 1rem;
      color: #00f0ff;
      animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
      0% { opacity: 0.3; }
      50% { opacity: 1; }
      100% { opacity: 0.3; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="logo-wrapper">
      <img src="{{ url_for('static', filename=logo_file) }}" alt="Firewall Logo">
    </div>
    <h1>Bias-Free Firewall</h1>
    <p>Scan your AI API requests for bias in seconds.</p>

    <form method="POST" onsubmit="showLoading()">
      <label>Step 1: API Endpoint</label>
      <input type="text" name="requestUrl" placeholder="/api/predict" required />

      <label>Step 2: User Context</label>
      <select name="userType" required>
        <option value="">Select...</option>
        <option value="diverse">Diverse User Base</option>
        <option value="single">Single Demographic</option>
      </select>

      <label>Step 3: Request Payload</label>
      <textarea name="dataContent" placeholder="e.g., age=45" required></textarea>

      <button type="submit">🚀 Run Bias Check</button>
      <div class="loading" id="loading">🔍 Scanning request for bias...</div>
    </form>

    {% if result %}
    <div id="results">
      <h3 style="color:#00f0ff;">Firewall Analysis</h3>
      <p>{{ result|safe }}</p>
    </div>
    {% endif %}
  </div>

  <script>
    function showLoading() {
      document.getElementById('loading').style.display = 'block';
    }
  </script>
</body>
</html>
"""

def analyze_request(url, user_type, data):
    lower_data = data.lower()
    output = f"<strong>Request:</strong> {url}<br>"
    output += f"<strong>User Context:</strong> {user_type}<br>"
    output += f"<strong>Payload:</strong> {data}<br><br>"

    biased_keywords = [
        "only men", "only male", "males only", "only women", "only female", "females only",
        "no women", "no men", "exclude", "must be", "not allowed",
        "age limit", "younger than", "older than", "religion", "caste", "race",
        "ethnicity", "skin color", "country only", "citizens only"
    ]

    patterns = {
        "age": r"age\s*=\s*([a-zA-Z0-9_]+)",
        "gender": r"gender\s*=\s*([a-zA-Z0-9_]+)",
        "location": r"location\s*=\s*([a-zA-Z0-9_]+)"
    }

    for keyword in biased_keywords:
        if keyword in lower_data:
            output += '<span class="bias-indicator">⚠ Bias Alert:</span> '
            output += f"This request contains potential bias → <em>{keyword}</em><br>"
            output += "🛡 <strong>Firewall Response:</strong> Sent for human review.<br><br>"
            break

    if user_type == "single":
        for field, pattern in patterns.items():
            match = re.search(pattern, lower_data)
            if match and "diverse" not in lower_data:
                value = match.group(1)
                output += '<span class="bias-indicator">⚠ Bias Alert:</span> '
                output += f"Request may filter users by {field} → {field}={value}<br>"
                output += "🛡 <strong>Firewall Response:</strong> Flagged for human review.<br><br>"
                break

    result = classifier(data, candidate_labels=bias_categories)
    output += "<strong>AI-Based Bias Category Detection:</strong><br>"
    for label, score in zip(result['labels'], result['scores']):
        if score > 0.5:
            output += f"<span class='bias-indicator'>⚠ {label.capitalize()} Bias Likely:</span> Confidence {score:.2f}<br>"
        else:
            output += f"{label.capitalize()}: Confidence {score:.2f}<br>"

    if "Bias Alert" not in output:
        output += '<br><span class="fair-indicator">✅ No Bias Detected:</span> The request appears fair and inclusive.<br>'
        output += "🔓 <strong>Firewall Response:</strong> Approved to proceed."

    return output

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        url = request.form.get("requestUrl", "").strip()
        user_type = request.form.get("userType", "")
        data = request.form.get("dataContent", "").strip()
        time.sleep(1.5)
        result = analyze_request(url, user_type, data)
    return render_template_string(HTML_TEMPLATE, result=result, logo_file=LOGO_FILENAME)

if __name__ == "__main__":
    app.run(debug=True)
