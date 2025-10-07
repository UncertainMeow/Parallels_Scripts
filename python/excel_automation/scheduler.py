"""
Task scheduler for automated data pulls and Excel updates
"""

import schedule
import time
import signal
import sys
from typing import Callable, Dict, List, Optional
from datetime import datetime
from pathlib import Path
from .logger import setup_logger

logger = setup_logger(__name__)


class TaskScheduler:
    """Schedule and run automated tasks"""

    def __init__(self):
        """Initialize scheduler"""
        self.jobs: List[schedule.Job] = []
        self.running = False
        self.stop_requested = False

        # Set up signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_stop)
        signal.signal(signal.SIGTERM, self._handle_stop)

    def _handle_stop(self, signum, frame):
        """Handle stop signals gracefully"""
        logger.info("Stop signal received, shutting down gracefully...")
        self.stop_requested = True

    def add_job(
        self,
        func: Callable,
        schedule_str: str,
        name: Optional[str] = None,
        *args,
        **kwargs,
    ) -> schedule.Job:
        """
        Add a scheduled job.

        Args:
            func: Function to call
            schedule_str: Schedule string (cron-like)
            name: Job name for logging
            *args, **kwargs: Arguments to pass to function

        Returns:
            Schedule job instance

        Schedule string format:
            "every 1 hour"
            "every day at 08:00"
            "every monday at 09:00"
            "every 30 minutes"
        """
        job_name = name or func.__name__

        # Parse schedule string and create job
        job = self._parse_schedule(schedule_str, func, job_name, *args, **kwargs)

        if job:
            self.jobs.append(job)
            logger.info(f"✓ Scheduled job: {job_name} ({schedule_str})")
            return job
        else:
            raise ValueError(f"Invalid schedule string: {schedule_str}")

    def _parse_schedule(
        self, schedule_str: str, func: Callable, name: str, *args, **kwargs
    ) -> Optional[schedule.Job]:
        """Parse schedule string and create job"""

        # Wrap function to add logging
        def wrapped_func():
            try:
                logger.info(f"[{name}] Starting")
                start = time.time()

                result = func(*args, **kwargs)

                duration = time.time() - start
                logger.info(f"[{name}] Completed in {duration:.2f}s")

                return result

            except Exception as e:
                logger.error(f"[{name}] Failed: {e}", exc_info=True)
                raise

        # Parse common patterns
        parts = schedule_str.lower().strip().split()

        if not parts:
            return None

        # Handle "every X units"
        if parts[0] == "every":
            if len(parts) == 2:
                # "every hour", "every day", etc.
                unit = parts[1].rstrip('s')  # Remove plural s

                if unit == "hour":
                    return schedule.every().hour.do(wrapped_func)
                elif unit == "minute":
                    return schedule.every().minute.do(wrapped_func)
                elif unit == "day":
                    return schedule.every().day.do(wrapped_func)
                elif unit == "week":
                    return schedule.every().week.do(wrapped_func)
                elif unit in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                    return getattr(schedule.every(), unit).do(wrapped_func)

            elif len(parts) >= 3:
                # "every 30 minutes", "every 2 hours", etc.
                try:
                    interval = int(parts[1])
                    unit = parts[2].rstrip('s')

                    if unit == "hour":
                        return schedule.every(interval).hours.do(wrapped_func)
                    elif unit == "minute":
                        return schedule.every(interval).minutes.do(wrapped_func)
                    elif unit == "day":
                        return schedule.every(interval).days.do(wrapped_func)
                    elif unit == "week":
                        return schedule.every(interval).weeks.do(wrapped_func)

                except ValueError:
                    pass

            # Handle "every day at HH:MM"
            if len(parts) >= 4 and parts[2] == "at":
                time_str = parts[3]
                unit = parts[1]

                if unit == "day":
                    return schedule.every().day.at(time_str).do(wrapped_func)
                elif unit in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                    return getattr(schedule.every(), unit).at(time_str).do(wrapped_func)

        return None

    def run(self, run_pending_immediately: bool = False):
        """
        Run the scheduler (blocks until stopped).

        Args:
            run_pending_immediately: Run all jobs immediately on start
        """
        logger.info(f"Starting scheduler with {len(self.jobs)} job(s)")

        if run_pending_immediately:
            logger.info("Running all pending jobs immediately")
            schedule.run_all()

        self.running = True

        while self.running and not self.stop_requested:
            try:
                # Run pending jobs
                schedule.run_pending()

                # Sleep for a short interval
                time.sleep(1)

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break

            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)
                time.sleep(5)  # Brief pause before continuing

        self.running = False
        logger.info("Scheduler stopped")

    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler...")
        self.running = False

    def clear_jobs(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        self.jobs.clear()
        logger.info("All jobs cleared")

    def list_jobs(self) -> List[Dict[str, str]]:
        """
        List all scheduled jobs.

        Returns:
            List of job dictionaries with details
        """
        jobs_list = []

        for job in schedule.get_jobs():
            jobs_list.append(
                {
                    "next_run": str(job.next_run) if job.next_run else "N/A",
                    "interval": str(job.interval),
                    "unit": job.unit or "N/A",
                    "at_time": str(job.at_time) if job.at_time else "N/A",
                    "tags": ", ".join(job.tags) if job.tags else "N/A",
                }
            )

        return jobs_list

    def run_once(self):
        """Run all pending jobs once (useful for testing)"""
        logger.info("Running all jobs once")
        schedule.run_all()


def load_schedules_from_config(config: Dict) -> TaskScheduler:
    """
    Load scheduled tasks from configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Configured TaskScheduler instance

    Config format:
        automation:
          schedules:
            - name: "morning_refresh"
              cron: "every day at 08:00"
              task: "refresh_data"
              params: {...}
    """
    scheduler = TaskScheduler()

    schedules_config = config.get('automation', {}).get('schedules', [])

    if isinstance(schedules_config, dict):
        # Handle dict format (named schedules)
        for name, schedule_info in schedules_config.items():
            cron = schedule_info.get('cron')
            if not cron:
                logger.warning(f"Schedule '{name}' has no cron expression, skipping")
                continue

            # For now, just log the schedule
            # In a full implementation, this would map to actual task functions
            logger.info(f"Loaded schedule: {name} - {cron}")

    elif isinstance(schedules_config, list):
        # Handle list format
        for schedule_info in schedules_config:
            name = schedule_info.get('name', 'unnamed')
            cron = schedule_info.get('cron')

            if not cron:
                logger.warning(f"Schedule '{name}' has no cron expression, skipping")
                continue

            logger.info(f"Loaded schedule: {name} - {cron}")

    return scheduler
