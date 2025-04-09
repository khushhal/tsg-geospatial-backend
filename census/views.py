from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from census.models import CensusProfile
from census.serialzers import CensusProfileSerializer


class CensusProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CensusProfile.objects.all()
    serializer_class = CensusProfileSerializer

    @action(detail=False, methods=["get"])
    def by_entity(self, request, **kwargs):
        entity_type = kwargs.get("entity_type")
        entity_id = kwargs.get("entity_id")

        if not entity_type or not entity_id:
            raise ValidationError("entity_type and entity_id parameters are required")

        try:
            content_type = ContentType.objects.get(model=entity_type.lower())
            census_profile = (
                self.queryset.filter(content_type=content_type, object_id=entity_id).order_by("-year").first()
            )
            if census_profile:
                serializer = self.get_serializer(census_profile)
                return Response(serializer.data)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ContentType.DoesNotExist:
            raise ValidationError(f"Invalid entity_type: {entity_type}")
