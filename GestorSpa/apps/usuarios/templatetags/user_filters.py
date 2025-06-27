from django import template

register = template.Library()

@register.filter
def first_name(value):
    """
    Extrae el primer nombre de un nombre completo
    """
    if not value:
        return ""
    names = value.strip().split()
    return names[0] if names else ""

@register.filter 
def format_doctor_name(value):
    """
    Formatea el nombre del doctor para mostrar solo el primer nombre con Dr.
    """
    if not value:
        return "Doctor"
    names = value.strip().split()
    first = names[0] if names else "Doctor"
    return f"Dr. {first}"
