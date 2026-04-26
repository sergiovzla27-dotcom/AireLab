"""
AireLab - Inicializar encabezados en Google Sheets
Ejecuta este script para configurar las hojas con los encabezados correctos.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sheets import _get_sheet

ENCABEZADOS = {
    'suscriptores': [
        'id_suscriptor', 'fecha_suscripcion', 'timestamp', 'estado',
        'nombre', 'edad', 'vulnerable', 'canal_whatsapp', 'whatsapp',
        'email', 'frecuencia', 'acepta', 'canal_email'
    ],
    'encuesta': [
        'id_encuesta', 'fecha_respuesta', 'timestamp',
        'edad', 'ocupacion', 'vulnerables', 'actividades_aire',
        'calidad_aire', 'sintomas', 'meses_enfermo',
        'visitas_medico', 'enfermedades', 'sabia_calidad',
        'consulta_info', 'usaria_app', 'funciones',
        'impedimentos', 'recomendaria', 'comentario'
    ],
    'historial_alertas': [
        'fecha', 'id_suscriptor', 'tipo', 'frecuencia',
        'nivel', 'pm25', 'email_ok', 'whatsapp_ok'
    ]
}

def inicializar():
    for nombre_hoja, encabezados in ENCABEZADOS.items():
        print(f"Configurando hoja: {nombre_hoja}...")
        hoja = _get_sheet(nombre_hoja)
        hoja.clear()
        hoja.append_row(encabezados)
        print(f"  ✓ Encabezados escritos: {len(encabezados)} columnas")
    print("\n¡Listo! Todas las hojas inicializadas correctamente.")

if __name__ == '__main__':
    inicializar()