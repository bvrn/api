from typing import Dict

import requests
from pydantic import AnyUrl


class HttpUrlStatus(AnyUrl):
    """
    similar to pydantic.HttpUrl but test status code (http scheme only)
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.2403.157 Safari/537.36"
    }

    status_code: int = 200

    allowed_schemes = {"http"}
    tld_required = True
    # https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
    max_length = 2083

    @classmethod
    def validate_parts(cls, parts: Dict[str, str]) -> Dict[str, str]:
        super_return = super().validate_parts(parts)
        url: str = cls.build(
            scheme=parts["scheme"],
            user=parts["user"],
            password=parts["password"],
            host=parts["domain"],
            port=parts["port"],
            path=parts["path"],
            query=parts["query"],
            fragment=parts["fragment"],
        )
        r = requests.get(url, allow_redirects=False, headers=cls.headers)
        if r.status_code != cls.status_code:
            if r.status_code == 403:
                print(f"url {url} is 403")
            raise ValueError(
                f"url not matching the status code (expected: {cls.status_code}, got: {r.status_code}"
            )
        return super_return


class HttpsUrlStatus(HttpUrlStatus):
    """
    similar to pydantic.HttpUrl but test status code (https scheme only)
    """

    allowed_schemes = {"https"}
