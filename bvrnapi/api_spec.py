"""OpenAPI v3 Specification"""

import yaml
from apispec import APISpec
from apispec.utils import validate_spec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields


OPENAPI_SPEC = """
openapi: 3.0.2
basePath: /api/v1
info:
  description: Server API document
  title: Server API
  version: 0.0.1
"""

settings = yaml.safe_load(OPENAPI_SPEC)
# retrieve  title, version, and openapi version
title = settings["info"].pop("title")
spec_version = settings["info"].pop("version")
openapi_version = settings.pop("openapi")

# Create an APISpec
spec = APISpec(
    title=title,
    version=spec_version,
    openapi_version=openapi_version,
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
    **settings
)


# Define schemas
class AssociationRecordSchema(Schema):
    address = fields.String(description="Address of association.", example="Musterweg 666", required=True)
    association = fields.String(description="Name of association.", example="Musikverein Musik e.V.", required=True)
    city = fields.String(description="City of association.", example="Musterhausen", required=True)
    homepage = fields.String(description="Homepage of association.", example="https://example.com", required=False)
    plz = fields.Int(description="PLZ of association.", example=12345, required=True)


class AssociationsSchema(Schema):
    total = fields.Int(description="Number of elements returned.", example=1, required=True)
    values = fields.List(fields.Nested(AssociationRecordSchema), required=True)


class AddressSchema(Schema):
    city = fields.String(example="Heidelberg")
    country = fields.String(example="Deutschland")
    country_code = fields.String(example="de")
    state = fields.String(example="Baden-Württemberg")


class NamedetailsSchema(Schema):
    name = fields.String(example="Heidelberg", required=True)
    name_ar = fields.String(example="هايدلبرغ", data_key="name:ar")
    name_de = fields.String(example="Heidelberg", data_key="name:de")
    name_el = fields.String(example="Χαϊδελβέργη", data_key="name:el")
    name_en = fields.String(example="Heidelberg", data_key="name:en")
    name_fr = fields.String(example="Heidelberg", data_key="name:fr")
    name_ja = fields.String(example="ハイデルベルク", data_key="name:ja")
    name_ko = fields.String(example="하이델베르크", data_key="name:ko")
    name_la = fields.String(example="Heidelberga", data_key="name:la")
    name_nds = fields.String(example="Heidelbarg", data_key="name:nds")
    name_pfl = fields.String(example="Haidlbärsch", data_key="name:pfl")
    name_ru = fields.String(example="Гейдельберг", data_key="name:ru")
    name_sr = fields.String(example="Хајделберг", data_key="name:sr")
    name_uk = fields.String(example="Гайдельберг", data_key="name:uk")


class LocationRecordSchema(Schema):
    place_id = fields.Int(description="reference to the Nominatim internal database ID", example=258050005, required=True)
    osm_id = fields.Int(description="reference to the OSM object (with osm_type)", example=285864, required=True)
    osm_type = fields.String(description="reference to the OSM object (with osm_id)", example="relation", required=True)
    boundingbox = fields.List(fields.String, example=["49.3520029", "49.4596927", "8.5731788", "8.7940496"], description="area of corner coordinates [min latitude, max latitude, min longitude, max longitude]", required=True)
    lat = fields.String(description="latitude of the centroid of the object", example="49.4093582", required=True)
    long = fields.String(description="longitude of the centroid of the object", example="8.694724", required=True)
    display_name = fields.String(description="full comma-separated address", example="Heidelberg, Baden-Württemberg, Deutschland", required=True)
    importance = fields.Float(description="computed importance rank", example=0.7630143067958192, required=True)
    icon = fields.String(description="link to class icon (if available)", example="https://nominatim.openstreetmap.org/ui/mapicons//poi_boundary_administrative.p.20.png", required=True)
    address = fields.Nested(AddressSchema, description="dictionary of address details", required=True)
    namedetails = fields.Nested(NamedetailsSchema, description="dictionary with full list of available names including ref etc.", required=True)


class LocationsSchema(Schema):
    locations = fields.Dict(keys=fields.String(), values=fields.Nested(LocationRecordSchema))


class InputSchema(Schema):
    number = fields.Int(description="An integer.", required=True)


class OutputSchema(Schema):
    msg = fields.String(description="A message.", required=True)


# register schemas with spec
spec.components.schema("AssociationRecord", schema=AssociationRecordSchema)
spec.components.schema("Associations", schema=AssociationsSchema)
spec.components.schema("LocationRecord", schema=LocationRecordSchema)
spec.components.schema("Locations", schema=LocationsSchema)
spec.components.schema("Input", schema=InputSchema)
spec.components.schema("Output", schema=OutputSchema)

# add swagger tags that are used for endpoint annotation
tags = [
    {'name': 'associations',
     'description': 'Vereine / Verbände'
     },
    {'name': 'testing',
     'description': 'For testing the API.'
     },
    {'name': 'calculation',
     'description': 'Functions for calculating.'
     },
]

for tag in tags:
    print(f"Adding tag: {tag['name']}")
    spec.tag(tag)
