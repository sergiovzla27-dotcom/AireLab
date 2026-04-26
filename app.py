"""
AireLab - Aplicacion Flask principal
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sys
import os

# Agregar src/ al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from openweather import obtener_datos_actuales, obtener_datos_historicos_24h
from analisis import obtener_stats_publicas, obtener_stats_admin
from notificaciones import enviar_alerta_a_suscriptor
from sheets import (
    guardar_suscriptor,
    guardar_encuesta,
    dar_de_baja,
    leer_suscriptores_activos,
    leer_historial_hoy,
    guardar_historial_alerta,
    obtener_stats_sheets
)

app = Flask(__name__)
app.secret_key = 'airelab-2026-navojoa-secret-key'

# ============================================
# CREDENCIALES DE ADMIN
# ============================================
ADMIN_USER = os.environ.get('ADMIN_USER', 'Sergio')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'NavojoaAire2026')


# ============================================
# RUTAS PRINCIPALES
# ============================================

@app.route('/')
def index():
    """Dashboard principal"""
    datos_actuales = obtener_datos_actuales()
    datos_historicos = obtener_datos_historicos_24h()
    stats = obtener_stats_publicas()
    return render_template(
        'dashboard.html',
        datos=datos_actuales,
        historico=datos_historicos,
        stats=stats
    )


@app.route('/encuesta')
def encuesta():
    return render_template('encuesta.html')


@app.route('/alertas')
def alertas():
    return render_template('alertas.html')


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/resultados')
def resultados():
    """Pagina publica de resultados"""
    stats = obtener_stats_publicas()
    stats_sheets = obtener_stats_sheets()
    return render_template('resultados.html', stats=stats, stats_sheets=stats_sheets)


# ============================================
# PANEL DE ADMIN (con login)
# ============================================

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Panel privado de administracion"""

    if session.get('admin_logueado'):
        stats = obtener_stats_admin()
        stats_sheets = obtener_stats_sheets()
        resultado_auto = verificar_y_enviar_alertas_automaticas()
        return render_template(
            'admin.html',
            stats=stats,
            stats_sheets=stats_sheets,
            autenticado=True,
            alerta_automatica=resultado_auto
        )

    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '').strip()

        if usuario == ADMIN_USER and password == ADMIN_PASS:
            session['admin_logueado'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin.html', autenticado=False, error="Usuario o contraseña incorrectos")

    return render_template('admin.html', autenticado=False)


@app.route('/admin/logout')
def admin_logout():
    """Cerrar sesion de admin"""
    session.pop('admin_logueado', None)
    return redirect(url_for('admin'))


# ============================================
# APIS
# ============================================

@app.route('/api/aire')
def api_aire():
    return jsonify(obtener_datos_actuales())


@app.route('/api/historico')
def api_historico():
    return jsonify(obtener_datos_historicos_24h())


@app.route('/api/stats')
def api_stats():
    return jsonify(obtener_stats_publicas())


# ============================================
# PROCESAMIENTO DE FORMULARIOS
# ============================================

@app.route('/procesar-encuesta', methods=['POST'])
def procesar_encuesta():
    try:
        datos = request.get_json()
        print("DATOS RECIBIDOS:", datos)  # línea temporal
        id_unico = guardar_encuesta(datos)
        return jsonify({"exito": True, "mensaje": "Encuesta guardada", "id": id_unico})
    except Exception as e:
        print(f"Error al guardar encuesta: {e}")
        return jsonify({"exito": False, "error": str(e)})


@app.route('/procesar-alerta', methods=['POST'])
def procesar_alerta():
    """Guarda los suscriptores de alertas en Google Sheets"""
    try:
        datos = request.get_json()
        id_unico = guardar_suscriptor(datos)
        return jsonify({"exito": True, "mensaje": "Suscripcion registrada", "id": id_unico})
    except Exception as e:
        print(f"Error al guardar suscripcion: {e}")
        return jsonify({"exito": False, "error": str(e)})


# ============================================
# DARSE DE BAJA DE ALERTAS
# ============================================

@app.route('/baja')
def darse_de_baja():
    """
    Permite a un suscriptor darse de baja con su ID
    URL: /baja?id=SUB-0001
    """
    id_suscriptor = request.args.get('id', '').strip()

    if not id_suscriptor:
        return render_template('baja.html', exito=False, mensaje="Falta el ID del suscriptor")

    try:
        resultado = dar_de_baja(id_suscriptor)

        if resultado.get('exito'):
            nombre = resultado.get('nombre', 'Usuario')
            ya_inactivo = resultado.get('ya_inactivo', False)
            if ya_inactivo:
                return render_template('baja.html', exito=True,
                    mensaje=f"Hola {nombre}, ya estabas dado de baja anteriormente.",
                    nombre=nombre, ya_inactivo=True)
            return render_template('baja.html', exito=True,
                mensaje="Te diste de baja correctamente.",
                nombre=nombre, ya_inactivo=False)
        else:
            return render_template('baja.html', exito=False,
                mensaje=resultado.get('mensaje', 'Error desconocido'))

    except Exception as e:
        print(f"Error al dar de baja: {e}")
        return render_template('baja.html', exito=False, mensaje=f"Error: {str(e)}")


# ============================================
# ENVIO MANUAL DE ALERTAS (desde admin)
# ============================================

@app.route('/api/enviar-alertas', methods=['POST'])
def api_enviar_alertas():
    """Envia alertas a todos los suscriptores activos. Solo admin."""

    if not session.get('admin_logueado'):
        return jsonify({"error": "No autorizado"}), 401

    try:
        datos_aire = obtener_datos_actuales()
        if not datos_aire:
            return jsonify({"error": "No se pudieron obtener datos del aire"}), 500

        suscriptores = leer_suscriptores_activos()

        if not suscriptores:
            return jsonify({"exito": False, "mensaje": "No hay suscriptores activos"})

        emails_exitosos = 0
        emails_fallidos = 0
        whatsapp_exitosos = 0
        whatsapp_fallidos = 0
        resultados = []

        for suscriptor in suscriptores:
            resultado = enviar_alerta_a_suscriptor(suscriptor, datos_aire)
            resultados.append(resultado)

            email_ok = resultado.get('email', {}).get('exito', False) if resultado.get('email') else False
            wa_ok = resultado.get('whatsapp', {}).get('exito', False) if resultado.get('whatsapp') else False

            if email_ok:
                emails_exitosos += 1
            else:
                emails_fallidos += 1

            if wa_ok:
                whatsapp_exitosos += 1
            else:
                whatsapp_fallidos += 1

        return jsonify({
            "exito": True,
            "total_suscriptores": len(suscriptores),
            "emails_exitosos": emails_exitosos,
            "emails_fallidos": emails_fallidos,
            "whatsapp_exitosos": whatsapp_exitosos,
            "whatsapp_fallidos": whatsapp_fallidos,
            "detalles": resultados
        })

    except Exception as e:
        print(f"Error al enviar alertas: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# SISTEMA AUTOMATICO DE ALERTAS
# ============================================

def debe_recibir_alerta(frecuencia, nivel_color):
    frecuencia = str(frecuencia).lower().strip()
    nivel = str(nivel_color).lower().strip()

    if frecuencia == 'diario':
        return True
    if frecuencia in ['precaucion', 'precaución']:
        return nivel in ['naranja', 'rojo', 'morado']
    if frecuencia in ['peligroso', 'urgente']:
        return nivel in ['rojo', 'morado']
    return nivel in ['naranja', 'rojo', 'morado']


def verificar_y_enviar_alertas_automaticas():
    """
    Verifica el aire actual y envia alertas automaticas
    respetando la frecuencia de cada suscriptor.
    Solo envia 1 vez por dia (evita spam).
    """
    try:
        datos_aire = obtener_datos_actuales()
        if not datos_aire:
            return {"enviado": False, "razon": "No se pudieron obtener datos del aire"}

        nivel_color = datos_aire.get('nivel', {}).get('color', 'verde')
        nivel_texto = datos_aire.get('nivel', {}).get('texto', 'Bueno')
        pm25 = datos_aire.get('pm2_5', 0)

        suscriptores = leer_suscriptores_activos()
        if not suscriptores:
            return {"enviado": False, "razon": "No hay suscriptores activos"}

        ya_enviados_hoy = leer_historial_hoy()

        emails_ok = 0
        whatsapp_ok = 0
        suscriptores_filtrados = []
        suscriptores_omitidos = []
        ya_recibidos = []

        for suscriptor in suscriptores:
            id_sub = suscriptor.get('id_suscriptor', '')
            frecuencia = suscriptor.get('frecuencia', 'diario')

            if id_sub in ya_enviados_hoy:
                ya_recibidos.append(id_sub)
                continue

            if not debe_recibir_alerta(frecuencia, nivel_color):
                suscriptores_omitidos.append({'id': id_sub})
                continue

            suscriptores_filtrados.append(suscriptor)

        if not suscriptores_filtrados:
            if ya_recibidos:
                razon = f"Todos ya recibieron alerta hoy ({len(ya_recibidos)})"
            elif suscriptores_omitidos:
                razon = f"Aire {nivel_texto} - nadie con esta preferencia debe recibir alerta"
            else:
                razon = "Aire en buen estado y nadie pidio resumen diario"
            return {
                "enviado": False,
                "razon": razon,
                "nivel": nivel_color,
                "pm25": pm25,
                "ya_recibidos_hoy": len(ya_recibidos)
            }

        for suscriptor in suscriptores_filtrados:
            resultado = enviar_alerta_a_suscriptor(suscriptor, datos_aire)

            email_ok = resultado.get('email', {}).get('exito', False) if resultado.get('email') else False
            wa_ok = resultado.get('whatsapp', {}).get('exito', False) if resultado.get('whatsapp') else False

            if email_ok:
                emails_ok += 1
            if wa_ok:
                whatsapp_ok += 1

            guardar_historial_alerta(
                id_suscriptor=suscriptor.get('id_suscriptor', ''),
                tipo='automatico',
                frecuencia=suscriptor.get('frecuencia', ''),
                nivel=nivel_color,
                pm25=pm25,
                email_ok=email_ok,
                whatsapp_ok=wa_ok
            )

        print(f"[ALERTA AUTO] Nivel: {nivel_color} | PM2.5: {pm25} | Enviados: {len(suscriptores_filtrados)} | Emails OK: {emails_ok}")

        return {
            "enviado": True,
            "nivel": nivel_color,
            "nivel_texto": nivel_texto,
            "pm25": pm25,
            "total_suscriptores": len(suscriptores),
            "alertas_enviadas": len(suscriptores_filtrados),
            "emails_enviados": emails_ok,
            "whatsapp_enviados": whatsapp_ok,
            "ya_recibidos_hoy": len(ya_recibidos),
            "omitidos_por_frecuencia": len(suscriptores_omitidos)
        }

    except Exception as e:
        print(f"Error en alertas automaticas: {e}")
        import traceback
        traceback.print_exc()
        return {"enviado": False, "razon": f"Error: {str(e)}"}


if __name__ == '__main__':
    print("=" * 50)
    print("AireLab - Servidor iniciando...")
    print("Abre tu navegador en: http://localhost:5000")
    print("Panel de admin: http://localhost:5000/admin")
    print("=" * 50)
    app.run(debug=True, port=5000)