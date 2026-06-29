from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str          # "low", "medium", "high"
    category: str = "general"

    def is_high_priority(self) -> bool:
        return self.priority == "high"


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: list[str] = field(default_factory=list)
    _tasks: list[Task] = field(default_factory=list, repr=False)

    def add_task(self, task: Task) -> None:
        self._tasks.append(task)

    def list_tasks(self) -> list[Task]:
        return list(self._tasks)


@dataclass
class Owner:
    name: str
    available_minutes: int = 120
    preferences: list[str] = field(default_factory=list)
    _pets: list[Pet] = field(default_factory=list, repr=False)

    def add_pet(self, pet: Pet) -> None:
        self._pets.append(pet)

    def set_available_time(self, minutes: int) -> None:
        self.available_minutes = minutes


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: Optional[list[Task]] = None):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks if tasks is not None else pet.list_tasks()

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: order.get(t.priority, 99))

    def filter_by_time(self, tasks: list[Task]) -> list[Task]:
        selected, time_used = [], 0
        for task in tasks:
            if time_used + task.duration_minutes <= self.owner.available_minutes:
                selected.append(task)
                time_used += task.duration_minutes
        return selected

    def build_plan(self) -> list[Task]:
        sorted_tasks = self.sort_by_priority(self.tasks)
        return self.filter_by_time(sorted_tasks)

    def explain_plan(self, plan: list[Task]) -> str:
        if not plan:
            return f"No tasks fit within {self.owner.available_minutes} minutes today."

        lines = [
            f"Daily plan for {self.pet.name} ({self.pet.species}) — "
            f"{self.owner.available_minutes} min available:\n"
        ]
        time_cursor = 0
        for task in plan:
            hours, mins = divmod(time_cursor, 60)
            lines.append(
                f"  {hours:02d}:{mins:02d} — {task.title} "
                f"({task.duration_minutes} min) [priority: {task.priority}]"
            )
            time_cursor += task.duration_minutes

        total = sum(t.duration_minutes for t in plan)
        lines.append(f"\nTotal time scheduled: {total} min")
        return "\n".join(lines)
