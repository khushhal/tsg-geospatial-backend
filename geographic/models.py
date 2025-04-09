from django.db import models

from common.models import BaseTimeStampedUUIDModel, BaseGeoEntityModel


class State(BaseTimeStampedUUIDModel, BaseGeoEntityModel):
    population = models.BigIntegerField(null=True)
    fips = models.CharField(max_length=2, help_text="State FIPS code")
    abbreviation = models.CharField(max_length=2, help_text="State abbreviation")

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

    @property
    def qf_fips(self):
        return self.fips

    @property
    def quick_fact_slug(self):
        return self.abbreviation.lower()


class County(BaseTimeStampedUUIDModel, BaseGeoEntityModel):
    population = models.BigIntegerField(null=True)
    fips = models.CharField(max_length=3, help_text="County FIPS code")
    namelsad = models.CharField(max_length=225, help_text="Full legal/statistical name")
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="counties")

    def __str__(self):
        return f"{self.name}, {self.state.abbreviation}"

    @property
    def qf_fips(self):
        return f"{self.state.fips}{self.fips}"

    @property
    def quick_fact_slug(self):
        return self.qf_fips


class City(BaseTimeStampedUUIDModel, BaseGeoEntityModel):
    population = models.BigIntegerField(null=True)
    fips = models.CharField(max_length=7, help_text="City FIPS code")
    namelsad = models.CharField(max_length=225, help_text="Full legal/statistical name")
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities")
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True, related_name="cities")

    def __str__(self):
        return f"{self.name}, {self.state.abbreviation}"

    @property
    def qf_fips(self):
        return f"{self.state.qf_fips}{self.fips}"

    @property
    def quick_fact_slug(self):
        return self.qf_fips


class MSA(BaseTimeStampedUUIDModel, BaseGeoEntityModel):
    fips = models.CharField(max_length=7, help_text="City FIPS code")
    lsad = models.CharField(max_length=4, help_text="Type: M1 = Metropolitan (MSA), M2 = Micropolitan")
    namelsad = models.CharField(max_length=225, help_text="Full legal/statistical name")

    def __str__(self):
        return f"{self.name}"
