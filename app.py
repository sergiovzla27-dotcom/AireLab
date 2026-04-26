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

app = Flask(__name__)
app.secret_key = 'airelab-2026-navojoa-secret-key'

# ============================================
# CREDENCIALES DE ADMIN
# ============================================
# Estas son las credenciales para entrar al panel /admin
# Para cambiarlas, modifica las dos lineas de abajo
ADMIN_USER = 'Sergio'
ADMIN_PASS = 'NavojoaAire2026'


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
    return render_template('resultados.html', stats=stats)


# ============================================
# PANEL DE ADMIN (con login)    
# ============================================

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Panel privado de administracion"""
    
    if session.get('admin_logueado'):
        stats = obtener_stats_admin()
        
        # SISTEMA AUTOMATICO: verificar y enviar alertas si es necesario
        resultado_auto = verificar_y_enviar_alertas_automaticas()
        
        return render_template(
            'admin.html', 
            stats=stats, 
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
    """Guarda las respuestas de la encuesta en un CSV con Pandas + ID unico"""
    import pandas as pd
    from datetime import datetime
    
    try:
        datos = request.get_json()
        ruta_csv = os.path.join(os.path.dirname(__file__), 'data', 'encuestas.csv')
        os.makedirs(os.path.dirname(ruta_csv), exist_ok=True)
        
        if os.path.exists(ruta_csv):
            df_existente = pd.read_csv(ruta_csv)
            siguiente_numero = len(df_existente) + 1
        else:
            df_existente = None
            siguiente_numero = 1
        
        id_unico = f"ENC-{siguiente_numero:04d}"
        ahora = datetime.now()
        
        datos_completos = {
            'id_encuesta': id_unico,
            'fecha_respuesta': ahora.strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': int(ahora.timestamp())
        }
        datos_completos.update(datos)
        
        for key, value in datos_completos.items():
            if isinstance(value, list):
                datos_completos[key] = ','.join(value)
        
        df_nuevo = pd.DataFrame([datos_completos])
        
        if df_existente is not None:
            df = pd.concat([df_existente, df_nuevo], ignore_index=True)
        else:
            df = df_nuevo
        
        df.to_csv(ruta_csv, index=False, encoding='utf-8')
        
        print(f"Encuesta guardada con ID: {id_unico} | Total: {len(df)}")
        
        return jsonify({"exito": True, "mensaje": "Encuesta guardada", "id": id_unico})
    
    except Exception as e:
        print(f"Error al guardar encuesta: {e}")
        return jsonify({"exito": False, "error": str(e)})


@app.route('/procesar-alerta', methods=['POST'])
def procesar_alerta():
    """Guarda los suscriptores de alertas en suscriptores.csv con Pandas"""
    import pandas as pd
    from datetime import datetime
    
    try:
        datos = request.get_json()
        ruta_csv = os.path.join(os.path.dirname(__file__), 'data', 'suscriptores.csv')
        os.makedirs(os.path.dirname(ruta_csv), exist_ok=True)
        
        if os.path.exists(ruta_csv):
            df_existente = pd.read_csv(ruta_csv)
            siguiente_numero = len(df_existente) + 1
        else:
            df_existente = None
            siguiente_numero = 1
        
        id_unico = f"SUB-{siguiente_numero:04d}"
        ahora = datetime.now()
        
        datos_completos = {
            'id_suscriptor': id_unico,
            'fecha_suscripcion': ahora.strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': int(ahora.timestamp()),
            'estado': 'activo'
        }
        datos_completos.update(datos)
        
        for key, value in datos_completos.items():
            if isinstance(value, list):
                datos_completos[key] = ','.join(value)
        
        df_nuevo = pd.DataFrame([datos_completos])
        
        if df_existente is not None:
            df = pd.concat([df_existente, df_nuevo], ignore_index=True)
        else:
            df = df_nuevo
        
        df.to_csv(ruta_csv, index=False, encoding='utf-8')
        
        print(f"Nuevo suscriptor: {id_unico} | Total: {len(df)}")
        
        return jsonify({"exito": True, "mensaje": "Suscripcion registrada", "id": id_unico})
    
    except Exception as e:
        print(f"Error al guardar suscripcion: {e}")
        return jsonify({"exito": False, "error": str(e)})


# ============================================
# INICIAR
# ============================================
# ============================================
# ENVIO DE ALERTAS
# ============================================

# ============================================
# SISTEMA AUTOMATICO DE ALERTAS
# ============================================

def debe_recibir_alerta(frecuencia, nivel_color):
    """
    Decide si un suscriptor debe recibir alerta segun su preferencia.
    
    Frecuencias posibles:
    - 'diario': recibe TODOS los dias sin importar el nivel
    - 'precaucion': solo si nivel >= naranja
    - 'peligroso': solo si nivel >= rojo
    
    Returns: True si debe recibir, False si no
    """
    
    frecuencia = str(frecuencia).lower().strip()
    nivel = str(nivel_color).lower().strip()
    
    # Resumen diario: SIEMPRE recibe
    if frecuencia == 'diario':
        return True
    
    # Precaucion: naranja, rojo o morado
    if frecuencia in ['precaucion', 'precaución']:
        return nivel in ['naranja', 'rojo', 'morado']
    
    # Peligroso: solo rojo o morado
    if frecuencia in ['peligroso', 'urgente']:
        return nivel in ['rojo', 'morado']
    
    # Por defecto, asumir precaucion
    return nivel in ['naranja', 'rojo', 'morado']


def verificar_y_enviar_alertas_automaticas():
    """
    Verifica el aire actual y envia alertas automaticas
    respetando la frecuencia que cada suscriptor eligio.
    
    Solo envia 1 vez por dia a cada suscriptor (evita spam).
    
    Returns:
        dict con info de lo que se hizo
    """
    import csv
    from datetime import datetime
    
    try:
        # 1. Obtener datos actuales del aire
        datos_aire = obtener_datos_actuales()
        
        if not datos_aire:
            return {"enviado": False, "razon": "No se pudieron obtener datos del aire"}
        
        nivel_color = datos_aire.get('nivel', {}).get('color', 'verde')
        nivel_texto = datos_aire.get('nivel', {}).get('texto', 'Bueno')
        pm25 = datos_aire.get('pm2_5', 0)
        
        # 2. Leer suscriptores activos
        ruta_csv = os.path.join(os.path.dirname(__file__), 'data', 'suscriptores.csv')
        
        if not os.path.exists(ruta_csv):
            return {"enviado": False, "razon": "No hay suscriptores"}
        
        suscriptores = []
        with open(ruta_csv, 'r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                if fila.get('estado', '').lower() == 'activo':
                    suscriptores.append(fila)
        
        if not suscriptores:
            return {"enviado": False, "razon": "No hay suscriptores activos"}
        
        # 3. Leer historial - quien YA recibio hoy
        ruta_historial = os.path.join(os.path.dirname(__file__), 'data', 'historial_alertas.csv')
        os.makedirs(os.path.dirname(ruta_historial), exist_ok=True)
        
        hoy = datetime.now().strftime('%Y-%m-%d')
        ya_enviados_hoy = set()
        
        if os.path.exists(ruta_historial):
            with open(ruta_historial, 'r', encoding='utf-8') as f:
                lector = csv.DictReader(f)
                for fila in lector:
                    if fila.get('fecha', '').startswith(hoy):
                        ya_enviados_hoy.add(fila.get('id_suscriptor', ''))
        
        # 4. Filtrar y enviar a quienes corresponde
        emails_ok = 0
        whatsapp_ok = 0
        suscriptores_filtrados = []
        suscriptores_omitidos = []
        ya_recibidos = []
        
        for suscriptor in suscriptores:
            id_sub = suscriptor.get('id_suscriptor', '')
            frecuencia = suscriptor.get('frecuencia', 'diario')
            
            # ¿Ya recibio hoy?
            if id_sub in ya_enviados_hoy:
                ya_recibidos.append(id_sub)
                continue
            
            # ¿Le toca segun su frecuencia?
            if not debe_recibir_alerta(frecuencia, nivel_color):
                suscriptores_omitidos.append({
                    'id': id_sub,
                    'razon': f'Frecuencia {frecuencia}, nivel {nivel_color}'
                })
                continue
            
            # Le toca! Enviar
            suscriptores_filtrados.append(suscriptor)
        
        # 5. Si nadie debe recibir, salir
        if not suscriptores_filtrados:
            razon_principal = "Aire en buen estado y nadie pidio resumen diario"
            
            if ya_recibidos:
                razon_principal = f"Todos los suscriptores ya recibieron su alerta hoy ({len(ya_recibidos)})"
            elif suscriptores_omitidos:
                razon_principal = f"Aire {nivel_texto} - nadie con esta preferencia debe recibir alerta"
            
            return {
                "enviado": False,
                "razon": razon_principal,
                "nivel": nivel_color,
                "nivel_texto": nivel_texto,
                "pm25": pm25,
                "ya_recibidos_hoy": len(ya_recibidos)
            }
        
        # 6. Enviar y registrar
        ahora = datetime.now()
        archivo_existe = os.path.exists(ruta_historial)
        
        with open(ruta_historial, 'a', encoding='utf-8', newline='') as f:
            escritor = csv.writer(f)
            
            if not archivo_existe:
                escritor.writerow([
                    'fecha', 'id_suscriptor', 'tipo', 'frecuencia', 
                    'nivel', 'pm25', 'email_ok', 'whatsapp_ok'
                ])
            
            for suscriptor in suscriptores_filtrados:
                resultado = enviar_alerta_a_suscriptor(suscriptor, datos_aire)
                
                email_ok = resultado.get('email', {}).get('exito', False) if resultado.get('email') else False
                wa_ok = resultado.get('whatsapp', {}).get('exito', False) if resultado.get('whatsapp') else False
                
                if email_ok:
                    emails_ok += 1
                if wa_ok:
                    whatsapp_ok += 1
                
                escritor.writerow([
                    ahora.strftime('%Y-%m-%d %H:%M:%S'),
                    suscriptor.get('id_suscriptor', ''),
                    'automatico',
                    suscriptor.get('frecuencia', ''),
                    nivel_color,
                    pm25,
                    'si' if email_ok else 'no',
                    'si' if wa_ok else 'no'
                ])
        
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
    
    # ============================================
# DARSE DE BAJA DE ALERTAS
# ============================================

@app.route('/baja')
def darse_de_baja():
    """
    Permite a un suscriptor darse de baja con su ID
    URL: /baja?id=SUB-0001
    """
    import pandas as pd
    
    id_suscriptor = request.args.get('id', '').strip()
    
    if not id_suscriptor:
        return render_template('baja.html', exito=False, mensaje="Falta el ID del suscriptor")
    
    try:
        ruta_csv = os.path.join(os.path.dirname(__file__), 'data', 'suscriptores.csv')
        
        if not os.path.exists(ruta_csv):
            return render_template('baja.html', exito=False, mensaje="No se encontró la base de datos")
        
        # Leer el CSV
        df = pd.read_csv(ruta_csv)
        
        # Buscar el suscriptor
        if 'id_suscriptor' not in df.columns:
            return render_template('baja.html', exito=False, mensaje="ID no encontrado")
        
        mask = df['id_suscriptor'] == id_suscriptor
        
        if not mask.any():
            return render_template('baja.html', exito=False, mensaje=f"No se encontró el suscriptor {id_suscriptor}")
        
        # Obtener el nombre antes de cambiar
        nombre = df.loc[mask, 'nombre'].values[0] if 'nombre' in df.columns else 'Usuario'
        
        # Verificar si ya estaba inactivo
        estado_actual = df.loc[mask, 'estado'].values[0] if 'estado' in df.columns else 'activo'
        
        if str(estado_actual).lower() == 'inactivo':
            return render_template('baja.html', exito=True, mensaje=f"Hola {nombre}, ya estabas dado de baja anteriormente.", nombre=nombre, ya_inactivo=True)
        
        # Cambiar estado a inactivo
        df.loc[mask, 'estado'] = 'inactivo'
        df.to_csv(ruta_csv, index=False, encoding='utf-8')
        
        print(f"Suscriptor {id_suscriptor} ({nombre}) se dio de baja")
        
        return render_template('baja.html', exito=True, mensaje=f"Te diste de baja correctamente.", nombre=nombre, ya_inactivo=False)
    
    except Exception as e:
        print(f"Error al dar de baja: {e}")
        return render_template('baja.html', exito=False, mensaje=f"Error: {str(e)}")

@app.route('/api/enviar-alertas', methods=['POST'])
def api_enviar_alertas():
    """
    Envia alertas a todos los suscriptores activos.
    Solo accesible desde admin.
    """
    import csv
    
    # Verificar que sea admin
    if not session.get('admin_logueado'):
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        # Obtener datos actuales del aire
        datos_aire = obtener_datos_actuales()
        
        if not datos_aire:
            return jsonify({"error": "No se pudieron obtener datos del aire"}), 500
        
        # Leer suscriptores activos
        ruta_csv = os.path.join(os.path.dirname(__file__), 'data', 'suscriptores.csv')
        
        if not os.path.exists(ruta_csv):
            return jsonify({"error": "No hay suscriptores"}), 404
        
        suscriptores = []
        with open(ruta_csv, 'r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                if fila.get('estado', '').lower() == 'activo':
                    suscriptores.append(fila)
        
        if not suscriptores:
            return jsonify({
                "exito": False,
                "mensaje": "No hay suscriptores activos"
            })
        
        # Enviar a cada suscriptor
        resultados = []
        emails_exitosos = 0
        whatsapp_exitosos = 0
        emails_fallidos = 0
        whatsapp_fallidos = 0
        
        for suscriptor in suscriptores:
            resultado = enviar_alerta_a_suscriptor(suscriptor, datos_aire)
            resultados.append(resultado)
            
            if resultado.get('email'):
                if resultado['email'].get('exito'):
                    emails_exitosos += 1
                else:
                    emails_fallidos += 1
            
            if resultado.get('whatsapp'):
                if resultado['whatsapp'].get('exito'):
                    whatsapp_exitosos += 1
                else:
                    whatsapp_fallidos += 1
        
        print(f"Alertas enviadas | Total: {len(suscriptores)} | Emails OK: {emails_exitosos} | WA OK: {whatsapp_exitosos}")
        
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

if __name__ == '__main__':
    print("=" * 50)
    print("AireLab - Servidor iniciando...")
    print("Abre tu navegador en: http://localhost:5000")
    print("Panel de admin: http://localhost:5000/admin")
    print("Resultados publicos: http://localhost:5000/resultados")
    print("=" * 50)
    print("CREDENCIALES ADMIN:")
    print(f"  Usuario: {ADMIN_USER}")
    print(f"  Password: {ADMIN_PASS}")
    print("=" * 50)
    app.run(debug=True, port=5000)