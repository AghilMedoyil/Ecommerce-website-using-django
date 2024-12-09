from django import template
from django.utils.datastructures import MultiValueDict

register = template.Library()

@register.filter
def chunks(lst, chunk_size):
    """
    Break a list into fixed-size chunks
    
    Usage in template: 
    {% for chunk in mylist|chunks:3 %}
        Process each chunk
    {% endfor %}
    """
    if not lst:
        return []
    
    chunk_size = int(chunk_size)
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]