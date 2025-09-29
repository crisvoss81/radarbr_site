from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Roda publicações automáticas periodicamente"

    def add_arguments(self, parser):
        parser.add_argument("--every", default="*/15")   # minutos
        parser.add_argument("--limit", type=int, default=5)

    def handle(self, *args, **opts):
        sched = BlockingScheduler(timezone="America/Sao_Paulo")
        def job():
            self.stdout.write("⏱  trends_publish…")
            call_command("trends_publish", limit=opts["limit"])
        trig = CronTrigger.from_crontab(f"{opts['every']} * * * *")
        sched.add_job(job, trig, id="trends_publish", replace_existing=True)
        self.stdout.write(self.style.SUCCESS(f"Scheduler ON – a cada {opts['every']} min"))
        try:
            sched.start()
        except (KeyboardInterrupt, SystemExit):
            pass
