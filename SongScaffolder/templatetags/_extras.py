from django import template

register = template.Library()

@register.filter(name="addstr")
def addstr(arg1, arg2):
    """Returns a concatenation of arg 1 and arg2, after replacing problematic characters in both."""
    arg1 = str(arg1).replace("/", "-over-").replace(" ", "-space-")
    arg2 = str(arg2).replace("/", "-over-").replace(" ", "-space-")
    return arg1 + arg2

@register.filter(name="replace_dashes")
def replace_dashes(arg1, arg2):
    """Returns a string with any dashes replaced by spaces."""
    return str(arg2).replace("-", " ")
