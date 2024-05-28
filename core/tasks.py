from celery import shared_task

from .controllers.Google import sync_sheets


@shared_task
def celery_sync_sheets():
    sync_sheets.sync_sheets()


@shared_task
def store_sheets_leads(data: dict, first_time: bool = False):
    sync_sheets.store_rows_in_db(data, first_time)
