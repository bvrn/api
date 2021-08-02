from typing import Dict, List, Optional

from pydantic import BaseModel, Field

lr_example = {
    "place_id": 258050005,
    "licence": "Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
    "osm_type": "relation",
    "osm_id": 285864,
    "boundingbox": ["49.3520029", "49.4596927", "8.5731788", "8.7940496"],
    "lat": "49.4093582",
    "lon": "8.694724",
    "display_name": "Heidelberg, Baden-Württemberg, Deutschland",
    "class": "boundary",
    "type": "administrative",
    "importance": 0.7630143067958192,
    "icon": "https://nominatim.openstreetmap.org/ui/mapicons//poi_boundary_administrative.p.20.png",
    "address": {
        "city": "Heidelberg",
        "state": "Baden-Württemberg",
        "country": "Deutschland",
        "country_code": "de",
    },
    "extratags": {
        "ele": "114",
        "de:place": "city",
        "wikidata": "Q2966",
        "wikipedia": "de:Heidelberg",
        "population": "152113",
        "ref:LOCODE": "DEHEI",
        "ref:nuts:3": "DE125",
        "name:prefix": "Stadt",
        "linked_place": "city",
        "de:regionalschluessel": "082210000000",
        "TMC:cid_58:tabcd_1:Class": "Area",
        "TMC:cid_58:tabcd_1:LCLversion": "8.00",
        "TMC:cid_58:tabcd_1:LocationCode": "456",
        "de:amtlicher_gemeindeschluessel": "08221000",
    },
    "namedetails": {
        "name": "Heidelberg",
        "name:ar": "هايدلبرغ",
        "name:de": "Heidelberg",
        "name:el": "Χαϊδελβέργη",
        "name:en": "Heidelberg",
        "name:fr": "Heidelberg",
        "name:ja": "ハイデルベルク",
        "name:ko": "하이델베르크",
        "name:la": "Heidelberga",
        "name:ru": "Гейдельберг",
        "name:sr": "Хајделберг",
        "name:uk": "Гайдельберг",
        "name:zh": "海德堡",
        "name:nds": "Heidelbarg",
        "name:pfl": "Haidlbärsch",
        "alt_name:ar": "هايدلبرج",
        "name:zh-Hant": "海德堡",
    },
}


class Address(BaseModel):
    continent: Optional[str]
    country: Optional[str]
    country_code: Optional[str]
    region: Optional[str]
    state: Optional[str]
    state_district: Optional[str]
    country: Optional[str]
    municipality: Optional[str]
    city: Optional[str]
    town: Optional[str]
    village: Optional[str]
    city_district: Optional[str]
    district: Optional[str]
    borough: Optional[str]
    suburb: Optional[str]
    subdivision: Optional[str]
    hamlet: Optional[str]
    croft: Optional[str]
    isolated_dwelling: Optional[str]
    neighbourhood: Optional[str]
    allotments: Optional[str]
    quarter: Optional[str]
    city_block: Optional[str]
    redidental: Optional[str]
    farm: Optional[str]
    farmyard: Optional[str]
    industrial: Optional[str]
    commercial: Optional[str]
    retail: Optional[str]
    road: Optional[str]
    house_number: Optional[str]
    house_name: Optional[str]
    emergency: Optional[str]
    historic: Optional[str]
    military: Optional[str]
    natural: Optional[str]
    landuse: Optional[str]
    place: Optional[str]
    railway: Optional[str]
    man_made: Optional[str]
    aerialway: Optional[str]
    boundary: Optional[str]
    amenity: Optional[str]
    aeroway: Optional[str]
    club: Optional[str]
    craft: Optional[str]
    leisure: Optional[str]
    office: Optional[str]
    mountain_pass: Optional[str]
    shop: Optional[str]
    tourism: Optional[str]
    bridge: Optional[str]
    tunnel: Optional[str]
    waterway: Optional[str]

    class Config:
        extra = "allow"


class Extratags(BaseModel):
    ele: Optional[str]
    de_place: Optional[str]
    wikidata: Optional[str]
    wikipedia: Optional[str]
    population: Optional[str]
    ref_LOCODE: Optional[str]
    ref_nuts_3: Optional[str]
    name_prefix: Optional[str]
    linked_place: Optional[str]
    de_regionalschluessel: Optional[str]
    de_amtlicher_gemeindeschluessel: Optional[str]

    class Config:
        extra = "allow"
        fields = {
            "de_place": "de:place",
            "ref_LOCODE": "ref:LOCODE",
            "ref_nuts_3": "ref:nuts:3",
            "name_prefix": "name:prefix",
            "de_regionalschluessel": "de:regionalschluessel",
            "de_amtlicher_gemeindeschluessel": "de:amtlicher_gemeindeschluessel",
        }


class Namedetails(BaseModel):
    name: str

    class Config:
        extra = "allow"


class LocationRecord(BaseModel):
    place_id: int
    osm_id: int
    osm_type: str
    boundingbox: List[str] = Field(..., min_items=4, max_items=4)
    lat: str
    lon: str
    display_name: str
    class_: Optional[str]
    type: Optional[str]
    importance: float
    icon: Optional[str]
    address: Address
    extratags: Extratags
    namedetails: Namedetails

    class Config:
        fields = {
            "class_": "class",
        }
        schema_extra = {"example": lr_example}


class Locations(BaseModel):
    locations: Dict[str, LocationRecord]

    class Config:
        schema_extra = {"example": {"Heidelberg": lr_example}}
