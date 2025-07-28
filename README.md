# Encuesta Anónima Web

Este proyecto es una aplicación Flask para realizar encuestas anónimas con acceso por token y respuestas ocultas hasta una fecha específica.

## Cómo desplegar en Render

1. Crear una cuenta en [https://render.com](https://render.com).
2. Crear un nuevo servicio web y conectar este repositorio.
3. Asegurarse de que el archivo `Procfile` esté presente.
4. Render instalará automáticamente las dependencias desde `requirements.txt`.
5. Acceder a la encuesta con: `https://TU_APP.render.com/encuesta?token=token001`
6. Acceder al panel de administración con: `https://TU_APP.render.com/admin?password=admin123`

## Estructura

- `app.py`: aplicación principal Flask.
- `tokens.json`: tokens únicos para participantes.
- `responses/`: carpeta donde se guardan las respuestas.
- `requirements.txt`: dependencias.
- `Procfile`: configuración para Render.
