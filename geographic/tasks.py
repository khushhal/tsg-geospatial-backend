import glob
import logging
import os
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from celery import shared_task

from common.helpers import read_shapefile, geometry_to_multipolygon
from geographic.helpers import update_model_population, fetch_census_population_data
from geographic.models import State, County, City, MSA

logger = logging.getLogger(__name__)


@shared_task
def import_msas_from_shapefile_task(shapefile_path="data/tl_2024_us_cbsa/tl_2024_us_cbsa.shp"):
    """
    Reads MSA shapefile and saves only Metropolitan Statistical Areas to the database.
    """
    gdf = read_shapefile(shapefile_path)
    if gdf is None:
        logger.error("Failed to read CBSA shapefile.")
        return

    for _, row in gdf.iterrows():
        geoid = row["GEOID"]
        name = row["NAME"]
        fips = row["CBSAFP"]
        geometry = geometry_to_multipolygon(row.geometry)

        msa, created = MSA.objects.update_or_create(
            fips=fips,
            defaults={
                "name": name,
                "lsad": row["LSAD"],
                "namelsad": row["NAMELSAD"],
                "geoid": row["GEOID"],
                "boundary": geometry,
                "centroid": geometry.centroid,
            },
        )
        logger.info("%s MSA: %s (GEOID: %s)", "Created" if created else "Updated", name, geoid)


@shared_task
def import_states_from_shapefile_task(shapefile_path="data/tl_2024_us_state/tl_2024_us_state.shp"):
    """
    Reads state shapefile and saves state records to the database.
    """
    gdf = read_shapefile(shapefile_path)
    if gdf is None:
        logger.error("Failed to read state shapefile.")
        return

    for _, row in gdf.iterrows():
        name = row["NAME"]
        abbreviation = row["STUSPS"]
        fips = row["STATEFP"]
        geometry = geometry_to_multipolygon(row.geometry)

        state, created = State.objects.update_or_create(
            fips=fips,
            defaults={
                "name": name,
                "geoid": row["GEOID"],
                "abbreviation": abbreviation,
                "boundary": geometry,
                "centroid": geometry.centroid,
            },
        )
        logger.info("%s state: %s (%s), FIPS: %s", "Created" if created else "Updated", name, abbreviation, fips)


@shared_task
def import_counties_from_shapefile_task(shapefile_path="data/tl_2024_us_county/tl_2024_us_county.shp"):
    """
    Reads county shapefile and saves county records to the database, linking them to states.
    """
    gdf = read_shapefile(shapefile_path)
    if gdf is None:
        logger.error("Failed to read county shapefile.")
        return

    for _, row in gdf.iterrows():
        name = row["NAME"]
        state_fips = row["STATEFP"]
        county_fips = row["COUNTYFP"]
        geometry = geometry_to_multipolygon(row.geometry)

        state = State.objects.filter(fips=state_fips).first()
        if not state:
            logger.error("State with FIPS %s not found. Skipping county %s.", state_fips, name)
            continue

        county, created = County.objects.update_or_create(
            fips=county_fips,
            state=state,
            defaults={
                "name": name,
                "namelsad": row["NAMELSAD"],
                "geoid": row["GEOID"],
                "boundary": geometry,
                "centroid": geometry.centroid,
            },
        )
        print(f"{'Created' if created else 'Updated'} county: {name}, FIPS: {county_fips}")


@shared_task
def import_cities_from_place_zips_task(places_directory="data/places"):
    """
    Reads city data from zipped shapefiles in the provided directory and saves city records to the database.
    Only includes cities (LSAD = '25').
    """
    zip_files = glob.glob(os.path.join(places_directory, "tl_2024_*_place.zip"))
    if not zip_files:
        logger.error("No city ZIP files found in %s", places_directory)
        return

    for zip_path in zip_files:
        with tempfile.TemporaryDirectory() as tmpdirname:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmpdirname)

            shp_files = glob.glob(os.path.join(tmpdirname, "*.shp"))
            if not shp_files:
                logger.error("No shapefile found in %s", zip_path)
                continue

            shapefile_path = shp_files[0]
            gdf = read_shapefile(shapefile_path)

        if gdf is None:
            logger.error("Failed to read shapefile: %s", shapefile_path)
            continue

        # 🔽 Only include rows where LSAD == '25' (i.e., cities)
        cities_only = gdf[gdf["LSAD"] == "25"]

        for _, row in cities_only.iterrows():
            name = row.get("NAME")
            geometry = geometry_to_multipolygon(row.geometry)

            try:
                state = State.objects.get(fips=row.get("STATEFP"))
            except State.DoesNotExist:
                logger.error("State with FIPS %s not found. Skipping city %s.", row.get("STATEFP"), name)
                continue

            county = County.objects.filter(boundary__contains=geometry.centroid, state=state).first()

            city, created = City.objects.update_or_create(
                name=name,
                state=state,
                fips=row["PLACEFP"],
                defaults={
                    "county": county,
                    "boundary": geometry,
                    "geoid": row["GEOID"],
                    "namelsad": row["NAMELSAD"],
                    "centroid": geometry.centroid,
                },
            )

            county_info = f", County: {county.name}" if county else ""
            logger.info(
                "%s city: %s, State: %s%s", "Created" if created else "Updated", name, state.abbreviation, county_info
            )


def update_population_threaded(model_class, level: str, fips_field: str):
    """
    Generic threaded function to fetch and update population for counties or cities.
    Iterates over all states and updates the population for the provided model.
    """
    states = list(State.objects.all())
    failed_states = []

    def process_state(state):
        try:
            df = fetch_census_population_data(level, state_fips=state.fips)
            update_model_population(df, model_class, fips_field=fips_field, state_filter=True)
        except Exception as e:
            logger.error("❌ Failed for %s: %s", state.name, e)
            failed_states.append(state.fips)

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_state, state) for state in states]
        for future in as_completed(futures):
            # This will re-raise exceptions (if any) that haven't been caught in process_state.
            try:
                future.result()
            except Exception:
                # Exceptions are already logged in process_state, so we can safely pass here.
                pass

    return failed_states


@shared_task
def update_populations_for_states_task():
    df = fetch_census_population_data("state")
    update_model_population(df, State, fips_field="state", state_filter=False)


@shared_task
def update_populations_for_counties_task():
    return update_population_threaded(County, level="county", fips_field="county")


@shared_task
def update_populations_for_cities_task():
    return update_population_threaded(City, level="place", fips_field="place")
