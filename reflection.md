# PawPal+ Reflection

## 1. System Design

**a. Initial design**

The system uses four classes.
`Task` is a dataclass holding a care activity's description, time (HH:MM), duration, frequency (once/daily/weekly), priority, completion flag, and due date.
`Pet` owns a list of Tasks and exposes add, remove, and count methods.
`Owner` aggregates one or more Pets and provides `get_all_tasks()` which returns all (Pet, Task) pairs.
`Scheduler` holds a reference to the Owner and contains all sorting, filtering, conflict detection, and recurrence logic — it holds no task state itself, so it never goes out of sync.

The three core user actions identified before coding:
1. Add a pet to the owner's household.
2. Schedule a care task for a specific pet.
3. Generate and view today's sorted, conflict-checked schedule.

**b. Design changes**

The original sketch put conflict detection on `Pet`, checking only that pet's own tasks.
During implementation it became clear that conflicts almost always happen across pets (e.g., a dog's morning walk and a cat's breakfast both at 07:30), so the method moved to `Scheduler` where it can scan all pets in one pass.
`sort_by_priority` was also added as a first-class method — the initial UML only had time-based sorting.
`mark_complete()` was changed to return a new Task instead of mutating the existing one, so the completed task stays as an immutable record and the follow-up is a separate object.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers time (HH:MM), priority (high/medium/low), and due date.
Time is the default sort order because most pet care tasks have hard time constraints.
Priority is a secondary sort axis for quick triage when time is tight.
Due date is used for filtering — `todays_schedule()` only returns tasks due today.

**b. Tradeoffs**

The conflict detector only flags tasks that share an exact time string (e.g., both at "07:30").
It does not detect overlapping duration windows — two tasks at 07:00 (60 min) and 07:45 (30 min) would not be flagged even though they overlap.
This is acceptable for a pet-care app where most tasks are short and owners think in named time slots rather than precise durations.
A full interval-overlap check would require converting each task to a (start, end) range and sweeping — more correct but significantly more complex for the edge cases it covers.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used for three things: generating the initial UML sketch and discussing class responsibilities, producing dataclass skeletons and method stubs to establish consistent file structure early, and drafting the pytest suite including fixture ideas and edge-case suggestions.
Specific prompts worked better than broad ones — "given this `detect_conflicts()` method, what edge cases should the test suite cover?" was more useful than "help me test my app."

**b. Judgment and verification**

The initial AI-generated `mark_complete()` mutated the existing task's due_date and reset `completed` to False, recycling the same object.
This was rejected because it destroys completion history — the owner can no longer see that a task was done on a specific date.
The final version returns a new Task for the next occurrence while leaving the original completed.
Two tests were written to verify this: `test_recurrence_preserves_attributes` and `test_mark_complete_appends_next_task_to_pet`.

---

## 4. Testing and Verification

**a. What you tested**

23 tests cover: completion flag changes, recurrence object creation (daily and weekly), one-off tasks returning None, adding and removing tasks from a pet, owner aggregation across multiple pets, chronological sort correctness, priority sort ordering, pet-name filtering, completion-status filtering, due-date filtering, exact-time conflict detection, three-way conflict grouping, and the Scheduler recurrence integration path.
These matter because sorting and conflict detection bugs are invisible in the UI — a sort that silently produces the wrong order is worse than a crash.

**b. Confidence**

4/5. All 23 tests pass and cover the main paths and primary edge cases.
Main gap: no tests for invalid input (e.g., time string "25:99") since the implementation trusts the UI to validate before creating a Task.
Next tests to add: overlapping-duration conflicts, JSON serialization round-trips, multi-day schedule generation.

---

## 5. Reflection

**a. What went well**

Building and verifying `pawpal_system.py` through `main.py` before touching `app.py` was the most effective decision.
Every Streamlit button click connected to code that had already been shown to work in the terminal, which eliminated the worst debugging scenarios where UI state bugs and logic bugs look identical.

**b. What you would improve**

The `Task.time` field would be changed from a plain string to a `datetime.time` object.
HH:MM strings sort correctly lexicographically only when zero-padded — "9:00" would sort after "10:00" because "9" > "1".
The current code handles this by enforcing zero-padding in the UI, but using `datetime.time` would make the invariant explicit rather than implicit.

**c. Key takeaway**

AI is most useful as a fast first drafter, not a final decision maker.
Every AI suggestion needed to be evaluated against the system's actual invariants — the recurrence mutation bug is the clearest example of something that looked correct in isolation but broke a real requirement.
Acting as lead architect means keeping the design intent in your head and using it as the filter for everything the AI produces.
