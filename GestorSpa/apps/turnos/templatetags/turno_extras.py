from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sum_total(turnos):
    """Suma el total de todos los turnos"""
    try:
        total = sum(turno.total or 0 for turno in turnos)
        return Decimal(str(total))
    except (TypeError, AttributeError):
        return Decimal('0')

@register.filter
def avg_total(turnos):
    """Calcula el promedio del total de todos los turnos"""
    try:
        turnos_list = list(turnos)
        if not turnos_list:
            return Decimal('0')
        total = sum(turno.total or 0 for turno in turnos_list)
        return Decimal(str(total)) / len(turnos_list)
    except (TypeError, AttributeError, ZeroDivisionError):
        return Decimal('0')

@register.filter
def mul(value, arg):
    """Multiplica dos valores"""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0

@register.filter
def div(value, arg):
    """Divide dos valores"""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (TypeError, ValueError):
        return 0
