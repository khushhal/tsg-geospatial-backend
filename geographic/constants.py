from geographic.models import State, County, City

ZOOM_TOLERANCE = {
    3: 0.05,
    5: 0.02,
    7: 0.01,
    9: 0.005,
    12: 0.001,
    14: 0.0005,
}

ENTITY_MODELS = {
    "state": State,
    "county": County,
    "city": City,
}
