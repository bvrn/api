from datetime import datetime
from http.client import responses

import requests
from flask import Response


def get_response(
    status_code=500,
    payload=None,
    mimetype="application/json",
    r: requests.models.Response = None,
):
    if r:
        status_code = r.status_code
        try:
            payload = r.json()
        except ValueError:
            payload = r.text
            mimetype = "text/plain"
    return Response(payload, status=status_code, mimetype=mimetype)


def get_error_response(message, path, status_code=500):
    payload = __format_payload(status_code, message, path)
    return Response(payload, status=status_code, mimetype="application/json")


def __format_payload(status_code, message, path):
    return {
        "timestamp": str(datetime.now()),
        "status": status_code,
        "status_desc": responses[status_code],
        "message": message,
        "path": path,
    }
