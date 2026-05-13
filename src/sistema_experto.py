"""
AireLab - Sistema Experto de Soluciones
Genera recomendaciones individuales y comunitarias segun el nivel del aire.
Implementa reglas de produccion del tipo SI-ENTONCES.
"""


def obtener_soluciones_por_nivel(pm25):
    """
    Sistema Experto: aplica reglas de produccion para determinar
    las soluciones segun el nivel actual de PM2.5.
    
    Reglas:
    - SI PM2.5 <= 12   ENTONCES nivel = limpio
    - SI PM2.5 <= 35   ENTONCES nivel = aceptable
    - SI PM2.5 <= 55   ENTONCES nivel = danino_sensibles
    - SI PM2.5 <= 150  ENTONCES nivel = peligroso
    - SI PM2.5 > 150   ENTONCES nivel = emergencia
    """
    
    if pm25 <= 12:
        return SOLUCIONES_NIVELES['limpio']
    elif pm25 <= 35:
        return SOLUCIONES_NIVELES['aceptable']
    elif pm25 <= 55:
        return SOLUCIONES_NIVELES['danino_sensibles']
    elif pm25 <= 150:
        return SOLUCIONES_NIVELES['peligroso']
    else:
        return SOLUCIONES_NIVELES['emergencia']


def obtener_todos_los_niveles():
    """Devuelve el plan de accion completo para TODOS los niveles"""
    return [
        SOLUCIONES_NIVELES['limpio'],
        SOLUCIONES_NIVELES['aceptable'],
        SOLUCIONES_NIVELES['danino_sensibles'],
        SOLUCIONES_NIVELES['peligroso'],
        SOLUCIONES_NIVELES['emergencia']
    ]


# ============================================
# BASE DE CONOCIMIENTO DEL SISTEMA EXPERTO
# ============================================

SOLUCIONES_NIVELES = {
    
    'limpio': {
        'id': 'limpio',
        'rango': '0 - 12 µg/m³',
        'nombre': 'Aire limpio',
        'color': 'verde',
        'icono': 'check-circle-2',
        'descripcion': 'El aire esta en optimas condiciones. Es momento de aprovechar y fortalecer habitos saludables.',
        'urgencia': 1,
        'soluciones_individuales': [
            {
                'icono': 'wind',
                'titulo': 'Ventila tu casa',
                'detalle': 'Abre las ventanas para renovar el aire interior y eliminar humedad acumulada.'
            },
            {
                'icono': 'baby',
                'titulo': 'Lleva a los ninos al parque',
                'detalle': 'Es un buen momento para que jueguen y respiren aire de calidad.'
            },
            {
                'icono': 'bike',
                'titulo': 'Haz ejercicio al aire libre',
                'detalle': 'Aprovecha para caminar, correr o andar en bicicleta sin riesgo.'
            },
            {
                'icono': 'sprout',
                'titulo': 'Planta arboles',
                'detalle': 'Cada arbol absorbe CO2 y libera oxigeno. Contribuye a mantener este nivel.'
            }
        ],
        'soluciones_comunitarias': [
            {
                'icono': 'megaphone',
                'titulo': 'Campanas educativas',
                'detalle': 'Aprovechar para difundir educacion ambiental sin la presion de una crisis.'
            },
            {
                'icono': 'trees',
                'titulo': 'Programas de reforestacion',
                'detalle': 'Plantar arboles en avenidas, escuelas y zonas publicas para mantener calidad.'
            },
            {
                'icono': 'bike',
                'titulo': 'Promover uso de bicicleta',
                'detalle': 'Habilitar ciclovias y programas de bicicletas compartidas en la ciudad.'
            },
            {
                'icono': 'school',
                'titulo': 'Educacion en escuelas',
                'detalle': 'Incluir educacion ambiental en el curriculo escolar.'
            }
        ]
    },
    
    'aceptable': {
        'id': 'aceptable',
        'rango': '12 - 35 µg/m³',
        'nombre': 'Aire aceptable',
        'color': 'amarillo',
        'icono': 'circle-check',
        'descripcion': 'El aire esta en niveles aceptables, pero las personas sensibles deben tomar precauciones.',
        'urgencia': 2,
        'soluciones_individuales': [
            {
                'icono': 'activity',
                'titulo': 'Actividades normales',
                'detalle': 'Puedes seguir con tu rutina diaria, pero estate atento si te cuesta respirar.'
            },
            {
                'icono': 'pill',
                'titulo': 'Lleva tu inhalador',
                'detalle': 'Si eres asmatico, asegurate de tener tu medicamento de rescate contigo.'
            },
            {
                'icono': 'droplet',
                'titulo': 'Hidratate bien',
                'detalle': 'Tomar agua frecuentemente ayuda a tu sistema respiratorio a filtrar particulas.'
            },
            {
                'icono': 'eye',
                'titulo': 'Vigila a los vulnerables',
                'detalle': 'Pregunta a ninos y adultos mayores si se sienten bien durante el dia.'
            }
        ],
        'soluciones_comunitarias': [
            {
                'icono': 'school',
                'titulo': 'Activar monitoreo escolar',
                'detalle': 'Las escuelas deben observar a estudiantes con problemas respiratorios.'
            },
            {
                'icono': 'stethoscope',
                'titulo': 'Alertar a clinicas',
                'detalle': 'Notificar a centros de salud para anticipar consultas respiratorias.'
            },
            {
                'icono': 'wheat',
                'titulo': 'Recomendar pausas agricolas',
                'detalle': 'Sugerir pausas en actividad agricola intensa durante horas pico.'
            },
            {
                'icono': 'mail',
                'titulo': 'Difundir alertas tempranas',
                'detalle': 'Enviar mensajes a la poblacion suscrita para que tome precauciones.'
            }
        ]
    },
    
    'danino_sensibles': {
        'id': 'danino_sensibles',
        'rango': '35 - 55 µg/m³',
        'nombre': 'Danino para grupos sensibles',
        'color': 'naranja',
        'icono': 'alert-circle',
        'descripcion': 'Los ninos, adultos mayores y personas con asma deben tomar precauciones serias.',
        'urgencia': 3,
        'soluciones_individuales': [
            {
                'icono': 'home',
                'titulo': 'Quedate en casa si eres sensible',
                'detalle': 'Ninos menores de 5, adultos mayores y personas con asma: permanece dentro.'
            },
            {
                'icono': 'door-closed',
                'titulo': 'Cierra ventanas y puertas',
                'detalle': 'Evita que el aire contaminado entre a tu hogar.'
            },
            {
                'icono': 'shield',
                'titulo': 'Usa cubrebocas',
                'detalle': 'Si tienes que salir, usa cubrebocas tipo KN95 o N95 para mayor proteccion.'
            },
            {
                'icono': 'ban',
                'titulo': 'Evita ejercicio al aire libre',
                'detalle': 'No corras ni hagas deporte afuera. Cambia a ejercicio bajo techo.'
            },
            {
                'icono': 'leaf',
                'titulo': 'Plantas purificadoras',
                'detalle': 'Mantén plantas como sansevieria, pothos o palma de bambu que limpian el aire.'
            }
        ],
        'soluciones_comunitarias': [
            {
                'icono': 'school',
                'titulo': 'Suspender deportes escolares',
                'detalle': 'Cancelar educacion fisica y recreos al aire libre en escuelas.'
            },
            {
                'icono': 'building-2',
                'titulo': 'Activar protocolos en asilos',
                'detalle': 'Asilos y hospitales deben cerrar ventanas y vigilar a residentes.'
            },
            {
                'icono': 'briefcase',
                'titulo': 'Alertar a empresas',
                'detalle': 'Empresas con trabajadores al aire libre deben proveer mascarillas N95.'
            },
            {
                'icono': 'map-pin',
                'titulo': 'Habilitar zonas de aire limpio',
                'detalle': 'Centros comunitarios con purificadores para refugio temporal de vulnerables.'
            }
        ]
    },
    
    'peligroso': {
        'id': 'peligroso',
        'rango': '55 - 150 µg/m³',
        'nombre': 'Aire danino para todos',
        'color': 'rojo',
        'icono': 'alert-triangle',
        'descripcion': 'TODA la poblacion puede experimentar efectos en la salud. Se requieren medidas urgentes.',
        'urgencia': 4,
        'soluciones_individuales': [
            {
                'icono': 'home',
                'titulo': 'TODOS deben quedarse en casa',
                'detalle': 'No salgas a menos que sea estrictamente necesario.'
            },
            {
                'icono': 'door-closed',
                'titulo': 'Sella ventanas y puertas',
                'detalle': 'Cierra todo y considera usar cinta para sellar fugas.'
            },
            {
                'icono': 'shield-check',
                'titulo': 'Cubrebocas N95 obligatorio',
                'detalle': 'Si tienes que salir, usa N95 ajustado correctamente.'
            },
            {
                'icono': 'fan',
                'titulo': 'Crea una habitacion limpia',
                'detalle': 'Designa un cuarto con purificador o ventilador con filtro HEPA.'
            },
            {
                'icono': 'pill',
                'titulo': 'Ten medicamentos a la mano',
                'detalle': 'Inhaladores, antihistaminicos y broncodilatadores accesibles.'
            },
            {
                'icono': 'droplet',
                'titulo': 'Hidrata constantemente',
                'detalle': 'Beber agua ayuda a las membranas mucosas a eliminar contaminantes.'
            }
        ],
        'soluciones_comunitarias': [
            {
                'icono': 'graduation-cap',
                'titulo': 'SUSPENDER clases',
                'detalle': 'Todas las escuelas y universidades deben cerrar de inmediato.'
            },
            {
                'icono': 'hospital',
                'titulo': 'Activar centros respiratorios',
                'detalle': 'Habilitar areas especiales en hospitales para urgencias respiratorias.'
            },
            {
                'icono': 'flame',
                'titulo': 'Detener quemas agricolas',
                'detalle': 'Gobierno debe prohibir cualquier quema en el valle del Mayo.'
            },
            {
                'icono': 'car',
                'titulo': 'Restringir trafico vehicular',
                'detalle': 'Activar programa hoy-no-circula para reducir emisiones inmediatas.'
            },
            {
                'icono': 'package',
                'titulo': 'Distribuir cubrebocas N95',
                'detalle': 'Reparto gratuito en colonias vulnerables y a personas en situacion de calle.'
            },
            {
                'icono': 'building',
                'titulo': 'Habilitar refugios de aire limpio',
                'detalle': 'Edificios publicos con aire acondicionado y filtros como zonas seguras.'
            }
        ]
    },
    
    'emergencia': {
        'id': 'emergencia',
        'rango': '+150 µg/m³',
        'nombre': 'EMERGENCIA AMBIENTAL',
        'color': 'morado',
        'icono': 'alert-octagon',
        'descripcion': 'Nivel critico. Riesgo grave para la salud de toda la poblacion. Accion inmediata requerida.',
        'urgencia': 5,
        'soluciones_individuales': [
            {
                'icono': 'octagon-alert',
                'titulo': 'NO SALIR bajo ninguna circunstancia',
                'detalle': 'A menos que sea para buscar atencion medica urgente.'
            },
            {
                'icono': 'shield-alert',
                'titulo': 'Sellar puertas con cinta',
                'detalle': 'Usar cinta adhesiva en marcos de puertas y ventanas para evitar filtraciones.'
            },
            {
                'icono': 'phone',
                'titulo': 'Llamar a urgencias si hay sintomas',
                'detalle': 'Cualquier dificultad respiratoria requiere atencion medica inmediata.'
            },
            {
                'icono': 'briefcase-medical',
                'titulo': 'Kit de emergencia listo',
                'detalle': 'Agua, medicamentos, mascarillas N95, documentos importantes.'
            },
            {
                'icono': 'users',
                'titulo': 'Verifica a tus vecinos',
                'detalle': 'Llama por telefono a adultos mayores y personas vulnerables que vivan solas.'
            }
        ],
        'soluciones_comunitarias': [
            {
                'icono': 'siren',
                'titulo': 'Declarar emergencia ambiental',
                'detalle': 'El ayuntamiento debe activar protocolo oficial de emergencia.'
            },
            {
                'icono': 'truck',
                'titulo': 'Evacuar grupos vulnerables',
                'detalle': 'Transportar a ninos, ancianos y enfermos a zonas con aire limpio.'
            },
            {
                'icono': 'hospital',
                'titulo': 'Activar hospitales respiratorios',
                'detalle': 'Habilitar salas adicionales y personal medico de emergencia.'
            },
            {
                'icono': 'factory',
                'titulo': 'Prohibir actividad industrial',
                'detalle': 'Detener fabricas, agricultura intensiva y cualquier fuente de emision.'
            },
            {
                'icono': 'building-2',
                'titulo': 'Solicitar apoyo estatal y federal',
                'detalle': 'Activar Proteccion Civil, SEDENA y apoyo de gobierno estatal.'
            },
            {
                'icono': 'radio',
                'titulo': 'Alertas masivas continuas',
                'detalle': 'Medios de comunicacion, redes sociales y altavoces en colonias.'
            }
        ]
    }
}