# scheduler.py
import threading
import time
from datetime import datetime

def schedule_task(run_function, run_time_str, *args):
    """Run function at specific time"""
    run_time = datetime.strptime(run_time_str, "%Y-%m-%d %H:%M")
    now = datetime.now()
    delay = (run_time - now).total_seconds()

    if delay <= 0:
        print("Scheduled time is in the past!")
        return

    print(f"🕒 Task scheduled for {run_time_str}")

    timer = threading.Timer(delay, run_function, args)
    timer.start()
    return timer