from rest_framework import serializers

from census.models import (
    CensusPopulation,
    CensusDemographics,
    CensusBusiness,
    CensusGeography,
    CensusSocioEconomicProfile,
    CensusProfile,
)


class CensusPopulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CensusPopulation
        exclude = ["created_at", "updated_at"]


class CensusDemographicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CensusDemographics
        exclude = ["created_at", "updated_at"]


class CensusBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = CensusBusiness
        exclude = ["created_at", "updated_at"]


class CensusGeographySerializer(serializers.ModelSerializer):
    class Meta:
        model = CensusGeography
        exclude = ["created_at", "updated_at"]


class CensusSocioEconomicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CensusSocioEconomicProfile
        exclude = ["created_at", "updated_at"]


class CensusProfileSerializer(serializers.ModelSerializer):
    population = CensusPopulationSerializer(read_only=True)
    demographics = CensusDemographicsSerializer(read_only=True)
    business = CensusBusinessSerializer(read_only=True)
    geography = CensusGeographySerializer(read_only=True)
    socio_economic = CensusSocioEconomicProfileSerializer(read_only=True)

    class Meta:
        model = CensusProfile
        fields = [
            "uuid",
            "quick_fact_slug",
            "population",
            "demographics",
            "business",
            "geography",
            "socio_economic",
            "year",
            "name",
        ]
