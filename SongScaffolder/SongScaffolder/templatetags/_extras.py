from django import template

register = template.Library()

@register.filter(name="addstr")
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    arg1 = str(arg1).replace("/", "-over-").replace(" ", "-space-")
    arg2 = str(arg2).replace("/", "-over-").replace(" ", "-space-")
    return arg1 + arg2