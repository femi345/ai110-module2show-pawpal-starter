"""
pawpal_system.py — PawPal+ logic layer.

Classes: Task, Pet, Owner, Scheduler
All scheduling algorithms live in Scheduler so the UI and tests can import
a single, coherent object.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Literal, Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

FrequencyT = Literal["once", "daily", "weekly"]
PriorityT = Literal["low", "medium", "high"]


@dataclass
class Task:
    """A single pet-care activity with scheduling metadata."""

    description: str
    time: str  # "HH:MM" 24-hour format
    duration_minutes: int
    frequency: FrequencyT = "once"
    priority: PriorityT = "medium"
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # ------------------------------------------------------------------
    def mark_complete(self) -> Optional["Task"]:
        """Mark the task done and return a new Task for the next recurrence.

        Returns None for one-off tasks, or a fresh Task scheduled for the
        next due date for daily/weekly tasks.
        """
        self.completed = True
        if self.frequency == "daily":
            return Task(
                description=self.description,
                time=self.time,
                duration_minutes=self.duration_minutes,
                frequency=self.frequency,
                priority=self.priority,
                due_date=self.due_date + timedelta(days=1),
            )
        if self.frequency == "weekly":
            return Task(
                description=self.description,
                time=self.time,
                duration_minutes=self.duration_minutes,
                frequency=self.frequency,
                priority=self.priority,
                due_date=self.due_date + timedelta(weeks=1),
            )
        return None

    # ------------------------------------------------------------------
    def __str__(self) -> str:
        status = "[done]" if self.completed else "[pending]"
        freq_tag = f"[{self.frequency}]" if self.frequency != "once" else ""
        return (
            f"{status} {self.time}  {self.description} "
            f"({self.duration_minutes}min, {self.priority}) {freq_tag}".strip()
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------


@dataclass
class Pet:
    """A pet belonging to an owner, with its own list of care tasks."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    # ------------------------------------------------------------------
    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    # ------------------------------------------------------------------
    def remove_task(self, task_id: str) -> bool:
        """Remove a task by its id. Returns True if found and removed."""
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        return len(self.tasks) < before

    # ------------------------------------------------------------------
    def task_count(self) -> int:
        """Return the total number of tasks registered for this pet."""
        return len(self.tasks)

    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return f"{self.name} ({self.species})"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------


class Owner:
    """Represents the pet owner who manages one or more pets."""

    def __init__(self, name: str) -> None:
        """Initialise with the owner's name and an empty pet list."""
        self.name = name
        self.pets: List[Pet] = []

    # ------------------------------------------------------------------
    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to the owner's household."""
        self.pets.append(pet)

    # ------------------------------------------------------------------
    def remove_pet(self, pet_name: str) -> bool:
        """Remove the first pet whose name matches. Returns True if removed."""
        before = len(self.pets)
        self.pets = [p for p in self.pets if p.name != pet_name]
        return len(self.pets) < before

    # ------------------------------------------------------------------
    def get_all_tasks(self) -> List[tuple[Pet, Task]]:
        """Return every (Pet, Task) pair across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return f"Owner: {self.name} | Pets: {len(self.pets)}"


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


class Scheduler:
    """The brain of PawPal+: retrieves, sorts, filters, and validates tasks."""

    def __init__(self, owner: Owner) -> None:
        """Bind the scheduler to an owner so it can traverse their pets."""
        self.owner = owner

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------

    def all_tasks(self) -> List[tuple[Pet, Task]]:
        """Return all (Pet, Task) pairs from the owner."""
        return self.owner.get_all_tasks()

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def sort_by_time(self, pairs: Optional[List[tuple[Pet, Task]]] = None) -> List[tuple[Pet, Task]]:
        """Sort (Pet, Task) pairs chronologically by task time (HH:MM).

        When pairs is None the full owner task list is used.
        """
        source = pairs if pairs is not None else self.all_tasks()
        return sorted(source, key=lambda pt: pt[1].time)

    def sort_by_priority(self, pairs: Optional[List[tuple[Pet, Task]]] = None) -> List[tuple[Pet, Task]]:
        """Sort by priority (high → medium → low), then by time as a tiebreaker."""
        source = pairs if pairs is not None else self.all_tasks()
        return sorted(
            source,
            key=lambda pt: (_PRIORITY_RANK[pt[1].priority], pt[1].time),
        )

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        due_date: Optional[date] = None,
    ) -> List[tuple[Pet, Task]]:
        """Return a filtered list of (Pet, Task) pairs.

        Any combination of pet_name, completion status, and due_date may be
        supplied; unset filters are ignored.
        """
        results = self.all_tasks()
        if pet_name is not None:
            results = [(p, t) for p, t in results if p.name.lower() == pet_name.lower()]
        if completed is not None:
            results = [(p, t) for p, t in results if t.completed == completed]
        if due_date is not None:
            results = [(p, t) for p, t in results if t.due_date == due_date]
        return results

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self) -> List[str]:
        """Scan for tasks across all pets that share the exact same time slot.

        Returns a list of human-readable warning strings (empty list = no conflicts).
        Complexity: O(n²) on task count — acceptable for typical household sizes.
        """
        pairs = self.all_tasks()
        warnings: List[str] = []
        seen: dict[str, list[tuple[Pet, Task]]] = {}
        for pet, task in pairs:
            key = task.time
            seen.setdefault(key, []).append((pet, task))
        for time_slot, group in seen.items():
            if len(group) > 1:
                labels = ", ".join(f"{p.name}→{t.description}" for p, t in group)
                warnings.append(f"Conflict at {time_slot}: {labels}")
        return warnings

    # ------------------------------------------------------------------
    # Recurring task management
    # ------------------------------------------------------------------

    def mark_task_complete(self, pet: Pet, task: Task) -> Optional[Task]:
        """Mark a task complete and, if recurring, append the next instance to the pet.

        Returns the newly created follow-up Task, or None for one-off tasks.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task

    # ------------------------------------------------------------------
    # Daily schedule
    # ------------------------------------------------------------------

    def todays_schedule(self) -> List[tuple[Pet, Task]]:
        """Return today's incomplete tasks sorted chronologically by time."""
        today = date.today()
        pending = self.filter_tasks(completed=False, due_date=today)
        return self.sort_by_time(pending)

    # ------------------------------------------------------------------
    # Formatted output
    # ------------------------------------------------------------------

    def format_schedule(self, pairs: Optional[List[tuple[Pet, Task]]] = None) -> str:
        """Render a schedule as a readable multi-line string for the terminal."""
        source = pairs if pairs is not None else self.todays_schedule()
        if not source:
            return "No tasks scheduled."
        lines = ["Today's PawPal+ Schedule", "=" * 40]
        for pet, task in source:
            lines.append(f"  [{pet.name}]  {task}")
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("")
            lines.extend(conflicts)
        return "\n".join(lines)
