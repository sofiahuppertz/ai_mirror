import re

def remove_link(html_string):
    pattern = r'<a[^>]*>(.*?)</a>'
    return re.sub(pattern, '', html_string)