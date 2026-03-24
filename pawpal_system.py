from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
import uuid
import json
import os


# ══════════════════════════════════════════════════════════════
# TASK
# ══════════════════════════════════════════════════════════════

@dataclass
class Task:
    """
    Represents a single pet care activity.

    Attributes
    ----------
    description : Human-readable label, e.g. "Morning walk"
    due_time    : 24-hour time string "HH:MM", e.g. "08:30"
    due_date    : ISO date string "YYYY-MM-DD", e.g. "2025-06-01"
    frequency   : "once" | "daily" | "weekly"
    priority    : "low" | "medium" | "high"
    completed   : Whether the task has been marked done
    task_type   : "walk" | "feeding" | "medication" | "vet" | "general"
    task_id     : Unique identifier — auto-generated via uuid so two tasks
                  with the same description can still be told apart.
    """

    description: str
    due_time:    str
    due_date:    str
    frequency:   str  = "once"
    priority:    str  = "medium"
    completed:   bool = False
    task_type:   str  = "general"
    task_id:     str  = field(default_factory=lambda: str(uuid.uuid4()))

    def mark_complete(self) -> str:
        """Set completed = True and return a confirmation message."""
        self.completed = True
        return f"✅ '{self.description}' marked complete!"

    def reschedule(self) -> Optional["Task"]:
        """
        If this is a recurring task, build and return the next Task.
        Returns None for one-time tasks.

        Uses timedelta so month and year rollovers are handled automatically.
        Daily  → tomorrow  (current date + 1 day)
        Weekly → next week (current date + 7 days)
        """
        if self.frequency == "once":
            return None

        current   = date.fromisoformat(self.due_date)
        delta     = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        next_date = current + delta

        return Task(
            description=self.description,
            due_time=self.due_time,
            due_date=str(next_date),
            frequency=self.frequency,
            priority=self.priority,
            completed=False,
            task_type=self.task_type,
        )

    def to_dict(self) -> dict:
        """Convert to a plain dict — useful for saving and printing."""
        return {
            "description": self.description,
            "due_time":    self.due_time,
            "due_date":    self.due_date,
            "frequency":   self.frequency,
            "priority":    self.priority,
            "completed":   self.completed,
            "task_type":   self.task_type,
            "task_id":     self.task_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Recreate a Task from a plain dict."""
        return cls(
            description=data["description"],
            due_time=data["due_time"],
            due_date=data["due_date"],
            frequency=data.get("frequency", "once"),
            priority=data.get("priority",   "medium"),
            completed=data.get("completed", False),
            task_type=data.get("task_type", "general"),
            task_id=data.get("task_id",     str(uuid.uuid4())),
        )

    def emoji(self) -> str:
        """Return a task-type emoji for readable output."""
        return {
            "walk":       "🐾",
            "feeding":    "🍖",
            "medication": "💊",
            "vet":        "🏥",
            "general":    "📋",
        }.get(self.task_type, "📋")

    def priority_emoji(self) -> str:
        """Return a colour-coded circle matching the priority level."""
        return {
            "high":   "🔴",
            "medium": "🟡",
            "low":    "🟢",
        }.get(self.priority, "⚪")


# ══════════════════════════════════════════════════════════════
# PET
# ══════════════════════════════════════════════════════════════

@dataclass
class Pet:
    """
    Represents a pet and its collection of care tasks.

    field(default_factory=list) is used for tasks so each Pet instance
    gets its own fresh list — avoids the Python shared-default-list bug.
    """

    name:    str
    species: str
    breed:   str
    age:     int
    tasks:   list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's schedule."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """
        Remove the first task whose description matches (case-insensitive).
        Returns True if removed, False if not found.
        """
        for task in self.tasks:
            if task.description.lower() == description.lower():
                self.tasks.remove(task)
                return True
        return False

    def remove_task_by_id(self, task_id: str) -> bool:
        """
        Remove a task by its unique task_id.
        More reliable than description matching when two tasks share a label.
        """
        for task in self.tasks:
            if task.task_id == task_id:
                self.tasks.remove(task)
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> list[Task]:
        """Return all tasks already completed."""
        return [t for t in self.tasks if t.completed]

    def task_count(self) -> int:
        """Total number of tasks — completed and pending combined."""
        return len(self.tasks)

    def species_emoji(self) -> str:
        """Return an emoji matching this pet's species."""
        return {
            "dog":    "🐶",
            "cat":    "🐱",
            "rabbit": "🐰",
            "bird":   "🐦",
            "fish":   "🐠",
        }.get(self.species.lower(), "🐾")

    def to_dict(self) -> dict:
        """Serialize to a plain dict."""
        return {
            "name":    self.name,
            "species": self.species,
            "breed":   self.breed,
            "age":     self.age,
            "tasks":   [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Recreate a Pet from a plain dict."""
        pet = cls(
            name=data["name"],
            species=data["species"],
            breed=data["breed"],
            age=data["age"],
        )
        pet.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return pet


# ══════════════════════════════════════════════════════════════
# OWNER
# ══════════════════════════════════════════════════════════════

class Owner:
    """
    Top-level data store.
    Holds a collection of Pet objects and provides get_all_tasks(),
    which gives the Scheduler a flat view of every task across every pet.
    Also handles saving and loading data so it survives app restarts.
    """

    def __init__(self, name: str, email: str = ""):
        """Initialise an Owner with an empty pets list."""
        self.name:  str       = name
        self.email: str       = email
        self.pets:  list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's household."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name (case-insensitive). Returns True if removed."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                self.pets.remove(pet)
                return True
        return False

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Find and return a Pet by name, or None if not found."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """
        Return every task across every pet as (pet_name, Task) tuples.
        This is the single data-access point the Scheduler uses —
        keeping pet context attached to each task without coupling
        Scheduler directly to individual Pet objects.
        """
        result: list[tuple[str, Task]] = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append((pet.name, task))
        return result

    def pet_count(self) -> int:
        """How many pets does this owner have?"""
        return len(self.pets)

    def save_to_json(self, filepath: str = "data.json") -> None:
        """
        Serialise the entire owner → pets → tasks tree to a JSON file.
        Creates parent directories automatically if needed.
        """
        data = {
            "owner": {
                "name":  self.name,
                "email": self.email,
                "pets":  [p.to_dict() for p in self.pets],
            }
        }
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(filepath, "w") as fh:
            json.dump(data, fh, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> Optional["Owner"]:
        """
        Load owner data from a JSON file.
        Returns None instead of crashing if the file does not exist yet.
        """
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r") as fh:
            data = json.load(fh)
        od    = data["owner"]
        owner = cls(name=od["name"], email=od.get("email", ""))
        owner.pets = [Pet.from_dict(p) for p in od.get("pets", [])]
        return owner

    def to_dict(self) -> dict:
        """Convert to a plain dict."""
        return {
            "name":  self.name,
            "email": self.email,
            "pets":  [p.to_dict() for p in self.pets],
        }


# ══════════════════════════════════════════════════════════════
# SCHEDULER
# ══════════════════════════════════════════════════════════════

# Numeric rank used as a sort key — higher number = more urgent
_PRIORITY_RANK: dict[str, int] = {"high": 3, "medium": 2, "low": 1}


class Scheduler:
    """
    The algorithmic brain of PawPal+.
    Receives an Owner at construction time.
    Does not store data — only reads from Owner and returns results.
    """

    def __init__(self, owner: Owner):
        """Attach this Scheduler to a specific Owner."""
        self.owner = owner

    # ── SORTING ───────────────────────────────────────────────

    def sort_by_time(
        self, tasks: list[tuple[str, Task]] | None = None
    ) -> list[tuple[str, Task]]:
        """
        Sort tasks chronologically by due_time.
        Zero-padded HH:MM strings sort correctly with plain string
        comparison, so no datetime parsing is needed.
        """
        task_list = tasks if tasks is not None else self.owner.get_all_tasks()
        return sorted(task_list, key=lambda pair: pair[1].due_time)

    def sort_by_priority(
        self, tasks: list[tuple[str, Task]] | None = None
    ) -> list[tuple[str, Task]]:
        """
        Sort tasks high → medium → low.
        Within the same priority tier, sub-sort by time.
        Composite key: (-priority_rank, due_time).
        Negating the rank makes high sort first with ascending order.
        """
        task_list = tasks if tasks is not None else self.owner.get_all_tasks()
        return sorted(
            task_list,
            key=lambda pair: (
                -_PRIORITY_RANK.get(pair[1].priority, 0),
                pair[1].due_time,
            ),
        )

    def sort_by_priority_then_time(
        self, tasks: list[tuple[str, Task]] | None = None
    ) -> list[tuple[str, Task]]:
        """Sort by priority first, then time as a tiebreaker within each tier."""
        return self.sort_by_priority(tasks)

    # ── FILTERING ─────────────────────────────────────────────

    def filter_by_pet(self, pet_name: str) -> list[tuple[str, Task]]:
        """Return only tasks that belong to the named pet."""
        return [
            (name, task)
            for name, task in self.owner.get_all_tasks()
            if name.lower() == pet_name.lower()
        ]

    def filter_by_status(self, completed: bool) -> list[tuple[str, Task]]:
        """Return only completed tasks (True) or only pending tasks (False)."""
        return [
            (name, task)
            for name, task in self.owner.get_all_tasks()
            if task.completed == completed
        ]

    def filter_by_date(self, target_date: str) -> list[tuple[str, Task]]:
        """Return tasks whose due_date matches target_date (YYYY-MM-DD)."""
        return [
            (name, task)
            for name, task in self.owner.get_all_tasks()
            if task.due_date == target_date
        ]

    def filter_by_priority(self, priority: str) -> list[tuple[str, Task]]:
        """Return tasks of a specific priority level."""
        return [
            (name, task)
            for name, task in self.owner.get_all_tasks()
            if task.priority.lower() == priority.lower()
        ]

    def get_todays_tasks(self) -> list[tuple[str, Task]]:
        """Return today's tasks sorted by priority then time."""
        todays = self.filter_by_date(str(date.today()))
        return self.sort_by_priority_then_time(todays)

    # ── CONFLICT DETECTION ────────────────────────────────────

    def detect_conflicts(self) -> list[str]:
        """
        Scan every task and flag any two tasks sharing the same
        (due_date, due_time) slot.

        Uses a single-pass dictionary — each slot key maps to a list
        of (pet_name, description) entries. Any key with 2+ entries
        is a conflict. Returns warning strings, never raises.
        """
        groups: dict[tuple, list] = {}
        for pet_name, task in self.owner.get_all_tasks():
            slot = (task.due_date, task.due_time)
            groups.setdefault(slot, []).append((pet_name, task.description))

        warnings = []
        for (t_date, t_time), entries in groups.items():
            if len(entries) > 1:
                detail = ", ".join(f"{p}: '{d}'" for p, d in entries)
                warnings.append(
                    f"⚠️  CONFLICT  {t_date} @ {t_time}  →  {detail}"
                )
        return warnings

    # ── RECURRING TASKS ───────────────────────────────────────

    def mark_task_complete_and_reschedule(
        self, pet_name: str, task_description: str
    ) -> str:
        """
        Mark a task done. If it recurs (daily / weekly), automatically
        add the next occurrence to that pet's task list.
        Returns a status string — never raises an exception.
        """
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return f"❌ Pet '{pet_name}' not found."

        for task in pet.tasks:
            if (
                task.description.lower() == task_description.lower()
                and not task.completed
            ):
                task.mark_complete()
                next_task = task.reschedule()
                if next_task:
                    pet.add_task(next_task)
                    return (
                        f"✅ '{task.description}' done!  "
                        f"Next scheduled: {next_task.due_date} @ {next_task.due_time}"
                    )
                return f"✅ '{task.description}' complete (one-time task)."

        return f"❌ '{task_description}' not found for {pet_name}, or already complete."

    # ── NEXT AVAILABLE SLOT ───────────────────────────────────

    def find_next_available_slot(
        self, target_date: str, start_time: str = "07:00"
    ) -> str:
        """
        Find the first free 30-minute slot on target_date at or after start_time.

        Builds a set of all booked HH:MM times on that date (O(1) lookup),
        then walks candidate slots in 30-minute increments until a free one
        is found. Caps at 22:00 as an end-of-day fallback.
        """
        booked: set[str] = {
            task.due_time
            for _, task in self.filter_by_date(target_date)
        }
        hour, minute = map(int, start_time.split(":"))
        while hour < 22:
            candidate = f"{hour:02d}:{minute:02d}"
            if candidate not in booked:
                return candidate
            minute += 30
            if minute >= 60:
                minute = 0
                hour  += 1
        return "22:00"

    # ── PRIORITY-WEIGHTED SCHEDULE ────────────────────────────

    def build_priority_schedule(
        self, target_date: str, max_tasks: int = 10
    ) -> list[tuple[str, Task]]:
        """
        Return the top max_tasks pending tasks for target_date ranked by
        a weighted priority score.

        Scoring:
          high   → 30 pts
          medium → 20 pts
          low    → 10 pts
          +5 bonus if task_type is medication (never skip meds)

        Tasks with equal scores are sub-sorted by time.
        """
        candidates = [
            (pet_name, task)
            for pet_name, task in self.filter_by_date(target_date)
            if not task.completed
        ]

        def score(pair: tuple) -> int:
            _, task = pair
            pts = _PRIORITY_RANK.get(task.priority, 0) * 10
            if task.task_type == "medication":
                pts += 5
            return pts

        ranked = sorted(candidates, key=lambda p: (-score(p), p[1].due_time))
        return ranked[:max_tasks]

    # ── SUMMARY ───────────────────────────────────────────────

    def get_summary(self) -> dict:
        """Return a metrics dict for the dashboard."""
        all_tasks = self.owner.get_all_tasks()
        total     = len(all_tasks)
        done      = sum(1 for _, t in all_tasks if t.completed)
        hi_pend   = sum(
            1 for _, t in all_tasks
            if t.priority == "high" and not t.completed
        )
        return {
            "total":                 total,
            "completed":             done,
            "pending":               total - done,
            "high_priority_pending": hi_pend,
            "pets":                  self.owner.pet_count(),
        }