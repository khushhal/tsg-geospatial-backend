import json

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point, Polygon, GEOSGeometry
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from geographic.constants import ENTITY_MODELS
from geographic.helpers import get_simplification_tolerance
from geographic.models import County, City, MSA
from geographic.serializers import NearbyCitySerializer, CityByPolygonSerializer


class BoundariesAPIView(APIView):
    """
    API endpoint that returns simplified geo-boundary data for states, counties, or cities,
    filtered by bounding box and zoom level. This refactored version includes caching.
    """

    def get(self, request):
        entity_type = request.GET.get("type")
        bbox = request.GET.get("bbox")
        try:
            zoom = float(request.GET.get("zoom", 6))
        except ValueError:
            return Response({"error": "Invalid zoom value"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the entity type.
        model = ENTITY_MODELS.get(entity_type)
        if not model:
            return Response({"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that bbox is provided.
        if not bbox:
            return Response({"error": "Missing bbox"}, status=status.HTTP_400_BAD_REQUEST)

        # Build a unique cache key based on the request parameters.
        cache_key = f"boundaries:{entity_type}:{bbox}:{zoom}"
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            # If a cached response exists, return it immediately.
            return Response(cached_response)

        # Parse the bbox string and create a polygon for filtering.
        try:
            min_lng, min_lat, max_lng, max_lat = map(float, bbox.split(","))
            bbox_poly = Polygon.from_bbox((min_lng, min_lat, max_lng, max_lat))
            bbox_poly.srid = 4326
        except ValueError:
            return Response({"error": "Invalid bbox format"}, status=status.HTTP_400_BAD_REQUEST)

        tolerance = get_simplification_tolerance(zoom)
        queryset = model.objects.filter(boundary__intersects=bbox_poly)

        features = []
        for obj in queryset:
            if obj.boundary:
                boundary = obj.boundary

                # Only apply simplification when zoom level is lower than 12
                if zoom < 12:
                    boundary = boundary.simplify(tolerance, preserve_topology=True)

                # Ensure the spatial reference is set correctly
                boundary.srid = 4326

                try:
                    geometry = json.loads(boundary.geojson)
                except Exception:
                    continue  # Skip this object if the geometry is invalid

                features.append(
                    {
                        "type": "Feature",
                        "geometry": geometry,
                        "properties": {
                            "uuid": obj.uuid,
                            "name": obj.name,
                            "slug": obj.quick_fact_slug,
                        },
                    }
                )

        result = {"type": "FeatureCollection", "features": features}
        # Cache the result for 5 minutes (300 seconds)
        cache.set(cache_key, result, timeout=300)
        return Response(result)


class NearbyCitiesAPIView(APIView):
    def get(self, request):
        try:
            lat = float(request.GET.get("lat"))
            lng = float(request.GET.get("lng"))
        except (TypeError, ValueError):
            return Response({"error": "Invalid or missing latitude/longitude."}, status=status.HTTP_400_BAD_REQUEST)

        radius = float(request.GET.get("radius", 20000))  # default radius in meters

        # Create a point using the provided coordinates
        point = Point(lng, lat, srid=4326)

        # Annotate the distance and filter out cities without a centroid.
        cities = (
            City.objects.annotate(distance=Distance("centroid", point))
            .filter(distance__lte=radius, centroid__isnull=False)
            .order_by("distance")
        )

        serializer = NearbyCitySerializer(cities, many=True)
        return Response(serializer.data)


class CitiesByPolygonAPIView(APIView):
    def post(self, request):
        geojson = request.data.get("geometry")

        if not geojson:
            return Response({"error": "Missing geometry"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a polygon from the provided geojson geometry
        polygon = GEOSGeometry(str(geojson), srid=4326)

        # Filter cities with boundaries intersecting the polygon and ensure centroid is present.
        cities = City.objects.filter(boundary__intersects=polygon, centroid__isnull=False)

        # Serialize the queryset
        serializer = CityByPolygonSerializer(cities, many=True)
        return Response(serializer.data)


class EncompassingRegionAPIView(APIView):
    def get(self, request):
        lat = float(request.GET.get("lat"))
        lng = float(request.GET.get("lng"))

        point = Point(lng, lat, srid=4326)

        city = City.objects.filter(boundary__contains=point).first()
        county = County.objects.filter(boundary__contains=point).first()
        msa = MSA.objects.filter(boundary__contains=point).first()

        return Response(
            {
                "city": city.name if city else None,
                "county": county.name if county else None,
                "msa": msa.name if msa else None,
            }
        )
