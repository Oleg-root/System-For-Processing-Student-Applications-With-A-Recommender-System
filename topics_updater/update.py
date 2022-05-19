from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from topics_updater import updater

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(updater.execute(), 'interval', minutes=10080) # that's a week in minutes
    scheduler.start()