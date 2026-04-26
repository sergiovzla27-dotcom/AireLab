"""
AireLab - Módulo de Google Sheets
Reemplaza los archivos CSV locales por Google Sheets persistente.
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ============================================
# CONFIGURACION
# ============================================

SHEET_ID = '1VZa7au1aI4TapGJApJTa0lUsQ3fYj1KGCH_jaTwhsOw'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

COLUMNAS_SUSCRIPTORES = [
    'id_suscriptor', 'fecha_suscripcion', 'timestamp', 'estado',
    'nombre', 'edad', 'vulnerable', 'canal_whatsapp', 'whatsapp',
    'email', 'frecuencia', 'acepta', 'canal_email'
]

# Nombres reales que envía el formulario de la encuesta
COLUMNAS_ENCUESTAS = [
    'id_encuesta', 'fecha_respuesta', 'timestamp',
    'edad', 'ocupacion', 'vulnerables', 'actividades_aire',
    'calidad_aire', 'sintomas', 'meses_enfermo',
    'visitas_medico', 'enfermedades', 'sabia_calidad',
    'consulta_info', 'usaria_app', 'funciones',
    'impedimentos', 'recomendaria', 'comentario'
]

COLUMNAS_HISTORIAL = [
    'fecha', 'id_suscriptor', 'tipo', 'frecuencia',
    'nivel', 'pm25', 'email_ok', 'whatsapp_ok'
]


# ============================================
# CONEXION
# ============================================

def _get_client():
    """Crea el cliente de Google Sheets."""
    creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        ruta = os.path.join(os.path.dirname(__file__), '..', 'credenciales_google.json')
        creds = Credentials.from_service_account_file(ruta, scopes=SCOPES)
    
    return gspread.authorize(creds)


def _get_sheet(nombre_hoja):
    """Obtiene una hoja específica."""
    client = _get_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    hoja = spreadsheet.worksheet(nombre_hoja)
    return hoja


# ============================================
# SUSCRIPTORES
# ============================================

def leer_suscriptores():
    """Lee todos los suscriptores como lista de dicts."""
    try:
        hoja = _get_sheet('suscriptores')
        return hoja.get_all_records()
    except Exception as e:
        print(f"[Sheets] Error leyendo suscriptores: {e}")
        return []


def leer_suscriptores_activos():
    """Lee solo los suscriptores con estado 'activo'."""
    todos = leer_suscriptores()
    return [s for s in todos if str(s.get('estado', '')).lower() == 'activo']


def guardar_suscriptor(datos):
    """Guarda un nuevo suscriptor en Google Sheets."""
    try:
        hoja = _get_sheet('suscriptores')
        registros = hoja.get_all_records()
        siguiente_numero = len(registros) + 1
        id_unico = f"SUB-{siguiente_numero:04d}"
        ahora = datetime.now()

        fila = {col: '' for col in COLUMNAS_SUSCRIPTORES}
        fila['id_suscriptor'] = id_unico
        fila['fecha_suscripcion'] = ahora.strftime('%Y-%m-%d %H:%M:%S')
        fila['timestamp'] = int(ahora.timestamp())
        fila['estado'] = 'activo'

        for key, value in datos.items():
            if isinstance(value, list):
                fila[key] = ','.join(value)
            else:
                fila[key] = value

        fila_lista = [fila.get(col, '') for col in COLUMNAS_SUSCRIPTORES]
        hoja.append_row(fila_lista)

        print(f"[Sheets] Suscriptor guardado: {id_unico}")
        return id_unico

    except Exception as e:
        print(f"[Sheets] Error guardando suscriptor: {e}")
        raise


def dar_de_baja(id_suscriptor):
    """Cambia el estado de un suscriptor a 'inactivo'."""
    try:
        hoja = _get_sheet('suscriptores')
        registros = hoja.get_all_records()

        for i, registro in enumerate(registros):
            if registro.get('id_suscriptor') == id_suscriptor:
                nombre = registro.get('nombre', 'Usuario')
                estado_actual = str(registro.get('estado', 'activo')).lower()

                if estado_actual == 'inactivo':
                    return {'exito': True, 'nombre': nombre, 'ya_inactivo': True}

                fila_sheets = i + 2
                col_estado = COLUMNAS_SUSCRIPTORES.index('estado') + 1
                hoja.update_cell(fila_sheets, col_estado, 'inactivo')

                print(f"[Sheets] Suscriptor {id_suscriptor} dado de baja")
                return {'exito': True, 'nombre': nombre, 'ya_inactivo': False}

        return {'exito': False, 'mensaje': f'No se encontró el suscriptor {id_suscriptor}'}

    except Exception as e:
        print(f"[Sheets] Error dando de baja: {e}")
        return {'exito': False, 'mensaje': str(e)}


# ============================================
# ENCUESTAS
# ============================================

def leer_encuestas():
    """Lee todas las encuestas como lista de dicts."""
    try:
        hoja = _get_sheet('encuesta')
        return hoja.get_all_records()
    except Exception as e:
        print(f"[Sheets] Error leyendo encuestas: {e}")
        return []


def guardar_encuesta(datos):
    """Guarda una nueva respuesta de encuesta en Google Sheets."""
    try:
        hoja = _get_sheet('encuesta')
        registros = hoja.get_all_records()
        siguiente_numero = len(registros) + 1
        id_unico = f"ENC-{siguiente_numero:04d}"
        ahora = datetime.now()

        fila = {col: '' for col in COLUMNAS_ENCUESTAS}
        fila['id_encuesta'] = id_unico
        fila['fecha_respuesta'] = ahora.strftime('%Y-%m-%d %H:%M:%S')
        fila['timestamp'] = int(ahora.timestamp())

        for key, value in datos.items():
            if isinstance(value, list):
                fila[key] = ','.join(value)
            else:
                fila[key] = value

        fila_lista = [fila.get(col, '') for col in COLUMNAS_ENCUESTAS]
        hoja.append_row(fila_lista)

        print(f"[Sheets] Encuesta guardada: {id_unico} | Total: {siguiente_numero}")
        return id_unico

    except Exception as e:
        print(f"[Sheets] Error guardando encuesta: {e}")
        raise


# ============================================
# HISTORIAL DE ALERTAS
# ============================================

def leer_historial_hoy():
    """Retorna un set de IDs de suscriptores que ya recibieron alerta hoy."""
    try:
        hoja = _get_sheet('historial_alertas')
        registros = hoja.get_all_records()
        hoy = datetime.now().strftime('%Y-%m-%d')
        return {r['id_suscriptor'] for r in registros if str(r.get('fecha', '')).startswith(hoy)}
    except Exception as e:
        print(f"[Sheets] Error leyendo historial: {e}")
        return set()


def guardar_historial_alerta(id_suscriptor, tipo, frecuencia, nivel, pm25, email_ok, whatsapp_ok):
    """Guarda un registro en el historial de alertas."""
    try:
        hoja = _get_sheet('historial_alertas')
        ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fila = [
            ahora, id_suscriptor, tipo, frecuencia,
            nivel, pm25,
            'si' if email_ok else 'no',
            'si' if whatsapp_ok else 'no'
        ]
        hoja.append_row(fila)
    except Exception as e:
        print(f"[Sheets] Error guardando historial: {e}")


# ============================================
# STATS
# ============================================

def obtener_stats_sheets():
    """Retorna estadísticas básicas."""
    try:
        suscriptores = leer_suscriptores()
        encuestas = leer_encuestas()

        activos = sum(1 for s in suscriptores if str(s.get('estado', '')).lower() == 'activo')

        return {
            'total_suscriptores': len(suscriptores),
            'suscriptores_activos': activos,
            'total_encuestas': len(encuestas),
        }
    except Exception as e:
        print(f"[Sheets] Error en stats: {e}")
        return {
            'total_suscriptores': 0,
            'suscriptores_activos': 0,
            'total_encuestas': 0,
        }