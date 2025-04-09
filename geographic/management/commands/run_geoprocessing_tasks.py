from django.core.management.base import BaseCommand

from geographic.tasks import (
    import_msas_from_shapefile_task,
    import_states_from_shapefile_task,
    import_counties_from_shapefile_task,
    import_cities_from_place_zips_task,
    update_populations_for_states_task,
    update_populations_for_counties_task,
    update_populations_for_cities_task,
)


class Command(BaseCommand):
    help = "Enqueue geospatial import and population update tasks via Celery."

    def handle(self, *args, **options):
        self.stdout.write("Enqueuing import tasks...")

        import_msas_from_shapefile_task.delay()
        import_states_from_shapefile_task.delay()
        import_counties_from_shapefile_task.delay()
        import_cities_from_place_zips_task.delay()
        update_populations_for_states_task.delay()
        update_populations_for_counties_task.delay()
        update_populations_for_cities_task.delay()

        self.stdout.write("All tasks have been enqueued.")
