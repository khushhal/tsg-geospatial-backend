import logging
from decimal import Decimal, InvalidOperation

import requests
from bs4 import BeautifulSoup
from django.contrib.contenttypes.models import ContentType
from fake_useragent import UserAgent

from census.constants import (
    POPULATION_MAPPING,
    DEMOGRAPHICS_MAPPING,
    BUSINESS_MAPPING,
    GEOGRAPHY_MAPPING,
    SOCIO_ECONOMIC_MAPPING,
)
from census.models import (
    CensusDemographics,
    CensusPopulation,
    CensusBusiness,
    CensusGeography,
    CensusSocioEconomicProfile,
    CensusProfile,
)
from turl_street_group_assignment.settings import CENSUS_QUICKFACT_MNEMONIC_CODE, CENSUS_QUICKFACT_SCRAPED_YEAR

logger = logging.getLogger(__name__)


class CensusQuickFactsParser:
    """
    Fetches, parses, and saves U.S. Census QuickFacts data
    based on a provided state, county, or city instance.
    """

    DECIMAL_UNITS = {"PCT", "RTE", "MIN", "DOL", "SQM"}

    def __init__(self, state=None, county=None, city=None):
        self.state = state
        self.county = county
        self.city = city
        self.data = None
        self.year = CENSUS_QUICKFACT_SCRAPED_YEAR

    def run(self, dry_run=False):
        """
        Shortcut to fetch and save census data.
        Set dry_run=True to preview parsed model data without saving.
        """
        if dry_run:
            return self._preview_parsed_data()
        return self.save()

    def _preview_parsed_data(self):
        """
        Returns parsed data without saving any models.
        """
        url = self._build_quickfacts_url()
        soup = self._get_soup(url)
        self.data = self._extract_data(soup)

        return {
            "population": self._parse_model_data(POPULATION_MAPPING),
            "demographics": self._parse_model_data(DEMOGRAPHICS_MAPPING),
            "business": self._parse_model_data(BUSINESS_MAPPING),
            "geography": self._parse_model_data(GEOGRAPHY_MAPPING),
            "socio_economic": self._parse_model_data(SOCIO_ECONOMIC_MAPPING),
        }

    def save(self):
        """
        Creates or updates CensusProfile and all related model instances using GenericForeignKey.
        """
        url = self._build_quickfacts_url()
        soup = self._get_soup(url)
        self.data = self._extract_data(soup)
        region_name = soup.select_one("div.qf-titlebar h2").get_text(strip=True)

        region_fips, _ = self.data.get("fips")

        # Determine the geographic object and content type
        region = self.state or self.county or self.city
        if not region:
            raise ValueError("Must provide one of: state, county, or city.")

        if region_fips != region.qf_fips:
            raise Exception(f"FIPS code mismatched for {region_name}")

        content_type = ContentType.objects.get_for_model(region.__class__)
        object_id = region.uuid

        profile = CensusProfile.objects.filter(content_type=content_type, object_id=object_id, year=self.year).first()

        parsed_population = self._parse_model_data(POPULATION_MAPPING)
        parsed_demographics = self._parse_model_data(DEMOGRAPHICS_MAPPING)
        parsed_business = self._parse_model_data(BUSINESS_MAPPING)
        parsed_geography = self._parse_model_data(GEOGRAPHY_MAPPING)
        parsed_socio = self._parse_model_data(SOCIO_ECONOMIC_MAPPING)

        if profile:
            # Update existing related models
            for model_instance, parsed_data in [
                (profile.population, parsed_population),
                (profile.demographics, parsed_demographics),
                (profile.business, parsed_business),
                (profile.geography, parsed_geography),
                (profile.socio_economic, parsed_socio),
            ]:
                for field, value in parsed_data.items():
                    setattr(model_instance, field, value)
                model_instance.save()

            logger.info(f"🔄 Updated Census profile for {region}")
            created = False
        else:
            # Create new related records and profile
            population = CensusPopulation.objects.create(**parsed_population)
            demographics = CensusDemographics.objects.create(**parsed_demographics)
            business = CensusBusiness.objects.create(**parsed_business)
            geography = CensusGeography.objects.create(**parsed_geography)
            socio = CensusSocioEconomicProfile.objects.create(**parsed_socio)

            profile = CensusProfile.objects.create(
                year=self.year,
                content_type=content_type,
                object_id=object_id,
                population=population,
                demographics=demographics,
                business=business,
                geography=geography,
                socio_economic=socio,
            )

            logger.info(f"✅ Created Census profile for {region}")
            created = True

        return created, profile

    def _build_quickfacts_url(self):
        """
        Constructs QuickFacts URL using `quick_fact_slug` from state, county, or city.
        """
        if self.state and hasattr(self.state, "quick_fact_slug"):
            slug = self.state.quick_fact_slug
        elif self.county and hasattr(self.county, "quick_fact_slug"):
            slug = self.county.quick_fact_slug
        elif self.city and hasattr(self.city, "quick_fact_slug"):
            slug = self.city.quick_fact_slug
        else:
            raise ValueError("You must provide a state, county, or city with `quick_fact_slug` property.")

        return f"https://www.census.gov/quickfacts/fact/table/{slug}/{CENSUS_QUICKFACT_MNEMONIC_CODE}"

    def _get_soup(self, url):
        response = requests.get(url, headers=self._headers(), timeout=4)
        return BeautifulSoup(response.content, "html.parser")

    @staticmethod
    def _extract_data(soup):
        data_map = {}
        for row in soup.select("tr.fact"):
            mnemonic = row.get("data-mnemonic")
            unit = row.get("data-unit")
            if not mnemonic or not unit:
                continue

            tds = row.find_all("td")
            if len(tds) < 2:
                continue

            value_td = tds[-1]
            for el in value_td.select(".qf-sourcenote"):
                el.decompose()

            value = value_td.get_text(strip=True)
            if value in {"", "D", "F", "FN", "NA", "S", "X", "Z", "-", "N"}:
                continue

            data_map[mnemonic] = (value, unit)
        return data_map

    def _parse_model_data(self, mapping):
        return {
            field: self._parse_by_unit(val) for mnemonic, field in mapping.items() if (val := self.data.get(mnemonic))
        }

    @staticmethod
    def _parse_number(value):
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_decimal(value):
        try:
            return Decimal(value)
        except (ValueError, TypeError, InvalidOperation):
            return None

    @staticmethod
    def _headers():
        return {
            "cache-control": "no-cache",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "user-agent": UserAgent().random,
        }

    def _parse_by_unit(self, value_unit):
        if not value_unit:
            return None

        value, unit = value_unit
        value = value.replace(",", "").replace("%", "").replace("$", "").strip()

        if unit in self.DECIMAL_UNITS:
            return self._parse_decimal(value)
        elif unit == "ABS":
            return self._parse_number(value)
        elif unit == "STR":
            return value
        return value

    def _location_label(self):
        return self.state or self.county or self.city
