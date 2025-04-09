import pandas as pd
import requests

from geographic.constants import ZOOM_TOLERANCE
from turl_street_group_assignment.settings import CENSUS_API_BASE_URL, CENSUS_API_KEY


def get_simplification_tolerance(zoom):
    for z, tol in sorted(ZOOM_TOLERANCE.items(), reverse=True):
        if zoom >= z:
            return tol
    return 0.0001  # Fallback for very high zoom


def fetch_census_population_data(level: str, state_fips: str = None):
    """
    Fetches population data from the Census API for the given level ('state', 'county', or 'place').
    Optionally filter by state FIPS for 'county' or 'place'.
    """
    if level == "state":
        url = f"{CENSUS_API_BASE_URL}?get=NAME,P1_001N&for=state:*&key={CENSUS_API_KEY}"
    elif level in ("county", "place") and state_fips:
        url = f"{CENSUS_API_BASE_URL}?get=NAME,P1_001N&for={level}:*&in=state:{state_fips}&key={CENSUS_API_KEY}"
    else:
        raise ValueError("Invalid level or missing state_fips")

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data[1:], columns=data[0])


def update_model_population(df, model_class, fips_field, state_filter=False):
    """
    Updates population field in the given model using the DataFrame.
    """
    for _, row in df.iterrows():
        try:
            fips = row[fips_field]
            filters = {"fips": fips}

            if state_filter:
                filters["state__fips"] = row["state"].zfill(2)

            obj = model_class.objects.get(**filters)
            obj.population = int(row["P1_001N"])
            obj.save()
            print(f"✅ Updated: {obj}")
        except model_class.DoesNotExist:
            print(f"❌ {model_class.__name__} with FIPS {fips} not found.")
