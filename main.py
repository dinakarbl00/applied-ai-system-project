from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def banner(title: str) -> None:
    print(f"\n{'═' * 58}")
    print(f"  🐾  {title}")
    print(f"{'═' * 58}")


def print_tasks(title: str, task_list: list) -> None:
    """Print a readable list of (pet_name, Task) tuples."""
    print(f"\n  ── {title}")
    if not task_list:
        print("    (no tasks)")
        return
    for pet_name, task in task_list:
        status = "✅" if task.completed else "⬜"
        print(
            f"  {status} {task.priority_emoji()} {task.emoji()}  "
            f"[{task.due_time}]  {pet_name:10}  {task.description}"
        )


# ─────────────────────────────────────────────────────────────
# 1. SET UP OWNER AND PETS
# ─────────────────────────────────────────────────────────────

banner("1 · Owner & Pets")

owner = Owner(name="Jordan Lee", email="jordan@example.com")

buddy    = Pet(name="Buddy",    species="dog",    breed="Labrador",    age=3)
whiskers = Pet(name="Whiskers", species="cat",    breed="Siamese",     age=5)
thumper  = Pet(name="Thumper",  species="rabbit", breed="Holland Lop", age=2)

owner.add_pet(buddy)
owner.add_pet(whiskers)
owner.add_pet(thumper)

print(f"  Owner : {owner.name}")
for pet in owner.pets:
    print(f"          {pet.species_emoji()}  {pet.name} — {pet.breed}, age {pet.age}")


# ─────────────────────────────────────────────────────────────
# 2. ADD TASKS (intentionally out of order to test sorting)
# ─────────────────────────────────────────────────────────────

banner("2 · Add Tasks")

today = str(date.today())

buddy.add_task(Task("Evening walk",      "18:00", today, "daily",  "medium", task_type="walk"))
buddy.add_task(Task("Morning walk",      "07:30", today, "daily",  "high",   task_type="walk"))
buddy.add_task(Task("Breakfast feeding", "08:00", today, "daily",  "high",   task_type="feeding"))
buddy.add_task(Task("Heartworm pill",    "09:00", today, "weekly", "high",   task_type="medication"))
buddy.add_task(Task("Vet checkup",       "10:00", today, "once",   "high",   task_type="vet"))

whiskers.add_task(Task("Breakfast feeding", "08:00", today, "daily",  "high",   task_type="feeding"))
whiskers.add_task(Task("Flea medication",   "09:30", today, "weekly", "medium", task_type="medication"))
whiskers.add_task(Task("Playtime",          "15:00", today, "daily",  "low",    task_type="general"))

thumper.add_task(Task("Morning feeding", "07:00", today, "daily",  "high",   task_type="feeding"))
thumper.add_task(Task("Cage cleaning",   "11:00", today, "weekly", "medium", task_type="general"))
thumper.add_task(Task("Evening feeding", "18:00", today, "daily",  "high",   task_type="feeding"))

print(f"  Buddy    — {buddy.task_count()} tasks")
print(f"  Whiskers — {whiskers.task_count()} tasks")
print(f"  Thumper  — {thumper.task_count()} tasks")

scheduler = Scheduler(owner)


# ─────────────────────────────────────────────────────────────
# 3. SORTING
# ─────────────────────────────────────────────────────────────

banner("3 · Sorting")

print_tasks("Sorted by TIME only",          scheduler.sort_by_time())
print_tasks("Sorted by PRIORITY then time", scheduler.sort_by_priority_then_time())


# ─────────────────────────────────────────────────────────────
# 4. FILTERING
# ─────────────────────────────────────────────────────────────

banner("4 · Filtering")

print_tasks("Buddy's tasks only",         scheduler.filter_by_pet("Buddy"))
print_tasks("High priority tasks only",   scheduler.filter_by_priority("high"))
print_tasks("Today's tasks (smart view)", scheduler.get_todays_tasks())


# ─────────────────────────────────────────────────────────────
# 5. CONFLICT DETECTION
# ─────────────────────────────────────────────────────────────

banner("5 · Conflict Detection")

# Add a deliberate clash to demonstrate detection
buddy.add_task(Task("Grooming", "08:00", today, "once", "medium", task_type="vet"))

conflicts = scheduler.detect_conflicts()
if conflicts:
    print("\n  Conflicts found:")
    for c in conflicts:
        print(f"    {c}")
else:
    print("  No conflicts ✅")

buddy.remove_task("Grooming")
print("  (demo conflict removed)")


# ─────────────────────────────────────────────────────────────
# 6. COMPLETE TASKS + AUTO RESCHEDULING
# ─────────────────────────────────────────────────────────────

banner("6 · Complete & Reschedule")

print()
print("  " + scheduler.mark_task_complete_and_reschedule("Buddy",    "Morning walk"))
print("  " + scheduler.mark_task_complete_and_reschedule("Whiskers", "Breakfast feeding"))
print("  " + scheduler.mark_task_complete_and_reschedule("Buddy",    "Vet checkup"))

print_tasks("Buddy after completions", scheduler.filter_by_pet("Buddy"))


# ─────────────────────────────────────────────────────────────
# 7. NEXT AVAILABLE SLOT
# ─────────────────────────────────────────────────────────────

banner("7 · Next Available Slot")

tomorrow  = str(date.today() + timedelta(days=1))
print(f"\n  First free slot today    : {scheduler.find_next_available_slot(today,    '07:00')}")
print(f"  First free slot tomorrow : {scheduler.find_next_available_slot(tomorrow, '07:00')}")


# ─────────────────────────────────────────────────────────────
# 8. PRIORITY-WEIGHTED SCHEDULE
# ─────────────────────────────────────────────────────────────

banner("8 · Priority-Weighted Schedule")

print_tasks("Top 5 tasks by weighted score", scheduler.build_priority_schedule(today, max_tasks=5))


# ─────────────────────────────────────────────────────────────
# 9. SUMMARY
# ─────────────────────────────────────────────────────────────

banner("9 · Summary")

s = scheduler.get_summary()
print(f"\n  🐾 Pets           : {s['pets']}")
print(f"  📋 Total tasks    : {s['total']}")
print(f"  ✅ Completed      : {s['completed']}")
print(f"  ⬜ Pending        : {s['pending']}")
print(f"  🔴 High priority  : {s['high_priority_pending']}")


# ─────────────────────────────────────────────────────────────
# 10. DATA PERSISTENCE
# ─────────────────────────────────────────────────────────────

banner("10 · Save & Load Data")

owner.save_to_json("data.json")
print("  Saved to data.json")

loaded = Owner.load_from_json("data.json")
if loaded:
    total = sum(p.task_count() for p in loaded.pets)
    print(f"  Loaded owner : {loaded.name}")
    print(f"  Pets         : {[p.name for p in loaded.pets]}")
    print(f"  Tasks        : {total}")


print("\n\n  🎉  Demo complete!\n")