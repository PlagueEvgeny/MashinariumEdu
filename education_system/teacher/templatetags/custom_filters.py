from django import template

register = template.Library()

@register.filter
def percentage(score, passing_score):
    if passing_score > 0:
        return (score / passing_score) * 100
    return None  # Или любое значение, которое вы хотите вернуть


@register.filter
def zip_lists(list1, list2):
    return zip(list1, list2)