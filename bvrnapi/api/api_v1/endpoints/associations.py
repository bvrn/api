import json
import urllib.request
from datetime import datetime
from enum import Enum
from io import StringIO
from typing import List

import folium
import numpy as np
import pandas as pd
import requests.exceptions
from fastapi import APIRouter, Depends, BackgroundTasks, status, UploadFile, File, Response
from fastapi.responses import HTMLResponse
from folium import plugins as folium_plugins
from geopy.point import Point
from pydantic import parse_obj_as, HttpUrl, ValidationError
from sqlalchemy.orm import Session

from bvrnapi import crud, models, schemas
from bvrnapi.api import deps
from bvrnapi.config import settings
from bvrnapi.lib.connectors.nominatim import geocode_city
from bvrnapi.lib.converters.http import best_httpurl
from bvrnapi.lib.crawler import link_by_name
from bvrnapi.schemas.geopy import Locations

router = APIRouter()


class Separator(str, Enum):
    semicolon = ";"
    comma = ","
    tab = "t"
    pipe = "|"
    colon = ":"


class Encoding(str, Enum):
    utf8 = "utf-8"
    utf16 = "utf-16"


class ClusterMode(str, Enum):
    all = "all"
    city = "city"


@router.put(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        204: {"description": "No Content: updated or not modified"},
        201: {"description": "Created: new record(s) created"},
    },
)
async def put_associations(
        background_tasks: BackgroundTasks,
        sep: Separator = ";",
        enc: Encoding = "utf-16",
        file: UploadFile = File(...),
        db: Session = Depends(deps.get_db),
):
    """
    Put DSV file (commonly known as CSV / TSV) to create / update associations. Default separator is a semicolon (;).

    First row must contain the following header names:
    * Verbandsnummer
    * Kurzname
    * Vereinsort
    * Verein/Verband
    * Straße/Postfach
    * PLZ
    * Ort
    * Homepage
    * E-Mail Vorsitzender
    * E-Mail EDV-Beauftragter
    * Stand

    The Task will be processed in background.

    _The request is idempotent._
    """
    background_tasks.add_task(_put_associations, db, sep, enc, file)
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get(
    "/update/impressen",
    status_code=202,
    responses={204: {"description": "No Content: updated or not modified"}},
)
async def get_associations_update_impressen(
        background_tasks: BackgroundTasks,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
):
    """
    Update the 'Impressen' of all member associations of BVRN. The Task will be processed in background.
    """
    background_tasks.add_task(_update_impressen, skip, limit, db)
    return Response(status_code=202)


@router.get("/locations", response_model=Locations, response_model_exclude_none=True)
async def get_locations(
        skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)
):
    """
    Get all locations (by Vereinsort) of member associations of BVRN (cached for 7 d).
    """
    locations: Locations

    with urllib.request.urlopen(str(settings.get_nominatim_url())) as url:
        relations = json.loads(url.read().decode())
    min_lat = min(place["boundingbox"][0] for place in relations)
    max_lat = max(place["boundingbox"][1] for place in relations)
    min_lon = min(place["boundingbox"][2] for place in relations)
    max_lon = max(place["boundingbox"][3] for place in relations)
    locations = _get_locations(db, skip, limit, viewbox=((min_lat, min_lon), (max_lat, max_lon)))

    return locations


@router.get("/map", response_class=HTMLResponse)
async def get_associations_map(
        cluster: ClusterMode = ClusterMode.all, skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)
):
    """
    Get all member associations of BVRN as a map.
    Use cluster to choose the cluster mode (Clustering per ***city*** or ***all*** together).
    """
    associations: List[models.Association]
    locations: Locations

    with urllib.request.urlopen(str(settings.get_nominatim_url())) as url:
        relations = json.loads(url.read().decode())
    min_lat = min(place["boundingbox"][0] for place in relations)
    max_lat = max(place["boundingbox"][1] for place in relations)
    min_lon = min(place["boundingbox"][2] for place in relations)
    max_lon = max(place["boundingbox"][3] for place in relations)
    locations = _get_locations(db, skip, limit, viewbox=((min_lat, min_lon), (max_lat, max_lon)))

    folium_map = folium.Map(
        control_scale=True,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
    )

    folium_plugins.Fullscreen().add_to(folium_map)
    folium_plugins.LocateControl().add_to(folium_map)

    marker_cluster = None
    if cluster == ClusterMode.all:
        marker_cluster = folium_plugins.MarkerCluster().add_to(folium_map)
    for city, location in locations.locations.items():
        if cluster == ClusterMode.city:
            marker_cluster = folium_plugins.MarkerCluster(name=city).add_to(folium_map)
        associations = crud.association.get_by_city(db, city=city)
        for association in associations:
            homepage = association.homepage
            impressum = association.impressum
            homepage_a = (
                f'<a target="_blank" href="{homepage}">{homepage}</a>' if homepage else "-"
            )
            impressum_a = (
                f' (<a target="_blank" href="{impressum}">Impressum</a>)'
                if impressum
                else ""
            )
            shortname = association.shortname if association.shortname else "-"
            city_wikipedia_a = (
                f'<a target="_blank" href="https://de.wikipedia.org/wiki/{location.extratags.wikipedia}">Wikipedia</a>'
                if location.extratags.wikipedia
                else None
            )
            city_wikidata_a = (
                f'<a target="_blank" href="https://www.wikidata.org/entity/{location.extratags.wikidata}">Wikidata</a>'
                if location.extratags.wikidata
                else None
            )
            city_wiki_str = (
                f" ({city_wikipedia_a}, {city_wikidata_a})"
                if city_wikipedia_a and city_wikidata_a
                else f" ({city_wikipedia_a})"
                if city_wikipedia_a
                else f" ({city_wikidata_a})"
                if city_wikidata_a
                else " "
            )
            html = f"""
            <h1>{association.association_name}</h1>
            <p>Kurzname: {shortname}</p>
            <p>Ort: {association.city}{city_wiki_str}</p>
            <p>Homepage: {homepage_a}{impressum_a}</p>
            <p>Stand: {association.mtime.date().strftime("%-d.%-m.%Y")}</p>
            """
            # f"<p>Vorsitzende: {association.representative_address}, {association.representative_plz} {association.representative_city}</p>"
            iframe = folium.IFrame(html=html)
            folium_html = folium.Html(html, script=True)
            popup = folium.Popup(folium_html, max_width=400)
            folium.Marker(
                location=[location.lat, location.lon],
                popup=popup,
                tooltip=association.association_name,
                icon=folium.DivIcon(
                    icon_size=(25, 25),
                    html=f"""<div>
                            <svg xmlns="http://www.w3.org/2000/svg" id="Layer_1" data-name="Layer 1" viewBox="0 0 25 25">
                            <path id="Music_Note" d="M12.55,0a.51.51,0,0,0-.39.13A.5.5,0,0,0,12,.5V17.68a5.2,5.2,0,0,0-5.23-1.5,5.16,5.16,0,0,0-3.2,2.38,4.13,4.13,0,0,0-.41,3.21A4.75,4.75,0,0,0,7.84,25a5.57,5.57,0,0,0,1.4-.18,5.16,5.16,0,0,0,3.2-2.37A4.19,4.19,0,0,0,13,20L13,6c4,0,8,5.69,8.08,5.75A.5.5,0,0,0,22,11.5C22,1.09,12.65,0,12.55,0Z" fill="#0e1d25"/>
                            </svg>
                            </div>
                            """
                ),
            ).add_to(marker_cluster)
    folium.GeoJson(str(settings.get_nominatim_url(with_polygons=True)), name="BVRN").add_to(folium_map)

    folium_map.fit_bounds([[min_lat, max_lon], [max_lat, min_lon]])

    return HTMLResponse(content=folium_map.get_root().render(), status_code=200)


def _put_associations(db: Session, sep: Separator = ";", enc: Encoding = "utf-16", file: UploadFile = File(...)):
    df = pd.read_csv(
        StringIO(str(file.file.read(), enc)), encoding=enc, sep=sep
    ).replace({np.nan: None})
    for i, row in df.iterrows():
        association = crud.association.get_by_number(db, number=row["Verbandsnummer"])
        exists = True if association else False
        try:
            mtime_new = datetime.strptime(row["Stand"], "%d.%m.%Y")
        except ValueError:
            try:
                mtime_new = datetime.strptime(row["Stand"], "%d.%m.%Y %H:%M:%S")
            except ValueError:
                mtime_new = datetime.now()  # fallback

        if not exists or association.mtime < mtime_new:
            homepage_exception = None
            try:
                homepage = best_httpurl(row["Homepage"])
                if homepage and homepage.startswith("http://"):
                    homepage_exception = "Homepage should be available over https:// (SSL)"
                elif homepage and not homepage.startswith(row["Homepage"]):
                    homepage_exception = f"Homepage in Commusic should be like {homepage}"

            except (ValueError, ValidationError, requests.exceptions.ConnectionError) as e:
                print(f"Error: {e}")
                homepage = None
                homepage_exception = e

            association_new_data = dict(
                number=row["Verbandsnummer"],
                shortname=row["Kurzname"],
                association_name=row["Verein/Verband"],
                city=row["Vereinsort"],
                representative=schemas.Representative(
                    address=row["Straße/Postfach"],
                    plz=row["PLZ"],
                    city=row["Ort"],
                    email=row["E-Mail Vorsitzender"],
                ),
                it_representative=row["E-Mail EDV-Beauftragter"],
                mtime=mtime_new,
                homepage=homepage,
            )

            if exists:  # update
                crud.association.update(db=db, db_obj=association, obj_in=association_new_data)
            else:  # insert
                association = crud.association.create(db=db, obj_in=schemas.AssociationCreate(**association_new_data))

            if homepage_exception:
                problem = schemas.ProblemCreate(
                    type=schemas.ProblemType.homepage,
                    data={
                        "homepage": row["Homepage"],
                        "error": f"Error: {homepage_exception}",
                    },
                    mtime=datetime.now()
                )
                crud.problem.create_with_association(db=db, obj_in=problem, association_id=association.id)


def _update_impressen(skip: int, limit: int, db: Session):
    associations = crud.association.get_multi(db, skip=skip, limit=limit)
    for association in associations:
        homepage = association.homepage
        if homepage:
            link = link_by_name(homepage, settings.IMPRESSEN_KEYWORDS)
            if link:
                try:
                    parse_obj_as(HttpUrl, link)
                except ValidationError:
                    problem = schemas.ProblemCreate(
                        type=schemas.ProblemType.impressum_no_http_url,
                        data={
                            "homepage": homepage,
                            "link": link,
                        },
                        mtime=datetime.now()
                    )
                    crud.problem.create_with_association(db=db, obj_in=problem, association_id=association.id)
                    print(f"Can't validate impressum {link} from association {association.association_name}")
                    continue
                association.impressum = link
                db.commit()
                db.refresh(association)
            else:
                problem = schemas.ProblemCreate(
                    type=schemas.ProblemType.impressum_not_found,
                    data={
                        "homepage": homepage,
                    },
                    mtime=datetime.now()
                )
                crud.problem.create_with_association(db=db, obj_in=problem, association_id=association.id)
                print(f"No impressum found from association {association.association_name} with homepage {homepage}")


def _get_locations(db, skip, limit, viewbox=None):
    associations = crud.association.get_multi(db, skip=skip, limit=limit)

    locations_var = {}

    for association in associations:
        if association.city not in locations_var:
            # TODO: bounds
            geocode_city_result = geocode_city(association.city, viewbox=viewbox)
            if geocode_city_result:
                locations_var[association.city] = geocode_city_result.raw
            else:
                problem = schemas.ProblemCreate(
                    type=schemas.ProblemType.city_not_found,
                    data={
                        "city": association.city
                    },
                    mtime=datetime.now()
                )
                crud.problem.create_with_association(db=db, obj_in=problem, association_id=association.id)
                print(f"Location {association.city} not found or something else?")

    locations = Locations(locations=locations_var)

    return locations
