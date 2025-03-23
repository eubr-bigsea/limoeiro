import datetime
import json
import uuid
import requests
import os
import typing

API_URL = os.environ["API_URL"]


# Serialize UUID properties in json_body
def custom_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(
        f"Object of type {obj.__class__.__name__} is not JSON serializable"
    )


def _format_url(route: str, path: typing.Optional[str] = None):
    """Method to format url and parameters to be used in requests."""
    url = API_URL.rstrip("/") + "/" + route.lstrip("/")
    if path:
        url += "/" + path.lstrip("/")
    return url


def post_request(route, json_body):
    """Method to perform a post request."""

    url = _format_url(route)

    response = requests.post(
        url, data=json.dumps(json_body, default=custom_serializer)
    )
    assert response.status_code == 201, response.text
    return response.json()


def patch_request(route, path, json_body):
    """Method to perform a patch request."""
    url = _format_url(route, path)

    response = requests.patch(
        url, data=json.dumps(json_body, default=custom_serializer)
    )

    assert response.status_code == 200, response.text
    return response.json()

def patch_request2(route: str, path: typing.Optional[str], json_body):
    """Method to perform a patch request."""
    url = _format_url(route, path)

    response = requests.patch(
        url, data=json.dumps(json_body, default=custom_serializer)
    )

    assert response.status_code == 200
    return response.json()


def get_request(route: str, path: typing.Optional[str] = None, params=None):
    """Method to perform a get request."""
    url = _format_url(route, path)
    response = requests.get(url, params=params)
    return response.status_code, response.json()
