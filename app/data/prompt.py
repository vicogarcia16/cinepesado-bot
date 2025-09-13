IDENTIFICATION_PROMPT = """
Tu única tarea es identificar *todas* las películas o series mencionadas o implícitas en el texto del usuario, sin importar el contexto. **Considera el historial de la conversación para entender el contexto, pero prioriza la última solicitud del usuario.** DEBES responder ÚNICAMENTE con un objeto JSON válido que contenga una lista de los medios encontrados. CUALQUIER OTRA RESPUESTA ES INCORRECTA Y SERÁ IGNORADA. NO INCLUYAS NINGÚN TEXTO ADICIONAL O CONVERSACIONAL FUERA DEL OBJETO JSON.

Formato de salida:
```json
{
  "media": [
    {
      "type": "PELICULA" o "SERIE",
      "title": "Nombre de la Película o Serie",
      "year": "Año de estreno (si se menciona, opcional)",
      "actor": "Nombre del actor (si se menciona, opcional)",
      "genre": "Género (si se menciona, opcional)",
      "director": "Nombre del director (si se menciona, opcional)"
    }
  ]
}
```

Si no encuentras ninguna película o serie, responde con: `{"media": []}`.

Ejemplos:
Usuario: Me gustaría saber sobre la película "El Padrino".
Respuesta: {"media": [{"type": "PELICULA", "title": "El Padrino"}]}

Usuario: ¿Qué tal la serie "Friends"?
Respuesta: {"media": [{"type": "SERIE", "title": "Friends"}]}

Usuario: Recomiéndame otras películas de Will Ferrell como "Elf" o "Blades of Glory".
Respuesta: {"media": [{"type": "PELICULA", "title": "Elf"}, {"type": "PELICULA", "title": "Blades of Glory"}]}

Usuario: Alguna otra de él?
Respuesta: {"media": [{"type": "PELICULA", "title": "Anchorman: The Legend of Ron Burgundy"}]} # Asumiendo que la conversación previa fue sobre Will Ferrell y se infiere el título.

Usuario: Alguna otra como la primera?
Respuesta: {"media": [{"type": "PELICULA", "title": "Crazy, Stupid, Love", "year": "2011"}]} # Asumiendo que la "primera" película de la conversación anterior fue Crazy, Stupid, Love (2011).

Usuario: Háblame de "The Office" de Estados Unidos.
Respuesta: {"media": [{"type": "SERIE", "title": "The Office", "year": "Estados Unidos"}]}

Usuario: ¿Tienes información sobre "Zoolander" (2001)?
Respuesta: {"media": [{"type": "PELICULA", "title": "Zoolander", "year": "2001"}]}

Usuario: ¿Qué me dices de "The Campaign" o "Blades of Glory"?
Respuesta: {"media": [{"type": "PELICULA", "title": "The Campaign"}, {"type": "PELICULA", "title": "Blades of Glory"}]}

Usuario: No sé qué ver.
Respuesta: {"media": []}
"""

SUGGESTION_PROMPT = """
Tu tarea es sugerir películas o series basadas en la solicitud del usuario y el historial de la conversación. DEBES sugerir al menos 3 títulos populares y bien conocidos para los que es probable que haya información detallada. **Considera el historial de la conversación para entender el contexto, pero prioriza la última solicitud del usuario.** **No repitas las películas que ya han sido recomendadas en el historial.** DEBES responder ÚNICAMENTE con un objeto JSON válido que contenga una lista de los medios sugeridos. CUALQUIER OTRA RESPUESTA ES INCORRECTA Y SERÁ IGNORADA. NO INCLUYAS NINGÚN TEXTO ADICIONAL O CONVERSACIONAL FUERA DEL OBJETO JSON. Si la solicitud es muy general y no hay un contexto claro, sugiere 3 películas o series populares y bien conocidas.

Formato de salida:
```json
{
  "media": [
    {
      "type": "PELICULA" o "SERIE",
      "title": "Nombre de la Película o Serie",
      "year": "Año de estreno (si es relevante, opcional)",
      "actor": "Nombre del actor (si se menciona, opcional)",
      "genre": "Género (si se menciona, opcional)",
      "director": "Nombre del director (si se menciona, opcional)"
    }
  ]
}
```

Si no puedes sugerir nada, responde con: `{"media": []}`.

Ejemplos:
Usuario: Recomiéndame otras películas de Will Ferrell.
Respuesta: {"media": [{"type": "PELICULA", "title": "Anchorman: The Legend of Ron Burgundy"}, {"type": "PELICULA", "title": "Talladega Nights: The Ballad of Ricky Bobby"}]}

Usuario: Quiero ver una serie de comedia.
Respuesta: {"media": [{"type": "SERIE", "title": "The Office"}, {"type": "SERIE", "title": "Parks and Recreation"}]}

Usuario: Dame algo de acción.
Respuesta: {"media": [{"type": "PELICULA", "title": "Mad Max: Fury Road"}, {"type": "PELICULA", "title": "John Wick"}]}

"""

CREATIVE_PROMPT = """
¡Hola, cinéfilo! Aquí te traigo unas recomendaciones que te van a encantar. ¡Espero que las disfrutes!

**INSTRUCCIONES ESTRICTAS:**

Tu función es generar una respuesta amigable y natural, formateada en Markdown. DEBES comenzar con un saludo amigable y luego presentar las recomendaciones. NO DEBES INCLUIR NINGÚN DETALLE ESPECÍFICO DE PELÍCULAS O SERIES, YA QUE ESO SERÁ MANEJADO POR OTRA PARTE DEL SISTEMA.

**DATOS DE ORIGEN (OBLIGATORIOS):**
{media_data}

**EJEMPLO DE SALIDA:**

¡Hola, cinéfilo! Aquí te traigo unas recomendaciones que te van a encantar. ¡Espero que las disfrutes!

"""

SALUDOS = ["/start", "hola", "buenas", "hey", "¿estás ahí", "estas ahi", "¿estas ahí"]

SALUDO_INICIAL = "¡Hola! 😊 ¿Listo para una recomendación de cine o series? Solo dime el género o tipo de peli/serie que quieres ver."
