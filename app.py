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
        return "Acceso denegado", 403

    if datetime.now() < UNLOCK_DATE:
        return f"Las respuestas estarán disponibles después del {UNLOCK_DATE.strftime('%Y-%m-%d')}."

    responses = {}

    for filename in os.listdir("responses"):
        if filename.endswith(".json"):
            date_part = filename.split("_")[0]
            with open(os.path.join("responses", filename), "r") as f:
                data = json.load(f)
            if date_part not in responses:
                responses[date_part] = []
            responses[date_part].append(data)

    html = "<h1>Respuestas por fecha</h1>"
    for date, entries in sorted(responses.items()):
        html += f"<h2>{date}</h2><ul>"
        for entry in entries:
            html += "<li>"
            html += f"<b>1:</b> {entry['q1']}<br>"
            html += f"<b>2:</b> {entry['q2']}<br>"
            html += f"<b>3:</b> {entry['q3']}<br>"
            html += f"<b>4:</b> {entry['q4']}<br>"
            html += "</li><br>"
        html += "</ul>"
    return html

@app.route("/")
def home():
    return """
    <h1>Bienvenido a la Encuesta Anónima</h1>
    <p>Para participar, hacé clic en el siguiente enlace con tu token:</p>
    <a href="/encuesta?token=token001">Ir a la encuesta</a>
    <p>Panel de administración (requiere contraseña):</p>
    <a href="/admin?password=admin123">Ver respuestas</a>
    """

from uuid import uuid4

@app.route("/generar_tokens")
def generar_tokens():
    clave = request.args.get("clave")
    if clave != "miclave123":  # Cambiá esto por una clave segura
        return "Acceso no autorizado", 403

    today = datetime.today().strftime("%Y-%m-%d")
    TOKENS_FILE = "tokens.json"

    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            all_tokens = json.load(f)
    else:
        all_tokens = {}

    if today in all_tokens:
        return f"Los tokens para {today} ya existen."

    tokens = [f"token_{uuid4().hex[:8]}" for _ in range(50)]
    all_tokens[today] = {token: "unused" for token in tokens}

    with open(TOKENS_FILE, "w") as f:
        json.dump(all_tokens, f, indent=2)

    return f"Se generaron 50 tokens para {today}."
@app.route("/encuesta_auto", methods=["GET", "POST"])
def encuesta_auto():
    token = request.args.get("token")
    today = datetime.today().strftime("%Y-%m-%d")

    if not token:
        return "Falta el token.", 400

    if not os.path.exists(TOKENS_FILE):
        return "No hay tokens disponibles.", 404

    with open(TOKENS_FILE, "r") as f:
        all_tokens = json.load(f)

    if today not in all_tokens or token not in all_tokens[today]:
        return "Token inválido o no corresponde a hoy.", 403

    if all_tokens[today][token] == "used":
        return "Este token ya fue utilizado.", 403

    if request.method == "POST":
        data = {
            "q1": request.form["q1"],
            "q2": request.form["q2"],
            "q3": request.form["q3"],
            "q4": request.form["q4"]
        }
        filename = f"responses/{today}_{token}.json"
        with open(filename, "w") as f:
            json.dump(data, f)

        all_tokens[today][token] = "used"
        with open(TOKENS_FILE, "w") as f:
            json.dump(all_tokens, f, indent=2)

        return "Gracias por completar la encuesta."

    return render_template_string(form_template)
