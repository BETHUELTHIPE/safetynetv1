from django import template

register = template.Library()

@register.filter
def currency_format(value):
    """Format a number as currency"""
    if value is None:
        return "N/A"
    return f"R{value:,.2f}"
