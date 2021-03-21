from flask import Blueprint, jsonify, request, current_app, url_for
from flask_api import status
import requests
import numpy as np
import os
import json

from bvrnapi.cache import cache
from bvrnapi.lib.helper.responses.response_filter import is_success
from bvrnapi.lib.connect.commusic import commusic_df, ResponseException
from bvrnapi.lib.connect.nominatim import geocode_city
from bvrnapi.lib.helper.responses import get_error_response

associations_bp = Blueprint(name="associations", import_name=__name__)


@associations_bp.route('', methods=['GET'])
@cache.cached(timeout=60*60*12, response_filter=is_success)
def associations():
    """
    ---
    get:
      description: Get all member associations of BVRN (cached for 12 h).
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: Associations
      tags:
          - Associations
    """
    try:
        table = commusic_df(current_app.config["COMMUSIC_ASSOCIATION_URL"])
    except ResponseException as e:
        return get_error_response(e.message, request.path, e.status_code)

    response_json = {
        "total": len(table.index),  # TODO: add other attributes?
        "values": table.replace(np.nan, '', regex=True).to_dict('records')
    }

    return jsonify(response_json)


@associations_bp.route('/locations', methods=['GET'])
def associations_locations():
    """
    ---
    get:
      description: Get all locations (by Vereinsort) of member associations of BVRN (cached for 12 h - 7 d).
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: Locations
      tags:
          - Associations
    """
    # r = requests.get(url_for('associations.associations'))  # TODO: get full path
    r = requests.get("http://localhost:5000/api/v1/associations")
    if not status.is_success(r.status_code):
        return get_error_response(r.text, request.path, r.status_code)

    association_list = r.json()  # TODO: catch ValueError

    locations = {}

    for association in association_list["values"]:
        city = association["city"]
        geocode_city_result = geocode_city(city)
        if geocode_city_result is not None:
            locations[city] = geocode_city_result.raw
        else:
            print("city '{}' from association '{}' not found".format(city, association["association"]))  # TODO: just for debugging, remove / replace by notification
    # file_path = os.path.join(current_app.config["CACHE_DIR"], "locations.json")
    # if os.path.isfile(file_path):
    #     with open(file_path, 'r') as file:
    #         locations = json.load(file)
    # else:
    #     with open(file_path, "x"):
    #         pass
    # for association in association_list["values"]:
    #     city = association["city"]
    #     if city not in locations and (geocode_city := nominatim.geocode_city(city)) is not None:
    #         locations[city] = geocode_city.raw
    # with open(file_path, 'w') as file:
    #     json.dump(locations, file, indent=4)

    return jsonify({"locations": locations})
