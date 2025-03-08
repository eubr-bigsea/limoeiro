
import requests
import os

API_URL = os.environ['API_URL']

def _format_url(route, param=None):
# Method to format url and parameters to be used in requests.
    url = API_URL
    if API_URL[-1] != '/':
        url += '/'

    url = API_URL+route
    if (param is not None) and (param != ""):
        url +="/"+param
    
    return url

def post_request (route, json_body):
# Method to do a post request.

    url = _format_url(route)

    response = requests.post(url, json = json_body)
    assert response.status_code == 201
    return response.json()

def patch_request (route, route_param, json_body):
# Method to do a patch request.
    url = _format_url(route, route_param)

    response = requests.patch(url, json = json_body)

    assert response.status_code == 200
    return response.json()

def get_request (route, route_param, dict_param=None):
# Method to do a get request.
    url = _format_url(route, route_param)
    response = requests.get(url, params=dict_param)
    return response.status_code, response.json()
