from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from common.models import BaseTimeStampedUUIDModel


class CensusPopulation(BaseTimeStampedUUIDModel):
    pop_estimate_july_2024 = models.BigIntegerField(help_text="Population estimate, July 1, 2024 (V2024)", null=True)
    pop_estimate_july_2023 = models.BigIntegerField(help_text="Population estimate, July 1, 2023 (V2023)", null=True)
    pop_estimate_base_apr2020_v2024 = models.BigIntegerField(
        help_text="Population estimate base, April 1, 2020 (V2024)", null=True
    )
    pop_estimate_base_apr2020_v2023 = models.BigIntegerField(
        help_text="Population estimate base, April 1, 2020 (V2023)", null=True
    )
    pop_percent_change_apr2020_to_july2024 = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percent change, Apr 2020 to Jul 2024", null=True
    )
    pop_percent_change_apr2020_to_july2023 = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percent change, Apr 2020 to Jul 2023", null=True
    )
    pop_census_apr2020 = models.BigIntegerField(help_text="Census count, April 1, 2020", null=True)
    pop_census_apr2010 = models.BigIntegerField(help_text="Census count, April 1, 2010", null=True)

    def __str__(self):
        return f"Population (2020 Census: {self.pop_census_apr2020})"


class CensusDemographics(BaseTimeStampedUUIDModel):
    # Age and Sex
    persons_under_5_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Persons under 5 years (%)", null=True
    )
    persons_under_18_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Persons under 18 years (%)", null=True
    )
    persons_65_over_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Persons 65+ years (%)", null=True
    )
    female_persons_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Female persons (%)", null=True
    )

    # Race and Hispanic Origin
    white_alone_percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="White alone (%)", null=True)
    black_alone_percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="Black alone (%)", null=True)
    american_indian_alaska_native_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="American Indian/Alaska Native (%)", null=True
    )
    asian_alone_percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="Asian alone (%)", null=True)
    native_hawaiian_pacific_islander_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Native Hawaiian/Other Pacific Islander (%)", null=True
    )
    two_or_more_races_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Two or more races (%)", null=True
    )
    hispanic_or_latino_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Hispanic or Latino (%)", null=True
    )
    white_alone_not_hispanic_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="White alone, not Hispanic (%)", null=True
    )

    # Population Characteristics
    veterans_2019_2023 = models.BigIntegerField(help_text="Veterans (2019-2023)", null=True)
    foreign_born_percent_2019_2023 = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Foreign-born (%) 2019-2023", null=True
    )

    def __str__(self):
        return f"Demographics (Under 5: {self.persons_under_5_percent}%)"


class CensusBusiness(BaseTimeStampedUUIDModel):
    total_employer_establishments = models.BigIntegerField(help_text="Total employer establishments, 2022", null=True)
    total_employment = models.BigIntegerField(help_text="Total employment, 2022", null=True)
    total_annual_payroll = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total annual payroll, 2022 ($1,000)", null=True
    )
    total_employment_percent_change = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Employment percent change (2021-2022)", null=True
    )
    total_nonemployer_establishments = models.BigIntegerField(
        help_text="Total nonemployer establishments, 2022", null=True
    )
    all_employer_firms = models.BigIntegerField(help_text="All employer firms, 2022", null=True)
    men_owned_employer_firms = models.CharField(
        max_length=10, null=True, blank=True, help_text="Men-owned employer firms, 2022"
    )
    women_owned_employer_firms = models.BigIntegerField(
        null=True, blank=True, help_text="Women-owned employer firms, 2022"
    )
    minority_owned_employer_firms = models.CharField(
        max_length=10, null=True, blank=True, help_text="Minority-owned employer firms, 2022"
    )
    nonminority_owned_employer_firms = models.CharField(
        max_length=10, null=True, blank=True, help_text="Nonminority-owned employer firms, 2022"
    )
    veteran_owned_employer_firms = models.CharField(
        max_length=10, null=True, blank=True, help_text="Veteran-owned employer firms, 2022"
    )
    nonveteran_owned_employer_firms = models.CharField(
        max_length=10, null=True, blank=True, help_text="Nonveteran-owned employer firms, 2022"
    )


class CensusGeography(BaseTimeStampedUUIDModel):
    population_per_sq_mile_2020 = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Population per sq mile, 2020", null=True
    )
    population_per_sq_mile_2010 = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Population per sq mile, 2010", null=True
    )
    land_area_sq_miles_2020 = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Land area, sq miles, 2020", null=True
    )
    land_area_sq_miles_2010 = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Land area, sq miles, 2010", null=True
    )
    fips_code = models.CharField(max_length=10, help_text="FIPS Code")

    def __str__(self):
        return f"Geography (FIPS: {self.fips_code})"


class CensusSocioEconomicProfile(BaseTimeStampedUUIDModel):
    # Housing
    housing_units_v2023 = models.BigIntegerField(help_text="Housing Units, July 1, 2023 (V2023)", null=True)
    owner_occupied_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Owner-occupied housing unit rate, 2019-2023 (%)", null=True
    )
    median_owner_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        help_text="Median value of owner-occupied housing units, 2019-2023 (in dollars)",
    )
    median_owner_cost_with_mortgage = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Median monthly owner cost with mortgage, 2019-2023 (in dollars)",
        null=True,
    )
    median_owner_cost_without_mortgage = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Median monthly owner cost without mortgage, 2019-2023 (in dollars)",
        null=True,
    )
    median_gross_rent = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Median gross rent, 2019-2023 (in dollars)", null=True
    )
    building_permits = models.BigIntegerField(help_text="Building Permits, 2023", null=True)

    # Families & Living Arrangements
    households = models.BigIntegerField(help_text="Households, 2019-2023", null=True)
    persons_per_household = models.DecimalField(
        max_digits=4, decimal_places=2, help_text="Persons per household, 2019-2023", null=True
    )
    same_house_living_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percent of persons living in the same house 1 year ago, 2019-2023",
        null=True,
    )
    language_non_english_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percent speaking a language other than English at home (age 5+), 2019-2023",
        null=True,
    )

    # Computer and Internet Use
    households_with_computer_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Households with a computer, percent, 2019-2023", null=True
    )
    households_with_broadband_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Households with a broadband Internet subscription, percent, 2019-2023",
        null=True,
    )

    # Education
    high_school_grad_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="High school graduate or higher, percent (age 25+), 2019-2023",
        null=True,
    )
    bachelors_degree_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Bachelor's degree or higher, percent (age 25+), 2019-2023", null=True
    )

    # Health
    disability_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percent with a disability (under age 65), 2019-2023", null=True
    )
    no_health_insurance_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percent without health insurance (under age 65)", null=True
    )

    # Economy
    civilian_labor_force_total_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Total civilian labor force, percent (age 16+), 2019-2023", null=True
    )
    civilian_labor_force_female_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Female civilian labor force, percent (age 16+), 2019-2023", null=True
    )
    total_accommodation_food_sales = models.BigIntegerField(
        help_text="Total accommodation and food services sales, 2022 ($1,000)", null=True
    )
    total_health_care_revenue = models.BigIntegerField(
        help_text="Total health care and social assistance receipts, 2022 ($1,000)", null=True
    )
    total_transportation_revenue = models.BigIntegerField(
        help_text="Total transportation and warehousing receipts, 2022 ($1,000)", null=True
    )
    total_retail_sales = models.BigIntegerField(help_text="Total retail sales, 2022 ($1,000)", null=True)
    total_retail_sales_per_capita = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total retail sales per capita, 2022", null=True
    )

    # Transportation
    mean_travel_time = models.DecimalField(
        max_digits=4, decimal_places=1, help_text="Mean travel time to work (minutes), 2019-2023", null=True
    )

    # Income & Poverty
    median_household_income = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Median household income (in 2023 dollars), 2019-2023", null=True
    )
    per_capita_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Per capita income in past 12 months (in 2023 dollars), 2019-2023",
        null=True,
    )
    persons_in_poverty_percent = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percent of persons in poverty", null=True
    )

    def __str__(self):
        return f"Census Socio-Economic Profile ({self.id})"


class CensusProfile(BaseTimeStampedUUIDModel):
    year = models.PositiveIntegerField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    population = models.ForeignKey("CensusPopulation", on_delete=models.CASCADE, null=True, blank=True)
    demographics = models.ForeignKey("CensusDemographics", on_delete=models.CASCADE, null=True, blank=True)
    business = models.ForeignKey("CensusBusiness", on_delete=models.CASCADE, null=True, blank=True)
    geography = models.ForeignKey("CensusGeography", on_delete=models.CASCADE, null=True, blank=True)
    socio_economic = models.ForeignKey("CensusSocioEconomicProfile", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Census Profile for {self.content_object}"

    @property
    def region(self):
        return self.content_object

    @property
    def name(self):
        return self.content_object.name

    @property
    def quick_fact_slug(self):
        return self.content_object.quick_fact_slug
