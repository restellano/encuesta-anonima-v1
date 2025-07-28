from flask import Flask, request, render_template_string
import os
import json
from datetime import datetime
from uuid import uuid4

app = Flask(__name__)

TOKENS_FILE = "tokens.json"
RESPONSES_DIR = "responses"
UNLOCK_DATE = datetime(2025, 8, 1)
ADMIN_PASSWORD = "admin123"
GEN_PASS = "miclave123"

form_template = """
<form method='post'>
  <label>1. Cuanto disfrutas de realizar actividades al aire libre? (1-5)</label><br>
  <input type='number' name='q1' min='1' max='5' required><br><br>
  <label>2. Cual fue el ultimo libro que leiste?</label><br>
  <input type='text' name='q2' required><br><br>
  <label>3. Cuantas horas usaste tu celular ayer?</label><br>
  <input type='text' name='q3' required><br><br>
  <label>4. Si reencarnaras en un animal, cual seria y por que?</label><br>
  <textarea name='q4' required></textarea><br><br>
  <input type='submit' value='Enviar'>
</form>
"""

@app.route("/")
def home():
    return render_template_string("""
    <h1>Bienvenido a la Encuesta Anónima</h1>
    <p>Para participar, usá el enlace con tu token:</p>
    <a href="/encuesta_auto?token=token001">Ir a la encuesta</a><br><br>
    <p>Panel de administración (requiere contraseña):</p>
    <a href="/admin?password=admin123">Ver respuestas</a>
    """)

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
        filename = os.path.join(RESPONSES_DIR, f"{today}_{token}.json")
        with open(filename, "w") as f:
            json.dump(data, f)

        all_tokens[today][token] = "used"
        with open(TOKENS_FILE, "w") as f:
            json.dump(all_tokens, f, indent=2)

        return "Gracias por completar la encuesta."

    return render_template_string(form_template)

@app.route("/admin")
def admin():
    password = request.args.get("password")
    if password != ADMIN_PASSWORD:
        return "Acceso denegado", 403

    if datetime.today() < UNLOCK_DATE:
        return f"Las respuestas estarán disponibles después del {UNLOCK_DATE.strftime('%Y-%m-%d')}."

    if not os.path.exists(RESPONSES_DIR):
        return "No hay respuestas aún."

    html = "<h2>Respuestas recibidas:</h2><ul>"
    for fname in os.listdir(RESPONSES_DIR):
        with open(os.path.join(RESPONSES_DIR, fname)) as f:
            data = json.load(f)
            html += f"<li><strong>{fname}</strong><br>"
            for k, v in data.items():
                html += f"{k}: {v}<br>"
            html += "</li><br>"
    html += "</ul>"
    return html

@app.route("/generar_tokens")
def generar_tokens():
    clave = request.args.get("clave")
    if clave != GEN_PASS:
        return "Acceso no autorizado", 403

    today = datetime.today().strftime("%Y-%m-%d")

    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            all_tokens = json.load(f)
    else:
        all_tokens = {}

    if today in all_tokens:
        return f"Los tokens para {today} ya existen."

    tokens = {f"token_{uuid4().hex[:8]}": "unused" for _ in range(50)}
    all_tokens[today] = tokens

    with open(TOKENS_FILE, "w") as f:
        json.dump(all_tokens, f, indent=2)

    return f"Se generaron 50 tokens para {today}."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
