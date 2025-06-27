# -*- coding: utf-8 -*-
"""
Comando para marcar automáticamente los turnos como completados
cuando su hora programada haya pasado.

Este comando debe ejecutarse periódicamente mediante un cron job o task scheduler.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
from GestorSpa.apps.turnos.models import Turno
import logging


class Command(BaseCommand):
    help = 'Marca automáticamente los turnos confirmados como completados cuando su hora programada ha pasado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta una simulación sin realizar cambios reales en la base de datos',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada del proceso',
        )
        parser.add_argument(
            '--hours-offset',
            type=int,
            default=0,
            help='Número de horas adicionales a esperar después de la hora programada antes de marcar como completado (default: 0)',
        )

    def handle(self, *args, **options):
        # Configurar logging
        logger = logging.getLogger(__name__)
        
        # Configurar verbosidad
        verbosity = options.get('verbosity', 1)
        verbose = options.get('verbose', False)
        dry_run = options.get('dry_run', False)
        hours_offset = options.get('hours_offset', 0)

        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO SIMULACIÓN - No se realizarán cambios reales')
            )

        # Obtener fecha y hora actual
        now = timezone.now()
        current_date = now.date()
        current_time = now.time()
        
        # Calcular el offset de tiempo si se especifica
        if hours_offset > 0:
            offset_datetime = now - timedelta(hours=hours_offset)
            offset_date = offset_datetime.date()
            offset_time = offset_datetime.time()
            
            if verbose:
                self.stdout.write(f"Usando offset de {hours_offset} horas.")
                self.stdout.write(f"Fecha y hora con offset: {offset_date} {offset_time}")
        else:
            offset_date = current_date
            offset_time = current_time

        if verbose:
            self.stdout.write(f"Fecha y hora actual: {current_date} {current_time}")

        # Buscar turnos confirmados que deberían estar completados
        # Criterios:
        # 1. Estado = 'confirmado'
        # 2. Fecha < fecha actual OR (fecha = fecha actual AND hora_fin < hora actual)
        
        from django.db.models import Q
        
        # Crear una consulta combinada usando Q objects
        turnos_a_completar = Turno.objects.filter(
            Q(estado='confirmado') & (
                Q(fecha__lt=offset_date) |  # Turnos de días anteriores
                (Q(fecha=offset_date) & Q(hora_fin__lt=offset_time) & Q(hora_fin__isnull=False))  # Turnos de hoy cuya hora ya pasó
            )
        ).order_by('-fecha', '-hora_inicio')
        
        total_turnos = turnos_a_completar.count()
        
        if total_turnos == 0:
            self.stdout.write(
                self.style.SUCCESS('No hay turnos confirmados pendientes de marcar como completados.')
            )
            return

        self.stdout.write(f"Se encontraron {total_turnos} turnos para marcar como completados:")
        
        if verbose:
            self.stdout.write("\nDetalle de turnos a procesar:")
            self.stdout.write("-" * 80)
            
            for turno in turnos_a_completar:
                hora_fin_display = turno.hora_fin.strftime('%H:%M') if turno.hora_fin else 'No definida'
                self.stdout.write(
                    f"ID: {turno.id:4d} | {turno.fecha} {turno.hora_inicio}-{hora_fin_display} | "
                    f"{turno.nombre} | {turno.servicio.nombre} | {turno.profesional}"
                )
            self.stdout.write("-" * 80)

        if not dry_run:
            # Procesar cada turno
            turnos_procesados = 0
            turnos_con_error = 0
            
            for turno in turnos_a_completar:
                try:
                    # Usar el método del modelo para cambiar estado de forma segura
                    if turno.puede_cambiar_estado('completado'):
                        turno.cambiar_estado('completado')
                        turnos_procesados += 1
                        
                        if verbose:
                            self.stdout.write(
                                f"✓ Turno {turno.id} marcado como completado: {turno.nombre} - {turno.servicio.nombre}"
                            )
                    else:
                        turnos_con_error += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f"✗ No se pudo cambiar el estado del turno {turno.id}: transición no permitida"
                            )
                        )
                        
                except Exception as e:
                    turnos_con_error += 1
                    error_msg = f"Error al procesar turno {turno.id}: {str(e)}"
                    self.stdout.write(self.style.ERROR(f"✗ {error_msg}"))
                    logger.error(error_msg)

            # Mostrar resumen
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write("RESUMEN DE PROCESAMIENTO:")
            self.stdout.write(f"Total turnos encontrados: {total_turnos}")
            self.stdout.write(f"Turnos procesados exitosamente: {turnos_procesados}")
            
            if turnos_con_error > 0:
                self.stdout.write(
                    self.style.ERROR(f"Turnos con errores: {turnos_con_error}")
                )
            
            if turnos_procesados > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Proceso completado. {turnos_procesados} turnos marcados como completados."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING("⚠ No se procesaron turnos exitosamente.")
                )
                
            # Log del proceso
            logger.info(
                f"Auto-completado de turnos ejecutado: {turnos_procesados} turnos procesados, "
                f"{turnos_con_error} errores"
            )
                
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"SIMULACIÓN: Se habrían marcado {total_turnos} turnos como completados."
                )
            )

        self.stdout.write("=" * 50)
