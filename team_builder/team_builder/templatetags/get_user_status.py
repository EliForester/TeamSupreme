from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def get_user_status(context):
    pass
