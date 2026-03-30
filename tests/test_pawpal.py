"""
tests/test_pawpal.py — Automated test suite for PawPal+

Run with:  python -m pytest
"""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def today() -> date:
    return date.today()


@pytest.fixture
def simple_pet(today) -> Pet:
    """A pet with two tasks at different times."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task("Evening walk",  time="18:00", duration_minutes=30,
                      frequency="daily", priority="high", due_date=today))
    pet.add_task(Task("Morning walk",  time="07:30", duration_minutes=20,
                      frequency="daily", priority="high", due_date=today))
    return pet


@pytest.fixture
def owner_with_two_pets(today) -> Owner:
    """An owner who has a dog and a cat, each with tasks."""
    owner = Owner("Jordan")
    dog = Pet(name="Mochi", species="dog")
    cat = Pet(name="Luna",  species="cat")

    dog.add_task(Task("Morning walk",     time="07:30", duration_minutes=20,
                      frequency="daily",  priority="high",   due_date=today))
    dog.add_task(Task("Flea medication",  time="12:00", duration_minutes=5,
                      frequency="weekly", priority="high",   due_date=today))
    cat.add_task(Task("Breakfast feeding", time="07:30", duration_minutes=10,
                      frequency="daily",   priority="high",  due_date=today))
    cat.add_task(Task("Playtime",          time="17:00", duration_minutes=15,
                      frequency="daily",   priority="medium", due_date=today))

    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------


class TestTaskCompletion:
    def test_mark_complete_sets_flag(self, today):
        task = Task("Walk", time="08:00", duration_minutes=15, due_date=today)
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True

    def test_one_off_task_returns_none(self, today):
        task = Task("Vet visit", time="10:00", duration_minutes=60,
                    frequency="once", due_date=today)
        result = task.mark_complete()
        assert result is None

    def test_daily_recurrence_creates_next_day(self, today):
        task = Task("Feeding", time="08:00", duration_minutes=10,
                    frequency="daily", due_date=today)
        next_task = task.mark_complete()
        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=1)
        assert next_task.completed is False
        assert next_task.description == task.description

    def test_weekly_recurrence_creates_next_week(self, today):
        task = Task("Grooming", time="10:00", duration_minutes=45,
                    frequency="weekly", due_date=today)
        next_task = task.mark_complete()
        assert next_task is not None
        assert next_task.due_date == today + timedelta(weeks=1)

    def test_recurrence_preserves_attributes(self, today):
        task = Task("Meds", time="09:00", duration_minutes=5,
                    frequency="daily", priority="high", due_date=today)
        next_task = task.mark_complete()
        assert next_task.time == "09:00"
        assert next_task.priority == "high"
        assert next_task.frequency == "daily"


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------


class TestPet:
    def test_add_task_increases_count(self, today):
        pet = Pet(name="Rex", species="dog")
        assert pet.task_count() == 0
        pet.add_task(Task("Walk", time="08:00", duration_minutes=20, due_date=today))
        assert pet.task_count() == 1
        pet.add_task(Task("Feed", time="07:00", duration_minutes=5,  due_date=today))
        assert pet.task_count() == 2

    def test_remove_task_by_id(self, today):
        pet = Pet(name="Bella", species="cat")
        task = Task("Play", time="15:00", duration_minutes=10, due_date=today)
        pet.add_task(task)
        assert pet.task_count() == 1
        removed = pet.remove_task(task.id)
        assert removed is True
        assert pet.task_count() == 0

    def test_remove_nonexistent_task_returns_false(self):
        pet = Pet(name="Max", species="dog")
        assert pet.remove_task("nonexistent-id") is False

    def test_empty_pet_has_zero_tasks(self):
        pet = Pet(name="Ghost", species="cat")
        assert pet.task_count() == 0


# ---------------------------------------------------------------------------
# Owner tests
# ---------------------------------------------------------------------------


class TestOwner:
    def test_add_pet_increases_count(self):
        owner = Owner("Alex")
        assert len(owner.pets) == 0
        owner.add_pet(Pet(name="Buddy", species="dog"))
        assert len(owner.pets) == 1

    def test_get_all_tasks_aggregates_across_pets(self, today):
        owner = Owner("Sam")
        dog = Pet(name="Rover", species="dog")
        cat = Pet(name="Whiskers", species="cat")
        dog.add_task(Task("Walk",  time="08:00", duration_minutes=20, due_date=today))
        cat.add_task(Task("Feed",  time="07:00", duration_minutes=5,  due_date=today))
        cat.add_task(Task("Brush", time="09:00", duration_minutes=10, due_date=today))
        owner.add_pet(dog)
        owner.add_pet(cat)
        assert len(owner.get_all_tasks()) == 3


# ---------------------------------------------------------------------------
# Scheduler – sorting
# ---------------------------------------------------------------------------


class TestSchedulerSorting:
    def test_sort_by_time_returns_chronological_order(self, owner_with_two_pets):
        scheduler = Scheduler(owner_with_two_pets)
        sorted_pairs = scheduler.sort_by_time()
        times = [t.time for _, t in sorted_pairs]
        assert times == sorted(times), "Tasks are not in chronological order"

    def test_sort_by_time_handles_single_task(self, today):
        owner = Owner("Solo")
        pet = Pet(name="Dot", species="cat")
        pet.add_task(Task("Nap", time="14:00", duration_minutes=60, due_date=today))
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        result = scheduler.sort_by_time()
        assert len(result) == 1

    def test_sort_by_priority_high_first(self, today):
        owner = Owner("Pri")
        pet = Pet(name="Tag", species="dog")
        pet.add_task(Task("Low task",    time="10:00", duration_minutes=5,
                          priority="low",    due_date=today))
        pet.add_task(Task("High task",   time="10:01", duration_minutes=5,
                          priority="high",   due_date=today))
        pet.add_task(Task("Medium task", time="10:02", duration_minutes=5,
                          priority="medium", due_date=today))
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        priorities = [t.priority for _, t in scheduler.sort_by_priority()]
        assert priorities[0] == "high"
        assert priorities[-1] == "low"


# ---------------------------------------------------------------------------
# Scheduler – filtering
# ---------------------------------------------------------------------------


class TestSchedulerFiltering:
    def test_filter_by_pet_name(self, owner_with_two_pets):
        scheduler = Scheduler(owner_with_two_pets)
        luna_tasks = scheduler.filter_tasks(pet_name="Luna")
        assert all(p.name == "Luna" for p, _ in luna_tasks)
        assert len(luna_tasks) == 2

    def test_filter_by_completed_false(self, today):
        owner = Owner("Jo")
        pet = Pet(name="Ace", species="dog")
        done = Task("Old walk", time="06:00", duration_minutes=20,
                    completed=True, due_date=today)
        pending = Task("New walk", time="08:00", duration_minutes=20, due_date=today)
        pet.add_task(done)
        pet.add_task(pending)
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        incomplete = scheduler.filter_tasks(completed=False)
        assert all(not t.completed for _, t in incomplete)
        assert len(incomplete) == 1

    def test_filter_by_due_date(self, today):
        owner = Owner("Kim")
        pet = Pet(name="Bear", species="dog")
        pet.add_task(Task("Today task",    time="10:00", duration_minutes=10,
                          due_date=today))
        pet.add_task(Task("Tomorrow task", time="10:00", duration_minutes=10,
                          due_date=today + timedelta(days=1)))
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        todays = scheduler.filter_tasks(due_date=today)
        assert len(todays) == 1
        assert todays[0][1].description == "Today task"

    def test_filter_on_empty_owner_returns_empty(self):
        scheduler = Scheduler(Owner("Empty"))
        assert scheduler.filter_tasks(pet_name="Nobody") == []


# ---------------------------------------------------------------------------
# Scheduler – conflict detection
# ---------------------------------------------------------------------------


class TestSchedulerConflicts:
    def test_conflict_detected_for_same_time(self, owner_with_two_pets):
        """Mochi and Luna both have 07:30 tasks — expect a warning."""
        scheduler = Scheduler(owner_with_two_pets)
        warnings = scheduler.detect_conflicts()
        assert len(warnings) == 1
        assert "07:30" in warnings[0]

    def test_no_conflict_when_times_differ(self, today):
        owner = Owner("Peaceful")
        dog = Pet(name="Calm", species="dog")
        cat = Pet(name="Chill", species="cat")
        dog.add_task(Task("Walk",  time="08:00", duration_minutes=20, due_date=today))
        cat.add_task(Task("Feed",  time="09:00", duration_minutes=5,  due_date=today))
        owner.add_pet(dog)
        owner.add_pet(cat)
        scheduler = Scheduler(owner)
        assert scheduler.detect_conflicts() == []

    def test_three_way_conflict_appears_once(self, today):
        owner = Owner("Busy")
        for name in ("Rex", "Fido", "Spot"):
            pet = Pet(name=name, species="dog")
            pet.add_task(Task("Walk", time="08:00", duration_minutes=20, due_date=today))
            owner.add_pet(pet)
        scheduler = Scheduler(owner)
        warnings = scheduler.detect_conflicts()
        assert len(warnings) == 1


# ---------------------------------------------------------------------------
# Scheduler – recurring tasks via mark_task_complete
# ---------------------------------------------------------------------------


class TestSchedulerRecurrence:
    def test_mark_complete_appends_next_task_to_pet(self, today):
        owner = Owner("Recurse")
        pet = Pet(name="Daily", species="dog")
        task = Task("Morning walk", time="07:00", duration_minutes=20,
                    frequency="daily", due_date=today)
        pet.add_task(task)
        owner.add_pet(pet)
        scheduler = Scheduler(owner)

        original_count = pet.task_count()
        scheduler.mark_task_complete(pet, task)
        assert pet.task_count() == original_count + 1

    def test_mark_complete_once_does_not_append(self, today):
        owner = Owner("Once")
        pet = Pet(name="Spot", species="dog")
        task = Task("Vet visit", time="10:00", duration_minutes=60,
                    frequency="once", due_date=today)
        pet.add_task(task)
        owner.add_pet(pet)
        scheduler = Scheduler(owner)

        scheduler.mark_task_complete(pet, task)
        assert pet.task_count() == 1  # no new task added
