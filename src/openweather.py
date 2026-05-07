"""
AireLab - Modulo de OpenWeather + Validacion Cruzada
Gestiona consultas a 3 fuentes (OpenWeather, WAQI, OpenAQ) y procesa con Pandas
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
LATITUD = float(os.getenv("LATITUD", 27.0772))
LONGITUD = float(os.getenv("LONGITUD", -109.4463))

URL_ACTUAL = "http://api.openweathermap.org/data/2.5/air_pollution"
URL_HISTORICO = "http://api.openweathermap.org/data/2.5/air_pollution/history"

# WAQI - World Air Quality Index (segunda fuente)
WAQI_TOKEN = os.getenv("WAQI_TOKEN")
URL_WAQI = "https://api.waqi.info/feed/geo:{lat};{lon}/"

# OpenAQ - Plataforma global de calidad del aire (tercera fuente)
URL_OPENAQ = "https://api.openaq.org/v3/locations"


def obtener_datos_actuales():
    """Obtiene datos actuales de calidad del aire con validacion cruzada (3 fuentes)"""
    
    parametros = {
        "lat": LATITUD,
        "lon": LONGITUD,
        "appid": API_KEY
    }
    
    try:
        respuesta = requests.get(URL_ACTUAL, params=parametros, timeout=10)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            contaminantes = datos['list'][0]['components']
            aqi = datos['list'][0]['main']['aqi']
            timestamp = datos['list'][0]['dt']
            
            # VALIDACION CRUZADA - Consultar 3 fuentes
            pm25_openweather = round(contaminantes['pm2_5'], 2)
            pm25_waqi = obtener_pm25_waqi()
            pm25_openaq = obtener_pm25_openaq()
            
            # Calcular PM2.5 final (promedio de las fuentes disponibles)
            fuentes_consultadas = ['OpenWeather']
            valores_pm25 = [pm25_openweather]
            
            if pm25_waqi is not None:
                fuentes_consultadas.append('WAQI')
                valores_pm25.append(pm25_waqi)
            
            if pm25_openaq is not None:
                fuentes_consultadas.append('OpenAQ')
                valores_pm25.append(pm25_openaq)
            
            pm25_promedio = round(sum(valores_pm25) / len(valores_pm25), 2)
            
            dias_es = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
            meses_es = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
            
            fecha_obj = datetime.fromtimestamp(timestamp)
            fecha_formateada = f"{dias_es[fecha_obj.weekday()]}, {fecha_obj.day} de {meses_es[fecha_obj.month-1]}"
            
            return {
                "exito": True,
                "fecha": fecha_formateada,
                "hora": fecha_obj.strftime('%H:%M'),
                "pm2_5": pm25_promedio,
                "pm10": round(contaminantes['pm10'], 2),
                "co": round(contaminantes['co'], 2),
                "no2": round(contaminantes['no2'], 2),
                "o3": round(contaminantes['o3'], 2),
                "so2": round(contaminantes['so2'], 2),
                "aqi": aqi,
                "nivel": interpretar_pm25(pm25_promedio),
                "recomendaciones": obtener_recomendaciones(pm25_promedio),
                "validacion": {
                    "fuentes_consultadas": fuentes_consultadas,
                    "total_fuentes": len(fuentes_consultadas),
                    "valores_individuales": {
                        "openweather": pm25_openweather,
                        "waqi": pm25_waqi,
                        "openaq": pm25_openaq
                    }
                }
            }
        else:
            return {"exito": False, "error": f"Error {respuesta.status_code}"}
    
    except Exception as e:
        return {"exito": False, "error": str(e)}


def obtener_pm25_waqi():
    """
    Consulta WAQI (segunda fuente para validacion cruzada).
    Devuelve solo PM2.5 para promediar con OpenWeather.
    """
    
    if not WAQI_TOKEN:
        return None
    
    try:
        url = URL_WAQI.format(lat=LATITUD, lon=LONGITUD)
        respuesta = requests.get(url, params={"token": WAQI_TOKEN}, timeout=10)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            
            if datos.get('status') == 'ok':
                iaqi = datos['data'].get('iaqi', {})
                pm25_valor = iaqi.get('pm25', {}).get('v')
                
                if pm25_valor is not None:
                    return round(float(pm25_valor), 2)
        
        return None
    
    except Exception as e:
        print(f"[WAQI] Error: {e}")
        return None


def obtener_pm25_openaq():
    """
    Consulta OpenAQ (tercera fuente para validacion cruzada).
    Busca la estacion mas cercana a Navojoa con datos de PM2.5.
    """
    
    try:
        # Buscar estaciones cercanas a Navojoa con PM2.5
        parametros = {
            "coordinates": f"{LATITUD},{LONGITUD}",
            "radius": 100000,  # 100 km de radio
            "parameter": "pm25",
            "limit": 1,
            "order_by": "distance"
        }
        
        respuesta = requests.get(URL_OPENAQ, params=parametros, timeout=10)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            resultados = datos.get('results', [])
            
            if resultados:
                # Obtener mediciones de la estacion mas cercana
                ubicacion_id = resultados[0].get('id')
                
                if ubicacion_id:
                    url_mediciones = f"https://api.openaq.org/v3/locations/{ubicacion_id}/latest"
                    resp_mediciones = requests.get(url_mediciones, timeout=10)
                    
                    if resp_mediciones.status_code == 200:
                        datos_med = resp_mediciones.json()
                        mediciones = datos_med.get('results', [])
                        
                        for medicion in mediciones:
                            if medicion.get('parameter') == 'pm25':
                                valor = medicion.get('value')
                                if valor is not None and valor >= 0:
                                    return round(float(valor), 2)
        
        return None
    
    except Exception as e:
        print(f"[OpenAQ] Error: {e}")
        return None


def obtener_datos_historicos_24h():
    """Obtiene datos historicos de las ultimas 24 horas"""
    
    fin = int(datetime.now().timestamp())
    inicio = int((datetime.now() - timedelta(hours=24)).timestamp())
    
    parametros = {
        "lat": LATITUD,
        "lon": LONGITUD,
        "start": inicio,
        "end": fin,
        "appid": API_KEY
    }
    
    try:
        respuesta = requests.get(URL_HISTORICO, params=parametros, timeout=15)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            lista = datos.get('list', [])
            
            if not lista:
                return {"exito": False, "error": "No hay datos historicos"}
            
            df = pd.DataFrame([
                {
                    'timestamp': item['dt'],
                    'hora': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
                    'pm2_5': item['components']['pm2_5'],
                    'pm10': item['components']['pm10']
                }
                for item in lista
            ])
            
            df = df.sort_values('timestamp')
            df = df.iloc[::3].reset_index(drop=True)
            
            return {
                "exito": True,
                "horas": df['hora'].tolist(),
                "pm2_5": [round(v, 2) for v in df['pm2_5'].tolist()],
                "pm10": [round(v, 2) for v in df['pm10'].tolist()],
                "estadisticas": {
                    "promedio_pm25": round(df['pm2_5'].mean(), 2),
                    "maximo_pm25": round(df['pm2_5'].max(), 2),
                    "minimo_pm25": round(df['pm2_5'].min(), 2)
                }
            }
        else:
            return {"exito": False, "error": f"Error {respuesta.status_code}"}
    
    except Exception as e:
        return {"exito": False, "error": str(e)}


def interpretar_pm25(pm25):
    """Nivel con textos calidos"""
    
    if pm25 <= 12:
        return {
            "color": "verde",
            "texto": "Aire limpio",
            "mensaje_calido": "Respira tranquilo, el aire esta limpio hoy",
            "icono": "check-circle-2"
        }
    elif pm25 <= 35:
        return {
            "color": "amarillo",
            "texto": "Aire aceptable",
            "mensaje_calido": "El aire esta bien, solo algunas personas sensibles deben tener cuidado",
            "icono": "circle-check"
        }
    elif pm25 <= 55:
        return {
            "color": "naranja",
            "texto": "Cuidado grupos sensibles",
            "mensaje_calido": "Los ninos, abuelitos y personas con asma deben tener precaucion",
            "icono": "alert-circle"
        }
    elif pm25 <= 150:
        return {
            "color": "rojo",
            "texto": "Aire danino",
            "mensaje_calido": "El aire no esta bien hoy, evita salir si puedes",
            "icono": "alert-triangle"
        }
    else:
        return {
            "color": "morado",
            "texto": "Emergencia",
            "mensaje_calido": "Por favor quedate en casa, el aire es muy peligroso",
            "icono": "alert-octagon"
        }


def obtener_recomendaciones(pm25):
    """Recomendaciones en lenguaje calido y simple"""
    
    if pm25 <= 12:
        return {
            "titulo": "El aire esta limpio",
            "poblacion_general": {
                "titulo": "Para todos",
                "texto": "Puedes salir y disfrutar del dia sin preocupacion. Es un buen momento para caminar, hacer ejercicio o llevar a los ninos al parque."
            },
            "grupos_sensibles": {
                "titulo": "Para ninos, abuelitos y personas con asma",
                "texto": "Todos pueden estar afuera con tranquilidad. No hay ningun riesgo especial hoy."
            },
            "grupos_incluidos": "ninos menores de 5 anos, personas mayores de 60 anos, y personas con asma, bronquitis o alergias."
        }
    elif pm25 <= 35:
        return {
            "titulo": "El aire esta bien",
            "poblacion_general": {
                "titulo": "Para todos",
                "texto": "Puedes hacer tus actividades normales al aire libre. No hay problema si sales a caminar o trabajar afuera."
            },
            "grupos_sensibles": {
                "titulo": "Para ninos, abuelitos y personas con asma",
                "texto": "Estate atento. Si te cansas rapido o te cuesta respirar, es mejor entrar a casa y descansar."
            },
            "grupos_incluidos": "ninos menores de 5 anos, personas mayores de 60 anos, y personas con asma, bronquitis o alergias."
        }
    elif pm25 <= 55:
        return {
            "titulo": "Hay que cuidarse",
            "poblacion_general": {
                "titulo": "Para todos",
                "texto": "Puedes salir, pero evita hacer ejercicio intenso al aire libre. Si notas irritacion en ojos o garganta, mejor entra a casa."
            },
            "grupos_sensibles": {
                "titulo": "Para ninos, abuelitos y personas con asma",
                "texto": "Mejor quedate dentro de casa lo mas posible. Si tienes que salir, usa cubrebocas y lleva tu medicamento si lo necesitas."
            },
            "grupos_incluidos": "ninos menores de 5 anos, personas mayores de 60 anos, y personas con asma, bronquitis o alergias."
        }
    elif pm25 <= 150:
        return {
            "titulo": "El aire es danino hoy",
            "poblacion_general": {
                "titulo": "Para todos",
                "texto": "Evita salir lo mas posible. Si tienes que hacerlo, usa cubrebocas. No hagas ejercicio afuera y mantente hidratado."
            },
            "grupos_sensibles": {
                "titulo": "Para ninos, abuelitos y personas con asma",
                "texto": "Por favor quedate en casa. Cierra las ventanas. Si te sientes mal (tos, falta de aire), busca atencion medica."
            },
            "grupos_incluidos": "ninos menores de 5 anos, personas mayores de 60 anos, y personas con asma, bronquitis o alergias."
        }
    else:
        return {
            "titulo": "Emergencia ambiental",
            "poblacion_general": {
                "titulo": "Para todos",
                "texto": "No salgas a menos que sea necesario. Sella puertas y ventanas. Usa cubrebocas N95 si tienes que salir."
            },
            "grupos_sensibles": {
                "titulo": "Para ninos, abuelitos y personas con asma",
                "texto": "ALERTA: Quedate en casa. Si presentas cualquier sintoma respiratorio, llama al doctor o acude a urgencias."
            },
            "grupos_incluidos": "ninos menores de 5 anos, personas mayores de 60 anos, y personas con asma, bronquitis o alergias."
        }