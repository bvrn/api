from flask_api import status


def is_success(resp):
    return status.is_success(resp.status_code)
