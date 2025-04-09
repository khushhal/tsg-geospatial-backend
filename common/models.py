import uuid

from django.contrib.gis.db import models as gis_models
from django.db import models


class BaseTimeStampedModel(models.Model):
    """An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class BaseTimeStampedUUIDModel(BaseTimeStampedModel):
    """
    Abstract model that uses UUID field as ID field
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class BaseGeoEntityModel(gis_models.Model):
    """
    Abstract base model for geographic entities.
    """

    geoid = models.IntegerField()
    name = models.CharField(max_length=100)
    boundary = gis_models.MultiPolygonField(null=True, blank=True, help_text="Geographic boundary")
    centroid = gis_models.PointField(null=True, blank=True, help_text="Representative centroid")

    class Meta:
        abstract = True

    @property
    def lat(self):
        return self.centroid.y if self.centroid else None

    @property
    def lng(self):
        return self.centroid.x if self.centroid else None

    @property
    def geo(self):
        return {
            "name": self.name,
            "geometry": self.boundary.geojson if self and self.boundary else None,
        }
