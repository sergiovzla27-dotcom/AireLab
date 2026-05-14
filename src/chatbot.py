"""
AireLab - Chatbot Hibrido (Reglas + Gemini AI)
Asistente inteligente sobre calidad del aire en Navojoa.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# ============================================
# REGLAS LOCALES (solo respuestas exactas)
# ============================================

REGLAS_RAPIDAS = {
    "saludo": {
        "palabras_clave": ["hola", "buenas tardes", "buenas noches", "buenos dias", "hey"],
        "respuesta": "¡Hola! Soy el asistente de AireLab. Puedo ayudarte con preguntas sobre la calidad del aire en Navojoa, recomendaciones de salud y cómo usar el sitio. ¿En qué te ayudo?"
    },
    "despedida": {
        "palabras_clave": ["adios", "bye", "hasta luego", "nos vemos"],
        "respuesta": "¡Hasta luego! Recuerda revisar AireLab cada día. Si quieres avisos automáticos, suscríbete en 'Alertas'."
    },
    "gracias": {
        "palabras_clave": ["gracias", "muchas gracias"],
        "respuesta": "¡De nada! Estoy aquí para ayudarte. ¿Quieres preguntar algo más?"
    }
}


def buscar_en_reglas(pregunta):
    """Solo responde con reglas si la pregunta es MUY simple (saludos, gracias, etc)"""
    
    pregunta_lower = pregunta.lower().strip()
    pregunta_lower = pregunta_lower.replace("?", "").replace("¿", "")
    pregunta_lower = pregunta_lower.replace("¡", "").replace("!", "")
    pregunta_lower = pregunta_lower.replace(",", "").replace(".", "")
    
    # Solo si la pregunta es CORTA (menos de 5 palabras), busca reglas
    if len(pregunta_lower.split()) > 4:
        return None
    
    for tema, info in REGLAS_RAPIDAS.items():
        for palabra in info["palabras_clave"]:
            palabra_lower = palabra.lower()
            
            # Coincidencia exacta
            if pregunta_lower == palabra_lower or pregunta_lower.startswith(palabra_lower):
                return info["respuesta"]
    
    return None


def responder_con_gemini(pregunta, contexto_aire):
    """Llama a Gemini para responder cualquier pregunta"""
    
    if not GEMINI_API_KEY:
        return None
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt_sistema = f"""Eres el asistente virtual de AireLab, una plataforma de monitoreo de calidad del aire en Navojoa, Sonora, Mexico.

CONTEXTO ACTUAL DEL AIRE EN NAVOJOA:
- PM2.5 actual: {contexto_aire.get('pm2_5', 'N/A')} µg/m³
- Nivel: {contexto_aire.get('nivel_texto', 'N/A')}
- Color del nivel: {contexto_aire.get('nivel_color', 'N/A')}
- Fecha: {contexto_aire.get('fecha', 'N/A')}

INFORMACION DE AIRELAB:
- AireLab es una plataforma web desarrollada por estudiantes de Ingenieria en Software de UES Navojoa
- Usa datos de OpenWeather API actualizados cada hora
- Tiene secciones: Inicio, Encuesta, Alertas, Soluciones, Resultados, Sobre
- Los usuarios pueden suscribirse a alertas por correo
- La encuesta tiene 16 preguntas y toma 5 minutos
- Niveles PM2.5: 0-12 Limpio, 12-35 Aceptable, 35-55 Danino sensibles, 55-150 Peligroso, +150 Emergencia

INSTRUCCIONES:
- Responde en espanol mexicano, natural y cercano
- Maximo 3 parrafos cortos
- Si la pregunta es sobre salud personal, recuerda que no eres medico
- Si la pregunta es sobre algo ajeno al aire/salud/AireLab, redirige amablemente al tema
- Usa los datos actuales del aire si son relevantes
- No inventes datos: si no sabes, dilo
- No uses emojis
- Tono: amable, claro, sin tecnicismos innecesarios

PREGUNTA DEL USUARIO:
{pregunta}

Respuesta:"""
        
        respuesta = model.generate_content(prompt_sistema)
        return respuesta.text.strip()
        
    except Exception as e:
        print(f"[Chatbot] Error con Gemini: {e}")
        return None


def respuesta_generica():
    """Respuesta cuando Gemini falla"""
    return ("Lo siento, en este momento no puedo procesar tu pregunta. "
            "Puedes explorar las secciones del sitio o intentar de nuevo en un momento.")


def procesar_pregunta(pregunta, contexto_aire=None):
    """
    Funcion principal del chatbot.
    1. Si es saludo/despedida simple, regla local
    2. Cualquier otra cosa, va a Gemini
    3. Si Gemini falla, mensaje generico
    """
    
    if not pregunta or len(pregunta.strip()) < 2:
        return {
            "exito": False,
            "respuesta": "Por favor escribe una pregunta válida.",
            "fuente": "validacion"
        }
    
    # Paso 1: Solo reglas simples (saludos, gracias, adios)
    respuesta_local = buscar_en_reglas(pregunta)
    if respuesta_local:
        return {
            "exito": True,
            "respuesta": respuesta_local,
            "fuente": "reglas"
        }
    
    # Paso 2: Todo lo demas a Gemini
    if contexto_aire is None:
        contexto_aire = {}
    
    respuesta_gemini = responder_con_gemini(pregunta, contexto_aire)
    if respuesta_gemini:
        return {
            "exito": True,
            "respuesta": respuesta_gemini,
            "fuente": "gemini"
        }
    
    # Paso 3: Respaldo
    return {
        "exito": True,
        "respuesta": respuesta_generica(),
        "fuente": "generica"
    }