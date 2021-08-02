from cachetools import TTLCache, cached
from geopy.geocoders import Nominatim
from geopy.point import Point

bounding_box_rnk = (Point(49.17431, 8.450102), Point(49.625683, 9.101586))


@cached(cache=TTLCache(maxsize=128, ttl=3600 * 24 * 7))
def geocode_city(city: str, viewbox=bounding_box_rnk):
    return Nominatim(user_agent="bvrn-api").geocode(
        {"city": city},
        viewbox=viewbox,
        bounded=True,
        country_codes="de",
        namedetails=True,
        addressdetails=True,
        extratags=True,
        language="de,en",
        exactly_one=True,
    )
