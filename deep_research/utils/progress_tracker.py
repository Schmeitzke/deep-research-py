# deep_research/utils/progress_tracker.py

import time

class ProgressTracker:
    def __init__(self, total: int):
        self.total = total              # estimated total number of tasks
        self.completed = 0              # tasks completed so far
        self.start_time = time.time()   # timestamp when tracking began

    def update(self, count: int = 1):
        """Increment the count of completed tasks."""
        self.completed += count

    def get_progress(self):
        """Return a dict with percentage complete, elapsed time, and estimated remaining time."""
        elapsed = time.time() - self.start_time
        percent = (self.completed / self.total) * 100 if self.total > 0 else 100
        estimated_total = (elapsed / self.completed * self.total) if self.completed > 0 else 0
        remaining = estimated_total - elapsed if self.completed > 0 else 0
        return {
            "completed": self.completed,
            "total": self.total,
            "percentage": round(percent, 2),
            "elapsed": round(elapsed, 2),
            "remaining": round(remaining, 2),
        }
