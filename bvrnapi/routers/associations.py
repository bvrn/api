from datetime import datetime
from enum import Enum
from io import StringIO
from typing import List

import folium
import numpy as np
import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
from fastapi.responses import HTMLResponse
from pydantic import HttpUrl, ValidationError, parse_obj_as
from sqlalchemy.orm import Session
from starlette.responses import Response

from bvrnapi.db import crud
from bvrnapi.db.database import get_db
from bvrnapi.lib.connectors.nominatim import geocode_city
from bvrnapi.lib.converters.http import best_httpurl
from bvrnapi.lib.crawler.link_extractor import link_by_name
from bvrnapi.models.associations import (
    Association,
    AssociationCreate,
    AssociationHomepageCreate,
    Representative,
)
from bvrnapi.models.geopy import Locations

router = APIRouter(
    prefix="/associations",
    tags=["associations"],
)


class Separator(str, Enum):
    semicolon = ";"
    comma = ","
    tab = "t"
    pipe = "|"
    colon = ":"


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
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
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
    background_tasks.add_task(_put_associations, db, sep, file)
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get("", response_model=List[Association], response_model_exclude_none=True)
async def get_associations(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Get a list of all member associations of BVRN (cached for 12 h).
    """
    associations = crud.get_associations(db, skip, limit)
    return associations


@router.get("/locations", response_model=Locations, response_model_exclude_none=True)
async def get_association_locations(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Get all locations (by Vereinsort) of member associations of BVRN (cached for 7 d).
    """
    associations: List[Association]
    locations: Locations
    associations, locations = _get_associations_and_locations(db, skip, limit)

    return locations


@router.get("/map", response_class=HTMLResponse)
async def get_associations_map(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Get all member associations of BVRN as a map (cached for 12 h).
    """
    associations: List[Association]
    locations: Locations
    associations, locations = _get_associations_and_locations(db, skip, limit)

    min_lat = min(location.lat for location in locations.locations.values())
    max_lat = max(location.lat for location in locations.locations.values())
    min_lon = min(location.lon for location in locations.locations.values())
    max_lon = max(location.lon for location in locations.locations.values())

    folium_map = folium.Map()

    for association in associations:
        try:
            location = locations.locations[association.city]
        except KeyError:
            continue

        homepage = association.homepage.homepage
        impressum = association.homepage.impressum
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
            <p>Vorsitzende: {association.representative.address}, {association.representative.plz} {association.representative.city}</p>
            <p>Homepage: {homepage_a}{impressum_a}</p>
            <p>Stand: {association.mtime}</p>
            """

        iframe = folium.IFrame(html=html, width=400, height=400)
        popup = folium.Popup(iframe, max_width=2650)
        folium.Marker(
            location=[location.lat, location.lon],
            popup=popup,
            icon=folium.DivIcon(
                icon_size=(25, 25),
                html=f"""<div>
                <svg xmlns="http://www.w3.org/2000/svg" id="Layer_1" data-name="Layer 1" viewBox="0 0 25 25">
                <title>Music Note</title>
                <path id="Music_Note" data-name="Music Note" d="M12.55,0a.51.51,0,0,0-.39.13A.5.5,0,0,0,12,.5V17.68a5.2,5.2,0,0,0-5.23-1.5,5.16,5.16,0,0,0-3.2,2.38,4.13,4.13,0,0,0-.41,3.21A4.75,4.75,0,0,0,7.84,25a5.57,5.57,0,0,0,1.4-.18,5.16,5.16,0,0,0,3.2-2.37A4.19,4.19,0,0,0,13,20L13,6c4,0,8,5.69,8.08,5.75A.5.5,0,0,0,22,11.5C22,1.09,12.65,0,12.55,0Z" fill="#0e1d25"/>
                </svg>
                </div>
                """,
            ),
        ).add_to(folium_map)

    folium_map.fit_bounds([[min_lat, max_lon], [max_lat, min_lon]])

    return HTMLResponse(content=folium_map.get_root().render(), status_code=200)


@router.get(
    "/update/impressen",
    status_code=202,
    responses={204: {"description": "No Content: updated or not modified"}},
)
async def get_associations_update_impressen(
    background_tasks: BackgroundTasks,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Update the 'Impressen' of all member associations of BVRN. The Task will be processed in background.
    """
    background_tasks.add_task(_update_impressen, skip, limit, db)
    return Response(status_code=202)


def _update_impressen(skip: int, limit: int, db: Session):
    associations = crud.get_associations(db, skip, limit)
    for association in associations:
        homepage = crud.get_association_by_name(
            db, association.association_name
        ).homepage
        if homepage.homepage:
            link = link_by_name(
                homepage.homepage,
                ["impressum", "about", "kontakt", "contact", "ueber", "über"],
            )
            if link:
                try:
                    parse_obj_as(HttpUrl, link)
                except ValidationError:
                    # TODO insert problem (impressum no http url?)
                    continue
                homepage.impressum = link
                db.commit()
                db.refresh(homepage)
            else:
                pass  # TODO insert problem (no impressum found to url)


def _put_associations(db: Session, sep: Separator = ";", file: UploadFile = File(...)):
    df = pd.read_csv(
        StringIO(str(file.file.read(), "utf-8")), encoding="utf-8", sep=sep
    ).replace({np.nan: None})
    for i, row in df.iterrows():
        association = crud.get_association(db, row["Verbandsnummer"])
        exists = True if association else False
        try:
            mtime_new = datetime.strptime(row["Stand"], "%d.%m.%Y")
        except ValueError:
            try:
                mtime_new = datetime.strptime(row["Stand"], "%d.%m.%Y %H:%M:%S")
            except ValueError:
                mtime_new = datetime.now()  # fallback

        if not exists or association.mtime < mtime_new:
            association_new = AssociationCreate(
                number=row["Verbandsnummer"],
                shortname=row["Kurzname"],
                association_name=row["Verein/Verband"],
                city=row["Vereinsort"],
                homepage=AssociationHomepageCreate(
                    homepage=best_httpurl(row["Homepage"]),
                    association_number=row["Verbandsnummer"],
                ),
                representative=Representative(
                    address=row["Straße/Postfach"],
                    plz=row["PLZ"],
                    city=row["Ort"],
                    email=row["E-Mail Vorsitzender"],
                ),
                it_representative=row["E-Mail EDV-Beauftragter"],
                mtime=mtime_new,
            )
            if exists:  # update
                crud.update_association(db, row["Verbandsnummer"], association_new)
            else:  # insert
                crud.create_association(db, association_new)


def _get_associations_and_locations(db, skip, limit):
    associations = crud.get_associations(db, skip, limit)

    locations_var = {}

    for association in associations:
        geocode_city_result = geocode_city(association.city)
        if geocode_city_result is not None:
            locations_var[association.city] = geocode_city_result.raw
        else:
            pass  # TODO insert problem (accociation city not found) (city: ...))

    locations = Locations(locations=locations_var)

    return associations, locations
