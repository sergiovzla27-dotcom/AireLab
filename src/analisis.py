"""
AireLab - Modulo de Analisis de Datos
Procesa los CSVs con Pandas y conecta con datos de aire en tiempo real
"""

import os
import pandas as pd
from datetime import datetime
import sys

# Agregar src/ al path para importar openweather
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openweather import obtener_datos_actuales

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_ENCUESTAS = os.path.join(BASE_DIR, 'data', 'encuestas.csv')
RUTA_SUSCRIPTORES = os.path.join(BASE_DIR, 'data', 'suscriptores.csv')


def cargar_encuestas():
    if os.path.exists(RUTA_ENCUESTAS):
        try:
            return pd.read_csv(RUTA_ENCUESTAS)
        except Exception as e:
            print(f"Error cargando encuestas: {e}")
            return pd.DataFrame()
    return pd.DataFrame()


def cargar_suscriptores():
    if os.path.exists(RUTA_SUSCRIPTORES):
        try:
            return pd.read_csv(RUTA_SUSCRIPTORES)
        except Exception as e:
            print(f"Error cargando suscriptores: {e}")
            return pd.DataFrame()
    return pd.DataFrame()


def obtener_stats_publicas():
    """Genera las estadisticas publicas + datos de aire actual"""
    
    df = cargar_encuestas()
    df_subs = cargar_suscriptores()
    
    # NUEVO: Obtener datos del aire ahorita
    datos_aire = obtener_datos_actuales()
    
    if df.empty:
        return {
            "exito": False,
            "mensaje": "Aun no hay respuestas en la encuesta. Se el primero!",
            "total_respuestas": 0,
            "total_suscriptores": len(df_subs),
            "aire_actual": datos_aire if datos_aire.get('exito') else None
        }
    
    total = len(df)
    
    ultima_fecha = "N/A"
    if 'fecha_respuesta' in df.columns:
        try:
            df['fecha_respuesta'] = pd.to_datetime(df['fecha_respuesta'])
            ultima_fecha = df['fecha_respuesta'].max().strftime('%d/%m/%Y %H:%M')
        except:
            ultima_fecha = "N/A"
    
    # Porcentajes
    pct_sintomas = 0
    if 'sintomas' in df.columns:
        pct_sintomas = round((df['sintomas'] == 'si').sum() / total * 100, 1)
    
    pct_medico = 0
    if 'visitas_medico' in df.columns:
        visitas_si = df[df['visitas_medico'] != 'ninguna']
        pct_medico = round(len(visitas_si) / total * 100, 1)
    
    pct_usaria = 0
    if 'usaria_app' in df.columns:
        usarian = df[df['usaria_app'].isin(['prob_si', 'def_si'])]
        pct_usaria = round(len(usarian) / total * 100, 1)
    
    pct_recomendaria = 0
    if 'recomendaria' in df.columns:
        pct_recomendaria = round((df['recomendaria'] == 'si').sum() / total * 100, 1)
    
    # Edad
    distribucion_edad = {}
    if 'edad' in df.columns:
        conteo = df['edad'].value_counts()
        etiquetas_edad = {
            'menor_18': 'Menos de 18',
            '18_24': '18-24 años',
            '25_34': '25-34 años',
            '35_44': '35-44 años',
            '45_mas': '45+ años'
        }
        distribucion_edad = {etiquetas_edad.get(k, k): int(v) for k, v in conteo.items()}
    
    # Percepcion
    percepcion_aire = {}
    if 'calidad_aire' in df.columns:
        conteo = df['calidad_aire'].value_counts()
        etiquetas_aire = {
            'muy_buena': 'Muy buena', 'buena': 'Buena', 'regular': 'Regular',
            'mala': 'Mala', 'muy_mala': 'Muy mala'
        }
        percepcion_aire = {etiquetas_aire.get(k, k): int(v) for k, v in conteo.items()}
    
    # Meses enfermos
    meses_enfermos = {}
    if 'meses_enfermo' in df.columns:
        meses_dict = {}
        for valor in df['meses_enfermo'].dropna():
            if isinstance(valor, str):
                for mes in valor.split(','):
                    mes = mes.strip()
                    if mes:
                        meses_dict[mes] = meses_dict.get(mes, 0) + 1
        
        orden_meses = ['may_2025', 'jun_2025', 'jul_2025', 'ago_2025', 
                       'sep_2025', 'oct_2025', 'nov_2025', 'dic_2025',
                       'ene_2026', 'feb_2026', 'mar_2026', 'abr_2026']
        
        etiquetas = {
            'may_2025': 'May 25', 'jun_2025': 'Jun 25', 'jul_2025': 'Jul 25', 'ago_2025': 'Ago 25',
            'sep_2025': 'Sep 25', 'oct_2025': 'Oct 25', 'nov_2025': 'Nov 25', 'dic_2025': 'Dic 25',
            'ene_2026': 'Ene 26', 'feb_2026': 'Feb 26', 'mar_2026': 'Mar 26', 'abr_2026': 'Abr 26'
        }
        
        meses_enfermos = {etiquetas.get(m, m): meses_dict.get(m, 0) for m in orden_meses}
    
    # Vulnerables
    vulnerables_count = {'ninos': 0, 'adultos_mayores': 0, 'asma': 0, 'ninguna': 0}
    if 'vulnerables' in df.columns:
        for valor in df['vulnerables'].dropna():
            if isinstance(valor, str):
                for v in valor.split(','):
                    v = v.strip()
                    if v in vulnerables_count:
                        vulnerables_count[v] += 1
    
    # ============================================
    # NUEVO: ANALISIS DE CORRELACION AIRE - SALUD
    # ============================================
    correlacion = analizar_correlacion(df, datos_aire)
    
    return {
        "exito": True,
        "total_respuestas": total,
        "total_suscriptores": len(df_subs),
        "ultima_respuesta": ultima_fecha,
        "porcentajes": {
            "con_sintomas": pct_sintomas,
            "visitaron_medico": pct_medico,
            "usarian_app": pct_usaria,
            "recomendarian": pct_recomendaria
        },
        "distribucion_edad": distribucion_edad,
        "percepcion_aire": percepcion_aire,
        "meses_enfermos": meses_enfermos,
        "vulnerables": vulnerables_count,
        "aire_actual": datos_aire if datos_aire.get('exito') else None,
        "correlacion": correlacion
    }


def analizar_correlacion(df, datos_aire):
    """
    Analiza la posible relacion entre la calidad del aire y los sintomas reportados
    Esta es la PARTE CIENTIFICA mas importante del proyecto.
    """
    
    if df.empty or not datos_aire.get('exito'):
        return None
    
    pm25_actual = datos_aire.get('pm2_5', 0)
    nivel_color = datos_aire.get('nivel', {}).get('color', 'verde')
    nivel_texto = datos_aire.get('nivel', {}).get('texto', 'Bueno')
    
    total = len(df)
    
    # Cuantos reportaron sintomas
    con_sintomas = 0
    if 'sintomas' in df.columns:
        con_sintomas = (df['sintomas'] == 'si').sum()
    
    pct_sintomas = round(con_sintomas / total * 100, 1) if total > 0 else 0
    
    # Cuantos hogares tienen vulnerables
    con_vulnerables = 0
    if 'vulnerables' in df.columns:
        for valor in df['vulnerables'].dropna():
            if isinstance(valor, str) and valor != 'ninguna' and valor.strip():
                # Si tiene cualquier vulnerable que no sea 'ninguna'
                valores = [v.strip() for v in valor.split(',')]
                if any(v != 'ninguna' for v in valores):
                    con_vulnerables += 1
    
    pct_vulnerables = round(con_vulnerables / total * 100, 1) if total > 0 else 0
    
    # Generar mensaje educativo segun el nivel
    if nivel_color == 'verde':
        interpretacion = {
            "titulo": "Hoy el aire esta limpio",
            "mensaje": f"Aunque el aire esta bien ahora, el {pct_sintomas}% de los participantes ha tenido sintomas respiratorios este año. Esto significa que la calidad del aire no es estable y por eso es importante monitorearla.",
            "color": "verde"
        }
    elif nivel_color == 'amarillo':
        interpretacion = {
            "titulo": "El aire esta moderado",
            "mensaje": f"Con el aire en este nivel, las personas vulnerables ({pct_vulnerables}% de los hogares encuestados tienen una) deberian tener precaucion. El {pct_sintomas}% ya ha presentado sintomas en el año.",
            "color": "amarillo"
        }
    elif nivel_color == 'naranja':
        interpretacion = {
            "titulo": "Atencion: el aire afecta a grupos sensibles",
            "mensaje": f"Niños, adultos mayores y personas con asma deben cuidarse. El {pct_vulnerables}% de los hogares encuestados tiene a alguien vulnerable. Esto demuestra por que necesitamos AireLab.",
            "color": "naranja"
        }
    else:
        interpretacion = {
            "titulo": "Alerta: el aire es peligroso",
            "mensaje": f"En este nivel todos deben cuidarse. El {pct_sintomas}% de las personas ya ha tenido sintomas respiratorios. Niveles asi pueden estar causando estos sintomas.",
            "color": "rojo"
        }
    
    return {
        "pm25_actual": pm25_actual,
        "nivel_color": nivel_color,
        "nivel_texto": nivel_texto,
        "pct_sintomas": pct_sintomas,
        "pct_vulnerables": pct_vulnerables,
        "interpretacion": interpretacion
    }


def obtener_stats_admin():
    """Estadisticas detalladas para el panel de admin"""
    
    publicas = obtener_stats_publicas()
    df = cargar_encuestas()
    df_subs = cargar_suscriptores()
    
    if df.empty:
        return publicas
    
    ocupaciones = {}
    if 'ocupacion' in df.columns:
        ocupaciones = df['ocupacion'].value_counts().to_dict()
    
    funciones_count = {}
    if 'funciones' in df.columns:
        for valor in df['funciones'].dropna():
            if isinstance(valor, str):
                for f in valor.split(','):
                    f = f.strip()
                    if f:
                        funciones_count[f] = funciones_count.get(f, 0) + 1
    
    columnas_mostrar = ['id_encuesta', 'fecha_respuesta', 'edad', 'ocupacion', 
                        'sintomas', 'usaria_app', 'recomendaria']
    columnas_existen = [c for c in columnas_mostrar if c in df.columns]
    tabla_encuestas = df[columnas_existen].fillna('-').to_dict('records')
    
    tabla_suscriptores = []
    if not df_subs.empty:
        columnas_subs = ['id_suscriptor', 'fecha_suscripcion', 'nombre', 'edad', 'frecuencia', 'estado']
        columnas_existen_subs = [c for c in columnas_subs if c in df_subs.columns]
        tabla_suscriptores = df_subs[columnas_existen_subs].fillna('-').to_dict('records')
    
    resultado = publicas.copy()
    resultado['ocupaciones'] = ocupaciones
    resultado['funciones_deseadas'] = funciones_count
    resultado['tabla_encuestas'] = tabla_encuestas
    resultado['tabla_suscriptores'] = tabla_suscriptores
    
    return resultado