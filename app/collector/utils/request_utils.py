import datetime
import json
import uuid
import requests
import os
import typing
from decimal import Decimal
import math

# Serialize UUID properties in json_body
def custom_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)

    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()

    elif isinstance(obj, datetime.date):
        return obj.isoformat()

    elif isinstance(obj, Decimal):
        float_obj = float(obj)
        if math.isnan(float_obj):
            return None
        else:
            return float_obj

    elif isinstance(obj, float) and math.isnan(obj):
        return None

    raise TypeError(
        f"Object of type {obj.__class__.__name__} is not JSON serializable"
    )

def sanitize_for_json(obj):
    """Recursively sanitize data for JSON (replace NaN, inf, etc.)"""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    return obj
    

def _format_url(route: str, path: typing.Optional[str] = None):
    """Method to format url and parameters to be used in requests."""
    api_url = os.environ["API_URL"]
    url = api_url.rstrip("/") + "/" + route.lstrip("/")
    if path:
        url += "/" + path.lstrip("/")
    return url


def post_request(route, json_body):
    """Method to perform a POST request."""

    url = _format_url(route)
    
    clean_json_body = sanitize_for_json(json_body)
    response = requests.post(
        url, data=json.dumps(clean_json_body, default=custom_serializer)
    )
    assert response.status_code in [200, 201], response.text
    return response.json()

def patch_request(route, path, json_body):
    """Method to perform a PATCH request."""
    url = _format_url(route, path)

    clean_json_body = sanitize_for_json(json_body)
    response = requests.patch(
        url, data=json.dumps(clean_json_body, default=custom_serializer)
    )

    assert response.status_code == 200, response.text
    return response.json()

def patch_request2(route: str, path: typing.Optional[str], json_body):
    """Method to perform a PATCH request."""
    url = _format_url(route, path)

    clean_json_body = sanitize_for_json(json_body)
    response = requests.patch(
        url, data=json.dumps(clean_json_body, default=custom_serializer)
    )

    assert response.status_code == 200
    return response.json()


def get_request(route: str, path: typing.Optional[str] = None, params=None):
    """Method to perform a GET request."""
    url = _format_url(route, path)
    response = requests.get(url, params=params)
    return response.status_code, response.json()

def options_request(route: str, path: typing.Optional[str] = None, params=None):
    """Method to perform a OPTIONS request."""
    url = _format_url(route, path)
    response = requests.options(url, params=params)
    return response.status_code, response.json()
