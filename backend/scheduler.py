import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

log = logging.getLogger(__name__)


def start_scheduler():
    from src.retrain import run_full_retrain
    from src.predictor import reload_models

    def monthly_job():
        log.info("Scheduled monthly retrain triggered")
        run_full_retrain()
        reload_models()
        log.info("Scheduled monthly retrain complete")

    scheduler = BackgroundScheduler(timezone='UTC')

    # 1st of every month at 02:00 UTC
    scheduler.add_job(
        monthly_job,
        trigger=CronTrigger(day=1, hour=2, minute=0),
        id='monthly_retrain',
        name='Monthly model retrain',
        replace_existing=True,
        misfire_grace_time=None,   # never run missed jobs on startup — data stays as-is
    )

    scheduler.start()
    log.info("Scheduler started — next retrain: 1st of every month at 02:00 UTC")
    return scheduler
