# Encuesta Anónima Web

## Descripción
Aplicación Flask para encuestas anónimas con tokens diarios, respuestas ocultas hasta una fecha específica y panel de administración.

## Despliegue en Render

1. Subí este proyecto a un repositorio en GitHub.
2. En https://render.com, creá un nuevo Web Service.
3. Configuración:
   - Build Command: pip install -r requirements.txt
   - Start Command: python app.py
4. Accedé a:
   - Página de inicio: /
   - Encuesta automática: /encuesta_auto?token=...
   - Panel admin: /admin?password=admin123
   - Generar tokens: /generar_tokens?clave=miclave123
