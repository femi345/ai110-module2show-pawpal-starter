"""
main.py — CLI demo script for PawPal+

Run with:  python main.py

This script exercises the full logic layer in pawpal_system.py without
touching Streamlit so the backend can be verified in the terminal alone.
"""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # ------------------------------------------------------------------ #
    # 1. Set up owner and pets
    # ------------------------------------------------------------------ #
    owner = Owner("Jordan")

    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # ------------------------------------------------------------------ #
    # 2. Add tasks in intentionally scrambled time order to test sorting
    # ------------------------------------------------------------------ #
    today = date.today()

    mochi.add_task(Task("Evening walk",      time="18:00", duration_minutes=30,
                        frequency="daily",  priority="high",   due_date=today))
    mochi.add_task(Task("Morning walk",      time="07:30", duration_minutes=20,
                        frequency="daily",  priority="high",   due_date=today))
    mochi.add_task(Task("Flea medication",   time="12:00", duration_minutes=5,
                        frequency="weekly", priority="high",   due_date=today))
    mochi.add_task(Task("Teeth brushing",    time="20:00", duration_minutes=5,
                        frequency="weekly", priority="low",    due_date=today))

    luna.add_task(Task("Breakfast feeding",  time="07:30", duration_minutes=10,
                       frequency="daily",   priority="high",   due_date=today))
    luna.add_task(Task("Playtime",           time="17:00", duration_minutes=15,
                       frequency="daily",   priority="medium", due_date=today))

    # ------------------------------------------------------------------ #
    # 3. Print the schedule
    # ------------------------------------------------------------------ #
    scheduler = Scheduler(owner)
    print(scheduler.format_schedule())

    # ------------------------------------------------------------------ #
    # 4. Demonstrate conflict detection
    # ------------------------------------------------------------------ #
    print("\n--- Conflict Detection Demo ---")
    print("(Mochi's 'Morning walk' and Luna's 'Breakfast feeding' are both at 07:30)")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for w in conflicts:
            print(w)
    else:
        print("No conflicts found.")

    # ------------------------------------------------------------------ #
    # 5. Demonstrate filtering
    # ------------------------------------------------------------------ #
    print("\n--- Filter: Luna's tasks only ---")
    for pet, task in scheduler.filter_tasks(pet_name="Luna"):
        print(f"  {pet.name}: {task}")

    print("\n--- Filter: high-priority tasks (all pets) ---")
    high_pairs = [(p, t) for p, t in scheduler.all_tasks() if t.priority == "high"]
    for pet, task in scheduler.sort_by_time(high_pairs):
        print(f"  [{pet.name}] {task}")

    # ------------------------------------------------------------------ #
    # 6. Demonstrate recurring task creation
    # ------------------------------------------------------------------ #
    print("\n--- Recurring Task Demo ---")
    morning_walk = mochi.tasks[1]  # "Morning walk" (index after add order)
    print(f"Completing: {morning_walk}")
    next_task = scheduler.mark_task_complete(mochi, morning_walk)
    if next_task:
        print(f"Next occurrence created: {next_task} (due {next_task.due_date})")

    # ------------------------------------------------------------------ #
    # 7. Sorted by priority
    # ------------------------------------------------------------------ #
    print("\n--- Priority-Sorted View ---")
    for pet, task in scheduler.sort_by_priority():
        print(f"  [{pet.name}] {task}")


if __name__ == "__main__":
    main()
