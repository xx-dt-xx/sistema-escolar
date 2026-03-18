# courses/management/commands/seed_courses.py
#
# Estructura de carpetas necesaria:
#   courses/
#   └── management/
#       ├── __init__.py
#       └── commands/
#           ├── __init__.py
#           └── seed_courses.py
#
# Ejecutar con:
#   python manage.py seed_courses

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from courses.models import Category, Course, CourseGroup, Schedule
from datetime import date


class Command(BaseCommand):
    help = 'Carga los cursos iniciales de CECATI 97 en la base de datos.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando categorías...')
        categories = self._create_categories()

        self.stdout.write('Creando cursos...')
        courses = self._create_courses(categories)

        self.stdout.write('Creando grupos y horarios...')
        self._create_groups(courses)

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ {len(courses)} cursos creados exitosamente.'
        ))

    # ─── CATEGORÍAS ───────────────────────────────────────────────────────────

    def _create_categories(self):
        data = [
            ('Automotriz',          'Cursos relacionados con mecánica y afinación de vehículos.'),
            ('Electricidad',        'Instalaciones eléctricas residenciales e industriales.'),
            ('Manufactura',         'Carpintería, tornería y operación de maquinaria industrial.'),
            ('Confección Textil',   'Corte, confección y operación de máquinas de costura.'),
            ('Tecnología',          'Diseño gráfico, mecanografía y herramientas digitales.'),
            ('Idiomas',             'Cursos de lenguas extranjeras.'),
            ('Belleza y Estética',  'Cosmetología, estética y cuidado personal.'),
        ]
        cats = {}
        for name, desc in data:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            cats[name] = cat
            status = 'creada' if created else 'ya existe'
            self.stdout.write(f'  Categoría "{name}" — {status}')
        return cats

    # ─── CURSOS ────────────────────────────────────────────────────────────────

    def _create_courses(self, cats):
        data = [
            {
                'name': 'Electricidad',
                'category': cats['Electricidad'],
                'short_description': 'Aprende instalaciones eléctricas residenciales e industriales desde cero.',
                'description': (
                    'Este curso te proporciona los conocimientos teóricos y prácticos para realizar '
                    'instalaciones eléctricas residenciales e industriales de manera segura y eficiente. '
                    'Aprenderás a interpretar planos eléctricos, instalar tableros de distribución y '
                    'diagnosticar fallas en circuitos.'
                ),
                'objectives': (
                    '• Identificar y manejar herramientas e instrumentos de medición eléctrica.\n'
                    '• Realizar instalaciones eléctricas residenciales conforme a la NOM.\n'
                    '• Instalar y conectar tableros de distribución.\n'
                    '• Diagnosticar y corregir fallas en circuitos eléctricos.'
                ),
                'requirements': 'Secundaria terminada. No se requieren conocimientos previos.',
                'target_audience': 'Personas interesadas en el área eléctrica, técnicos o personas que deseen emprender.',
                'duration_weeks': 16,
                'hours_per_week': 6,
                'monthly_price': 350,
            },
            {
                'name': 'Afinación de motores a gasolina',
                'category': cats['Automotriz'],
                'short_description': 'Diagnóstico y afinación de motores de gasolina con equipo moderno.',
                'description': (
                    'Desarrolla habilidades para diagnosticar, mantener y afinar motores de gasolina '
                    'utilizando escáner automotriz y equipo de diagnóstico electrónico. Aprenderás '
                    'el funcionamiento de los sistemas de inyección electrónica y encendido.'
                ),
                'objectives': (
                    '• Identificar los componentes del motor de combustión interna.\n'
                    '• Usar escáner automotriz para leer códigos de falla.\n'
                    '• Realizar afinaciones preventivas y correctivas.\n'
                    '• Ajustar sistemas de inyección y encendido electrónico.'
                ),
                'requirements': 'Conocimientos básicos de mecánica o haber cursado el nivel básico automotriz.',
                'target_audience': 'Mecánicos en formación, técnicos automotrices y aficionados al mundo automotriz.',
                'duration_weeks': 20,
                'hours_per_week': 8,
                'monthly_price': 450,
            },
            {
                'name': 'Mecánica de emergencia automotriz',
                'category': cats['Automotriz'],
                'short_description': 'Resuelve averías comunes de automóviles en campo de forma segura y rápida.',
                'description': (
                    'Curso orientado a brindar al participante las habilidades necesarias para atender '
                    'emergencias mecánicas en campo: cambio de llantas, arranque de batería, cambio de '
                    'aceite, revisión de frenos y diagnóstico básico de fallas frecuentes.'
                ),
                'objectives': (
                    '• Identificar y resolver las 10 fallas mecánicas más comunes en carretera.\n'
                    '• Realizar cambio de llantas, aceite y filtros.\n'
                    '• Diagnosticar problemas básicos de batería y sistema eléctrico.\n'
                    '• Aplicar medidas de seguridad vial durante una emergencia.'
                ),
                'requirements': 'No se requieren conocimientos previos. Mayor de 15 años.',
                'target_audience': 'Conductores en general, choferes, personas que deseen mayor autonomía vehicular.',
                'duration_weeks': 8,
                'hours_per_week': 6,
                'monthly_price': 300,
            },
            {
                'name': 'Mecánica de emergencia de motocicletas',
                'category': cats['Automotriz'],
                'short_description': 'Atiende emergencias mecánicas en motocicletas con confianza y seguridad.',
                'description': (
                    'Aprende a diagnosticar y resolver las averías más frecuentes en motocicletas: '
                    'sistema de frenos, cadena y transmisión, batería, sistema de encendido y carburador. '
                    'Curso eminentemente práctico con motocicletas de taller.'
                ),
                'objectives': (
                    '• Identificar los sistemas principales de una motocicleta.\n'
                    '• Realizar mantenimiento preventivo básico.\n'
                    '• Diagnosticar y resolver fallas comunes en campo.\n'
                    '• Aplicar normas de seguridad durante el trabajo.'
                ),
                'requirements': 'No se requieren conocimientos previos. Deseable tener motocicleta propia.',
                'target_audience': 'Motociclistas, repartidores, personas que deseen independencia mecánica.',
                'duration_weeks': 8,
                'hours_per_week': 6,
                'monthly_price': 300,
            },
            {
                'name': 'Operación de máquinas industriales de costura',
                'category': cats['Confección Textil'],
                'short_description': 'Maneja máquinas de costura industriales con velocidad y precisión.',
                'description': (
                    'Curso técnico para operar máquinas de costura industriales de tipo plano, '
                    'fileteadora y máquina de collareta. Aprenderás desde el enhebrado y calibración '
                    'hasta la confección de piezas completas a ritmo industrial.'
                ),
                'objectives': (
                    '• Operar máquina plana, fileteadora y collareta.\n'
                    '• Realizar enhebrado, tensión y calibración de máquinas.\n'
                    '• Confeccionar piezas básicas con acabados de calidad.\n'
                    '• Aplicar normas de seguridad e higiene en el taller.'
                ),
                'requirements': 'No se requieren conocimientos previos.',
                'target_audience': 'Personas interesadas en la industria textil o en emprender un negocio de confección.',
                'duration_weeks': 16,
                'hours_per_week': 6,
                'monthly_price': 350,
            },
            {
                'name': 'Carpintería',
                'category': cats['Manufactura'],
                'short_description': 'Trabaja la madera desde lo básico hasta muebles terminados.',
                'description': (
                    'Aprende a utilizar herramientas manuales y eléctricas para trabajar la madera: '
                    'corte, ensamblado, lijado y acabados. Al finalizar serás capaz de fabricar muebles '
                    'básicos y piezas decorativas con calidad profesional.'
                ),
                'objectives': (
                    '• Identificar y usar correctamente herramientas de carpintería.\n'
                    '• Realizar cortes, ensambles y uniones en madera.\n'
                    '• Aplicar técnicas de lijado, barnizado y pintura.\n'
                    '• Fabricar un mueble funcional como proyecto final.'
                ),
                'requirements': 'No se requieren conocimientos previos. Se recomienda ropa de trabajo.',
                'target_audience': 'Personas que deseen aprender un oficio o emprender en el sector mueblero.',
                'duration_weeks': 20,
                'hours_per_week': 6,
                'monthly_price': 380,
            },
            {
                'name': 'Elaboración de mesa torneada',
                'category': cats['Manufactura'],
                'short_description': 'Fabrica mesas con patas torneadas usando técnicas tradicionales y modernas.',
                'description': (
                    'Curso especializado en el torneado de madera para la fabricación de mesas. '
                    'Aprenderás a operar el torno de madera, seleccionar materiales, realizar '
                    'diseños de patas y ensamblar el producto final con acabados de calidad.'
                ),
                'objectives': (
                    '• Operar el torno de madera con seguridad.\n'
                    '• Diseñar y tornear patas y elementos decorativos.\n'
                    '• Ensamblar y dar acabado a una mesa completa.\n'
                    '• Calcular materiales y costos de producción.'
                ),
                'requirements': 'Se recomienda haber cursado Carpintería o tener experiencia básica con madera.',
                'target_audience': 'Carpinteros en formación, artesanos y emprendedores del sector madera.',
                'duration_weeks': 16,
                'hours_per_week': 6,
                'monthly_price': 380,
            },
            {
                'name': 'Torneado de piezas por CNC',
                'category': cats['Manufactura'],
                'short_description': 'Programa y opera tornos CNC para la fabricación de piezas de precisión.',
                'description': (
                    'Aprende a programar y operar tornos de control numérico computarizado (CNC) '
                    'para la fabricación de piezas metálicas y plásticas. Incluye fundamentos de '
                    'programación G-Code, setup de máquina y control de calidad dimensional.'
                ),
                'objectives': (
                    '• Interpretar planos de taller y especificaciones dimensionales.\n'
                    '• Programar ciclos básicos en G-Code para torno CNC.\n'
                    '• Realizar setup, montaje de herramientas y corrección de offsets.\n'
                    '• Verificar dimensiones con instrumentos de medición de precisión.'
                ),
                'requirements': 'Secundaria terminada. Deseable conocimiento básico de matemáticas.',
                'target_audience': 'Técnicos en manufactura, operadores de maquinaria y personas que buscan empleo industrial.',
                'duration_weeks': 24,
                'hours_per_week': 8,
                'monthly_price': 500,
            },
            {
                'name': 'Inglés',
                'category': cats['Idiomas'],
                'short_description': 'Desarrolla habilidades de comunicación en inglés en cuatro niveles.',
                'description': (
                    'Programa de inglés comunicativo con enfoque en situaciones cotidianas y laborales. '
                    'Se desarrollan las cuatro habilidades: escucha, habla, lectura y escritura. '
                    'El programa cuenta con cuatro niveles: básico, pre-intermedio, intermedio y avanzado.'
                ),
                'objectives': (
                    '• Comunicarse en inglés en situaciones cotidianas y laborales.\n'
                    '• Comprender textos y conversaciones en inglés estándar.\n'
                    '• Redactar textos básicos como correos y formularios.\n'
                    '• Ampliar vocabulario técnico y profesional.'
                ),
                'requirements': 'No se requieren conocimientos previos para el nivel básico.',
                'target_audience': 'Personas de cualquier edad que deseen aprender o mejorar su inglés.',
                'duration_weeks': 20,
                'hours_per_week': 5,
                'monthly_price': 400,
            },
            {
                'name': 'Diseño gráfico',
                'category': cats['Tecnología'],
                'short_description': 'Crea diseños profesionales con herramientas digitales de la industria.',
                'description': (
                    'Aprende a diseñar piezas gráficas para medios impresos y digitales usando '
                    'software profesional como Adobe Illustrator y Photoshop. Desarrollarás criterio '
                    'estético, manejo del color, tipografía y composición visual.'
                ),
                'objectives': (
                    '• Dominar las herramientas básicas de Illustrator y Photoshop.\n'
                    '• Aplicar principios de diseño: color, tipografía y composición.\n'
                    '• Diseñar logotipos, carteles, tarjetas y piezas para redes sociales.\n'
                    '• Preparar archivos para impresión y medios digitales.'
                ),
                'requirements': 'Conocimientos básicos de computación. Se trabaja en laboratorio de cómputo.',
                'target_audience': 'Personas creativas, emprendedores y profesionales que deseen agregar habilidades de diseño.',
                'duration_weeks': 20,
                'hours_per_week': 6,
                'monthly_price': 420,
            },
            {
                'name': 'Mecanografía',
                'category': cats['Tecnología'],
                'short_description': 'Escribe al teclado con velocidad y precisión usando el método de diez dedos.',
                'description': (
                    'Curso de mecanografía con método de diez dedos al tacto. Desarrollarás velocidad '
                    'y precisión en el teclado mediante ejercicios progresivos. Al finalizar alcanzarás '
                    'una velocidad mínima de 40 palabras por minuto con alta precisión.'
                ),
                'objectives': (
                    '• Adoptar la postura y posición correcta frente al teclado.\n'
                    '• Dominar el método de mecanografía al tacto con diez dedos.\n'
                    '• Alcanzar una velocidad mínima de 40 ppm con 95% de precisión.\n'
                    '• Aplicar formatos básicos de documentos en procesador de textos.'
                ),
                'requirements': 'No se requieren conocimientos previos. Se trabaja en laboratorio de cómputo.',
                'target_audience': 'Estudiantes, profesionistas, administrativos y cualquier persona que use computadora.',
                'duration_weeks': 8,
                'hours_per_week': 5,
                'monthly_price': 280,
            },
            {
                'name': 'Cosmetología',
                'category': cats['Belleza y Estética'],
                'short_description': 'Domina técnicas de corte, coloración, peinado y tratamientos capilares.',
                'description': (
                    'Programa completo de cosmetología que abarca corte de cabello, coloración, '
                    'permanente, alisado, tratamientos capilares y maquillaje básico. Incluye '
                    'prácticas en modelos reales y manejo de productos profesionales.'
                ),
                'objectives': (
                    '• Realizar cortes de cabello para dama y caballero.\n'
                    '• Aplicar técnicas de coloración, mechas y decoloración.\n'
                    '• Ejecutar tratamientos de hidratación y restauración capilar.\n'
                    '• Aplicar maquillaje social básico.'
                ),
                'requirements': 'No se requieren conocimientos previos. Se requiere bata y kit básico de herramientas.',
                'target_audience': 'Personas que deseen dedicarse a la estética profesional o emprender un salón.',
                'duration_weeks': 24,
                'hours_per_week': 8,
                'monthly_price': 480,
            },
            {
                'name': 'Corte y confección',
                'category': cats['Confección Textil'],
                'short_description': 'Diseña y confecciona prendas de vestir desde el trazo hasta el acabado final.',
                'description': (
                    'Aprende a trazar patrones, cortar telas y confeccionar prendas de vestir para '
                    'dama, caballero y niño. El curso integra técnicas de costura a mano y en máquina, '
                    'así como conocimientos básicos de diseño y moda.'
                ),
                'objectives': (
                    '• Tomar medidas y trazar patrones básicos.\n'
                    '• Cortar telas con precisión siguiendo patrones.\n'
                    '• Confeccionar prendas básicas en máquina de costura.\n'
                    '• Aplicar técnicas de acabado y presentación de prendas.'
                ),
                'requirements': 'No se requieren conocimientos previos.',
                'target_audience': 'Personas que deseen aprender a confeccionar ropa para uso personal o negocio propio.',
                'duration_weeks': 20,
                'hours_per_week': 6,
                'monthly_price': 370,
            },
        ]

        created_courses = {}
        for item in data:
            slug = slugify(item['name'])
            course, created = Course.objects.get_or_create(
                slug=slug,
                defaults={
                    'name':             item['name'],
                    'category':         item['category'],
                    'short_description':item['short_description'],
                    'description':      item['description'],
                    'objectives':       item['objectives'],
                    'requirements':     item['requirements'],
                    'target_audience':  item['target_audience'],
                    'duration_weeks':   item['duration_weeks'],
                    'hours_per_week':   item['hours_per_week'],
                    'monthly_price':    item['monthly_price'],
                    'language':         'Español',
                    'is_active':        True,
                }
            )
            created_courses[item['name']] = course
            status = 'creado' if created else 'ya existe'
            self.stdout.write(f'  Curso "{item["name"]}" — {status}')

        return created_courses

    # ─── GRUPOS Y HORARIOS ────────────────────────────────────────────────────

    def _create_groups(self, courses):
        """
        Genera grupos de ejemplo para cada curso.
        Cada curso tendrá 2 grupos: matutino y vespertino (o sabatino para cursos largos).
        """

        # Fechas de inicio del próximo ciclo
        start_a  = date(2026, 4, 7)   # Grupo A — Matutino
        start_b  = date(2026, 4, 7)   # Grupo B — Vespertino
        start_c  = date(2026, 4, 11)  # Grupo C — Sabatino
        deadline = date(2026, 4, 4)   # Fecha límite inscripción

        group_templates = [
            # (sufijo, turno, capacidad, días, hora_inicio, hora_fin)
            ('A', CourseGroup.MORNING, 20, ['monday', 'wednesday', 'friday'], '08:00', '10:00', start_a),
            ('B', CourseGroup.AFTERNOON, 20, ['tuesday', 'thursday'], '16:00', '19:00', start_b),
            ('C', CourseGroup.SATURDAY, 25, ['saturday'], '09:00', '14:00', start_c),
        ]

        for course_name, course in courses.items():
            weeks = course.duration_weeks
            for suffix, shift, capacity, days, h_start, h_end, start in group_templates:
                # Solo agregar grupo sabatino a cursos de 16+ semanas
                if shift == CourseGroup.SATURDAY and weeks < 16:
                    continue

                end = date(start.year, start.month + (weeks // 4), start.day)
                # Ajuste simple si el mes supera 12
                if end.month > 12:
                    end = date(end.year + 1, end.month - 12, end.day)

                group_name = f'Grupo {suffix} — {course.name}'
                group, created = CourseGroup.objects.get_or_create(
                    course=course,
                    name=group_name,
                    defaults={
                        'shift':               shift,
                        'status':              CourseGroup.OPEN,
                        'max_capacity':        capacity,
                        'start_date':          start,
                        'end_date':            end,
                        'enrollment_deadline': deadline,
                    }
                )

                if created:
                    # Crear horarios
                    for day in days:
                        Schedule.objects.get_or_create(
                            group=group,
                            day=day,
                            defaults={
                                'start_time': h_start,
                                'end_time':   h_end,
                                'classroom':  f'Taller {suffix}',
                            }
                        )
                    status = 'creado'
                else:
                    status = 'ya existe'

                self.stdout.write(f'    Grupo "{group_name}" — {status}')
