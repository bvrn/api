import requests
from pydantic import ValidationError
from pydantic.tools import parse_obj_as

from bvrnapi.models.httpurl_status import HttpsUrlStatus, HttpUrlStatus


def best_httpurl(url: str):
    """
    validates url and returns best possible HttpUrl class
    :param url: (bad) url string
    :return: HttpUrlStatus, HttpsUrlStatus or None
    """
    if not url or "@" in url:  # empty url or url with @ symbol will always return None
        return None
    if "@" in url:  # url with @ symbol will also return None
        # TODO insert problem (why @ symbol in url? url with authentication or e-mail address?)
        return None

    url_formatted = url.lower()
    if url_formatted.startswith("http://"):
        url_formatted = url_formatted.replace("http://", "https://")
    if not url_formatted.startswith("https://"):
        url_formatted = f"https://{url_formatted}"
    assert url_formatted.startswith("https://")

    try:
        parsed = parse_obj_as(HttpsUrlStatus, url_formatted)
        if url_formatted is not url:
            pass  # TODO insert problem (homepage should be https (url: ...))
        return parsed
    except (
        requests.exceptions.SSLError,
        requests.exceptions.ConnectionError,
        ValidationError,
    ):
        # no https available
        url_formatted = url_formatted.replace("https://", "http://")
        assert url_formatted.startswith("http://")
        try:
            parsed = parse_obj_as(HttpUrlStatus, url_formatted)
            if url_formatted is not url:
                pass  # TODO insert problem (homepage should be available via https (url: ...))
            return parsed
        except (ValidationError, requests.exceptions.ConnectionError):
            # TODO insert problem (homepage not found / reachable)
            return None
