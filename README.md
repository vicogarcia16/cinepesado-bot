## 📌 CinePesado Bot
Bot de Telegram que recomienda películas y conversa de forma natural usando FastAPI y un modelo LLM vía OpenRouter.

#### 🚀 Características
* Recibe mensajes vía webhook de Telegram.

* Detecta saludos y responde con un mensaje inicial.

* Interpreta mensajes del usuario para brindar respuestas naturales o recomendaciones de películas.

* Utiliza un modelo LLM (OpenRouter) para generar respuestas contextuales.

* Formatea mensajes con HTML para mejor presentación.

* Deploy sencillo en Render.

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
