# Generated by Django 4.2.20 on 2025-04-09 12:00

import uuid

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MSA",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("geoid", models.IntegerField()),
                ("name", models.CharField(max_length=100)),
                (
                    "boundary",
                    django.contrib.gis.db.models.fields.MultiPolygonField(
                        blank=True, help_text="Geographic boundary", null=True, srid=4326
                    ),
                ),
                (
                    "centroid",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, help_text="Representative centroid", null=True, srid=4326
                    ),
                ),
                ("fips", models.CharField(help_text="City FIPS code", max_length=7)),
                ("lsad", models.CharField(help_text="Type: M1 = Metropolitan (MSA), M2 = Micropolitan", max_length=4)),
                ("namelsad", models.CharField(help_text="Full legal/statistical name", max_length=225)),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="State",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("geoid", models.IntegerField()),
                ("name", models.CharField(max_length=100)),
                (
                    "boundary",
                    django.contrib.gis.db.models.fields.MultiPolygonField(
                        blank=True, help_text="Geographic boundary", null=True, srid=4326
                    ),
                ),
                (
                    "centroid",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, help_text="Representative centroid", null=True, srid=4326
                    ),
                ),
                ("population", models.BigIntegerField(null=True)),
                ("fips", models.CharField(help_text="State FIPS code", max_length=2)),
                ("abbreviation", models.CharField(help_text="State abbreviation", max_length=2)),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="County",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("geoid", models.IntegerField()),
                ("name", models.CharField(max_length=100)),
                (
                    "boundary",
                    django.contrib.gis.db.models.fields.MultiPolygonField(
                        blank=True, help_text="Geographic boundary", null=True, srid=4326
                    ),
                ),
                (
                    "centroid",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, help_text="Representative centroid", null=True, srid=4326
                    ),
                ),
                ("population", models.BigIntegerField(null=True)),
                ("fips", models.CharField(help_text="County FIPS code", max_length=3)),
                ("namelsad", models.CharField(help_text="Full legal/statistical name", max_length=225)),
                (
                    "state",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="counties", to="geographic.state"
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="City",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("geoid", models.IntegerField()),
                ("name", models.CharField(max_length=100)),
                (
                    "boundary",
                    django.contrib.gis.db.models.fields.MultiPolygonField(
                        blank=True, help_text="Geographic boundary", null=True, srid=4326
                    ),
                ),
                (
                    "centroid",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, help_text="Representative centroid", null=True, srid=4326
                    ),
                ),
                ("population", models.BigIntegerField(null=True)),
                ("fips", models.CharField(help_text="City FIPS code", max_length=7)),
                ("namelsad", models.CharField(help_text="Full legal/statistical name", max_length=225)),
                (
                    "county",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="cities",
                        to="geographic.county",
                    ),
                ),
                (
                    "state",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="cities", to="geographic.state"
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
    ]
