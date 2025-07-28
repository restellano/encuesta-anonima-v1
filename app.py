from flask import Flask, request, render_template_string, redirect
import os
import json
from datetime import datetime

app = Flask(__name__)

UNLOCK_DATE = datetime(2025, 8, 1)
ADMIN_PASSWORD = "admin123"
RESPONSES_DIR = "responses"
TOKENS_FILE = "tokens.json"

# Load tokens
with open(TOKENS_FILE) as f:
    tokens = json.load(f)

# Ensure responses directory exists
os.makedirs(RESPONSES_DIR, exist_ok=True)

# Survey form template
form_template = """
<!doctype html>
<html>
<head><title>Encuesta Anónima</title></head>
<body>
<h2>Encuesta Anónima</h2>
<form method="post">
  <label>1. ¿Cuánto disfrutas de realizar actividades al aire libre? (1-5)</label><br>
  <input type="number" name="q1" min="1" max="5" required><br><br>
  <label>2. ¿Cuál fue el último libro que leíste?</label><br>
  <input type="text" name="q2" required><br><br>
  <label>3. ¿Cuál fue la cantidad de horas que usaste tu celular ayer?</label><br>
  <input type="text" name="q3" required><br><br>
  <label>4. Si reencarnaras en un animal, ¿en cuál sería y por qué?</label><br>
  <textarea name="q4" required></textarea><br><br>
  <input type="submit" value="Enviar">
</form>
</body>
</html>
"""

@app.route("/encuesta", methods=["GET", "POST"])
def encuesta():
    token = request.args.get("token")
    if not token or token not in tokens or tokens[token] == "used":
        return "Token inválido o ya utilizado."

    if request.method == "POST":
        response = {
            "timestamp": datetime.now().isoformat(),
            "q1": request.form["q1"],
            "q2": request.form["q2"],
            "q3": request.form["q3"],
            "q4": request.form["q4"]
        }
        with open(os.path.join(RESPONSES_DIR, f"{token}.json"), "w") as f:
            json.dump(response, f)
        tokens[token] = "used"
        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f)
        return "Gracias por completar la encuesta."
    return render_template_string(form_template)

@app.route("/admin")
def admin():
    password = request.args.get("password")
    if password != ADMIN_PASSWORD:
        return "Acceso denegado."

    if datetime.now() < UNLOCK_DATE:
        return f"Las respuestas estarán disponibles después del {UNLOCK_DATE.strftime('%Y-%m-%d')}."

    results = []
    for fname in os.listdir(RESPONSES_DIR):
        with open(os.path.join(RESPONSES_DIR, fname)) as f:
            results.append(json.load(f))
    return {"responses": results}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


