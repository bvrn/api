from geopy.geocoders import Nominatim
from geopy.point import Point

from bvrnapi.cache import cache

bounding_box_rnk = (Point(49.17431, 8.450102), Point(49.625683, 9.101586))


@cache.memoize(timeout=60 * 60 * 24 * 7)
def geocode_city(city, viewbox=bounding_box_rnk):
    return Nominatim(user_agent="bvrn-api").geocode(
        city,
        viewbox=viewbox,
        country_codes="de",
        namedetails=True,
        addressdetails=True,
        extratags=True,
        language="de,en",
    )
