from django import template
from django.db.models import Avg

register = template.Library()

@register.filter
def avg_rating(reviews):
    """Calculate average rating from a queryset of reviews"""
    if not reviews:
        return None
    return reviews.aggregate(Avg('rating'))['rating__avg']
