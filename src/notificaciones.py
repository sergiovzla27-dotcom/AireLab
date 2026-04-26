"""
AireLab - Modulo de Notificaciones
Envia alertas reales por WhatsApp y Email
"""

import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GMAIL_USUARIO = os.getenv("GMAIL_USUARIO")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")


# ============================================
# WHATSAPP via CallMeBot
# ============================================

def enviar_whatsapp(numero, mensaje):
    if not WHATSAPP_API_KEY:
        return {"exito": False, "error": "No hay API Key de WhatsApp configurada"}
    
    try:
        numero_limpio = ''.join(filter(str.isdigit, str(numero)))
        
        if len(numero_limpio) == 10:
            numero_limpio = "521" + numero_limpio
        
        url = "https://api.callmebot.com/whatsapp.php"
        params = {
            "phone": numero_limpio,
            "text": mensaje,
            "apikey": WHATSAPP_API_KEY
        }
        
        respuesta = requests.get(url, params=params, timeout=15)
        
        if respuesta.status_code == 200:
            return {"exito": True, "mensaje": "WhatsApp enviado correctamente", "numero": numero_limpio}
        else:
            return {"exito": False, "error": f"Error {respuesta.status_code}: {respuesta.text}"}
    
    except Exception as e:
        return {"exito": False, "error": str(e)}


# ============================================
# EMAIL via Gmail SMTP
# ============================================

def enviar_email(destinatario, asunto, cuerpo_html):
    if not GMAIL_USUARIO or not GMAIL_PASSWORD:
        return {"exito": False, "error": "Gmail no configurado en .env"}
    
    try:
        mensaje = MIMEMultipart('alternative')
        mensaje['Subject'] = asunto
        mensaje['From'] = f"AireLab Navojoa <{GMAIL_USUARIO}>"
        mensaje['To'] = destinatario
        
        parte_html = MIMEText(cuerpo_html, 'html', 'utf-8')
        mensaje.attach(parte_html)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor:
            servidor.login(GMAIL_USUARIO, GMAIL_PASSWORD)
            servidor.send_message(mensaje)
        
        return {"exito": True, "mensaje": "Email enviado correctamente", "destinatario": destinatario}
    
    except Exception as e:
        return {"exito": False, "error": str(e)}


# ============================================
# GENERAR MENSAJES SEGUN NIVEL
# ============================================

def generar_mensaje_alerta(nombre, datos_aire, formato="whatsapp", id_suscriptor=""):
    nivel = datos_aire.get('nivel', {})
    pm25 = datos_aire.get('pm2_5', 0)
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    nivel_color = nivel.get('color', 'verde')
    nivel_texto = nivel.get('texto', 'Bueno')
    
    primer_nombre = nombre.split(' ')[0] if nombre else "amigo"
    
    emojis = {
        'verde': '🟢', 'amarillo': '🟡', 'naranja': '🟠',
        'rojo': '🔴', 'morado': '🟣'
    }
    emoji = emojis.get(nivel_color, '🔵')
    
    if nivel_color == 'verde':
        accion = "Es buen momento para salir y disfrutar del aire libre."
    elif nivel_color == 'amarillo':
        accion = "Si eres sensible (asma, alergias), ten precaucion."
    elif nivel_color == 'naranja':
        accion = "Ninos, adultos mayores y personas con asma deben quedarse adentro."
    elif nivel_color == 'rojo':
        accion = "EVITA salir lo mas posible. Usa cubrebocas si sales."
    else:
        accion = "EMERGENCIA: Quedate en casa, sella ventanas. Si tienes sintomas, busca atencion medica."
    
    if formato == "whatsapp":
        return f"""*AireLab - Alerta de Aire*

Hola {primer_nombre}!

{emoji} El aire en Navojoa esta: *{nivel_texto}*

PM2.5: {pm25} ug/m3
Fecha: {fecha}

*Recomendacion:*
{accion}

Mas info: http://localhost:5000

Para darte de baja: http://localhost:5000/baja?id={id_suscriptor}

_AireLab - analizando lo invisible_"""
    
    else:  # email html
        colores_html = {
            'verde': '#10b981', 'amarillo': '#eab308', 'naranja': '#f97316',
            'rojo': '#ef4444', 'morado': '#a855f7'
        }
        color = colores_html.get(nivel_color, '#10b981')
        
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; background: #f5f7f8; padding: 20px; margin: 0;">
    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        
        <div style="background: linear-gradient(135deg, #1a5f6f, #4a9ba8); padding: 32px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">AireLab</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-style: italic;">analizando lo invisible</p>
        </div>
        
        <div style="padding: 32px;">
            <h2 style="color: #1f2937; margin: 0 0 8px 0;">Hola {primer_nombre},</h2>
            <p style="color: #6b7280; margin: 0 0 24px 0;">Esto es lo que esta pasando con el aire en Navojoa ahorita:</p>
            
            <div style="background: {color}15; border: 2px solid {color}; border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 24px;">
                <div style="font-size: 48px; font-weight: 800; color: {color}; line-height: 1;">{pm25}</div>
                <div style="color: #6b7280; font-size: 14px; margin-top: 4px;">ug/m3 (PM2.5)</div>
                <div style="background: {color}; color: white; padding: 8px 20px; border-radius: 50px; display: inline-block; margin-top: 16px; font-weight: 600;">
                    {nivel_texto}
                </div>
            </div>
            
            <div style="background: #f1f5f6; border-left: 4px solid #1a5f6f; padding: 16px; border-radius: 8px; margin-bottom: 24px;">
                <strong style="color: #1f2937;">Recomendacion:</strong>
                <p style="color: #6b7280; margin: 8px 0 0 0; line-height: 1.6;">{accion}</p>
            </div>
            
            <div style="text-align: center; margin-top: 32px;">
                <a href="http://localhost:5000" style="display: inline-block; background: #1a5f6f; color: white; padding: 14px 28px; border-radius: 50px; text-decoration: none; font-weight: 600;">Ver mas detalles</a>
            </div>
        </div>
        
        <div style="background: #fef3f2; border-top: 1px solid #fecaca; padding: 24px; text-align: center;">
            <p style="margin: 0 0 12px 0; color: #6b7280; font-size: 14px;">
                ¿Ya no quieres recibir alertas?
            </p>
            <a href="http://localhost:5000/baja?id={id_suscriptor}" 
               style="display: inline-block; background: #ef4444; color: white; padding: 14px 32px; border-radius: 50px; text-decoration: none; font-weight: 600; font-size: 15px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);">
                🔕 Darme de baja (1 clic)
            </a>
            <p style="margin: 16px 0 0 0; color: #9ca3af; font-size: 12px;">
                Es inmediato. No tienes que escribir nada.
            </p>
        </div>
        
        <div style="background: #f1f5f6; padding: 16px; text-align: center; color: #6b7280; font-size: 12px;">
            <p style="margin: 0;"><strong>AireLab</strong> · Monitoreo ciudadano de Navojoa</p>
        </div>
    </div>
</body>
</html>"""


# ============================================
# ENVIAR ALERTA A UN SUSCRIPTOR
# ============================================

def enviar_alerta_a_suscriptor(suscriptor, datos_aire):
    resultados = {
        "id": suscriptor.get('id_suscriptor', ''),
        "nombre": suscriptor.get('nombre', ''),
        "whatsapp": None,
        "email": None
    }
    
    nombre = suscriptor.get('nombre', 'Usuario')
    id_suscriptor = suscriptor.get('id_suscriptor', '')
    
    if str(suscriptor.get('canal_whatsapp', '')).lower() == 'si':
        numero = suscriptor.get('whatsapp', '')
        if numero and str(numero).strip():
            mensaje_wa = generar_mensaje_alerta(nombre, datos_aire, "whatsapp", id_suscriptor)
            resultados['whatsapp'] = enviar_whatsapp(numero, mensaje_wa)
    
    if str(suscriptor.get('canal_email', '')).lower() == 'si':
        email = suscriptor.get('email', '')
        if email and str(email).strip():
            mensaje_html = generar_mensaje_alerta(nombre, datos_aire, "email", id_suscriptor)
            asunto = f"AireLab - Alerta de aire ({datos_aire.get('nivel', {}).get('texto', 'Bueno')})"
            resultados['email'] = enviar_email(email, asunto, mensaje_html)
    
    return resultados