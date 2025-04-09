import geopandas as gpd
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon


def read_shapefile(path):
    try:
        return gpd.read_file(path)
    except Exception as e:
        print(f"Error reading shapefile {path}: {e}")
        return None


def geometry_to_multipolygon(geometry):
    geom = GEOSGeometry(geometry.wkt, srid=4326)
    if isinstance(geom, Polygon):
        return MultiPolygon(geom)
    return geom
