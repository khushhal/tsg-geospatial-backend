import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from celery import shared_task
from django.contrib.contenttypes.models import ContentType

from census.models import CensusProfile
from census.parser import CensusQuickFactsParser
from geographic.models import State, County, City
from turl_street_group_assignment.settings import CENSUS_QUICKFACT_SCRAPED_YEAR

logger = logging.getLogger(__name__)


def scrape_census_data(model_class, parser_arg_name, threads=1, filter_by_population=False):
    failed_objects = []

    content_type = ContentType.objects.get_for_model(model_class)
    existing_profiles = CensusProfile.objects.filter(
        content_type=content_type, year=CENSUS_QUICKFACT_SCRAPED_YEAR
    ).values_list("object_id", flat=True)

    objects_to_process = model_class.objects.exclude(uuid__in=existing_profiles)

    if filter_by_population:
        objects_to_process = objects_to_process.filter(population__gt=4000)

    def process(obj):
        try:
            kwargs = {parser_arg_name: obj}
            created, _ = CensusQuickFactsParser(**kwargs).save()
            logger.info("%s ----> %s", obj.name, created)
            return None
        except Exception as e:
            logger.error("%s ----> %s", e, obj.name)
            return getattr(obj, "uuid", None)

    if threads > 1:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(process, obj): obj for obj in objects_to_process}
            for future in as_completed(futures):
                failed = future.result()
                if failed:
                    failed_objects.append(failed)
    else:
        for obj in objects_to_process:
            failed = process(obj)
            if failed:
                failed_objects.append(failed)

    return failed_objects


@shared_task
def scrape_census_data_for_states_task():
    scrape_census_data(State, parser_arg_name="state", threads=10)


@shared_task
def scrape_census_data_for_counties_task():
    scrape_census_data(County, parser_arg_name="county", threads=10)


@shared_task
def scrape_census_data_for_cities_task():
    scrape_census_data(City, parser_arg_name="city", threads=10, filter_by_population=True)
