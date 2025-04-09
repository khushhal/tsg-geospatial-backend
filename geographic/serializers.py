from rest_framework import serializers

from geographic.models import City


class NearbyCitySerializer(serializers.ModelSerializer):
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ("uuid", "name", "distance_km", "lat", "lng")

    @staticmethod
    def get_distance_km(obj):
        # The distance is annotated, so convert to km and round it off.
        return round(obj.distance.km, 2) if hasattr(obj, "distance") else None


class CityByPolygonSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("uuid", "name", "lat", "lng", "fips")
