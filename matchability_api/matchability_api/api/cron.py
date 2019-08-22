from django.conf import settings
from django_cron import CronJobBase, Schedule


class TrainModel(CronJobBase):
    RUN_EVERY_MINS = 1 if settings.DEBUG else 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'Update the Training Model'

    def do(self):
        exec(open("matchability_lib/matcha.py").read(), globals())
