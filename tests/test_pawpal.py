import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from pawpal_system import Owner, Pet, Task


# ══════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════

@pytest.fixture
def today() -> str:
    return str(date.today())

@pytest.fixture
def tomorrow() -> str:
    return str(date.today() + timedelta(days=1))

@pytest.fixture
def sample_task(today) -> Task:
    return Task(
        description="Morning walk",
        due_time="08:00",
        due_date=today,
        frequency="daily",
        priority="high",
        task_type="walk",
    )

@pytest.fixture
def sample_pet(sample_task) -> Pet:
    pet = Pet(name="Buddy", species="dog", breed="Labrador", age=3)
    pet.add_task(sample_task)
    return pet


# ══════════════════════════════════════════════════════════════
# TEST 1 — Task completion
# ══════════════════════════════════════════════════════════════

def test_mark_complete_changes_status(sample_task):
    """mark_complete() must flip completed from False to True."""
    assert sample_task.completed is False
    sample_task.mark_complete()
    assert sample_task.completed is True

def test_mark_complete_returns_message(sample_task):
    """mark_complete() should return a non-empty confirmation string."""
    result = sample_task.mark_complete()
    assert isinstance(result, str)
    assert len(result) > 0


# ══════════════════════════════════════════════════════════════
# TEST 2 — Adding tasks to a Pet
# ══════════════════════════════════════════════════════════════

def test_add_task_increases_count(today):
    """Each add_task() call should increase task_count() by 1."""
    pet = Pet(name="Luna", species="cat", breed="Persian", age=2)
    assert pet.task_count() == 0

    pet.add_task(Task("Feeding", "08:00", today, "daily", "high", task_type="feeding"))
    assert pet.task_count() == 1

    pet.add_task(Task("Playtime", "15:00", today, "daily", "low", task_type="general"))
    assert pet.task_count() == 2

def test_pet_tracks_pending_and_completed(today):
    """After marking one task done, pending and completed counts should update."""
    pet = Pet(name="Rex", species="dog", breed="Poodle", age=4)
    pet.add_task(Task("Walk", "08:00", today, "daily", "high", task_type="walk"))
    pet.add_task(Task("Feed", "09:00", today, "daily", "high", task_type="feeding"))

    assert len(pet.get_pending_tasks())   == 2
    assert len(pet.get_completed_tasks()) == 0

    pet.tasks[0].mark_complete()

    assert len(pet.get_pending_tasks())   == 1
    assert len(pet.get_completed_tasks()) == 1