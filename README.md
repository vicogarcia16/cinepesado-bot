## 📌 CinePesado Bot
Bot de Telegram que recomienda películas y conversa de forma natural usando FastAPI y un modelo LLM vía OpenRouter. Incluye un endpoint /ping para monitorizar la disponibilidad del servicio con herramientas como UptimeRobot.

#### 🚀 Características
* 📩 Webhook de Telegram: Recibe y responde mensajes automáticamente desde tu bot.

* 👋 Reconocimiento de saludos: Detecta saludos comunes y responde con un mensaje personalizado.

* 🤖 Conversación natural: Interpreta preguntas o frases del usuario y responde de manera fluida, como si estuvieras hablando con un amigo.

* 🎬 Recomendaciones de películas: Sugiere películas basadas en gustos, géneros o estados de ánimo.

* 🧠 IA potenciada con LLM (OpenRouter): Usa un modelo de lenguaje para generar respuestas contextuales y coherentes.

* 🖋️ Formato enriquecido: Usa HTML para mejorar la presentación de los mensajes en Telegram (negritas, cursivas, emojis, etc.).

* ☁️ Deploy simple: Preparado para desplegar fácilmente en Render, con soporte para monitoreo vía /ping.

#### 📁 Estructura del proyecto

```
app/
  main.py           # FastAPI app y webhook
  bot/
    handlers.py     # Lógica para manejar mensajes y respuestas
    telegram.py     # Funciones para enviar mensajes y acciones a Telegram
  core/
    config.py       # Configuración y carga de variables de entorno
    utils.py        # Funciones auxiliares (saludos, parseo)
  data/
    prompt.py       # Prompts y textos del bot
  routes/
    telegram.py     # Rutas FastAPI para webhook
  services/
    llm_agent.py    # Lógica para llamar a OpenRouter API
requirements.txt    # Dependencias
Procfile            # Comando para despliegue en Render
```
#### ⚙️ Requisitos
* Python 3.9+
* Telegram Bot Token
* API Key OpenRouter

#### 🔐 Archivo `.env` necesario

```env
TELEGRAM_TOKEN=telegram_token
OPENROUTER_API_KEY=openrouter_key
OPENROUTER_MODEL=modelo
TELEGRAM_API_URL=https://api.telegram.org/bot
BASE_URL=URL de render
```

#### 🧪 Instalación y Ejecución

##### Instalar dependencias

```bash
pipenv install --dev
```

##### Ejecutar servidor de desarrollo

```bash
pipenv run uvicorn app.main:app --reload
```

#### 🔍 Monitorización del servicio

Se expone un endpoint `/ping` para verificar que el bot está activo y responder a herramientas de monitoreo como [UptimeRobot](https://uptimerobot.com/?rid=62d4f0a7928e50).

Ejemplo de respuesta:

```json
{
  "message": "pong"
}
```
