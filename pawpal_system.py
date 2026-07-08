from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_FREQUENCIES = {"daily", "weekly", "as-needed"}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"       # "low", "medium", or "high"
    category: str = "general"
    description: str = ""
    frequency: str = "daily"       # "daily", "weekly", or "as-needed"
    completed: bool = False
    due_date: Optional[date] = None
    start_time: Optional[str] = None   # "HH:MM" — used for manual conflict detection

    def __post_init__(self) -> None:
        """Validate priority and frequency values on construction."""
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got '{self.priority}'")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {VALID_FREQUENCIES}, got '{self.frequency}'")

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        return self.priority == "high"

    def mark_complete(self) -> None:
        """Mark this task as done for today."""
        self.completed = True

    def reset(self) -> None:
        """Clear completion status so the task appears in tomorrow's plan."""
        self.completed = False


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list, init=False)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def list_tasks(self) -> list[Task]:
        """Return a copy of all tasks (completed and pending)."""
        return list(self.tasks)

    def pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed yet."""
        return [t for t in self.tasks if not t.completed]

    def completed_tasks(self) -> list[Task]:
        """Return only tasks that have been marked complete."""
        return [t for t in self.tasks if t.completed]


@dataclass
class Owner:
    name: str
    available_minutes: int = 120
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list, init=False)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def list_pets(self) -> list[Pet]:
        """Return a copy of all pets belonging to this owner."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.list_tasks())
        return all_tasks

    def set_available_time(self, minutes: int) -> None:
        """Update how many minutes the owner has free today."""
        self.available_minutes = minutes


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner, start_hour: int = 8):
        """Initialize with an owner and the hour the schedule should begin."""
        self.owner = owner
        self.start_hour = start_hour

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get_all_pending(self) -> list[tuple[Task, Pet]]:
        """Collect every incomplete task from all of the owner's pets."""
        result = []
        for pet in self.owner.list_pets():
            for task in pet.pending_tasks():
                result.append((task, pet))
        return result

    # ── Sorting ───────────────────────────────────────────────────────────────

    def sort_by_priority(
        self, pairs: list[tuple[Task, Pet]]
    ) -> list[tuple[Task, Pet]]:
        """Sort task-pet pairs from highest to lowest priority."""
        return sorted(pairs, key=lambda tp: PRIORITY_ORDER.get(tp[0].priority, 99))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by their start_time (HH:MM) ascending; untimed tasks go last."""
        def time_key(t: Task) -> tuple[int, int]:
            if t.start_time is None:
                return (999, 999)
            h, m = map(int, t.start_time.split(":"))
            return (h, m)
        return sorted(tasks, key=time_key)

    # ── Filtering ─────────────────────────────────────────────────────────────

    def filter_by_time(
        self, pairs: list[tuple[Task, Pet]]
    ) -> list[tuple[Task, Pet]]:
        """Keep tasks in order until the owner's available time is used up."""
        selected, time_used = [], 0
        for task, pet in pairs:
            if time_used + task.duration_minutes <= self.owner.available_minutes:
                selected.append((task, pet))
                time_used += task.duration_minutes
        return selected

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[tuple[Task, Pet]]:
        """Return tasks filtered by optional pet name and/or completion status."""
        result = []
        for pet in self.owner.list_pets():
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.list_tasks():
                if completed is not None and task.completed != completed:
                    continue
                result.append((task, pet))
        return result

    # ── Core scheduling ───────────────────────────────────────────────────────

    def build_plan(self) -> list[tuple[Task, Pet]]:
        """Build today's schedule: sort by priority then cut by available time."""
        pending = self._get_all_pending()
        sorted_pairs = self.sort_by_priority(pending)
        return self.filter_by_time(sorted_pairs)

    def detect_conflicts(self, plan: list[tuple[Task, Pet]]) -> list[str]:
        """Return warning strings for tasks whose manual start_time windows overlap."""
        timed = []
        for task, pet in plan:
            if task.start_time:
                h, m = map(int, task.start_time.split(":"))
                start_min = h * 60 + m
                end_min = start_min + task.duration_minutes
                timed.append((start_min, end_min, task, pet))

        warnings = []
        for i, (s1, e1, t1, p1) in enumerate(timed):
            for s2, e2, t2, p2 in timed[i + 1:]:
                if s1 < e2 and s2 < e1:
                    warnings.append(
                        f"Conflict: '{t1.title}' ({p1.name}, "
                        f"{t1.start_time}-{e1 // 60:02d}:{e1 % 60:02d}) overlaps "
                        f"'{t2.title}' ({p2.name}, "
                        f"{t2.start_time}-{e2 // 60:02d}:{e2 % 60:02d})"
                    )
        return warnings

    def reschedule_recurring(self, task: Task, pet: Pet) -> Optional[Task]:
        """Mark task complete and add a new copy for its next due date if recurring."""
        task.mark_complete()
        today = date.today()
        if task.frequency == "daily":
            next_due = today + timedelta(days=1)
        elif task.frequency == "weekly":
            next_due = today + timedelta(weeks=1)
        else:
            return None  # "as-needed" tasks do not auto-recur

        next_task = Task(
            title=task.title,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            category=task.category,
            description=task.description,
            frequency=task.frequency,
            due_date=next_due,
        )
        pet.add_task(next_task)
        return next_task

    def mark_complete(self, task: Task) -> None:
        """Delegate completion marking to the task itself."""
        task.mark_complete()

    def reset_all(self) -> None:
        """Reset every task across all pets (call at the start of a new day)."""
        for task in self.owner.get_all_tasks():
            task.reset()

    # ── Output ────────────────────────────────────────────────────────────────

    def explain_plan(self, plan: list[tuple[Task, Pet]]) -> str:
        """Format the plan as a human-readable schedule string."""
        if not plan:
            return (
                f"No tasks fit within {self.owner.available_minutes} minutes today. "
                "Try adding shorter tasks or increasing available time."
            )

        lines = [
            f"=== Today's Schedule for {self.owner.name} ===",
            f"Available time: {self.owner.available_minutes} min  |  "
            f"Starting at {self.start_hour:02d}:00\n",
        ]

        time_cursor = self.start_hour * 60
        for task, pet in plan:
            hours, mins = divmod(time_cursor, 60)
            status = "[done]" if task.completed else "[    ]"
            lines.append(
                f"  {status} {hours:02d}:{mins:02d}  {task.title} -- {pet.name}"
                f"  ({task.duration_minutes} min, {task.priority} priority)"
            )
            if task.description:
                lines.append(f"              {task.description}")
            time_cursor += task.duration_minutes

        total = sum(t.duration_minutes for t, _ in plan)
        skipped = len(self._get_all_pending()) - len(plan)
        lines.append(f"\nTotal scheduled: {total} min")
        if skipped:
            lines.append(f"Tasks skipped (not enough time): {skipped}")
        return "\n".join(lines)
