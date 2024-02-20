import re

def remove_link(html_string):
    pattern = r'<a[^>]*>(.*?)</a>'
    return re.sub(pattern, '', html_string)


def create_data_dict(response, next_route, buttons, reset_page):
    dict = {
        "server_response" : response,
        "route": next_route,
        "buttons": buttons,
        "reset_page": reset_page
    }
    return dict