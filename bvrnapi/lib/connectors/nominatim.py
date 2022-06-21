from cachetools import TTLCache, cached
from geopy.geocoders import Nominatim
from geopy.point import Point

bounding_box_germany = (Point(47.2701114, 5.8663153), Point(55.099161, 15.0419309))


@cached(cache=TTLCache(maxsize=128, ttl=3600 * 24 * 7))
def geocode_city(city: str, viewbox=bounding_box_germany):
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
